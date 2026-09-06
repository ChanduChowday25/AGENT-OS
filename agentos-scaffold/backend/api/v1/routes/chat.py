"""
POST /api/v1/chat

Chat controller.

Responsibilities:
- Validate the incoming request.
- Build the initial AgentState.
- Run the AgentOS LangGraph workflow.
- Return the final response and workflow trace.
"""

import uuid

from fastapi import APIRouter, HTTPException

from schemas.chat import ChatRequest, ChatResponse
from schemas.agent_state import AgentState
from workflows.agent_workflow import get_compiled_workflow


router = APIRouter()


# ================================================================
# Chat Endpoint
# ================================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
):
    """
    Execute a user request through the AgentOS workflow.
    """

    # ============================================================
    # Validate query
    # ============================================================

    if not request.query or not request.query.strip():

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    try:

        # ========================================================
        # Conversation ID
        # ========================================================

        conversation_id = (
            request.conversation_id
            or str(uuid.uuid4())
        )

        # ========================================================
        # Build initial AgentState
        # ========================================================

        state = AgentState(
            query=request.query.strip(),
            uploaded_files=request.uploaded_file_ids,
            conversation_history=[],
            status="pending",
        )

        # ========================================================
        # Get compiled workflow
        # ========================================================

        workflow = get_compiled_workflow()

        # ========================================================
        # Run complete AgentOS workflow
        # ========================================================

        result = workflow.invoke(state)

        # ========================================================
        # Convert result to AgentState
        # ========================================================

        if isinstance(result, AgentState):

            final_state = result

        else:

            final_state = AgentState.model_validate(
                result
            )

        # ========================================================
        # Check workflow failure
        # ========================================================

        if final_state.status == "failed":

            raise HTTPException(
                status_code=500,
                detail="Workflow execution failed.",
            )

        # ========================================================
        # Get final response
        # ========================================================

        final_response = (
            final_state.final_response
        )

        if not final_response:

            final_response = (
                "The workflow completed without "
                "producing a response."
            )

        # ========================================================
        # Build workflow trace
        # ========================================================

        workflow_trace = [
            event.model_dump()
            for event in final_state.workflow_trace
        ]

        # ========================================================
        # Return clean API response
        # ========================================================

        return ChatResponse(
            conversation_id=conversation_id,
            final_response=str(
                final_response
            ),
            workflow_trace=workflow_trace,
        )

    except HTTPException:

        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the chat request.",
        )