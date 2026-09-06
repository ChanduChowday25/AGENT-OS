"""
Document Agent

Responsibilities:
- Determine whether the user requested a document.
- Identify available source outputs.
- Select relevant information.
- Use the existing LLM service to create professional report content.
- Generate PDF/DOCX documents.
- Store the result in AgentState.document_output.

Important:
- The complete dataset is NEVER sent to the LLM.
- Only compact agent outputs are sent to the LLM.
- The LLM does NOT generate PDF/DOCX.
- DocumentService handles actual file generation.
- The existing llm_service is used, so the configured Groq
  model/provider remains centralized.
- Other agent output fields are never modified.
"""

import json
import logging
import re
from typing import Any

from agents.base_agent import BaseAgent
from services.report_service import create_report
from prompts.document_prompt import DOCUMENT_PROMPT
from schemas.agent_state import AgentState
from services.document_service import document_service
from services.llm_service import llm_service


logger = logging.getLogger(__name__)


class DocumentAgent(BaseAgent):

    name = "document"

    # ============================================================
    # Token / input protection
    # ============================================================

    MAX_SOURCE_CHARS = 6000

    # ============================================================
    # Validate
    # ============================================================

    def validate(
        self,
        state: AgentState,
    ) -> bool:
        """
        Validate the document request.
        """

        if state is None:
            return False

        if not state.query:
            return False

        if not state.query.strip():
            return False

        return True

    # ============================================================
    # Determine format
    # ============================================================

    def determine_format(
        self,
        query: str,
    ) -> str:
        """
        Determine whether the user requested PDF or DOCX.

        Default:
            PDF
        """

        query_lower = query.lower()

        if (
            "docx" in query_lower
            or "word document" in query_lower
            or "word file" in query_lower
        ):
            return "docx"

        return "pdf"

    # ============================================================
    # Identify sources
    # ============================================================

    def identify_sources(
        self,
        state: AgentState,
    ) -> list[str]:
        """
        Identify available agent outputs.
        """

        sources = []

        if state.analytics_output:
            sources.append("analytics")

        if state.research_output:
            sources.append("research")

        if state.rag_output:
            sources.append("rag")

        return sources

    # ============================================================
    # Build compact source information
    # ============================================================

    def build_source_information(
        self,
        state: AgentState,
        sources: list[str],
    ) -> str:
        """
        Build compact information for the Document LLM.

        The complete dataset is never sent to the LLM.

        The Document Agent extracts only the information that
        is useful for creating a professional document.

        Dataset-level information and operation-level information
        are kept separate so the LLM does not confuse:

            total dataset rows

        with:

            filtered/matched rows.
        """

        source_data: dict[str, Any] = {}

        # ========================================================
        # Analytics
        # ========================================================

        if "analytics" in sources:

            analytics_output = (
                state.analytics_output or {}
            )

            analytics_data: dict[str, Any] = {
                "status": analytics_output.get(
                    "status"
                ),
                "operation": analytics_output.get(
                    "operation"
                ),
                "column": analytics_output.get(
                    "column"
                ),
                "result": analytics_output.get(
                    "result"
                ),
                "answer": analytics_output.get(
                    "answer"
                ),
                "filters": analytics_output.get(
                    "filters"
                ),
                "group_column": analytics_output.get(
                    "group_column"
                ),
                "value_column": analytics_output.get(
                    "value_column"
                ),
            }

            # ----------------------------------------------------
            # Dataset information
            #
            # Keep this separate from operation-specific
            # information.
            # ----------------------------------------------------

            dataset_info = analytics_output.get(
                "dataset_info"
            )

            if isinstance(
                dataset_info,
                dict,
            ):

                compact_dataset_info = {}

                # ------------------------------------------------
                # Map dataset_info into explicit names.
                #
                # This helps the LLM understand exactly what
                # each number represents.
                # ------------------------------------------------

                if "rows" in dataset_info:

                    compact_dataset_info[
                        "total_rows"
                    ] = dataset_info["rows"]

                if "columns" in dataset_info:

                    compact_dataset_info[
                        "total_columns"
                    ] = dataset_info["columns"]

                if "column_names" in dataset_info:

                    column_names = (
                        dataset_info[
                            "column_names"
                        ]
                    )

                    if isinstance(
                        column_names,
                        list,
                    ):

                        compact_dataset_info[
                            "column_names"
                        ] = column_names[:20]

                    else:

                        compact_dataset_info[
                            "column_names"
                        ] = column_names

                if "numeric_columns" in dataset_info:

                    numeric_columns = (
                        dataset_info[
                            "numeric_columns"
                        ]
                    )

                    if isinstance(
                        numeric_columns,
                        list,
                    ):

                        compact_dataset_info[
                            "numeric_columns"
                        ] = numeric_columns[:20]

                    else:

                        compact_dataset_info[
                            "numeric_columns"
                        ] = numeric_columns

                if compact_dataset_info:

                    analytics_data[
                        "dataset"
                    ] = compact_dataset_info

            # ----------------------------------------------------
            # Filter information
            #
            # matched_rows belongs specifically to the filter
            # operation, so keep it under operation_result.
            # ----------------------------------------------------

            if (
                analytics_output.get(
                    "operation"
                )
                == "filter"
            ):

                analytics_data[
                    "operation_result"
                ] = {
                    "matched_rows": analytics_output.get(
                        "matched_rows"
                    ),
                    "filters": analytics_output.get(
                        "filters"
                    ),
                }

            # ----------------------------------------------------
            # GroupBy results
            #
            # Keep only a small number of grouped results.
            # ----------------------------------------------------

            grouped_rows = analytics_output.get(
                "grouped_rows"
            )

            if isinstance(
                grouped_rows,
                list,
            ):

                analytics_data[
                    "grouped_rows"
                ] = grouped_rows[:20]

                if len(grouped_rows) > 20:

                    analytics_data[
                        "grouped_rows_note"
                    ] = (
                        f"Showing first 20 of "
                        f"{len(grouped_rows)} "
                        f"grouped results."
                    )

            # ----------------------------------------------------
            # Sorted results
            #
            # Keep only the first 10 rows.
            # ----------------------------------------------------

            sorted_rows = analytics_output.get(
                "sorted_rows"
            )

            if isinstance(
                sorted_rows,
                list,
            ):

                analytics_data[
                    "sorted_rows"
                ] = sorted_rows[:10]

                if len(sorted_rows) > 10:

                    analytics_data[
                        "sorted_rows_note"
                    ] = (
                        f"Showing first 10 of "
                        f"{len(sorted_rows)} "
                        f"sorted results."
                    )

            # ----------------------------------------------------
            # IMPORTANT:
            #
            # filtered_rows is intentionally NOT included.
            #
            # The Analytics Agent can keep the complete data
            # internally for other parts of AgentOS, but the
            # Document LLM does not need the raw rows.
            # ----------------------------------------------------

            source_data[
                "analytics"
            ] = analytics_data

        # ========================================================
        # Research
        # ========================================================

        if "research" in sources:

            research_output = (
                state.research_output or {}
            )

            source_data[
                "research"
            ] = {
                "status": research_output.get(
                    "status"
                ),
                "answer": research_output.get(
                    "answer"
                ),
                "sources": research_output.get(
                    "sources",
                    [],
                ),
            }

        # ========================================================
        # RAG
        # ========================================================

        if "rag" in sources:

            rag_output = (
                state.rag_output or {}
            )

            source_data[
                "rag"
            ] = {
                "status": rag_output.get(
                    "status"
                ),
                "answer": rag_output.get(
                    "answer"
                ),
                "sources": rag_output.get(
                    "sources",
                    [],
                ),
            }

        # ========================================================
        # Convert to compact JSON
        # ========================================================

        serialized = json.dumps(
            source_data,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
            default=str,
        )

        # ========================================================
        # Final input-size protection
        # ========================================================

        if len(serialized) > self.MAX_SOURCE_CHARS:

            logger.warning(
                "Document Agent source information exceeded "
                "the configured character limit. "
                "Truncating before LLM call."
            )

            serialized = (
                serialized[
                    :self.MAX_SOURCE_CHARS
                ]
                + "\n[Source information truncated.]"
            )

        return serialized

    # ============================================================
    # Clean LLM response
    # ============================================================

    def clean_llm_response(
        self,
        response: str,
    ) -> str:
        """
        Clean common formatting added by the LLM.

        Handles responses such as:

            ```json
            {...}
            ```

        and:

            ```text
            {...}
            ```
        """

        response = response.strip()

        # --------------------------------------------------------
        # Remove code fences
        # --------------------------------------------------------

        response = re.sub(
            r"^```(?:json|JSON|text)?\s*",
            "",
            response,
        )

        response = re.sub(
            r"\s*```$",
            "",
            response,
        )

        response = response.strip()

        # --------------------------------------------------------
        # Find JSON object if the model added
        # a small explanation before/after it.
        # --------------------------------------------------------

        first_brace = response.find(
            "{"
        )

        last_brace = response.rfind(
            "}"
        )

        if (
            first_brace != -1
            and last_brace != -1
            and last_brace > first_brace
        ):

            response = response[
                first_brace:last_brace + 1
            ]

        return response.strip()

    # ============================================================
    # Validate report structure
    # ============================================================

    def validate_report_structure(
        self,
        report: Any,
    ) -> dict:
        """
        Validate and normalize the JSON returned by the LLM.
        """

        if not isinstance(
            report,
            dict,
        ):

            raise ValueError(
                "Document LLM response must be a JSON object."
            )

        title = report.get(
            "title"
        )

        summary = report.get(
            "summary",
            "",
        )

        sections = report.get(
            "sections",
            [],
        )

        if not title:

            raise ValueError(
                "Document report is missing a title."
            )

        if not isinstance(
            sections,
            list,
        ):

            raise ValueError(
                "Document report sections must be a list."
            )

        normalized_sections = []

        # --------------------------------------------------------
        # Executive Summary
        # --------------------------------------------------------

        if summary:

            normalized_sections.append(
                {
                    "heading": "Executive Summary",
                    "paragraphs": [
                        str(summary)
                    ],
                    "bullets": [],
                }
            )

        # --------------------------------------------------------
        # Sections
        # --------------------------------------------------------

        for section in sections:

            if not isinstance(
                section,
                dict,
            ):

                continue

            heading = section.get(
                "heading",
                "Section",
            )

            paragraphs = section.get(
                "paragraphs",
                [],
            )

            bullets = section.get(
                "bullets",
                [],
            )

            if not isinstance(
                paragraphs,
                list,
            ):

                paragraphs = [
                    paragraphs
                ]

            if not isinstance(
                bullets,
                list,
            ):

                bullets = [
                    bullets
                ]

            normalized_sections.append(
                {
                    "heading": str(
                        heading
                    ),
                    "paragraphs": [
                        str(value)
                        for value
                        in paragraphs
                        if value
                    ],
                    "bullets": [
                        str(value)
                        for value
                        in bullets
                        if value
                    ],
                }
            )

        return {
            "title": str(
                title
            ),
            "sections": normalized_sections,
        }

    # ============================================================
    # Generate structured report using LLM
    # ============================================================

    def generate_report_content(
        self,
        state: AgentState,
        sources: list[str],
    ) -> dict:
        """
        Ask the existing LLM service to create professional
        report content.

        Only compact agent output is sent.
        """

        source_information = (
            self.build_source_information(
                state,
                sources,
            )
        )

        prompt = DOCUMENT_PROMPT.format(
            query=state.query,
            source_information=source_information,
        )

        logger.info(
            "Document Agent sending compact information "
            "to LLM | sources=%s | chars=%d",
            sources,
            len(source_information),
        )

        # --------------------------------------------------------
        # Existing centralized LLM service.
        #
        # We do NOT create a separate Groq client here.
        # --------------------------------------------------------

        response = llm_service.generate(
            prompt,
            structured=True,
        )

        if not response:

            raise ValueError(
                "The Document LLM returned an empty response."
            )

        response = self.clean_llm_response(
            response
        )

        logger.debug(
            "Document LLM response received | chars=%d",
            len(response),
        )

        # --------------------------------------------------------
        # Parse JSON
        # --------------------------------------------------------

        try:

            report = json.loads(
                response
            )

        except json.JSONDecodeError as e:

            logger.error(
                "Document LLM returned invalid JSON."
            )

            raise ValueError(
                "The Document LLM returned invalid "
                "structured content."
            ) from e

        # --------------------------------------------------------
        # Validate structure
        # --------------------------------------------------------

        return self.validate_report_structure(
            report
        )

    # ============================================================
    # Create document
    # ============================================================

    def create_document(
        self,
        report_content: dict,
        document_format: str,
    ) -> str:
        """
        Pass structured report content to DocumentService.

        The LLM is not involved here.
        """

        title = report_content[
            "title"
        ]

        sections = report_content[
            "sections"
        ]

        if document_format == "docx":

            return document_service.create_docx(
                title=title,
                sections=sections,
                filename="agentos_report.docx",
            )

        return document_service.create_pdf(
            title=title,
            sections=sections,
            filename="agentos_report.pdf",
        )

    # ============================================================
    # Execute
    # ============================================================

    def execute(
        self,
        state: AgentState,
    ) -> AgentState:

        logger.info(
            "Document Agent started."
        )

        state.status = "running"

        try:

            # ====================================================
            # Validate
            # ====================================================

            if not self.validate(state):

                state.document_output = {
                    "status": "failed",
                    "answer": (
                        "A valid document request "
                        "is required."
                    ),
                }

                state.status = "failed"

                return state

            # ====================================================
            # Determine format
            # ====================================================

            document_format = (
                self.determine_format(
                    state.query
                )
            )

            # ====================================================
            # Identify sources
            # ====================================================

            sources = (
                self.identify_sources(
                    state
                )
            )

            # ====================================================
            # Validate source availability
            # ====================================================

            if not sources:

                state.document_output = {
                    "status": "failed",
                    "answer": (
                        "There is no analytics, research, "
                        "or document information available "
                        "to prepare the requested document."
                    ),
                    "format": document_format,
                    "sources": [],
                }

                state.status = "failed"

                return state

            # ====================================================
            # Generate professional report
            # ====================================================

            report_content = (
                self.generate_report_content(
                    state,
                    sources,
                )
            )

            # ====================================================
            # Create actual document
            # ====================================================

            file_path = (
                self.create_document(
                    report_content,
                    document_format,
                )
            )
            report_metadata = create_report(
           filename=file_path.split("\\")[-1],
           report_format=document_format,
           storage_path=file_path,
)

            # ====================================================
            # Store ONLY in document_output
            # ====================================================

            state.document_output = {
                "status": "completed",
                "format": document_format,
                "document_type": "report",
                "report_id": report_metadata["report_id"],
                "sources": sources,
                "title": report_content[
                    "title"
                ],
                "query": state.query,
                "file_path": file_path,
                "sections": report_content[
                    "sections"
                ],
            }

            state.status = "completed"

            logger.info(
                "Document generated successfully | "
                "format=%s | sources=%s | path=%s",
                document_format,
                sources,
                file_path,
            )

            return state

        # ========================================================
        # Error handling
        # ========================================================

        except Exception as e:

            logger.exception(
                "Document Agent execution failed."
            )

            state.document_output = {
                "status": "failed",
                "answer": (
                    "I was unable to prepare "
                    "the requested document."
                ),
                "error": str(e),
            }

            state.errors.append(
                str(e)
            )

            state.status = "failed"

            return state


# ================================================================
# Singleton
# ================================================================

document_agent = DocumentAgent()