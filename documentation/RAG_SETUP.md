# RAG Setup Guide for MAGI System

This guide explains how to set up and use the Retrieval-Augmented Generation (RAG) functionality in the MAGI system.

## Overview

The RAG feature allows MAGI agents to search and retrieve information from your own document collection using:

- **ChromaDB**: Vector database for storing document embeddings
- **LM Studio**: Provides embeddings through OpenAI-compatible API
- **LangChain**: Orchestrates document loading, splitting, and retrieval

## Prerequisites

### 1. Install RAG Dependencies

Install the optional RAG dependencies:

```bash
# Using pip
pip install -e ".[rag]"

# Or using uv
uv pip install -e ".[rag]"
```

This will install:
- `chromadb` - Vector database
- `pypdf` - PDF document support
- `unstructured` - Markdown and other document formats

### 2. Configure LM Studio for Embeddings

1. Open LM Studio
2. Load an embedding model (e.g., `nomic-ai/nomic-embed-text-v1.5` or similar)
3. Ensure the model is served at the endpoint in your `config.py`
4. Note the exact model name shown in LM Studio

## Configuration

In `config.py`, adjust these settings:

```python
# RAG Configuration
RAG_ENABLED = False  # Set to True to enable by default
RAG_COLLECTION_NAME = "magi_knowledge"  # ChromaDB collection name
RAG_PERSIST_DIR = "./chroma_db"  # Where to store the vector database
RAG_EMBEDDING_MODEL = "text-embedding-3-small"  # Your embedding model name from LM Studio
RAG_CHUNK_SIZE = 1000  # Text chunk size
RAG_CHUNK_OVERLAP = 200  # Overlap between chunks
RAG_SEARCH_K = 3  # Number of documents to retrieve per query
```

**Important**: Make sure `RAG_EMBEDDING_MODEL` matches the exact name shown in LM Studio.

## Usage

### Step 1: Ingest Documents

Use `ingest_documents.py` to load your documents:

```python
from ingest_documents import ingest_documents, ingest_from_directory, ingest_text_directly

# Method 1: Ingest specific files
files = ["documents/paper.pdf", "documents/notes.txt", "documents/readme.md"]
ingest_documents(files)

# Method 2: Ingest entire directory
ingest_from_directory("./documents", recursive=True)

# Method 3: Ingest text directly (no files needed)
texts = ["Your content here...", "More content..."]
metadatas = [{"source": "manual", "category": "guide"}]
ingest_text_directly(texts, metadatas)
```

Run the ingestion:

```bash
uv run ingest_documents.py
```

### Step 2: Enable RAG in Your Application

**Option A: Web UI (Recommended)**

1. Launch the Streamlit app: `python launch_webui.py`
2. In the sidebar, check "📚 Enable RAG (Knowledge Base)" before initialization
3. Click "Initialize System"
4. Agents will now have access to your knowledge base

**Option B: Programmatically**

```python
from agents.magi_system import MagiSystem

# Enable RAG when creating the system
system = MagiSystem(enable_search=True, enable_rag=True)
result = system.query_magi("What information do we have about quantum computing?")
```

**Option C: Config Default**

Set `RAG_ENABLED = True` in `config.py` to enable by default.

### Step 3: Query with MAGI Agents

The agents will automatically use the RAG tool when relevant:

```python
from agents.magi_system import MagiSystem

system = MagiSystem(enable_rag=True)
result = system.query_magi("What does our documentation say about X?")
```

The agents will:

1. Search DuckDuckGo for web information (if enabled)
2. Search the knowledge base using RAG (if enabled)
3. Combine both sources in their response

### Step 4: Verify RAG is Working

**Method 1: Debug Mode**

```python
# Enable debug mode to see tool calls
agent.respond("Your question", debug=True)
```

Look for tool calls to `knowledge_base_search` in the output.

**Method 2: Test Embeddings**

```bash
uv run test_embeddings.py
```

This will verify your LM Studio embedding setup is working correctly.

## Supported File Types

- **PDF** (`.pdf`)
- **Text** (`.txt`)
- **Markdown** (`.md`)

To add support for more file types, modify `ingest_documents.py`.

## How It Works

1. **Document Loading**: Files are loaded using appropriate LangChain loaders
2. **Text Splitting**: Documents are split into chunks (configurable size)
3. **Embedding**: Each chunk is embedded using LM Studio's embedding model
4. **Storage**: Embeddings are stored in ChromaDB
5. **Retrieval**: When agents query, similar chunks are retrieved
6. **Response**: Relevant chunks are provided as context to the agent

## Troubleshooting

### Dependencies not found

Make sure you installed the optional RAG dependencies:

```bash
pip install -e ".[rag]"
# or
uv pip install -e ".[rag]"
```

### Embedding API error: "'input' field must be a string or an array of strings"

This usually means:

1. **Wrong embedding model name**: Check that `RAG_EMBEDDING_MODEL` in `config.py` exactly matches the model name shown in LM Studio
2. **Model not loaded**: Ensure an embedding model is actually loaded and running in LM Studio
3. **Wrong endpoint**: Verify `LM_STUDIO_URL` is correct (default: `http://127.0.0.1:1234/v1`)

To test your setup:

```bash
uv run test_embeddings.py
```

### ChromaDB not found

```bash
pip install -e ".[rag]"
```

### No documents retrieved

- Verify documents were ingested successfully (check console output)
- Check ChromaDB directory exists: `./chroma_db`
- Try increasing `RAG_SEARCH_K` in `config.py` for more results
- Ensure the query is relevant to your ingested content

### Agent not using RAG

- **Web UI**: Ensure you checked "Enable RAG" before initializing the system
- **Code**: Pass `enable_rag=True` when creating `MagiSystem`
- **Config**: Set `RAG_ENABLED = True` in `config.py`
- The agent decides when to use RAG based on query relevance

### LM Studio connection issues

- Ensure LM Studio is running with the server started
- Verify the embedding model is loaded (not just the chat model)
- Check the base URL matches: `http://127.0.0.1:1234/v1`

## Advanced Usage

### Multiple Collections

Create separate knowledge bases for different topics:

```python
# Ingest scientific papers
ingest_documents(science_files, collection_name="science_kb")

# Ingest business docs
ingest_documents(business_files, collection_name="business_kb")

# Create agent with specific collection
agent = MagiAgent(..., rag_collection="science_kb")
```

### Custom Chunk Settings

Adjust for your document type:

```python
# For technical docs with dense content
ingest_documents(files, chunk_size=500, chunk_overlap=100)

# For narrative content
ingest_documents(files, chunk_size=2000, chunk_overlap=300)
```

### Programmatic Updates

Add documents dynamically:

```python
from rag_tool import RAGTool

rag = RAGTool(collection_name="magi_knowledge")
# Add new content to existing collection using ingest_documents
```

## Examples

See `ingest_example.py` for complete examples of:

- Ingesting specific files
- Batch ingesting from directories
- Direct text ingestion without files

## Tool Location

The RAG tool is located at `tools/rag_tool.py` and is automatically integrated with agents when enabled.

## Next Steps

1. Install RAG dependencies: `pip install -e ".[rag]"`
2. Create a `documents/` directory in your project
3. Add your documents (PDFs, text files, markdown)
4. Run `ingest_documents.py` to load them
5. Enable RAG in the Web UI or set `enable_rag=True` in code
6. Query your MAGI agents with questions about the content
7. Watch them combine web search + RAG for comprehensive answers!
