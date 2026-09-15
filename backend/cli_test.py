"""
CLI test harness for GadgetMart conversation manager.
For manual multi-turn conversation testing.
"""

from backend.conversation_manager import ConversationManager


def print_banner():
    """Print welcome banner."""
    print("=" * 70)
    print("GadgetMart Assistant - CLI Test Harness")
    print("=" * 70)
    print("\nCommands:")
    print("  /reset   - Reset current session (clear history)")
    print("  /new     - Start a new session")
    print("  /info    - Show session information")
    print("  /exit    - Exit the CLI")
    print("\nType your message and press Enter to chat.")
    print("=" * 70)


def print_session_info(manager, session_id):
    """Print session information."""
    info = manager.get_session_info(session_id)
    if info:
        print(f"\n[Session Info]")
        print(f"  ID: {session_id}")
        print(f"  Turns: {info['turn_count']}")
        print(f"  Created: {info['created_at']}")
        print(f"  Last activity: {info['last_activity']}")
        print()


def main():
    """Run interactive CLI."""
    print_banner()
    
    # Check Ollama availability
    manager = ConversationManager()
    
    print("\n[Checking Ollama availability...]")
    if not manager.ollama_client.health_check():
        print("[WARNING] Ollama does not appear to be running.")
        print("Make sure Ollama is started: ollama serve")
        print("And the model is available: ollama list")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    else:
        print("[OK] Ollama is available")
    
    # Create initial session
    session_id = manager.create_session()
    print(f"\n[Session created: {session_id[:8]}...]")
    print("\nYou can start chatting now.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input == "/exit":
                print("\nGoodbye!")
                break
            
            elif user_input == "/reset":
                manager.reset_session(session_id)
                print("[Session history cleared]\n")
                continue
            
            elif user_input == "/new":
                session_id = manager.create_session()
                print(f"[New session created: {session_id[:8]}...]\n")
                continue
            
            elif user_input == "/info":
                print_session_info(manager, session_id)
                continue
            
            # Get response from assistant
            print("Assistant: ", end="", flush=True)
            response = manager.get_response(session_id, user_input)
            
            if response:
                print(response)
            else:
                print("[ERROR: Failed to get response]")
            
            print()  # Blank line for readability
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Use /exit to quit properly.")
            print()
        
        except Exception as e:
            print(f"\n[ERROR: {type(e).__name__}: {e}]\n")


if __name__ == "__main__":
    main()
