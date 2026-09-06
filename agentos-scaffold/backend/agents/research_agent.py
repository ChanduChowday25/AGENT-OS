"""
Research Agent

Responsibilities
----------------
1. Validate the incoming AgentState.
2. Research / summarize public knowledge related to the query.
3. Generate a structured research response using LLM.
4. Store the result only in state.research_output.

The Research Agent does NOT:
- modify other agent outputs
- perform routing
- modify the execution plan
- generate the final workflow response
"""

import logging
from typing import Any, Dict

from agents.base_agent import BaseAgent
from schemas.agent_state import AgentState
from services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):

    name = "research"

    # ============================================================
    # Validation
    # ============================================================

    def validate(self, state: AgentState) -> bool:
        """
        Validate that a usable research query exists.
        """

        if state is None:
            return False

        if not state.query:
            return False

        if not state.query.strip():
            return False

        return True

    # ============================================================
    # Execute
    # ============================================================

    def execute(self, state: AgentState) -> AgentState:
        """
        Execute the research request.

        The Research Agent:
            1. Validates the state.
            2. Builds a research prompt.
            3. Sends the query to LLM.
            4. Stores the response in research_output.

        Only state.research_output is modified.
        """

        logger.info("Research Agent started.")

        # --------------------------------------------------------
        # Validation
        # --------------------------------------------------------

        if not self.validate(state):

            logger.error(
                "Research Agent validation failed."
            )

            state.status = "failed"

            state.errors.append(
                "Research query is empty."
            )

            return state

        try:

            # ----------------------------------------------------
            # Build research prompt
            # ----------------------------------------------------

            prompt = self._build_prompt(
                state.query
            )

            # ----------------------------------------------------
            # Generate research response
            # ----------------------------------------------------

            response = llm_service.generate(
                prompt
            )

            if not response or not response.strip():

                raise RuntimeError(
                    "Research service returned an empty response."
                )

            # ----------------------------------------------------
            # Store Research Agent output
            # ----------------------------------------------------

            state.research_output = {
                "status": "completed",
                "answer": response.strip(),
                "query": state.query,
            }

            state.status = "running"

            logger.info(
                "Research Agent completed successfully."
            )

            return state

        except Exception as e:

            logger.exception(
                "Research Agent failed."
            )

            state.research_output = {
                "status": "failed",
                "answer": None,
                "query": state.query,
                "error": str(e),
            }

            state.status = "failed"

            state.errors.append(
                f"Research Agent failed: {str(e)}"
            )

            return state

    # ============================================================
    # Prompt
    # ============================================================

    def _build_prompt(
        self,
        query: str,
    ) -> str:
        """
        Build a controlled research prompt.

        The model should:
        - understand the user's question
        - provide a useful explanation
        - distinguish facts from uncertainty
        - avoid inventing sources
        - answer directly
        """

        return f"""
You are the Research Agent in an enterprise AI system.

Your task is to research and explain the user's question using
your available general/public knowledge.

User question:
{query}

Instructions:

1. Answer the user's question directly.
2. Provide accurate and useful information.
3. Explain important concepts clearly.
4. If the question asks for a comparison, compare the relevant
   concepts in a structured way.
5. If the information may be uncertain, outdated, or dependent
   on recent events, clearly state that limitation.
6. Do not invent citations, URLs, sources, statistics, or facts.
7. Do not claim that you searched the internet unless an actual
   search tool was used.
8. Do not answer using information from uploaded private
   documents. Uploaded-document questions belong to the RAG Agent.
9. Keep the response focused on the user's question.

Return only the research answer.
"""