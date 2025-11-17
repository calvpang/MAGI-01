import os

import dotenv
from langchain.agents import create_agent
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class MagiAgent:
    """
    Individual Magi agent with memory, search capability, and unique personality.
    Supports both LM Studio and Google Gemini as LLM providers.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        session_id: str,
        llm_provider: str = "lm_studio",
        llm_base_url: str = "http://127.0.0.1:1234/v1",
        model_name: str = "gpt-oss-20b",
        api_key: str = "lm-studio-local",
        temperature: float = 0.7,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.session_id = session_id
        self.llm_provider = llm_provider.lower()

        # Set up memory with SQL backend
        self.message_history = SQLChatMessageHistory(
            session_id=f"{session_id}_{name}",
            connection="sqlite:///magi_agent_history.db",
            table_name=name.lower().replace("-", "_"),
        )

        # Initialise LLM based on provider
        if self.llm_provider == "gemini":
            # Use Google Gemini
            gemini_api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                raise ValueError(
                    "Gemini API key required. Set GEMINI_API_KEY environment variable."
                )

            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=gemini_api_key,
                temperature=temperature,
                convert_system_message_to_human=True,  # Gemini compatibility
            )
        else:
            self.llm = ChatOpenAI(
                base_url=llm_base_url,
                api_key=api_key or "lm-studio-local",
                model=model_name,
                temperature=temperature,
            )

        # Set up DuckDuckGo search tool
        self.search_tool = DuckDuckGoSearchRun()
        self.tools = [self.search_tool]

        self.prompt = system_prompt

        # Create agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.prompt,
        )

    def respond(self, query: str, debug: bool = False):
        """
        Generate a response to the query using the agent's tools and memory.
        
        Args:
            query: The user's question
            debug: If True, print detailed debugging information including search results
        """
        try:
            # Get message history
            chat_history = self.message_history.messages

            # Invoke agent with history
            response = self.agent.invoke({"messages": query, "context": chat_history})

            # Debug: Print all messages to see tool calls and results
            if debug:
                print(f"\n{'='*60}")
                print(f"DEBUG - {self.name} - Full Response Messages:")
                print(f"{'='*60}")
                for i, msg in enumerate(response["messages"]):
                    msg_type = getattr(msg, "type", "unknown")
                    print(f"\n[Message {i}] Type: {msg_type}")
                    
                    if msg_type == "ai":
                        # Check for tool calls
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            print(f"  Tool Calls: {len(msg.tool_calls)}")
                            for tc in msg.tool_calls:
                                print(f"    - Tool: {tc.get('name', 'unknown')}")
                                print(f"      Args: {tc.get('args', {})}")
                        if hasattr(msg, 'content') and msg.content:
                            print(f"  Content: {msg.content[:200]}...")
                    
                    elif msg_type == "tool":
                        # This is the search result!
                        print(f"  Tool Name: {getattr(msg, 'name', 'unknown')}")
                        print(f"  Tool Result:")
                        print(f"    {getattr(msg, 'content', 'No content')[:500]}...")
                    
                    elif msg_type == "human":
                        print(f"  Content: {getattr(msg, 'content', 'No content')}")
                print(f"{'='*60}\n")

            # Retrieve final agent response
            final_ai_response = next(
                m
                for m in reversed(response["messages"])
                if getattr(m, "type", None) == "ai"
            )

            # Save to history
            self.message_history.add_user_message(query)
            self.message_history.add_ai_message(final_ai_response.text)

            return {
                "agent": self.name,
                "response": final_ai_response.text,
                "success": True,
            }
        except Exception as e:
            return {
                "agent": self.name,
                "response": f"Error: {str(e)}",
                "success": False,
            }

    def clear_memory(self):
        """Clear the agent's conversation history."""
        self.message_history.clear()
