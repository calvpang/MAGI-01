# Magi System

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

# Select provider in the UI and start asking questions!
```

**That's it!** The beautiful web interface will open in your browser automatically. 🎉

For Gemini setup, see [GEMINI_GUIDE.md](GEMINI_GUIDE.md)

For detailed instructions, see [QUICKSTART_WEBUI.md](QUICKSTART_WEBUI.md)

---

## Overview

The Magi System is inspired by the MAGI supercomputer system, featuring a council of three AI agents with distinct personalities:

- **MELCHIOR-1**: Scientific & Analytical perspective
- **BALTHASAR-2**: Strategic & Pragmatic perspective  
- **CASPER-3**: Ethical & Philosophical perspective

Each agent can:

- Search the web using DuckDuckGo
- Maintain conversation memory using SQL storage
- Respond based on their unique personality and expertise

An independent **Judge Agent** evaluates all responses, scores them, and synthesizes a final answer.

## Architecture

```
User Query
    ↓
Council (3 Agents in parallel)
    ├── MELCHIOR-1 (Scientist) → Response + Search
    ├── BALTHASAR-2 (Strategist) → Response + Search
    └── CASPER-3 (Ethicist) → Response + Search
    ↓
Judge Agent
    ├── Evaluates responses
    ├── Scores each agent
    └── Synthesizes final answer
    ↓
Final Output
```

## Features

- **Multi-Agent Council**: Three agents with distinct personalities and reasoning approaches
- **Web Search**: Each agent can search DuckDuckGo for real-time information
- **Memory**: Conversation history persisted in SQLite for each agent
- **Independent Judge**: Objective evaluation and vote aggregation
- **LM Studio Integration**: Uses local LLMs via LM Studio's OpenAI-compatible API
- **LangChain Orchestration**: Built on LangChain for robust agent management
- **🎨 Streamlit Web UI**: Beautiful, interactive interface (NEW!)
- **📊 Visual Feedback**: Real-time progress and color-coded scores
- **📜 History Tracking**: Built-in query history and export

## User Interfaces

### 🌐 Web UI (Recommended)

Interactive Streamlit interface with visual feedback:

```bash
python3 launch_webui.py
```

**Features:**
- Real-time progress updates
- Color-coded scoring
- Query history
- One-click export
- Easy configuration

See [WEBUI_GUIDE.md](WEBUI_GUIDE.md) for details.

### 💻 Command Line

Traditional terminal interface:

```bash
python3 main.py
```

**Features:**
- Direct access
- Scriptable
- Lower overhead

## Prerequisites

1. **LM Studio**: Download and install from [lmstudio.ai](https://lmstudio.ai)
2. **Python 3.10+**: Required for running the application
3. **Model**: Load a model in LM Studio (e.g., Llama 3, Mistral, etc.)

## Installation

1. **Clone or navigate to the project directory**:
```bash
cd /Users/calvin/Projects/MagiSystem
```

2. **Install dependencies**:
```bash
pip install -e .
```

Or install dependencies directly:
```bash
pip install langchain langchain-community langchain-openai duckduckgo-search sqlalchemy
```

## Setup

### 1. Start LM Studio Server

1. Open LM Studio
2. Load a model (recommended: Llama-3-8B or similar)
3. Click "Start Server" (default: `http://localhost:1234`)
4. Note the model name shown in LM Studio

### 2. Configure Model (Optional)

If your LM Studio server runs on a different port or you want to specify the model name, edit `main.py`:

```python
LM_STUDIO_URL = "http://localhost:1234/v1"  # Change if needed
MODEL_NAME = "your-model-name"  # Change to match your loaded model
```

## Usage

### Interactive Mode

Run the main application for an interactive session:

```bash
python main.py
```

Commands:
- Type your question to query the council
- Type `clear` to clear all agent memories
- Type `quit` or `exit` to stop

Example interaction:
```
Your question: Should we invest in renewable energy?

--- MELCHIOR-1 is deliberating ---
[Scientific analysis with search results...]

--- BALTHASAR-2 is deliberating ---
[Strategic analysis with search results...]

--- CASPER-3 is deliberating ---
[Ethical analysis with search results...]

JUDGE EVALUATION
[Scores and reasoning for each agent...]

FINAL SYNTHESIZED ANSWER
[Combined recommendation...]
```

### Example Queries

Run pre-defined example queries:

```bash
python app.py
```

This will run several example questions and save results to JSON files.

### Custom Queries

```python
from main import MagiCouncil

council = MagiCouncil()
result = council.query_council("Your question here")
print(result['final_answer'])
```

## Project Structure

```
MagiSystem/
├── main.py              # Main entry point and orchestration
├── council_agent.py     # Individual Magi agent implementation
├── judge.py             # Judge agent for evaluation and voting
├── personalities.py     # Agent personality definitions
├── app.py              # Example usage and testing
├── pyproject.toml      # Project dependencies
├── README.md           # This file
└── magi_agent_history.db  # SQLite database (auto-created)
```

## How It Works

### 1. Query Submission
When you submit a question, it's sent to all three council agents simultaneously.

### 2. Agent Processing
Each agent:
- Receives the query with their personality context
- Can search DuckDuckGo for relevant information
- Accesses their conversation memory
- Generates a response based on their unique perspective

### 3. Judge Evaluation
The Judge agent:
- Receives all agent responses
- Scores each response (1-10) based on relevance, depth, evidence, and value
- Identifies agreements and contradictions
- Provides reasoning for scores

### 4. Synthesis
The Judge creates a final synthesized answer that:
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

Edit `council_agent.py` to add more tools or modify the search tool configuration.

### Changing Memory Backend

The system uses SQLite by default. To use a different backend, modify the `SQLChatMessageHistory` initialization in `council_agent.py`.

### Adjusting LLM Parameters

In `council_agent.py` and `judge.py`, modify the `ChatOpenAI` initialization:

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
- Check Python version: `python --version` (needs 3.10+)

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
- Web UI interface
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
