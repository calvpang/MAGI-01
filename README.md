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
- Maintain conversation memory using SQL storage
- Respond based on their unique personality and expertise

An independent **Deliberator Agent** evaluates all responses, scores them, and synthesizes a final answer.

## Architecture

```
User Query
    ↓
Council (3 Agents in parallel)
    ├── MELCHIOR (Scientist) → Response + Search
    ├── BALTHASAR (Strategist) → Response + Search
    └── CASPER (Ethicist) → Response + Search
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
- **Web Search**: Each agent can search DuckDuckGo for real-time information
- **Memory**: Conversation history persisted in SQLite for each agent
- **Independent Deliberation**: Objective evaluation and vote aggregation
- **LM Studio Integration**: Uses local LLMs via LM Studio's OpenAI-compatible API
- **LangChain Orchestration**: Built on LangChain for robust agent management
- **🎨 Streamlit Web UI**: Beautiful, interactive interface
- **📜 History Tracking**: Built-in query history and export

## User Interfaces

### 🌐 Web UI (Recommended)

Interactive Streamlit interface with visual feedback:

```bash
python3 launch_webui.py
```

### 💻 Command Line

Traditional terminal interface:

```bash
python3 main.py
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
2. Load a model (recommended: Llama-3-8B or similar)
3. Click "Start Server" (default: `http://localhost:1234`)
4. Note the model name shown in LM Studio

### 2. Configure Model (Optional)

If your LM Studio server runs on a different port or you want to specify the model name, edit `config.py`:

```python
LM_STUDIO_URL = "http://localhost:1234/v1"  # Change if needed
MODEL_NAME = "your-model-name"  # Change to match your loaded model
```

## Project Structure

```
MAGI-01/
├── agents/                      # Core agent modules
│   ├── magi_agent.py           # Individual Magi agent with search & memory
│   ├── magi_deliberator.py     # Deliberator agent for evaluation & synthesis
│   ├── magi_system.py          # System orchestration & coordination
│   └── personalities.py         # Agent personality definitions
├── config.py                    # Configuration (LLM provider, models, etc.)
├── main.py                      # CLI entry point
├── example.py                   # Quick example/demo script
├── test.py                      # Testing utilities
├── streamlit_app.py            # Streamlit web interface
├── launch_webui.py             # Web UI launcher script
├── pyproject.toml              # Project dependencies & metadata
├── .env                        # Environment variables (API keys)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── ARCHITECTURE.md             # System architecture documentation
├── magi_agent_history.db       # SQLite database (auto-created)
└── results/                    # Query results & exports
```

## How It Works

### 1. Query Submission
When you submit a question, it's sent to all three MAGI agents simultaneously.

### 2. Agent Processing
Each agent:
- Receives the query with their personality context
- Can search DuckDuckGo for relevant information
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

## Customization

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
