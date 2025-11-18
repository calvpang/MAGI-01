# MagiSystem Architecture

## System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                               │
│                   "Your question here"                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MAGI COUNCIL                                │
│                  (3 Agents in Parallel)                          │
└─────────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ MELCHIOR-1  │  │BALTHASAR-2  │  │  CASPER-3   │
│ (Scientist) │  │(Strategist) │  │ (Ethicist)  │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ • LM Studio │  │ • LM Studio │  │ • LM Studio │
│ • Memory    │  │ • Memory    │  │ • Memory    │
│ • DDG Search│  │ • DDG Search│  │ • DDG Search│
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              ┌─────────────────┐
              │  Response 1     │
              │  Response 2     │
              │  Response 3     │
              └────────┬────────┘
                       ▼
         ┌──────────────────────────┐
         │     JUDGE AGENT          │
         ├──────────────────────────┤
         │ • Evaluates responses    │
         │ • Scores (1-10)          │
         │ • Identifies conflicts   │
         │ • Finds agreements       │
         └──────────┬───────────────┘
                    ▼
         ┌──────────────────────────┐
         │   EVALUATION RESULTS     │
         ├──────────────────────────┤
         │ MELCHIOR: 8/10           │
         │ BALTHASAR: 9/10          │
         │ CASPER: 7/10             │
         └──────────┬───────────────┘
                    ▼
         ┌──────────────────────────┐
         │  SYNTHESIS PROCESS       │
         ├──────────────────────────┤
         │ • Combine best elements  │
         │ • Resolve conflicts      │
         │ • Create final answer    │
         └──────────┬───────────────┘
                    ▼
         ┌──────────────────────────┐
         │  FINAL SYNTHESIZED       │
         │       ANSWER             │
         └──────────────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          main.py                                 │
│                    (MagiCouncil Class)                           │
├─────────────────────────────────────────────────────────────────┤
│ • Orchestrates entire system                                     │
│ • Manages session state                                          │
│ • Coordinates agent communication                                │
└────┬──────────────────────────────────┬──────────────────────────┘
     │                                  │
     ▼                                  ▼
┌──────────────────────┐    ┌──────────────────────┐
│  council_agent.py    │    │     judge.py         │
│  (MagiAgent Class)   │    │  (JudgeAgent Class)  │
├──────────────────────┤    ├──────────────────────┤
│ • Individual agent   │    │ • Evaluation logic   │
│ • Memory management  │    │ • Scoring system     │
│ • Tool integration   │    │ • Synthesis engine   │
│ • LangChain executor │    │ • Voting mechanism   │
└──────┬───────────────┘    └──────────────────────┘
       │
       ▼
┌──────────────────────┐
│  personalities.py    │
├──────────────────────┤
│ • System prompts     │
│ • Agent definitions  │
│ • Role descriptions  │
└──────────────────────┘
```

## Data Flow

```
Input → Agent 1 → Response 1 ┐
                              ├→ Judge → Evaluation → Synthesis → Output
Input → Agent 2 → Response 2 │
                              │
Input → Agent 3 → Response 3 ┘

Each agent has:
├── Personality (from personalities.py)
├── Memory (SQLite database)
├── LLM (via LM Studio)
└── Tools (DuckDuckGo Search)
```

## Memory System

```
┌─────────────────────────────────────┐
│    magi_agent_history.db            │
│        (SQLite Database)            │
├─────────────────────────────────────┤
│                                     │
│  Table: melchior_1                  │
│  ├── session_id                     │
│  ├── timestamp                      │
│  ├── message (user/assistant)       │
│  └── content                        │
│                                     │
│  Table: balthasar_2                 │
│  ├── session_id                     │
│  ├── timestamp                      │
│  ├── message (user/assistant)       │
│  └── content                        │
│                                     │
│  Table: casper_3                    │
│  ├── session_id                     │
│  ├── timestamp                      │
│  ├── message (user/assistant)       │
│  └── content                        │
└─────────────────────────────────────┘
```

## LangChain Integration

```
┌──────────────────────────────────────┐
│         LangChain Stack              │
├──────────────────────────────────────┤
│                                      │
│  ┌────────────────────────────┐     │
│  │  AgentExecutor             │     │
│  │  ├── Agent                 │     │
│  │  ├── Tools                 │     │
│  │  └── Memory                │     │
│  └────────────────────────────┘     │
│                                      │
│  ┌────────────────────────────┐     │
│  │  ChatOpenAI                │     │
│  │  (LM Studio endpoint)      │     │
│  └────────────────────────────┘     │
│                                      │
│  ┌────────────────────────────┐     │
│  │  ConversationBufferMemory  │     │
│  │  (SQLChatMessageHistory)   │     │
│  └────────────────────────────┘     │
│                                      │
│  ┌────────────────────────────┐     │
│  │  DuckDuckGoSearchRun       │     │
│  │  (Web search tool)         │     │
│  └────────────────────────────┘     │
└──────────────────────────────────────┘
```

## LM Studio Connection

```
┌──────────────────────────────────────┐
│         LM Studio Server             │
│     http://localhost:1234/v1         │
├──────────────────────────────────────┤
│  • OpenAI-compatible API             │
│  • Model: (loaded in LM Studio)     │
│  • Inference: Local                  │
└──────────────┬───────────────────────┘
               │
               │ HTTP REST API
               │
┌──────────────▼───────────────────────┐
│      MagiSystem Application          │
│  (Uses langchain-openai adapter)     │
└──────────────────────────────────────┘
```

## Agent Interaction Pattern

```
1. Query Received
   ↓
2. For each agent:
   ├── Load personality
   ├── Load conversation memory
   ├── Create prompt with context
   ├── Call LLM (via LM Studio)
   ├── Agent may use search tool
   ├── Generate response
   └── Save to memory
   ↓
3. Judge receives all responses
   ↓
4. Judge evaluation:
   ├── Analyze each response
   ├── Score responses (1-10)
   ├── Identify patterns
   └── Generate evaluation
   ↓
5. Judge synthesis:
   ├── Combine best elements
   ├── Resolve conflicts
   └── Generate final answer
   ↓
6. Present to user
```

## Extensibility Points

```
┌─────────────────────────────────────────┐
│    Easy to Extend                       │
├─────────────────────────────────────────┤
│                                         │
│  1. Add more agents:                    │
│     └── Edit personalities.py           │
│                                         │
│  2. Add more tools:                     │
│     └── Extend council_agent.py         │
│     └── (calculator, code exec, etc.)   │
│                                         │
│  3. Different LLMs:                     │
│     └── Change ChatOpenAI config        │
│     └── (Azure, OpenAI, local, etc.)    │
│                                         │
│  4. Different memory:                   │
│     └── Swap SQLChatMessageHistory      │
│     └── (Redis, Postgres, etc.)         │
│                                         │
│  5. Web UI:                             │
│     └── Add Gradio/Streamlit layer      │
│                                         │
│  6. Custom voting:                      │
│     └── Modify judge.py logic           │
│                                         │
└─────────────────────────────────────────┘
```
