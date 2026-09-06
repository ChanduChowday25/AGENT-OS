"""
Chat Agent

Responsibilities
----------------
1. Validate the incoming AgentState.
2. Send the user's query to LLM.
3. Store the generated response in state.chat_output.
4. Return the updated AgentState.

The Chat Agent only handles general conversations.
"""

import logging

from agents.base_agent import BaseAgent
from prompts.chat_prompt import CHAT_PROMPT
from schemas.agent_state import AgentState, WorkflowTraceEvent
from services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):

    name = "chat"

    def validate(self, state: AgentState) -> bool:
        """
        Validate that the Chat Agent has a valid user query.
        """

        if state is None:
            return False

        if not state.query:
            return False

        if not state.query.strip():
            return False

        return True

    def execute(self, state: AgentState) -> AgentState:
        """
        Execute the Chat Agent.

        Reads the user's query, sends it to LLM,
        stores the generated response inside chat_output,
        and returns the updated state.
        """

        logger.info("Chat Agent started.")

        if not self.validate(state):

            logger.error(
                "Chat Agent validation failed."
            )

            state.status = "failed"

            state.errors.append(
                "User query is empty."
            )

            return state

        try:

            # ----------------------------------------------------
            # Generate response
            # ----------------------------------------------------

            answer = llm_service.generate(
                CHAT_PROMPT.format(query=state.query)
            )

            # ----------------------------------------------------
            # Store Chat Agent output
            #
            # The Chat Agent owns chat_output.
            # Supervisor will later aggregate this into
            # final_response.
            # ----------------------------------------------------

            state.chat_output = {
                "status": "completed",
                "answer": answer,
                "query": state.query,
            }

            state.status = "completed"

            # ----------------------------------------------------
            # Workflow trace
            # ----------------------------------------------------

            state.workflow_trace.append(
                WorkflowTraceEvent(
                    agent=self.name,
                    status="completed",
                    detail="Response generated successfully.",
                )
            )

            logger.info(
                "Chat Agent completed successfully."
            )

            return state

        except Exception as e:

            logger.exception(
                "Chat Agent execution failed."
            )

            state.chat_output = {
                "status": "failed",
                "answer": None,
                "query": state.query,
                "error": str(e),
            }

            state.status = "failed"

            state.errors.append(
                str(e)
            )

            return state