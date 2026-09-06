"""
Supervisor Agent

Responsibilities
----------------
1. Validate the incoming AgentState.
2. Understand the user's intent.
3. Choose the most appropriate agent or controlled
   sequence of agents.
4. Build an ExecutionPlan.
5. Store the ExecutionPlan inside AgentState.
6. Aggregate the selected agent's output into final_response.

The Supervisor owns routing and final aggregation.
Specialized agents own their respective output fields.
"""

import json
import logging

from agents.base_agent import BaseAgent
from prompts.supervisor_prompt import SUPERVISOR_PROMPT
from schemas.agent_state import AgentState, ExecutionPlan
from services.llm_service import llm_service


logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):

    name = "supervisor"

    # ============================================================
    # Validate
    # ============================================================

    def validate(
        self,
        state: AgentState,
    ) -> bool:
        """
        Validate that a user query exists.
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

    def execute(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Main entry point for the Supervisor.

        Validate the request.
        Create an execution plan.
        Store the execution plan inside AgentState.
        Return the updated state.
        """

        logger.info(
            "Supervisor started."
        )

        if not self.validate(state):

            logger.error(
                "Supervisor validation failed."
            )

            state.status = "failed"

            state.errors.append(
                "User query is empty."
            )

            return state

        try:

            execution_plan = (
                self.create_plan(state)
            )

            state.execution_plan = (
                execution_plan
            )

            state.status = "running"

            logger.info(
                "Supervisor selected agent(s): %s",
                execution_plan.agents,
            )

            return state

        except Exception as e:

            logger.exception(
                "Supervisor failed while "
                "creating execution plan."
            )

            state.status = "failed"

            state.errors.append(
                str(e)
            )

            return state

    # ============================================================
    # Create Execution Plan
    # ============================================================

    def create_plan(
        self,
        state: AgentState,
    ) -> ExecutionPlan:
        """
        Ask the LLM to create a controlled execution plan.

        The LLM returns JSON such as:

            {
                "agents": ["analytics"]
            }

        or:

            {
                "agents": ["analytics", "document"]
            }

        Only approved agents and approved multi-agent
        sequences are accepted.
        """

        prompt = SUPERVISOR_PROMPT.format(
            query=state.query
        )

        logger.info(
            "Supervisor requesting structured routing decision."
        )

        response = llm_service.generate(
            prompt,
            structured=True,
        )

        if not response:

            raise ValueError(
                "Supervisor LLM returned an empty response."
            )

        response = response.strip()

        # --------------------------------------------------------
        # Parse JSON
        # --------------------------------------------------------

        try:

            routing_plan = json.loads(
                response
            )

        except json.JSONDecodeError as e:

            logger.error(
                "Supervisor returned invalid JSON: %s",
                response,
            )

            raise ValueError(
                "Supervisor returned invalid "
                "structured routing content."
            ) from e

        # --------------------------------------------------------
        # Validate JSON object
        # --------------------------------------------------------

        if not isinstance(
            routing_plan,
            dict,
        ):

            raise ValueError(
                "Supervisor routing response must "
                "be a JSON object."
            )

        agents = routing_plan.get(
            "agents"
        )

        if not isinstance(
            agents,
            list,
        ):

            raise ValueError(
                "Supervisor routing response must "
                "contain an agents list."
            )

        # --------------------------------------------------------
        # Normalize agent names
        # --------------------------------------------------------

        normalized_agents = []

        for agent in agents:

            if not isinstance(
                agent,
                str,
            ):
                continue

            agent_name = (
                agent
                .strip()
                .lower()
            )

            if agent_name:
                normalized_agents.append(
                    agent_name
                )

        # --------------------------------------------------------
        # Allowed single-agent plans
        # --------------------------------------------------------

        allowed_single_agents = {
            "chat",
            "rag",
            "analytics",
            "research",
        }

        # --------------------------------------------------------
        # Allowed document sequences
        # --------------------------------------------------------

        allowed_document_sequences = {
            (
                "analytics",
                "document",
            ),
            (
                "research",
                "document",
            ),
            (
                "rag",
                "document",
            ),
        }

        # --------------------------------------------------------
        # Validate plan
        # --------------------------------------------------------

        if len(
            normalized_agents
        ) == 1:

            selected_agent = (
                normalized_agents[0]
            )

            if selected_agent in (
                allowed_single_agents
            ):

                logger.info(
                    "Supervisor routing decision: %s",
                    normalized_agents,
                )

                return ExecutionPlan(
                    agents=normalized_agents
                )

        # --------------------------------------------------------
        # Validate document sequence
        # --------------------------------------------------------

        if len(
            normalized_agents
        ) == 2:

            sequence = tuple(
                normalized_agents
            )

            if sequence in (
                allowed_document_sequences
            ):

                logger.info(
                    "Supervisor document execution plan: %s",
                    normalized_agents,
                )

                return ExecutionPlan(
                    agents=normalized_agents
                )

        # --------------------------------------------------------
        # Invalid plan
        # --------------------------------------------------------

        logger.warning(
            "Supervisor returned an unsupported execution plan: %s",
            normalized_agents,
        )

        # Safe fallback
        return ExecutionPlan(
            agents=["chat"],
            reason=(
                "The Supervisor returned an unsupported "
                "execution plan."
            ),
        )

    # ============================================================
    # Aggregate Agent Output
    # ============================================================

    def aggregate(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Convert specialized agent output into a clean
        user-facing final_response.

        The detailed structured output remains available
        internally in AgentState.

        The frontend should use final_response rather than
        displaying the complete analytics_output dictionary.
        """

        logger.info(
            "Supervisor aggregation started."
        )

        # ========================================================
        # Analytics Agent
        # ========================================================

        if (
            state.execution_plan
            and "analytics"
            in state.execution_plan.agents
        ):

            if not state.analytics_output:

                state.final_response = (
                    "The Analytics Agent did not "
                    "produce a response."
                )

                state.status = "completed"

                return state

            analytics_output = (
                state.analytics_output
            )

            # ----------------------------------------------------
            # Failed analytics request
            # ----------------------------------------------------

            if (
                analytics_output.get("status")
                == "failed"
            ):

                state.final_response = (
                    analytics_output.get(
                        "answer",
                        "I was unable to process "
                        "the analytical request.",
                    )
                )

                state.status = "failed"

                return state

            # ----------------------------------------------------
            # Document workflow
            # ----------------------------------------------------

            if (
                "document"
                in state.execution_plan.agents
            ):

                if state.document_output:

                    state.final_response = (
                        state.document_output.get(
                            "answer",
                            "The requested document "
                            "was generated successfully.",
                        )
                    )

                    state.status = "completed"

                    logger.info(
                        "Analytics → Document output "
                        "aggregated successfully."
                    )

                    return state

            # ----------------------------------------------------
            # If Analytics Agent already produced
            # a clean answer, use it.
            # ----------------------------------------------------

            operation = (
                analytics_output.get(
                    "operation"
                )
            )

            answer = (
                analytics_output.get(
                    "answer"
                )
            )

            if answer:

                state.final_response = answer

                state.status = "completed"

                logger.info(
                    "Analytics clean answer "
                    "aggregated successfully."
                )

                return state

            # ====================================================
            # FILTERING
            # ====================================================

            if "filters" in analytics_output:

                filters = (
                    analytics_output.get(
                        "filters",
                        {}
                    )
                )

                matched_rows = (
                    analytics_output.get(
                        "matched_rows",
                        0
                    )
                )

                filtered_rows = (
                    analytics_output.get(
                        "filtered_rows",
                        []
                    )
                )

                if len(filtered_rows) == 0:

                    state.final_response = (
                        "No matching records were found."
                    )

                elif not filters:

                    state.final_response = (
                        f"The dataset contains "
                        f"{matched_rows} records."
                    )

                else:

                    filter_text = ", ".join(
                        f"{key} = {value}"
                        for key, value
                        in filters.items()
                    )

                    state.final_response = (
                        f"Found {matched_rows} "
                        f"matching record(s) "
                        f"for {filter_text}."
                    )

                state.status = "completed"

                return state

            # ====================================================
            # SORTING
            # ====================================================

            if operation in (
                "sort_descending",
                "sort_ascending",
            ):

                column = (
                    analytics_output.get(
                        "column"
                    )
                )

                sorted_rows = (
                    analytics_output.get(
                        "sorted_rows",
                        []
                    )
                )

                if not sorted_rows:

                    state.final_response = (
                        "No records were available "
                        "to sort."
                    )

                else:

                    first_row = (
                        sorted_rows[0]
                    )

                    value = (
                        first_row.get(
                            column
                        )
                    )

                    if operation == (
                        "sort_descending"
                    ):

                        state.final_response = (
                            f"The highest {column} "
                            f"value is {value}."
                        )

                    else:

                        state.final_response = (
                            f"The lowest {column} "
                            f"value is {value}."
                        )

                state.status = "completed"

                return state

            # ====================================================
            # GROUP BY SUM
            # ====================================================

            if operation == "groupby_sum":

                group_column = (
                    analytics_output.get(
                        "group_column"
                    )
                )

                value_column = (
                    analytics_output.get(
                        "value_column"
                    )
                )

                grouped_rows = (
                    analytics_output.get(
                        "grouped_rows",
                        []
                    )
                )

                if not grouped_rows:

                    state.final_response = (
                        "No grouped results "
                        "were found."
                    )

                else:

                    lines = []

                    for row in grouped_rows:

                        group_value = (
                            row.get(
                                group_column
                            )
                        )

                        value = (
                            row.get(
                                value_column
                            )
                        )

                        lines.append(
                            f"{group_value}: {value}"
                        )

                    state.final_response = (
                        f"Total {value_column} "
                        f"by {group_column}:\n"
                        + "\n".join(lines)
                    )

                state.status = "completed"

                return state

            # ====================================================
            # FALLBACK
            # ====================================================

            state.final_response = (
                "The analytical request was "
                "completed successfully."
            )

            state.status = "completed"

            return state

        # ========================================================
        # RAG Agent
        # ========================================================

        if (
            state.execution_plan
            and "rag"
            in state.execution_plan.agents
        ):

            if state.rag_output:

                # ------------------------------------------------
                # Failed RAG request
                # ------------------------------------------------

                if (
                    state.rag_output.get("status")
                    == "failed"
                ):

                    state.final_response = (
                        state.rag_output.get(
                            "answer",
                            "I was unable to process "
                            "the uploaded document.",
                        )
                    )

                    state.status = "failed"

                    return state

                # ------------------------------------------------
                # Document workflow
                # ------------------------------------------------

                if (
                    "document"
                    in state.execution_plan.agents
                ):

                    if state.document_output:

                        state.final_response = (
                            state.document_output.get(
                                "answer",
                                "The requested document "
                                "was generated successfully.",
                            )
                        )

                        state.status = "completed"

                        logger.info(
                            "RAG → Document output "
                            "aggregated successfully."
                        )

                        return state

                state.final_response = (
                    state.rag_output.get(
                        "answer"
                    )
                )

                state.status = "completed"

                logger.info(
                    "RAG output aggregated "
                    "successfully."
                )

                return state

        # ========================================================
        # Chat Agent
        # ========================================================

        if (
            state.execution_plan
            and "chat"
            in state.execution_plan.agents
        ):

            if state.chat_output:

                # ------------------------------------------------
                # Failed Chat request
                # ------------------------------------------------

                if (
                    state.chat_output.get("status")
                    == "failed"
                ):

                    state.final_response = (
                        state.chat_output.get(
                            "answer",
                            "I was unable to process "
                            "the chat request.",
                        )
                    )

                    state.status = "failed"

                    return state

                state.final_response = (
                    state.chat_output.get(
                        "answer"
                    )
                )

                state.status = "completed"

                logger.info(
                    "Chat output aggregated "
                    "successfully."
                )

                return state

        # ========================================================
        # Research Agent
        # ========================================================

        if (
            state.execution_plan
            and "research"
            in state.execution_plan.agents
        ):

            if state.research_output:

                # ------------------------------------------------
                # Failed Research request
                # ------------------------------------------------

                if (
                    state.research_output.get("status")
                    == "failed"
                ):

                    state.final_response = (
                        state.research_output.get(
                            "answer",
                            "I was unable to process "
                            "the research request.",
                        )
                    )

                    state.status = "failed"

                    return state

                # ------------------------------------------------
                # Document workflow
                # ------------------------------------------------

                if (
                    "document"
                    in state.execution_plan.agents
                ):

                    if state.document_output:

                        state.final_response = (
                            state.document_output.get(
                                "answer",
                                "The requested document "
                                "was generated successfully.",
                            )
                        )

                        state.status = "completed"

                        logger.info(
                            "Research → Document output "
                            "aggregated successfully."
                        )

                        return state

                state.final_response = (
                    state.research_output.get(
                        "answer"
                    )
                )

                state.status = "completed"

                logger.info(
                    "Research output aggregated "
                    "successfully."
                )

                return state

        # ========================================================
        # Document Agent
        # ========================================================

        if (
            state.execution_plan
            and "document"
            in state.execution_plan.agents
        ):

            if state.document_output:

                # ------------------------------------------------
                # Failed Document request
                # ------------------------------------------------

                if (
                    state.document_output.get("status")
                    == "failed"
                ):

                    state.final_response = (
                        state.document_output.get(
                            "answer",
                            "I was unable to prepare "
                            "the requested document.",
                        )
                    )

                    state.status = "failed"

                    return state

                state.final_response = (
                    state.document_output.get(
                        "answer",
                        "The requested document "
                        "was generated successfully.",
                    )
                )

                state.status = "completed"

                logger.info(
                    "Document output aggregated "
                    "successfully."
                )

                return state

        # ========================================================
        # No output available
        # ========================================================

        state.final_response = (
            "The selected agent did not "
            "produce a response."
        )

        state.status = "completed"

        logger.warning(
            "No supported agent output was "
            "available for aggregation."
        )

        return state


# ================================================================
# Singleton
# ================================================================

supervisor_agent = SupervisorAgent()