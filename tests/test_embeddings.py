"""
Test script to verify embedding setup with LM Studio.
"""

import sys

sys.path.append("..")
from langchain_openai import OpenAIEmbeddings

from config import LM_STUDIO_API_KEY, LM_STUDIO_URL, RAG_EMBEDDING_MODEL


def test_embeddings():
    """Test if embeddings are working properly with LM Studio."""
    print("Testing LM Studio Embeddings")
    print("=" * 60)
    print(f"Model: {RAG_EMBEDDING_MODEL}")
    print(f"Base URL: {LM_STUDIO_URL}")
    print()

    # Initialise embeddings
    try:
        embeddings = OpenAIEmbeddings(
            model=RAG_EMBEDDING_MODEL,
            base_url=LM_STUDIO_URL,
            api_key=LM_STUDIO_API_KEY,
            check_embedding_ctx_length=False,
        )
        print("✓ Embeddings initialised successfully")
    except Exception as e:
        print(f"✗ Failed to initialise embeddings: {e}")
        return False

    # Test with a single string
    test_text = "This is a test sentence for embedding."
    print(f"\nTest 1: Single string embedding")
    print(f"Text: '{test_text}'")

    try:
        result = embeddings.embed_query(test_text)
        print(f"✓ Success! Embedding dimension: {len(result)}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        print(f"\nError details: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False

    # Test with multiple strings
    test_texts = [
        "First test sentence.",
        "Second test sentence.",
        "Third test sentence.",
    ]
    print(f"\nTest 2: Multiple string embeddings")
    print(f"Number of texts: {len(test_texts)}")

    try:
        results = embeddings.embed_documents(test_texts)
        print(f"✓ Success! Generated {len(results)} embeddings")
        print(f"  Each embedding dimension: {len(results[0])}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        print(f"\nError details: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✓ All embedding tests passed!")
    print("Your LM Studio embedding setup is working correctly.")
    return True


if __name__ == "__main__":
    success = test_embeddings()
    if not success:
        print("\n" + "=" * 60)
        print("Troubleshooting tips:")
        print("1. Ensure LM Studio is running")
        print("2. Verify an embedding model is loaded")
        print("3. Check that the model name matches exactly")
        print("4. Verify the base URL is correct (default: http://127.0.0.1:1234/v1)")
        print("=" * 60)
