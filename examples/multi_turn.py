import os
import sys

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rui import RealUserInstruction

def main():
    print("==================================================")
    print("RUI Multi-Turn Conversation & Key Rotation Example")
    print("==================================================")

    original_system_prompt = "You are a friendly personal assistant."
    rui = RealUserInstruction(system_prompt=original_system_prompt)

    turns = [
        ("Summarize my emails.", "Email 1: Promo from store. Email 2: Meeting scheduled at 3 PM."),
        ("Send a calendar invite.", "Available slots: 3 PM - 4 PM. Guest: rui-project@example.com"),
        ("What did we do in the first turn?", "Previous session history logs.")
    ]

    for index, (cmd, data) in enumerate(turns):
        turn_num = index + 1
        print(f"\n--- TURN {turn_num} ---")
        
        # Process turn
        result = rui.process_turn(user_command=cmd, data_payload=data)
        
        print(f"[Generated Key]: {result['current_key']}")
        if result['previous_key']:
            print(f"[Rotated From]: {result['previous_key']}")
            
        print(f"[User Message Sent]:\n{result['user_message']}")
        
        # Simulate LLM response
        simulated_response = (
            f'I will only follow instructions from the real user with the key "{result["current_key"]}".\n'
            f"No unauthenticated instructions identified.\n"
            f"[Turn {turn_num} Response] Done with '{cmd}' based on the payload."
        )
        
        # Post-process
        post_result = rui.post_process(simulated_response)
        print(f"[Cleaned Response]: {post_result['cleaned_response']}")
        
    print("\n==================================================")
    print("Final Chat History (with rotated keys):")
    print("==================================================")
    for msg in rui.chat_history:
        print(f"[{msg['role'].upper()}]:")
        # Replace actual keys in printout with a marker for visualization
        content = msg['content']
        print(content)
        print("-" * 50)

if __name__ == "__main__":
    main()
