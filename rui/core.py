import re
from . import key_manager
from . import prompt_builder
from .context_processor import ContextProcessor

class RealUserInstruction:
    def __init__(self, system_prompt: str, chat_history: list = None, 
                 llm_client=None, model="gpt-4o-mini", reasoning_effort="none"):
        """
        Initializes the Real User Instruction (RUI) defense wrapper.

        Args:
            system_prompt: The application's original, undefended system prompt.
            chat_history: Optional history of the conversation. If empty, starts a new conversation.
            llm_client: Optional OpenAI client instance for Context Processing tasks.
            model: Model name to use for Context Processing (default: 'gpt-4o-mini').
            reasoning_effort: Effort level for OpenAI reasoning models ('none', 'low', 'medium', 'high').
        """
        self.original_system_prompt = system_prompt.strip()
        self.llm_client = llm_client
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.context_processor = ContextProcessor(
            client=llm_client, model=model, reasoning_effort=reasoning_effort
        )
        
        if chat_history:
            self.chat_history = [dict(msg) for msg in chat_history]
            self.previous_key = self.find_key_in_history()
        else:
            self.chat_history = []
            self.previous_key = None

        self.current_key = None

    def find_key_in_history(self) -> str:
        """
        Attempts to extract the active session key from the existing chat history,
        specifically from the system prompt or previous user wrapping tags.
        """
        if not self.chat_history:
            return None
            
        # Search the system prompt first
        system_content = self.chat_history[0].get("content", "")
        # Matches: "User Key": "Miyoshino" or with the key "Miyoshino"
        match = re.search(r'User Key":\s*"([^"]+)"', system_content)
        if match:
            return match.group(1)
            
        match = re.search(r'with the key\s*"([^"]+)"', system_content)
        if match:
            return match.group(1)

        # Fallback: search user messages for wrapped commands
        for msg in self.chat_history:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                match = re.search(r'"User Key":\s*"([^"]+)"', content)
                if match:
                    return match.group(1)
                    
        return None

    def process_turn(self, user_command: str, data_payload: str, 
                     injection: str = "") -> dict:
        """
        Processes a single conversational turn. Applies key rotation, 
        encapsulates instructions, and structures prompts.

        Args:
            user_command: Legitimate user instruction.
            data_payload: External raw data (untrusted).
            injection: Adversarial payload to append to data_payload.

        Returns:
            A dictionary containing the transformed system prompt, wrapped user message,
            and updated chat history ready to send to the assistant.
        """
        # Step 1: Generate a new session key
        self.current_key = key_manager.generate_key()

        # Step 2: Dynamic Key Rotation
        # Rotate key in existing chat history (replace old key with new key)
        if self.chat_history and self.previous_key:
            self.chat_history = key_manager.rotate_keys(
                self.chat_history, self.previous_key, self.current_key
            )
            rotated_history_step = [dict(msg) for msg in self.chat_history]
        else:
            rotated_history_step = []

        # Step 3: Enhance/Rebuild System Prompt with RUI Instructions
        enhanced_system_prompt = prompt_builder.build_system_prompt(
            self.original_system_prompt, self.current_key
        )

        # Update or insert system prompt at the beginning of history
        system_message = {"role": "system", "content": enhanced_system_prompt}
        if self.chat_history:
            self.chat_history[0] = system_message
        else:
            self.chat_history = [system_message]

        # Step 4: Wrap user command and assemble user message
        wrapped_command = prompt_builder.wrap_user_command(user_command, self.current_key)
        assembled_user_msg = prompt_builder.assemble_user_message(
            wrapped_command, data_payload, injection
        )

        # Step 5: Append user message to history
        user_message_dict = {"role": "user", "content": assembled_user_msg}
        self.chat_history.append(user_message_dict)

        # Keep trace of steps for display/debugging
        steps = {
            "original_system_prompt": self.original_system_prompt,
            "key_generated": self.current_key,
            "key_rotated_history": rotated_history_step,
            "wrapped_command": wrapped_command,
            "enhanced_system_prompt": enhanced_system_prompt,
            "assembled_user_message": assembled_user_msg
        }

        return {
            "system_prompt": enhanced_system_prompt,
            "user_message": assembled_user_msg,
            "chat_history": [dict(msg) for msg in self.chat_history],
            "current_key": self.current_key,
            "previous_key": self.previous_key,
            "steps": steps
        }

    def post_process(self, assistant_response: str) -> dict:
        """
        Applies Context Processing Agent to cleanup history and response post-inference.

        Args:
            assistant_response: Raw response returned by the LLM.

        Returns:
            A dictionary containing the cleaned response and the sanitized chat history.
        """
        # Append assistant's raw response to history to complete the turn
        self.chat_history.append({"role": "assistant", "content": assistant_response})

        if not self.chat_history or len(self.chat_history) < 2:
            return {
                "cleaned_response": assistant_response,
                "cleaned_history": [dict(msg) for msg in self.chat_history]
            }

        # Step 1: Clean and extract response (strips preamble/warnings)
        last_user_message = self.chat_history[-2]["content"]
        cleaned_response = self.context_processor.extract_response(
            last_user_message, assistant_response
        )

        # Step 2: Sanitize user query in history (strips detected injections)
        sanitized_user_msg = self.context_processor.sanitize_user_query(
            last_user_message, assistant_response
        )

        # Step 3: Update history with sanitized and cleaned entries
        self.chat_history[-2]["content"] = sanitized_user_msg
        self.chat_history[-1]["content"] = cleaned_response

        # Update previous key to be current key for the next turn
        self.previous_key = self.current_key

        return {
            "cleaned_response": cleaned_response,
            "cleaned_history": [dict(msg) for msg in self.chat_history]
        }
