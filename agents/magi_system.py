"""
MAGI System - a multi-agent council with voting.
"""

import os
import uuid
from datetime import datetime
from typing import Dict

import dotenv

from agents.magi_agent import MagiAgent
from agents.magi_deliberator import DeliberatorAgent
from agents.personalities import get_all_personalities
from config import (
    AGENT_TEMPERATURE,
    GEMINI_MODEL,
    JUDGE_TEMPERATURE,
    LLM_PROVIDER,
    LM_STUDIO_API_KEY,
    LM_STUDIO_MODEL,
    LM_STUDIO_URL,
    RAG_COLLECTION_NAME,
    RAG_ENABLED,
    MEMORY_DB_PATH,
    SEARCH_ENABLED
)

dotenv.load_dotenv()  # Load environment variables from .env file if present


class MagiSystem:
    """
    Orchestrates the Magi agents and the deliberator agent.
    Supports both LM Studio and Google Gemini as LLM providers.
    """

    def __init__(
        self,
        enable_search: bool = SEARCH_ENABLED,
        enable_rag: bool = RAG_ENABLED,
    ):
        # Instantiate the Magi System with the specified LLM provider and session ID
        self.llm_provider = LLM_PROVIDER
        self.session_id = str(uuid.uuid4())
        self.enable_search = enable_search
        self.enable_rag = enable_rag

        # Set provider-specific defaults
        if self.llm_provider.lower() == "gemini":
            self.model_name = GEMINI_MODEL
            self.llm_base_url = None
            self.api_key = os.getenv("GEMINI_API_KEY")
            print(f"🤖 Using Google Gemini: {self.model_name}\n")
        else:
            self.model_name = LM_STUDIO_MODEL
            self.llm_base_url = LM_STUDIO_URL
            self.api_key = LM_STUDIO_API_KEY
            print(f"🖥️  Using LM Studio: {self.llm_base_url}\n")

        # Initialise Magi agents
        personalities = get_all_personalities()
        self.agents = [
            MagiAgent(
                name=p["name"],
                system_prompt=p["system_prompt"],
                session_id=self.session_id,
                llm_provider=self.llm_provider,
                llm_base_url=self.llm_base_url,
                model_name=self.model_name,
                api_key=self.api_key,
                temperature=AGENT_TEMPERATURE,
                enable_rag=self.enable_rag,
                rag_collection=RAG_COLLECTION_NAME,
                memory_db_path=MEMORY_DB_PATH,
                enable_search=self.enable_search,
            )
            for p in personalities
        ]

        # Initialise deliberator agent
        self.deliberator = DeliberatorAgent(
            llm_provider=self.llm_provider,
            llm_base_url=self.llm_base_url,
            model_name=self.model_name,
            api_key=self.api_key,
            temperature=JUDGE_TEMPERATURE,
            session_id=self.session_id,
            memory_db_path=MEMORY_DB_PATH,
        )

        print(f"MAGI System initialised with {len(self.agents)} agents")
        print(f"Session ID: {self.session_id}")
        print(f"Tools: Search={'✓' if self.enable_search else '✗'} | RAG={'✓' if self.enable_rag else '✗'}")
        for agent in self.agents:
            print(f"  - {agent.name}")

    def query_magi(self, question: str) -> Dict:
        """
        Submit a query to all MAGI agents and get deliberator's evaluation.
        """
        print("\n" + "=" * 80)
        print(f"MAGI QUERY: {question}")
        print("=" * 80 + "\n")

        # Collect responses from all agents
        responses = []
        for agent in self.agents:
            print(f"\n--- Querying {agent.name} ---")
            # Enable debug=True to see DuckDuckGo search results
            response = agent.respond(question, debug=False)
            responses.append(response)

            if response["success"]:
                print(f"\n{agent.name} response:")
                print(response["response"])
            else:
                print(f"\n{agent.name} encountered an error:")
                print(response["response"])

        # Deliberator evaluates and synthesizes
        result = self.deliberator.process_magi_decision(question, responses)

        return {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "agent_responses": responses,
            "evaluation": result.evaluation,
            "final_answer": result.final_answer,
        }

    def clear_all_memory(self):
        """Clear memory for all agents and the deliberator."""
        for agent in self.agents:
            agent.clear_memory()
        self.deliberator.clear_memory()
        print("All agent memories cleared.")
