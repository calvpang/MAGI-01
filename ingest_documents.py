"""
Document ingestion utility for the MAGI system.
Loads documents and adds them to the ChromaDB vector store.
"""

import os
from pathlib import Path
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    LM_STUDIO_API_KEY,
    LM_STUDIO_URL,
    RAG_CHUNK_OVERLAP,
    RAG_CHUNK_SIZE,
    RAG_COLLECTION_NAME,
    RAG_EMBEDDING_MODEL,
    RAG_PERSIST_DIR,
)


def ingest_documents(
    file_paths: List[str],
    collection_name: str = RAG_COLLECTION_NAME,
    persist_directory: str = RAG_PERSIST_DIR,
    embedding_model: str = RAG_EMBEDDING_MODEL,
    embedding_base_url: str = LM_STUDIO_URL,
    embedding_api_key: str = LM_STUDIO_API_KEY,
    chunk_size: int = RAG_CHUNK_SIZE,
    chunk_overlap: int = RAG_CHUNK_OVERLAP,
) -> int:
    """
    Ingest documents into the ChromaDB vector store.

    Args:
        file_paths: List of file paths to ingest
        collection_name: Name of the ChromaDB collection
        persist_directory: Directory to persist ChromaDB data
        embedding_model: Name of the embedding model to use
        embedding_base_url: Base URL for embeddings (defaults to LM Studio)
        embedding_api_key: API key for embeddings (defaults to LM Studio)
        chunk_size: Size of text chunks for splitting
        chunk_overlap: Overlap between chunks

    Returns:
        Number of document chunks added to the vector store
    """
    # Initialise embeddings with LM Studio
    embeddings = OpenAIEmbeddings(
        model=embedding_model,
        base_url=embedding_base_url,
        api_key=embedding_api_key,
        check_embedding_ctx_length=False,  # Disable length validation
    )

    # Test embeddings before proceeding
    print(f"Testing embeddings with model: {embedding_model}")
    try:
        test_result = embeddings.embed_query("test")
        print(f"✓ Embeddings working! Dimension: {len(test_result)}")
    except Exception as e:
        print(f"✗ Embedding test failed: {e}")
        print("Please ensure LM Studio is running with an embedding model loaded.")
        return 0

    # Initialise text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    # Load and process documents
    all_documents = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Warning: File not found - {file_path}")
            continue

        file_extension = Path(file_path).suffix.lower()

        try:
            # Choose loader based on file type
            if file_extension == ".pdf":
                loader = PyPDFLoader(file_path)
            elif file_extension == ".md":
                loader = UnstructuredMarkdownLoader(file_path)
            elif file_extension in [".txt", ".text"]:
                loader = TextLoader(file_path)
            else:
                print(f"Warning: Unsupported file type - {file_path}")
                continue

            # Load documents
            documents = loader.load()

            # Add source metadata
            for doc in documents:
                doc.metadata["source"] = file_path

            # Split documents into chunks
            chunks = text_splitter.split_documents(documents)
            all_documents.extend(chunks)

            print(f"✓ Loaded {len(chunks)} chunks from {file_path}")

        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            continue

    if not all_documents:
        print("No documents were successfully loaded.")
        return 0

    # Clean and validate documents
    cleaned_documents = []
    for doc in all_documents:
        # Ensure page_content is a string and not empty
        if isinstance(doc.page_content, str) and doc.page_content.strip():
            # Ensure metadata values are serializable (strings, numbers, booleans)
            clean_metadata = {}
            for key, value in doc.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                else:
                    clean_metadata[key] = str(value)

            cleaned_doc = Document(
                page_content=doc.page_content.strip(), metadata=clean_metadata
            )
            cleaned_documents.append(cleaned_doc)

    if not cleaned_documents:
        print("No valid documents after cleaning.")
        return 0

    print(f"Cleaned {len(cleaned_documents)} documents for ingestion...")

    # Initialise ChromaDB vector store
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    # Add documents to vector store
    try:
        # Add documents in batches to avoid API issues
        batch_size = 50
        total_added = 0

        for i in range(0, len(cleaned_documents), batch_size):
            batch = cleaned_documents[i : i + batch_size]
            try:
                vectorstore.add_documents(batch)
                total_added += len(batch)
                print(f"  Added batch {i // batch_size + 1}: {len(batch)} documents")
            except Exception as batch_error:
                print(f"  Error in batch {i // batch_size + 1}: {str(batch_error)}")
                # Try adding documents one by one in this batch
                for doc in batch:
                    try:
                        vectorstore.add_documents([doc])
                        total_added += 1
                    except Exception as doc_error:
                        print(f"    Skipped document: {str(doc_error)[:100]}")

        print(
            f"\n✓ Successfully added {total_added} document chunks to the vector store."
        )
        print(f"  Collection: {collection_name}")
        print(f"  Location: {persist_directory}")
        return total_added

    except Exception as e:
        print(f"Error adding documents to vector store: {str(e)}")
        return 0


