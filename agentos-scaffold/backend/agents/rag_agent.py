"""
RAG Agent for AgentOS.

Responsibilities:
- Validate that documents are available.
- Retrieve relevant information from uploaded documents.
- Use hybrid retrieval:
    Semantic Search + BM25 + RRF
- Stop safely when relevant information is not found.
- Generate a grounded answer using LLM.
- Preserve detailed retrieval trace for backend debugging.
- Generate clean, deduplicated citations for users.
- Store the result in state.rag_output.
"""

import logging
from typing import Any, Dict, List

from agents.base_agent import BaseAgent
from schemas.agent_state import AgentState

from prompts.rag_prompt import RAG_PROMPT
from services.llm_service import llm_service
from services.retrieval_service import retrieval_service


logger = logging.getLogger(__name__)


class RAGAgent(BaseAgent):
    """
    Retrieval-Augmented Generation agent.

    Flow:

        AgentState
            ↓
        Validate
            ↓
        Hybrid Retrieval
            ↓
        Relevance Gate
            ↓
        Build Context
            ↓
        RAG Prompt
            ↓
          LLM
            ↓
        Clean Answer + Citations
            ↓
        state.rag_output
    """

    name = "rag"

    # ============================================================
    # Validation
    # ============================================================

    def validate(
        self,
        state: AgentState,
    ) -> bool:
        """
        Validate that uploaded documents are available.
        """

        if not state.uploaded_files:

            logger.warning(
                "RAG validation failed: "
                "no uploaded files available."
            )

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
        Execute the complete RAG pipeline.

        The agent writes its result to:

            state.rag_output
        """

        logger.info(
            "RAG Agent started for query: %s",
            state.query,
        )

        # --------------------------------------------------------
        # 1. Validate
        # --------------------------------------------------------

        if not self.validate(state):

            state.rag_output = {
                "status": "failed",
                "answer": (
                    "No uploaded documents are available "
                    "for this question."
                ),
                "sources": [],
                "retrieved_chunks": [],
            }

            return state

        try:

            # ----------------------------------------------------
            # 2. Hybrid Retrieval
            # ----------------------------------------------------

            retrieval_response = (
                retrieval_service.search(
                    query=state.query,
                    file_ids=state.uploaded_files,
                )
            )

            relevant = retrieval_response.get(
                "relevant",
                False,
            )

            results = retrieval_response.get(
                "results",
                [],
            )

            reason = retrieval_response.get(
                "reason"
            )

            # ----------------------------------------------------
            # 3. Relevance Gate
            # ----------------------------------------------------

            if not relevant:

                state.rag_output = {
                    "status": "completed",
                    "answer": (
                        "The uploaded document does not "
                        "contain enough information to "
                        "answer this question."
                    ),
                    "sources": [],
                    "retrieved_chunks": [],
                    "reason": reason,
                }

                logger.info(
                    "RAG Agent stopped because no "
                    "sufficiently relevant information "
                    "was found."
                )

                return state

            # ----------------------------------------------------
            # 4. Build Context
            # ----------------------------------------------------

            context = self._build_context(
                results
            )

            # ----------------------------------------------------
            # 5. Build RAG Prompt
            # ----------------------------------------------------

            prompt = RAG_PROMPT.format(
                query=state.query,
                context=context,
            )

            # ----------------------------------------------------
            # 6. Generate Answer
            # ----------------------------------------------------

            answer = llm_service.generate(
                prompt=prompt
            )

            # ----------------------------------------------------
            # 7. Build Clean User-Facing Sources
            # ----------------------------------------------------

            sources = self._build_user_sources(
                results
            )

            # ----------------------------------------------------
            # 8. Build Detailed Backend Trace
            # ----------------------------------------------------

            retrieved_chunks = (
                self._build_retrieval_trace(
                    results
                )
            )

            # ----------------------------------------------------
            # 9. Store Final RAG Output
            # ----------------------------------------------------

            state.rag_output = {
                "status": "completed",
                "answer": answer,
                "sources": sources,
                "retrieved_chunks": retrieved_chunks,
            }

            logger.info(
                "RAG Agent completed successfully."
            )

            return state

        except Exception as exc:

            logger.exception(
                "RAG Agent execution failed."
            )

            state.rag_output = {
                "status": "failed",
                "answer": (
                    "I was unable to process the "
                    "uploaded document."
                ),
                "sources": [],
                "retrieved_chunks": [],
                "error": str(exc),
            }

            return state

    # ============================================================
    # Context Builder
    # ============================================================

    def _build_context(
        self,
        results: List[Dict[str, Any]],
    ) -> str:
        """
        Convert retrieved chunks into context for Gemini.

        Internal metadata is included so Gemini can understand
        the origin of each piece of retrieved information.


        LLM must not invent citation information.
        """

        context_parts = []

        for index, result in enumerate(
            results,
            start=1,
        ):

            metadata = result.get(
                "metadata",
                {},
            )

            source = metadata.get(
                "source",
                "Unknown source",
            )

            page = metadata.get(
                "page",
                "Unknown page",
            )

            chunk_id = result.get(
                "id",
                "Unknown chunk",
            )

            text = result.get(
                "text",
                "",
            )

            context_parts.append(
                f"""
[Context {index}]
Source: {source}
Page: {page}
Chunk ID: {chunk_id}

{text}
"""
            )

        return "\n".join(
            context_parts
        )

    # ============================================================
    # User-Facing Sources
    # ============================================================

    def _build_user_sources(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Build clean, deduplicated citations for the user.

        Multiple chunks from the same document and same page
        are grouped into a single source entry.

        Example:

            Chunk 1 → CompanyPolicy.pdf, Page 1
            Chunk 2 → CompanyPolicy.pdf, Page 1
            Chunk 3 → CompanyPolicy.pdf, Page 2

        becomes:

            CompanyPolicy.pdf
            Pages: [1, 2]
        """

        grouped: Dict[
            str,
            Dict[str, Any]
        ] = {}

        for result in results:

            metadata = result.get(
                "metadata",
                {},
            )

            source = metadata.get(
                "source",
                "Unknown source",
            )

            page = metadata.get(
                "page"
            )

            if source not in grouped:

                grouped[source] = {
                    "source": source,
                    "pages": [],
                }

            if (
                page is not None
                and page not in grouped[source]["pages"]
            ):
                grouped[source]["pages"].append(
                    page
                )

        # Sort page numbers for clean display.
        for source_data in grouped.values():

            source_data["pages"].sort()

        return list(
            grouped.values()
        )

    # ============================================================
    # Backend Retrieval Trace
    # ============================================================

    def _build_retrieval_trace(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Preserve detailed chunk-level retrieval information.

        This is intended for backend debugging, workflow traces,
        and future AgentOS observability.

        This information does NOT need to be shown directly
        to normal users.
        """

        trace = []

        for result in results:

            trace.append(
                {
                    "id": result.get(
                        "id"
                    ),
                    "semantic_score": result.get(
                        "semantic_score"
                    ),
                    "bm25_score": result.get(
                        "bm25_score",
                        0.0,
                    ),
                    "rrf_score": result.get(
                        "rrf_score",
                        0.0,
                    ),
                    "metadata": result.get(
                        "metadata",
                        {},
                    ),
                }
            )

        return trace


# ================================================================
# Singleton instance
# ================================================================

rag_agent = RAGAgent()