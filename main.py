from agents.magi_system import MagiSystem

def main():
    """
    Main function to run the Magi System.
    """
    print("=" * 80)
    print("MAGI SYSTEM - Multi-Agent Council with Voting")
    print("=" * 80)
    print("\nInitialising MAGI System...\n")

    # Initialise the MAGI System (uses config.py settings)
    magi_system = MagiSystem()

    # Interactive mode
    print("\n" + "=" * 80)
    print("MAGI System ready! Type your questions below.")
    print("Commands: 'quit' to exit, 'clear' to clear memory")
    print("=" * 80 + "\n")

    while True:
        try:
            query = input("\nYour query: ").strip()

            if not query:
                continue

            if query.lower() in ["quit", "exit", "q"]:
                print("\nShutting down Magi Council. Goodbye!")
                break

            if query.lower() == "clear":
                magi_system.clear_all_memory()
                continue

            # Process query through magi_system
            _ = magi_system.query_magi(query)
            # Result is already printed by the process, but we could save it here

        except KeyboardInterrupt:
            print("\n\nInterrupted. Shutting down...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