def ingest_from_directory(
    directory_path: str,
    collection_name: str = RAG_COLLECTION_NAME,
    persist_directory: str = RAG_PERSIST_DIR,
    embedding_model: str = RAG_EMBEDDING_MODEL,
    recursive: bool = True,
    file_extensions: Optional[List[str]] = None,
) -> int:
    """
    Ingest all supported documents from a directory.

    Args:
        directory_path: Path to the directory containing documents
        collection_name: Name of the ChromaDB collection
        persist_directory: Directory to persist ChromaDB data
        embedding_model: Name of the embedding model to use
        recursive: Whether to search subdirectories
        file_extensions: List of file extensions to include (e.g., ['.pdf', '.txt'])

    Returns:
        Number of document chunks added to the vector store
    """
    if file_extensions is None:
        file_extensions = [".pdf", ".txt", ".md"]

    # Find all files with supported extensions
    directory = Path(directory_path)
    file_paths = []

    if recursive:
        for ext in file_extensions:
            file_paths.extend([str(f) for f in directory.rglob(f"*{ext}")])
    else:
        for ext in file_extensions:
            file_paths.extend([str(f) for f in directory.glob(f"*{ext}")])

    if not file_paths:
        print(f"No files found in {directory_path} with extensions {file_extensions}")
        return 0

    print(f"Found {len(file_paths)} files to ingest:")
    for fp in file_paths:
        print(f"  - {fp}")
    print()

    return ingest_documents(
        file_paths=file_paths,
        collection_name=collection_name,
        persist_directory=persist_directory,
        embedding_model=embedding_model,
    )


def ingest_text_directly(
    texts: List[str],
    metadatas: Optional[List[dict]] = None,
    collection_name: str = RAG_COLLECTION_NAME,
    persist_directory: str = RAG_PERSIST_DIR,
    embedding_model: str = RAG_EMBEDDING_MODEL,
    chunk_size: int = RAG_CHUNK_SIZE,
    chunk_overlap: int = RAG_CHUNK_OVERLAP,
) -> int:
    """
    Ingest text content directly without loading from files.

    Args:
        texts: List of text strings to ingest
        metadatas: Optional list of metadata dicts for each text
        collection_name: Name of the ChromaDB collection
        persist_directory: Directory to persist ChromaDB data
        embedding_model: Name of the embedding model to use
        chunk_size: Size of text chunks for splitting
        chunk_overlap: Overlap between chunks

    Returns:
        Number of document chunks added to the vector store
    """
    # Initialise embeddings
    embeddings = OpenAIEmbeddings(
        model=embedding_model,
        base_url=LM_STUDIO_URL,
        api_key=LM_STUDIO_API_KEY,
        check_embedding_ctx_length=False,  # Disable length validation
    )

    # Initialise text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    # Create documents
    documents = []
    for i, text in enumerate(texts):
        metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
        if "source" not in metadata:
            metadata["source"] = f"direct_input_{i}"
        documents.append(Document(page_content=text, metadata=metadata))

    # Split documents
    chunks = text_splitter.split_documents(documents)

    # Clean and validate documents
    cleaned_chunks = []
    for doc in chunks:
        if isinstance(doc.page_content, str) and doc.page_content.strip():
            clean_metadata = {}
            for key, value in doc.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                else:
                    clean_metadata[key] = str(value)

            cleaned_doc = Document(
                page_content=doc.page_content.strip(), metadata=clean_metadata
            )
            cleaned_chunks.append(cleaned_doc)

    if not cleaned_chunks:
        print("No valid documents after cleaning.")
        return 0

    # Initialise ChromaDB vector store
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    # Add documents
    try:
        # Add documents in batches
        batch_size = 50
        total_added = 0

        for i in range(0, len(cleaned_chunks), batch_size):
            batch = cleaned_chunks[i : i + batch_size]
            try:
                vectorstore.add_documents(batch)
                total_added += len(batch)
            except Exception as batch_error:
                print(f"Error in batch {i // batch_size + 1}: {str(batch_error)}")
                # Try one by one
                for doc in batch:
                    try:
                        vectorstore.add_documents([doc])
                        total_added += 1
                    except Exception:
                        pass

        print(
            f"✓ Successfully added {total_added} document chunks to the vector store."
        )
        return total_added
    except Exception as e:
        print(f"Error adding documents to vector store: {str(e)}")
        return 0


if __name__ == "__main__":
    # Example usage
    print("MAGI Document Ingestion Utility")
    print("=" * 60)

    # Example 1: Ingest specific files
    example_files = [
        "documents/example.pdf",
        "documents/readme.txt",
    ]
    # Uncomment to run:
    # ingest_documents(example_files)

    # Example 2: Ingest from directory
    # ingest_from_directory(
    #     directory_path="./documents",
    #     recursive=True,
    # )

    # Example 3: Ingest text directly
    example_texts = [
        "The MAGI system is a multi-agent AI council inspired by Neon Genesis Evangelion.",
        "It utilizes advanced AI technologies and a knowledge base to provide informed responses.",
    ]

    example_metadata = [
        {"source": "system_description", "category": "overview"},
        {"source": "technology_info", "category": "database"},
    ]

    # Uncomment to run:
    # ingest_text_directly(example_texts, example_metadata)

    print("\nTo use this utility, uncomment one of the example calls above")
    print("or create your own ingestion script.")
