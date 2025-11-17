"""
Deliberation agent that evaluates and aggregates responses from the Magi agents.
"""

import json
from typing import Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


class DeliberatorAgent:
    """
    Independent deliberator that evaluates Magi responses and facilitates voting.
    Supports both LM Studio and Google Gemini as LLM providers.
    """

    def __init__(
        self,
        llm_provider: str = "lm_studio",
        llm_base_url: str = None,
        model_name: str = None,
        api_key: str = None,
        temperature: float = 0.3,
    ):
        self.llm_provider = llm_provider.lower()

        # Initialise LLM based on provider
        if self.llm_provider == "gemini":
            # Use Google Gemini
            gemini_api_key = api_key
            if not gemini_api_key:
                raise ValueError(
                    "Gemini API key required. Set GEMINI_API_KEY environment variable."
                )

            self.llm = ChatGoogleGenerativeAI(
                model=model_name or "gemini-2.5-flash",
                google_api_key=gemini_api_key,
                temperature=temperature,
                convert_system_message_to_human=True,  # Gemini compatibility
            )
        else:
            self.llm = ChatOpenAI(
                base_url=llm_base_url or "http://127.0.0.1:1234/v1",
                api_key=api_key or "lm-studio-local",
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
                    1. Individual scores and brief reasoning
                    2. Key insights from each perspective
                    3. Areas of agreement and disagreement
                    4. A synthesized recommendation

                    Format your response as JSON with this structure:
                    {{
                        "evaluations": [
                            {{"agent": "agent_name", "score": score, "reasoning": "brief explanation"}},
                            ...
                        ],
                        "synthesis": "overall analysis and recommendation",
                        "voting_result": "which response(s) were most valuable and why"
                    }}""",
                ),
            ]
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

    def evaluate_responses(self, question: str, responses: List[Dict]) -> Dict:
        """
        Evaluate all agent responses and provide scoring.
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
            # Get evaluation from deliberation agent
            messages = self.evaluation_prompt.format_messages(
                question=question, responses=formatted_responses
            )
            result = self.llm.invoke(messages)

            # Extract content from the result
            if hasattr(result, "content"):
                content = result.content
            else:
                content = str(result)

            # Try to parse JSON response
            try:
                evaluation = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, return structured data anyway
                evaluation = {
                    "evaluations": [
                        {
                            "agent": r["agent"],
                            "score": 7,
                            "reasoning": "Evaluation completed",
                        }
                        for r in responses
                        if r["success"]
                    ],
                    "synthesis": content,
                    "voting_result": "See synthesis for details",
                }

            return evaluation

        except Exception as e:
            print(f"\nDEBUG: Error in evaluate_responses: {str(e)}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            import traceback

            traceback.print_exc()
            return {
                "error": str(e),
                "evaluations": [],
                "synthesis": f"Error during evaluation: {str(e)}",
                "voting_result": "Error",
            }

    def synthesise_final_answer(
        self, question: str, responses: List[Dict], evaluation: Dict
    ) -> str:
        """
        Create a final synthesised answer based on all responses and evaluation.
        """
        # Build scored responses by combining evaluation scores with actual responses
        scored_items = []

        # Create a map of agent names to their responses
        response_map = {r["agent"]: r["response"] for r in responses if r["success"]}

        # Combine with evaluation scores if available
        if evaluation.get("evaluations"):
            for eval_item in evaluation["evaluations"]:
                agent_name = eval_item["agent"]
                agent_response = response_map.get(agent_name, "No response available")
                scored_items.append(
                    f"Agent: {agent_name}\n"
                    f"Score: {eval_item['score']}/10\n"
                    f"Reasoning: {eval_item['reasoning']}\n"
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

    def process_magi_decision(self, question: str, responses: List[Dict]) -> Dict:
        """
        Complete evaluation and synthesis process.
        """
        print("\n" + "=" * 80)
        print("MAGI DELIBERATION")
        print("=" * 80)

        # Evaluate responses
        evaluation = self.evaluate_responses(question, responses)

        # Check if synthesis contains JSON wrapped in markdown and extract it first
        synthesis = evaluation.get("synthesis", "No synthesis available")
        if synthesis.startswith("```json"):
            # Extract JSON from markdown code block
            try:
                json_text = synthesis.split("```json")[1].split("```")[0].strip()
                parsed = json.loads(json_text)
                # Update evaluation with the parsed data
                evaluation = parsed
            except (json.JSONDecodeError, IndexError, KeyError):
                # If parsing fails, keep original evaluation
                pass

        # Now print the correct scores
        if evaluation.get("evaluations"):
            print("\nIndividual Scores:")
            for eval_item in evaluation["evaluations"]:
                print(f"  {eval_item['agent']}: {eval_item['score']}/10")
                print(f"    {eval_item['reasoning']}")
        else:
            print("\nIndividual Scores: Not available")

        print("\nSynthesis:")
        print(evaluation.get("synthesis", "No synthesis available"))

        # Generate final answer
        final_answer = self.synthesise_final_answer(question, responses, evaluation)

        print("\n" + "=" * 80)
        print("FINAL SYNTHESISED ANSWER")
        print("=" * 80)
        print(final_answer)
        print("=" * 80 + "\n")

        return {
            "evaluation": evaluation,
            "final_answer": final_answer,
        }
