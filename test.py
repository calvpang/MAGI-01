#!/usr/bin/env python3
"""
Quick start script for the Magi System.
Provides a simple interface to test the council with a single query.
"""
from agents.magi_system import MagiSystem
import sys

def quick_test():
    """Run a quick test query."""
    print("="*80)
    print("MAGI SYSTEM - Quick Test")
    print("="*80)
    print("\nInitialising MAGI System...\n")
    
    # Check if LM Studio is likely running
    print("⚠️  Make sure LM Studio is running on http://localhost:1234")
    print("⚠️  Make sure a model is loaded in LM Studio\n")
    
    try:
        magi = MagiSystem(
        )
        
        # Test query
        test_query = "What are the key benefits and risks of using AI in healthcare?"
        
        print(f"\nTest Query: {test_query}\n")
        _ = magi.query_magi(test_query)
        
        print("\n" + "="*80)
        print("✅ Test completed successfully!")
        print("="*80)
        print("\nYou can now run 'python main.py' for interactive mode")
        print("or 'python webui.py' to run a Streamlit interface.")
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ Error occurred:")
        print("="*80)
        print(f"\n{e}\n")
        print("Common issues:")
        print("1. LM Studio server not running")
        print("2. No model loaded in LM Studio")
        print("3. Wrong URL or port")
        print("4. Missing dependencies (run: pip install -e .)")
        print("\nPlease fix the issue and try again.")
        sys.exit(1)

if __name__ == "__main__":
    quick_test()
