# MAGI System

A multi-agent LLM application using LangChain and LM Studio or Google Gemini, where multiple AI agents with different personalities collaborate, search for information, and vote on responses through an independent judge agent.

## 🚀 Quick Start - Web UI

```bash
# 1. Choose your LLM provider:
#    - LM Studio (local, free, private) - OR -
#    - Google Gemini (cloud, fast, $0.001/query)

# 2. Install dependencies
pip install -e .  # or: uv sync

# 3. Launch Web UI
python3 launch_webui.py

```

**That's it!** The web interface will open in your browser automatically. 🎉

---

## Overview

The Magi System is inspired by the MAGI supercomputer system, featuring a council of three AI agents with distinct personalities:

- **MELCHIOR**: Scientific & Analytical perspective
- **BALTHASAR**: Strategic & Pragmatic perspective  
- **CASPER**: Ethical & Philosophical perspective

Each agent can:

- Search the web using DuckDuckGo
- Query with RAG using ChromaDB
- Maintain conversation memory using SQL storage
- Respond based on their unique personality and expertise

An independent **Deliberator Agent** evaluates all responses, scores them, and synthesises a final answer.

## Architecture

```
User Query
    ↓
Council (3 Agents in parallel)
    ├── MELCHIOR (Scientist) → Response + Search + RAG
    ├── BALTHASAR (Strategist) → Response + Search + RAG
    └── CASPER (Ethicist) → Response + Search + RAG
    ↓
Judge Agent
    ├── Evaluates responses
    ├── Scores each agent
    └── Synthesises final answer
    ↓
Final Output
```

## Features

- **Multi-Agent Council**: Three agents with distinct personalities and reasoning approaches
- **Web Search**: Each agent can search DuckDuckGo for real-time information (toggleable)
- **RAG (Knowledge Base)**: Agents can search your own documents using ChromaDB and embeddings (toggleable)
- **Memory**: Conversation history persisted in SQLite for each agent and deliberator
- **Independent Deliberation**: Objective evaluation and vote aggregation with Pydantic models
- **Dual LLM Support**: Choose between LM Studio (local) or Google Gemini (cloud)
- **LangChain Orchestration**: Built on LangChain for agent management
- **🎨 Streamlit Web UI**: Interactive interface with tool toggles
- **📜 History Tracking**: Built-in query history and JSON export
- **Structured Output**: Type-safe responses using Pydantic models

## User Interfaces

### 🌐 Web UI (Recommended)

Interactive Streamlit interface with visual feedback:

```bash
python launch_webui.py
```

### 💻 Command Line

Traditional terminal interface:

```bash
python main.py
```

## Prerequisites

