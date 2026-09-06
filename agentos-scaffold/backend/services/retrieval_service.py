"""
Hybrid Retrieval Service for AgentOS.

Retrieval strategy:

    Semantic Search
          +
        BM25
          ↓
      RRF Fusion
          ↓
    Relevance Gate
          ↓
    Final relevant chunks

Responsibilities:
- Generate a semantic query embedding.
- Search ChromaDB semantically.
- Search indexed chunks using BM25.
- Combine both rankings using RRF.
- Evaluate whether retrieved evidence is relevant.
- Return retrieval results and relevance information.

The RAG Agent will use this service later.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from rank_bm25 import BM25Okapi

from config.settings import get_settings
from database.chroma_client import get_document_collection
from services.embedding_service import embedding_service


logger = logging.getLogger(__name__)

settings = get_settings()


class RetrievalService:
    """
    Provides semantic, BM25, and hybrid document retrieval.
    """

    def __init__(self):
        self.collection = get_document_collection()

    # ============================================================
    # Public Search
    # ============================================================

    def search(
        self,
        query: str,
        file_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform hybrid retrieval and evaluate relevance.

        Returns:

        {
            "relevant": True/False,
            "reason": "...",
            "results": [...]
        }
        """

        if not query or not query.strip():
            raise ValueError(
                "Retrieval query cannot be empty."
            )

        query = query.strip()

        # --------------------------------------------------------
        # 1. Load indexed chunks
        # --------------------------------------------------------

        documents = self._get_documents(file_ids)

        if not documents:
            return {
                "relevant": False,
                "reason": (
                    "No indexed documents are available."
                ),
                "results": [],
            }

        # --------------------------------------------------------
        # 2. Semantic retrieval
        # --------------------------------------------------------

        semantic_results = self._semantic_search(
            query=query,
            file_ids=file_ids,
        )

        # --------------------------------------------------------
        # 3. BM25 retrieval
        # --------------------------------------------------------

        bm25_results = self._bm25_search(
            query=query,
            documents=documents,
        )

        # --------------------------------------------------------
        # 4. RRF fusion
        # --------------------------------------------------------

        fused_results = self._rrf_fusion(
            semantic_results=semantic_results,
            bm25_results=bm25_results,
        )

        # --------------------------------------------------------
        # Retrieval result counts
        # --------------------------------------------------------

        logger.info(
            "SEMANTIC RESULTS COUNT: %d",
            len(semantic_results),
        )

        logger.info(
            "BM25 RESULTS COUNT: %d",
            len(bm25_results),
        )

        logger.info(
            "FUSED RESULTS COUNT: %d",
            len(fused_results),
        )

        # --------------------------------------------------------
        # 5. Relevance evaluation
        # --------------------------------------------------------

        relevant = self._is_relevant(
            fused_results
        )

        # --------------------------------------------------------
        # Relevance result
        # --------------------------------------------------------

        logger.info(
            "RAG RELEVANCE RESULT: %s",
            relevant,
        )

        if not relevant:
            logger.info(
                "No sufficiently relevant chunks found "
                "for query: %s",
                query,
            )

            return {
                "relevant": False,
                "reason": (
                    "The uploaded document does not "
                    "contain sufficiently relevant "
                    "information to answer this question."
                ),
                "results": fused_results[
                    :settings.FINAL_TOP_K
                ],
            }

        final_results = fused_results[
            :settings.FINAL_TOP_K
        ]

        logger.info(
            "Hybrid retrieval completed successfully. "
            "semantic=%d bm25=%d final=%d",
            len(semantic_results),
            len(bm25_results),
            len(final_results),
        )

        return {
            "relevant": True,
            "reason": None,
            "results": final_results,
        }

    # ============================================================
    # Get Documents
    # ============================================================

    def _get_documents(
        self,
        file_ids: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """
        Load indexed document chunks from ChromaDB.
        """

        if file_ids:
            if len(file_ids) == 1:
                where = {
                    "file_id": file_ids[0]
                }
            else:
                where = {
                    "file_id": {
                        "$in": file_ids
                    }
                }

            result = self.collection.get(
                where=where,
                include=[
                    "documents",
                    "metadatas",
                ],
            )

        else:
            result = self.collection.get(
                include=[
                    "documents",
                    "metadatas",
                ],
            )

        ids = result.get("ids", [])
        texts = result.get("documents", [])
        metadatas = result.get("metadatas", [])

        documents = []

        for index, chunk_id in enumerate(ids):
            text = (
                texts[index]
                if index < len(texts)
                else ""
            )

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            if not text:
                continue

            documents.append(
                {
                    "id": chunk_id,
                    "text": text,
                    "metadata": metadata or {},
                }
            )

        return documents

    # ============================================================
    # Semantic Search
    # ============================================================

    def _semantic_search(
        self,
        query: str,
        file_ids: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """
        Search ChromaDB using semantic similarity.
        """

        query_embedding = (
            embedding_service.embed_query(query)
        )

        query_kwargs = {
            "query_embeddings": [
                query_embedding
            ],
            "n_results": settings.SEMANTIC_TOP_K,
            "include": [
                "documents",
                "metadatas",
                "distances",
            ],
        }

        if file_ids:
            if len(file_ids) == 1:
                query_kwargs["where"] = {
                    "file_id": file_ids[0]
                }
            else:
                query_kwargs["where"] = {
                    "file_id": {
                        "$in": file_ids
                    }
                }

        result = self.collection.query(
            **query_kwargs
        )

        ids = result.get(
            "ids",
            [[]]
        )[0]

        texts = result.get(
            "documents",
            [[]]
        )[0]

        metadatas = result.get(
            "metadatas",
            [[]]
        )[0]

        distances = result.get(
            "distances",
            [[]]
        )[0]

        results = []

        for index, chunk_id in enumerate(ids):
            results.append(
                {
                    "id": chunk_id,
                    "text": texts[index],
                    "metadata": (
                        metadatas[index]
                        if index < len(metadatas)
                        else {}
                    ),
                    "distance": (
                        distances[index]
                        if index < len(distances)
                        else None
                    ),
                }
            )

        return results

    # ============================================================
    # BM25 Search
    # ============================================================

    def _bm25_search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Perform lexical BM25 retrieval.
        """

        if not documents:
            return []

        tokenized_documents = [
            self._tokenize(
                document["text"]
            )
            for document in documents
        ]

        bm25 = BM25Okapi(
            tokenized_documents
        )

        query_tokens = self._tokenize(
            query
        )

        if not query_tokens:
            return []

        scores = bm25.get_scores(
            query_tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        results = []

        for index in ranked_indices[
            :settings.BM25_TOP_K
        ]:
            document = documents[index]

            results.append(
                {
                    "id": document["id"],
                    "text": document["text"],
                    "metadata": document["metadata"],
                    "bm25_score": float(
                        scores[index]
                    ),
                }
            )

        return results

    # ============================================================
    # RRF Fusion
    # ============================================================

    def _rrf_fusion(
        self,
        semantic_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        rrf_k: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        Combine semantic and BM25 rankings using
        weighted Reciprocal Rank Fusion.
        """

        combined: Dict[
            str,
            Dict[str, Any]
        ] = {}

        # --------------------------------------------------------
        # Semantic ranking
        # --------------------------------------------------------

        for rank, result in enumerate(
            semantic_results,
            start=1,
        ):
            chunk_id = result["id"]

            if chunk_id not in combined:
                combined[chunk_id] = {
                    "id": chunk_id,
                    "text": result["text"],
                    "metadata": result.get(
                        "metadata",
                        {}
                    ),
                    "semantic_score": None,
                    "bm25_score": 0.0,
                    "rrf_score": 0.0,
                }

            combined[chunk_id][
                "semantic_score"
            ] = result.get(
                "distance"
            )

            combined[chunk_id][
                "rrf_score"
            ] += (
                settings.SEMANTIC_WEIGHT
                / (rrf_k + rank)
            )

        # --------------------------------------------------------
        # BM25 ranking
        # --------------------------------------------------------

        for rank, result in enumerate(
            bm25_results,
            start=1,
        ):
            chunk_id = result["id"]

            if chunk_id not in combined:
                combined[chunk_id] = {
                    "id": chunk_id,
                    "text": result["text"],
                    "metadata": result.get(
                        "metadata",
                        {}
                    ),
                    "semantic_score": None,
                    "bm25_score": 0.0,
                    "rrf_score": 0.0,
                }

            combined[chunk_id][
                "bm25_score"
            ] = result.get(
                "bm25_score",
                0.0,
            )

            combined[chunk_id][
                "rrf_score"
            ] += (
                settings.BM25_WEIGHT
                / (rrf_k + rank)
            )

        # --------------------------------------------------------
        # Sort by RRF score
        # --------------------------------------------------------

        results = list(
            combined.values()
        )

        results.sort(
            key=lambda item: item[
                "rrf_score"
            ],
            reverse=True,
        )

        return results

    # ============================================================
    # Relevance Gate
    # ============================================================

    def _is_relevant(
        self,
        results: List[Dict[str, Any]],
    ) -> bool:
        """
        Determine whether retrieved evidence is strong enough
        to send to the generation stage.

        A result is considered relevant when:

        1. There is a strong semantic match.

        OR

        2. There is a strong BM25 match combined with
           reasonable semantic similarity.

        A small positive BM25 score alone is NOT enough.
        """

        if not results:
            return False

        top_results = results[
            :settings.FINAL_TOP_K
        ]

        for result in top_results:
            semantic_distance = result.get(
                "semantic_score"
            )

            bm25_score = float(
                result.get(
                    "bm25_score",
                    0.0,
                )
            )

            # ----------------------------------------------------
            # Case 1:
            # Strong semantic match
            # ----------------------------------------------------

            if (
                semantic_distance is not None
                and semantic_distance
                <= settings.SEMANTIC_DISTANCE_THRESHOLD
            ):
                return True

            # ----------------------------------------------------
            # Case 2:
            # Strong lexical match AND
            # reasonable semantic similarity
            # ----------------------------------------------------

            if (
                semantic_distance is not None
                and semantic_distance <= 0.90
                and bm25_score
                >= settings.BM25_MIN_SCORE
            ):
                return True

        return False

    # ============================================================
    # Tokenization
    # ============================================================

    def _tokenize(
        self,
        text: str,
    ) -> List[str]:
        """
        Normalize and tokenize text for BM25.
        """

        return re.findall(
            r"\b\w+\b",
            text.lower(),
        )


# ================================================================
# Singleton instance
# ================================================================

retrieval_service = RetrievalService()