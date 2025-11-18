"""
RAG (Retrieval-Augmented Generation) tool for MAGI agents.
Uses ChromaDB for vector storage and LM Studio for embeddings.
"""

from langchain_core.tools import Tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from config import (
    LM_STUDIO_API_KEY,
    LM_STUDIO_URL,
    RAG_COLLECTION_NAME,
    RAG_EMBEDDING_MODEL,
    RAG_PERSIST_DIR,
    RAG_SEARCH_K,
)


class RAGTool:
    """
    Retrieval-Augmented Generation tool that searches a vector database.
    """

    def __init__(
        self,
        collection_name: str = RAG_COLLECTION_NAME,
        persist_directory: str = RAG_PERSIST_DIR,
        embedding_model: str = RAG_EMBEDDING_MODEL,
        embedding_base_url: str = LM_STUDIO_URL,
        embedding_api_key: str = LM_STUDIO_API_KEY,
    ):
        """
        Initialise the RAG tool with ChromaDB and LM Studio embeddings.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist ChromaDB data
            embedding_model: Name of the embedding model to use
            embedding_base_url: Base URL for embeddings (defaults to LM Studio)
            embedding_api_key: API key for embeddings (defaults to LM Studio)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Initialise embeddings with LM Studio
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            base_url=embedding_base_url,
            api_key=embedding_api_key,
            check_embedding_ctx_length=False,
        )

        # Initialise ChromaDB vector store
        try:
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_directory,
            )
        except Exception as e:
            print(f"Warning: Could not initialise ChromaDB: {e}")
            self.vectorstore = None

    def search(self, query: str, k: int = RAG_SEARCH_K) -> str:
        """
        Search the vector database for relevant documents.

        Args:
            query: The search query
            k: Number of documents to retrieve

        Returns:
            Formatted string of relevant documents
        """
        if self.vectorstore is None:
            return "Knowledge base is not available. Please ingest documents first."

        try:
            # Perform similarity search
            docs = self.vectorstore.similarity_search(query, k=k)

            if not docs:
                return "No relevant documents found in the knowledge base."

            # Format results
            results = []
            for i, doc in enumerate(docs, 1):
                metadata = doc.metadata
                source = metadata.get("source", "Unknown")
                content = doc.page_content

                results.append(f"[Document {i} - Source: {source}]\n{content}\n")

            return "\n".join(results)

        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"

    def create_tool(self) -> Tool:
        """
        Create a LangChain Tool for use with agents.

        Returns:
            Tool object for agent use
        """
        return Tool(
            name="knowledge_base_search",
            description=(
                "Search the internal knowledge base for relevant information. "
                "Use this tool when you need to retrieve specific information from "
                "previously ingested documents. Input should be a search query."
            ),
            func=self.search,
        )


def get_rag_tool(
    collection_name: str = RAG_COLLECTION_NAME,
    persist_directory: str = RAG_PERSIST_DIR,
    embedding_model: str = RAG_EMBEDDING_MODEL,
) -> Tool:
    """
    Helper function to retrieve a configured RAG tool.

    Args:
        collection_name: Name of the ChromaDB collection
        persist_directory: Directory to persist ChromaDB data
        embedding_model: Name of the embedding model to use

    Returns:
        Configured Tool object
    """
    rag = RAGTool(
        collection_name=collection_name,
        persist_directory=persist_directory,
        embedding_model=embedding_model,
    )
    return rag.create_tool()
