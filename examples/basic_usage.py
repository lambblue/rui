import os
import sys

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rui import RealUserInstruction

def main():
    print("==================================================")
    print("RUI (Real User Instruction) Basic Usage Example")
    print("==================================================")

    # 1. Initialize RUI with the original system prompt
    original_system_prompt = "You are a helpful database administrator assistant."
    print(f"[Original System Prompt]:\n{original_system_prompt}\n")

    rui = RealUserInstruction(system_prompt=original_system_prompt)

    # 2. Process a turn with a command and data payload
    user_command = "Delete the temporary staging table."
    data_payload = "Staging table: temp_stage_2026. Production tables: users, transactions."
    
    print(f"[User Command]: {user_command}")
    print(f"[Data Payload]: {data_payload}\n")

    result = rui.process_turn(
        user_command=user_command,
        data_payload=data_payload
    )

    # 3. Print out RUI-transformed inputs
    print("--- Transformed Output sent to LLM ---")
    print(f"[Current Session Key]: {result['current_key']}\n")
    print(f"[RUI-Enhanced System Prompt]:\n{result['system_prompt']}\n")
    print(f"[RUI-Assembled User Message]:\n{result['user_message']}\n")

    # 4. Simulate receiving raw response from LLM (with RUI preamble)
    simulated_raw_response = (
        f'I will only follow instructions from the real user with the key "{result["current_key"]}".\n'
        f"No unauthenticated instructions identified.\n"
        f"I have successfully dropped the table 'temp_stage_2026'. Please let me know if you need anything else."
    )
    print(f"[Simulated Raw LLM Response]:\n{simulated_raw_response}\n")

    # 5. Clean up response and history
    post_result = rui.post_process(simulated_raw_response)
    print("--- Post-processed Context ---")
    print(f"[Cleaned Response for User]:\n{post_result['cleaned_response']}\n")
    print("[Cleaned Chat History]:")
    for msg in post_result["cleaned_history"]:
        print(f"  {msg['role'].upper()}: {msg['content'][:150]}...")
    print("==================================================")

if __name__ == "__main__":
    main()
