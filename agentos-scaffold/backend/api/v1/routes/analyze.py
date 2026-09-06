"""
POST /api/v1/analyze

Analytics controller.

Responsibilities:
- Validate the incoming request.
- Resolve the uploaded file.
- Build the initial AgentState.
- Run the AgentOS LangGraph workflow.
- Return the analytics result.
"""

from fastapi import APIRouter, HTTPException

from schemas.analyze import AnalyzeRequest, AnalyzeResponse
from schemas.agent_state import AgentState
from services.file_service import resolve_file_path
from workflows.agent_workflow import get_compiled_workflow


router = APIRouter()


# ================================================================
# Analyze Endpoint
# ================================================================

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
async def analyze(
    request: AnalyzeRequest,
):
    """
    Execute an analytical request through the AgentOS workflow.
    """

    # ============================================================
    # Validate file ID
    # ============================================================

    if not request.file_id or not request.file_id.strip():
        raise HTTPException(
            status_code=400,
            detail="file_id cannot be empty.",
        )

    # ============================================================
    # Find uploaded file
    # ============================================================

    try:
        file_path = resolve_file_path(
            request.file_id
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Uploaded file not found.",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    # ============================================================
    # Build query
    # ============================================================

    query = (
        request.instructions
        if request.instructions
        and request.instructions.strip()
        else "Analyze the uploaded dataset."
    )

    try:

        # ========================================================
        # Build AgentState
        # ========================================================

        state = AgentState(
            query=query.strip(),
            uploaded_files=[
                str(file_path)
            ],
            conversation_history=[],
            status="pending",
        )

        # ========================================================
        # Get workflow
        # ========================================================

        workflow = get_compiled_workflow()

        # ========================================================
        # Execute workflow
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
        # Get analytics output
        # ========================================================

        analytics_output = final_state.analytics_output

        # ========================================================
        # Workflow / Analytics failure
        # ========================================================

        if final_state.status == "failed":
            raise HTTPException(
                status_code=500,
                detail=(
                    "Analytics workflow failed."
                ),
            )

        # ========================================================
        # No analytics output
        # ========================================================

        if not analytics_output:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Analytics Agent completed "
                    "without producing an output."
                ),
            )

        # ========================================================
        # Return analytics result
        # ========================================================

        return AnalyzeResponse(
            file_id=request.file_id,
            status=analytics_output.get(
                "status",
                "completed",
            ),
            result=analytics_output,
        )

    # ============================================================
    # HTTP Errors
    # ============================================================

    except HTTPException:
        raise

    # ============================================================
    # Unexpected Errors
    # ============================================================

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the analysis request.",
        )