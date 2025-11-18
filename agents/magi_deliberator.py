from typing import Dict, List

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


# Pydantic models for structured output
class AgentEvaluation(BaseModel):
    """Evaluation of a single agent's response"""

    agent: str = Field(description="Name of the agent being evaluated")
    score: int = Field(
        description="Score from 1-10 based on quality and relevance", ge=1, le=10
    )
    reasoning: str = Field(description="Brief explanation of the score")


class DeliberationResult(BaseModel):
    """Complete deliberation result with evaluations and synthesis"""

    evaluations: List[AgentEvaluation] = Field(
        description="Individual agent evaluations"
    )
    synthesis: str = Field(description="Overall analysis and recommendation")
    voting_result: str = Field(
        description="Which response(s) were most valuable and why"
    )


class FinalResult(BaseModel):
    """Final result output from the deliberation process"""

    evaluation: DeliberationResult = Field(
        description="The deliberation evaluation results"
    )
    final_answer: str = Field(description="The synthesized final answer")


# Deliberator agent for evaluating and aggregating responses
class DeliberatorAgent:
    """
    Independent deliberator that evaluates MAGI responses and facilitates voting.
    Supports both LM Studio and Google Gemini as LLM providers.
    """

    def __init__(
        self,
        llm_provider: str,
        llm_base_url: str,
        model_name: str,
        api_key: str,
        temperature: float,
        session_id: str,
        memory_db_path: str,
    ):
        self.llm_provider = llm_provider.lower()
        self.session_id = session_id

        # Set up memory with SQL backend
        self.message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection=memory_db_path,
            table_name="deliberator",
        )

        # Initialise LLM based on provider
        if self.llm_provider == "gemini":  # Use Google Gemini
            gemini_api_key = api_key
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
                api_key=api_key,
                model=model_name,
                temperature=temperature,
            )

        # Prompt for evaluating responses
        self.evaluation_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an independent judge evaluating responses from a council of AI agents.
                    Each agent has a different perspective: scientific, strategic, and ethical.

                    Your task is to:
                    1. Analyze each agent's response for quality, relevance, and insight
                    2. Identify strengths and weaknesses
                    3. Note any contradictions or complementary points
                    4. Provide a score (1-10) for each response based on:
                    - Relevance to the question
                    - Depth of analysis
                    - Use of evidence/reasoning
                    - Practical value

                    Be objective and fair in your evaluation.""",
                ),
                (
                    "human",
                    """Question: {question}

                    Agent Responses:
                    {responses}

                    Please evaluate each response and provide:
                    1. Individual scores and brief reasoning for each agent
                    2. Key insights from each perspective
                    3. Areas of agreement and disagreement
                    4. A synthesized recommendation""",
                ),
            ]
        )

        # Create structured output chain for evaluations
        self.evaluation_chain = (
            self.evaluation_prompt | self.llm.with_structured_output(DeliberationResult)
        )

        # Prompt for facilitating vote
        self.voting_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are facilitating a voting process among AI agents.
                    Based on the responses and your analysis, determine which approach or answer is most appropriate.
                    Consider all perspectives but make a clear decision.""",
                ),
                (
                    "human",
                    """Question: {question}

                    Responses with scores:
                    {scored_responses}

                    Based on the analysis, which response or combination of responses best answers the question?
                    Provide a final synthesized answer that incorporates the best elements.""",
                ),
            ]
        )

    def evaluate_responses(
        self, question: str, responses: List[Dict]
    ) -> DeliberationResult:
        """
        Evaluate all agent responses and provide scoring.
        Returns a structured DeliberationResult object.
        """
        # Format responses for evaluation
        formatted_responses = "\n\n".join(
            [
                f"Agent: {r['agent']}\nResponse: {r['response']}"
                for r in responses
                if r["success"]
            ]
        )

        try:
            # Get message history for context
            chat_history = self.message_history.messages

            # Use structured output chain to get Pydantic model directly
            evaluation = self.evaluation_chain.invoke(
                {
                    "question": question,
                    "responses": formatted_responses,
                    "chat_history": chat_history,
                }
            )

            return evaluation

        except Exception as e:
            print(f"\nDEBUG: Error in evaluate_responses: {str(e)}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            import traceback

            traceback.print_exc()

            # Return a default DeliberationResult on error
            return DeliberationResult(
                evaluations=[
                    AgentEvaluation(
                        agent=r["agent"], score=1, reasoning="Evaluation failed."
                    )
                    for r in responses
                    if r["success"]
                ],
                synthesis=f"Error during evaluation: {str(e)}",
                voting_result="Error",
            )

    def synthesise_final_answer(
        self, question: str, responses: List[Dict], evaluation: DeliberationResult
    ) -> str:
        """
        Create a final synthesised answer based on all responses and evaluation.
        """
        # Build scored responses by combining evaluation scores with actual responses
        scored_items = []

        # Create a map of agent names to their responses
        response_map = {r["agent"]: r["response"] for r in responses if r["success"]}

        # Combine with evaluation scores if available
        if evaluation.evaluations:
            for eval_item in evaluation.evaluations:
                agent_name = eval_item.agent
                agent_response = response_map.get(agent_name, "No response available")
                scored_items.append(
                    f"Agent: {agent_name}\n"
                    f"Score: {eval_item.score}/10\n"
                    f"Reasoning: {eval_item.reasoning}\n"
                    f"Full Response: {agent_response}"
                )
        else:
            # If no evaluations available, just use the raw responses
            for r in responses:
                if r["success"]:
                    scored_items.append(
                        f"Agent: {r['agent']}\n"
                        f"Score: N/A\n"
                        f"Reasoning: Evaluation not available\n"
                        f"Full Response: {r['response']}"
                    )

        scored_responses = "\n\n".join(scored_items)

        try:
            messages = self.voting_prompt.format_messages(
                question=question, scored_responses=scored_responses
            )
            result = self.llm.invoke(messages)

            # Extract content from the result
            if hasattr(result, "content"):
                return result.content
            else:
                return str(result)
        except Exception as e:
            print(f"\nDEBUG: Error in synthesise_final_answer: {str(e)}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            import traceback

            traceback.print_exc()
            return f"Error synthesizing answer: {str(e)}"

    def process_magi_decision(
        self, question: str, responses: List[Dict]
    ) -> FinalResult:
        """
        Complete evaluation and synthesis process.
        Returns a structured FinalResult object.
        """
        print("\n" + "=" * 80)
        print("MAGI DELIBERATION")
        print("=" * 80)

        # Evaluate responses (returns structured Pydantic model)
        evaluation = self.evaluate_responses(question, responses)

        # Print the evaluation scores
        if evaluation.evaluations:
            print("\nIndividual Scores:")
            for eval_item in evaluation.evaluations:
                print(f"  {eval_item.agent}: {eval_item.score}/10")
                print(f"    {eval_item.reasoning}")
        else:
            print("\nIndividual Scores: Not available")

        print("\nSynthesis:")
        print(evaluation.synthesis)

        # Generate final answer
        final_answer = self.synthesise_final_answer(question, responses, evaluation)

        # Store final answer in message history
        self.message_history.add_user_message(question)
        self.message_history.add_ai_message(final_answer)

        print("\n" + "=" * 80)
        print("FINAL SYNTHESISED ANSWER")
        print("=" * 80)
        print(final_answer)
        print("=" * 80 + "\n")

        return FinalResult(evaluation=evaluation, final_answer=final_answer)

    def clear_memory(self):
        """Clear the deliberator's conversation history."""
        self.message_history.clear()
