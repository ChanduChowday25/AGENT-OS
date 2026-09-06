"""
Analytics Planner Service.

Responsibilities:
- Convert a complex natural-language analytics request
  into a structured AnalysisPlan.
- Send only the user's query and dataset schema to the LLM.
- Never send the complete dataset to the LLM.
- Never perform the actual analytics calculation.

The actual computation is performed later by Pandas.
"""

import json
from typing import Any, Dict

from prompts.analytics_prompt import ANALYTICS_PLANNER_PROMPT
from schemas.analysis_plan import AnalysisPlan
from services.llm_service import llm_service


class AnalyticsPlannerService:
    """
    Creates structured analytics plans for complex requests.

    The planner is responsible only for understanding
    WHAT the user wants to do with the dataset.

    It does not perform the analysis itself.
    """

    def create_plan(
        self,
        query: str,
        schema: Dict[str, Any],
    ) -> AnalysisPlan:
        """
        Convert a natural-language analytics request
        into a validated AnalysisPlan.
        """

        prompt = ANALYTICS_PLANNER_PROMPT.format(
            query=query,
            schema=schema,
        )

        response = llm_service.generate(
            prompt,
            structured=True,
        )

        if isinstance(response, str):
            response = json.loads(response)

        return AnalysisPlan.model_validate(response)


analytics_planner_service = AnalyticsPlannerService()