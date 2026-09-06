"""
LangGraph workflow for AgentOS.

Workflow:

START
  ↓
Supervisor
  ↓
Validated ExecutionPlan
  ↓
Execute agents in order
  ↓
Supervisor Aggregation
  ↓
END

Supported agents:
- Chat
- RAG
- Analytics
- Research
- Document

Supported multi-agent workflows:
- Analytics → Document
- Research → Document
- RAG → Document

The Supervisor owns routing.
Each specialized agent owns only its own AgentState output.
"""

import logging
from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from agents.chat_agent import ChatAgent
from agents.rag_agent import rag_agent
from agents.analytics_agent import analytics_agent
from agents.research_agent import ResearchAgent
from agents.document_agent import document_agent
from agents.supervisor_agent import SupervisorAgent

from schemas.agent_state import AgentState


logger = logging.getLogger(__name__)


# ================================================================
# Agent Instances
# ================================================================

supervisor_agent = SupervisorAgent()
chat_agent = ChatAgent()
research_agent = ResearchAgent()


# ================================================================
# Supervisor Node
# ================================================================

def supervisor_node(
    state: AgentState,
) -> AgentState:
    """
    Execute the Supervisor.

    The Supervisor:
    - validates the query
    - determines the appropriate agent or agent sequence
    - creates the ExecutionPlan
    """

    logger.info(
        "LangGraph: Supervisor node started."
    )

    return supervisor_agent.execute(state)


# ================================================================
# Chat Node
# ================================================================

def chat_node(
    state: AgentState,
) -> AgentState:
    """
    Execute the Chat Agent.
    """

    logger.info(
        "LangGraph: Chat node started."
    )

    return chat_agent.execute(state)


# ================================================================
# RAG Node
# ================================================================

def rag_node(
    state: AgentState,
) -> AgentState:
    """
    Execute the RAG Agent.
    """

    logger.info(
        "LangGraph: RAG node started."
    )

    return rag_agent.execute(state)


# ================================================================
# Analytics Node
# ================================================================

def analytics_node(
    state: AgentState,
) -> AgentState:
    """
    Execute the Analytics Agent.
    """

    logger.info(
        "LangGraph: Analytics node started."
    )

    return analytics_agent.execute(state)


# ================================================================
# Research Node
# ================================================================

def research_node(
    state: AgentState,
) -> AgentState:
    """
    Execute the Research Agent.
    """

    logger.info(
        "LangGraph: Research node started."
    )

    return research_agent.execute(state)


# ================================================================
# Document Node
# ================================================================

def document_node(
    state: AgentState,
) -> AgentState:
    """
    Execute the Document Agent.

    The Document Agent consumes outputs that have already
    been produced by Analytics, Research, or RAG.
    """

    logger.info(
        "LangGraph: Document node started."
    )

    return document_agent.execute(state)


# ================================================================
# Route After Supervisor
# ================================================================

def route_after_supervisor(
    state: AgentState,
) -> str:
    """
    Route to the first agent in the Supervisor's
    validated execution plan.

    Examples:

        ["analytics"]
            → analytics

        ["research"]
            → research

        ["rag", "document"]
            → rag

    The remaining agents are handled by the routing
    functions after each agent completes.
    """

    if state.execution_plan is None:

        logger.error(
            "No execution plan was created by Supervisor."
        )

        return "end"

    agents = state.execution_plan.agents

    if not agents:

        logger.warning(
            "Supervisor created an empty execution plan."
        )

        return "end"

    selected_agent = (
        agents[0]
        .strip()
        .lower()
    )

    logger.info(
        "LangGraph first planned agent: %s",
        selected_agent,
    )

    if selected_agent == "chat":
        return "chat"

    if selected_agent == "rag":
        return "rag"

    if selected_agent == "analytics":
        return "analytics"

    if selected_agent == "research":
        return "research"

    if selected_agent == "document":
        return "document"

    logger.warning(
        "Agent '%s' is not connected to the workflow.",
        selected_agent,
    )

    return "end"


# ================================================================
# Route After Agent
# ================================================================

def route_after_agent(
    state: AgentState,
) -> str:
    """
    Determine what should execute after the current agent.

    Supported transitions:

        Analytics → Document
        Research  → Document
        RAG       → Document

    Otherwise:

        Agent → Aggregation
    """
