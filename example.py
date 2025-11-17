"""
Example usage and testing module for the Magi System.
"""
import json
from pathlib import Path

from agents.magi_system import MagiSystem


def run_example_queries():
    """
    Run example queries to demonstrate the Magi System.
    """
    # Initialise Magi System
    magi_system = MagiSystem()
    
    # Example queries
    example_queries = [
        "Should we invest in artificial general intelligence research?",
        "What are the implications of quantum computing for cybersecurity?",
        "How should society balance economic growth with environmental protection?",
    ]
    
    results = []
    
    for query in example_queries:
        print(f"\n\n{'#'*80}")
        print("# EXAMPLE QUERY")
        print(f"{'#'*80}\n")
        
        result = magi_system.query_magi(query)
        results.append(result)
        
        # Optional: save results to file
        Path("results").mkdir(exist_ok=True)
        with open(f"results/results_{result['timestamp'].replace(':', '-')}.json", "w") as f:
            json.dump(result, f, indent=2)
    
    return results


def run_single_query(question: str):
    """
    Run a single query for testing.
    """
    council = MagiSystem()
    result = council.query_magi(question)
    
    # Save result
    Path("results").mkdir(exist_ok=True)
    with open("results/example_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    return result


if __name__ == "__main__":
    # Run a single test query
    test_query = "What are the most important considerations when developing AI systems?"
    run_single_query(test_query)

    # Or run multiple example queries
    # run_example_queries()