1. **LM Studio**: Download and install from [lmstudio.ai](https://lmstudio.ai)
2. **Python 3.11+**: Required for running the application
3. **Model**: Load a model in LM Studio (e.g., Llama 3, Mistral, etc.)

## Installation

1. **Clone or navigate to the project directory**:
```bash
cd MAGI-01
```

2. **Install dependencies**:
```bash
pip install -e . # or uv sync
```

## Setup

### 1. Start LM Studio Server

1. Open LM Studio
2. Load a chat model (recommended: Llama-3-8B or similar)
3. **(Optional)** Load an embedding model if using RAG (e.g., nomic-embed-text)
4. Click "Start Server" (default: `http://localhost:1234`)
5. Note the model names shown in LM Studio

### 2. Configure Model (Optional)

If your LM Studio server runs on a different port or you want to specify the model name, edit `config.py`:

```python
LM_STUDIO_URL = "http://localhost:1234/v1"  # Change if needed
LM_STUDIO_MODEL = "your-model-name"  # Change to match your loaded chat model
RAG_EMBEDDING_MODEL = "your-model-name"  # Change to match embedding model
RAG_ENABLED = False  # Set to True to enable RAG by default
```

### 3. RAG Setup (Optional)

To enable document search capabilities, see the [RAG Setup Guide](documentation/RAG_SETUP.md) for detailed instructions.

**Quick start:**

```bash
# Install RAG dependencies
uv sync --extra rag

# Ingest documents
python ingest_documents.py

# Enable in Web UI: Toggle "Enable RAG" before initialisation
# Or in config.py: Set RAG_ENABLED = True
```

The RAG system allows agents to search your own documents using ChromaDB and embeddings from LM Studio.

## Project Structure

```
MAGI-01/
├── agents/                      # Core agent modules
│   ├── magi_agent.py           # Individual Magi agent with search & memory
│   ├── magi_deliberator.py     # Deliberator agent for evaluation & synthesis
│   ├── magi_system.py          # System orchestration & coordination
│   └── personalities.py         # Agent personality definitions
├── chroma_db/                  # ChromaDB vector store (auto-created)
├── documentation/              # Additional documentation
│   └── ARCHITECTURE.md         # Architecture diagram
│   └── RAG_SETUP.md             # RAG setup guide
├── results/                    # Query results & exports (auto-created)
├── tests/                       # Agent tools
│   └── test_embeddings.py       # Test embedding setup
│   └── test_magi_system.py       # Test magi_system
├── tools/                       # Agent tools
│   └── rag_tool.py             # RAG tool for document search
├── .env                        # Environment variables (API keys)
├── .gitignore                  # Git ignore rules
├── config.py                    # Configuration (LLM provider, models, etc.)
├── example.py                   # Quick example/demo script
├── ingest_documents.py         # Document ingestion utilities
├── launch_webui.py             # Web UI launcher script
├── magi_agent_history.db       # SQLite database (auto-created)
├── main.py                      # CLI entry point
├── pyproject.toml              # Project dependencies & metadata
├── README.md                   # This file
└── streamlit_app.py            # Streamlit web interface                   
```

## How It Works

### 1. Query Submission
When you submit a question, it's sent to all three MAGI agents simultaneously.

### 2. Agent Processing

Each agent:

- Receives the query with their personality context
- Can search DuckDuckGo for relevant information (if enabled)
- Can search the knowledge base using RAG (if enabled)
- Accesses their conversation memory
- Generates a response based on their unique perspective

### 3. Evaluation

The Deliberator agent:

- Receives all agent responses
- Scores each response (1-10) based on relevance, depth, evidence, and value
- Identifies agreements and contradictions
- Provides reasoning for scores

### 4. Synthesis

The Deliberator creates a final synthesised answer that:

- Incorporates the best elements from each perspective
- Resolves conflicts between agents
- Provides a comprehensive recommendation

## Customisation

### Tool Configuration

Toggle tools in the Streamlit Web UI before initialisation, or set defaults in `config.py`:

```python
# Enable/disable tools
RAG_ENABLED = True  # Enable RAG knowledge base search
SEARCH_ENABLED = True  # Enable DuckDuckGo web search
```

In code:

```python
from agents.magi_system import MagiSystem

# Create system with specific tool configuration
system = MagiSystem(enable_search=True, enable_rag=False)
```

### Adding New Agents

Edit `personalities.py`:

```python
PERSONALITIES["NEW_AGENT"] = {
    "name": "NEW_AGENT-4",
    "role": "Your Role",
    "system_prompt": """Your custom system prompt...""",
}
```

### Modifying Search Behavior

Edit `magi_agent.py` to add more tools or modify the search tool configuration.

### Changing Memory Backend

The system uses SQLite by default. To use a different backend, modify the `SQLChatMessageHistory` initialisation in `magi_agent.py`.

### Adjusting LLM Parameters

In `magi_agent.py` and `magi_deliberator.py`, modify the `ChatOpenAI` initialisation:

```python
self.llm = ChatOpenAI(
    base_url=llm_base_url,
    api_key="lm-studio",
    model=model_name,
    temperature=0.7,  # Adjust creativity (0.0-1.0)
    max_tokens=None,  # Limit response length
)
```

## Troubleshooting

### "Connection refused" error

- Make sure LM Studio server is running
- Check that the URL matches (default: `http://localhost:1234`)
- Verify a model is loaded in LM Studio

### Slow responses

- This is normal with local LLMs, especially with search enabled
- Consider using a smaller/faster model
- Each query requires 3+ LLM calls (3 agents + judge evaluation + synthesis)

### Import errors

- Make sure all dependencies are installed: `pip install -e .`
- Check Python version: `python --version` (needs 3.11+)

### Search not working

- Check internet connection
- DuckDuckGo search may be rate-limited; wait a moment and retry
- Verify `duckduckgo-search` package is installed

### Memory not persisting

- Check that `magi_agent_history.db` is being created in the project directory
- Make sure you have write permissions in the directory
- SQLite database is created automatically on first run

### RAG not working

- See [RAG_SETUP.md](documentation/RAG_SETUP.md) for detailed troubleshooting
- Ensure ChromaDB and dependencies are installed
- Verify documents have been ingested
- Check that embedding model is loaded in LM Studio

## Performance Notes

- **First Query**: May be slower as the LLM loads and caches activate
- **Subsequent Queries**: Should be faster with warm cache
- **Memory Usage**: Each agent maintains separate conversation history
- **Parallel Processing**: Agents query sequentially (can be made parallel with async)

## Future Enhancements

Potential improvements:

- Async parallel agent execution
- More sophisticated voting mechanisms
- Additional tools (calculator, code execution, etc.)
- Multiple LLM support (different models for different agents)
- Export and analysis of decision patterns
- Configurable agent personalities via UI

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Inspired by the MAGI system from Neon Genesis Evangelion
- Built with LangChain and LM Studio
- Uses DuckDuckGo for web search capabilities