# ------------------------------------------------------------
    # Stop workflow when an agent fails
    # ------------------------------------------------------------

    failed_outputs = [
        state.analytics_output,
        state.rag_output,
        state.research_output,
        state.chat_output,
        state.document_output,
    ]

    for output in failed_outputs:

        if (
            output
            and output.get("status") == "failed"
        ):

            logger.error(
                "Agent execution failed. "
                "Stopping workflow."
            )

            return "aggregation"

    if state.execution_plan is None:

        logger.error(
            "No execution plan available after agent execution."
        )

        return "aggregation"

    agents = [
        agent.strip().lower()
        for agent in state.execution_plan.agents
    ]

    # ------------------------------------------------------------
    # Analytics → Document
    # ------------------------------------------------------------

    if agents == [
        "analytics",
        "document",
    ]:

        if state.document_output:

            logger.info(
                "Document already executed. "
                "Routing to aggregation."
            )

            return "aggregation"

        logger.info(
            "Routing Analytics → Document."
        )

        return "document"

    # ------------------------------------------------------------
    # Research → Document
    # ------------------------------------------------------------

    if agents == [
        "research",
        "document",
    ]:

        if state.document_output:

            logger.info(
                "Document already executed. "
                "Routing to aggregation."
            )

            return "aggregation"

        logger.info(
            "Routing Research → Document."
        )

        return "document"

    # ------------------------------------------------------------
    # RAG → Document
    # ------------------------------------------------------------

    if agents == [
        "rag",
        "document",
    ]:

        if state.document_output:

            logger.info(
                "Document already executed. "
                "Routing to aggregation."
            )

            return "aggregation"

        logger.info(
            "Routing RAG → Document."
        )

        return "document"

    # ------------------------------------------------------------
    # Normal single-agent workflow
    # ------------------------------------------------------------

    logger.info(
        "Agent execution completed. "
        "Routing to aggregation."
    )

    return "aggregation"


# ================================================================
# Aggregation Node
# ================================================================

def aggregation_node(
    state: AgentState,
) -> AgentState:
    """
    Supervisor aggregation node.

    Converts the specialized agent output into
    final_response.
    """

    logger.info(
        "LangGraph: Supervisor aggregation started."
    )

    return supervisor_agent.aggregate(state)


# ================================================================
# Build Workflow
# ================================================================

def build_workflow() -> StateGraph:
    """
    Build the complete AgentOS workflow.

    Normal workflow:

        START
          ↓
       supervisor
          ↓
       selected agent
          ↓
       aggregation
          ↓
         END

    Document workflow:

        START
          ↓
       supervisor
          ↓
       source agent
          ↓
       document
          ↓
       aggregation
          ↓
         END

    Supported document sequences:

        Analytics → Document
        Research  → Document
        RAG       → Document
    """

    graph = StateGraph(
        AgentState
    )

    # ============================================================
    # Register Nodes
    # ============================================================

    graph.add_node(
        "supervisor",
        supervisor_node,
    )

    graph.add_node(
        "chat",
        chat_node,
    )

    graph.add_node(
        "rag",
        rag_node,
    )

    graph.add_node(
        "analytics",
        analytics_node,
    )

    graph.add_node(
        "research",
        research_node,
    )

    graph.add_node(
        "document",
        document_node,
    )

    graph.add_node(
        "aggregation",
        aggregation_node,
    )

    # ============================================================
    # START → Supervisor
    # ============================================================

    graph.add_edge(
        START,
        "supervisor",
    )

    # ============================================================
    # Supervisor → First Planned Agent
    # ============================================================

    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "chat": "chat",
            "rag": "rag",
            "analytics": "analytics",
            "research": "research",
            "document": "document",
            "end": END,
        },
    )

    # ============================================================
    # Agent → Next Step
    # ============================================================

    graph.add_conditional_edges(
        "chat",
        route_after_agent,
        {
            "aggregation": "aggregation",
            "document": "document",
        },
    )

    graph.add_conditional_edges(
        "rag",
        route_after_agent,
        {
            "aggregation": "aggregation",
            "document": "document",
        },
    )

    graph.add_conditional_edges(
        "analytics",
        route_after_agent,
        {
            "aggregation": "aggregation",
            "document": "document",
        },
    )

    graph.add_conditional_edges(
        "research",
        route_after_agent,
        {
            "aggregation": "aggregation",
            "document": "document",
        },
    )

    # ============================================================
    # Document → Aggregation
    # ============================================================

    graph.add_edge(
        "document",
        "aggregation",
    )

    # ============================================================
    # Aggregation → END
    # ============================================================

    graph.add_edge(
        "aggregation",
        END,
    )

    return graph


# ================================================================
# Compiled Workflow
# ================================================================

@lru_cache(maxsize=1)
def get_compiled_workflow():
    """
    Build and compile the workflow once.

    The compiled graph is cached so it is not rebuilt
    for every API request.
    """

    workflow = build_workflow()

    return workflow.compile()