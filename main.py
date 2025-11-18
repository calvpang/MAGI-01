import json
from pathlib import Path

from agents.magi_system import MagiSystem
from config import RESULTS_DIR


def main():
    """
    Main function to run the MAGI System.
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
            result = magi_system.query_magi(query)

            # Save result to file
            Path(RESULTS_DIR).mkdir(exist_ok=True)
            result_dict = {
                "question": result["question"],
                "timestamp": result["timestamp"],
                "agent_responses": result["agent_responses"],
                "evaluation": result["evaluation"].model_dump(),
                "final_answer": result["final_answer"],
            }
            with open(
                f"{RESULTS_DIR}/results_{result['timestamp'].replace(':', '-')}.json",
                "w",
            ) as f:
                json.dump(result_dict, f, indent=2)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Shutting down...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
