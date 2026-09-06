"""
Embedding service for AgentOS.

Responsibilities:
- Generate semantic embeddings for documents.
- Generate semantic embeddings for user queries.
- Keep embedding API communication outside the agents.
"""

import logging
from typing import List

from google import genai
from google.genai import types

from config.settings import get_settings


logger = logging.getLogger(__name__)

settings = get_settings()


class EmbeddingService:
    """
    Central service responsible for generating embeddings.
    """

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSIONALITY

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    # ============================================================
    # Document Embedding
    # ============================================================

    def embed_text(
        self,
        text: str
    ) -> List[float]:
        """
        Generate an embedding for a single document text.
        """

        if not text or not text.strip():
            raise ValueError(
                "Cannot generate embedding for empty text."
            )

        try:

            content = types.Content(
                parts=[
                    types.Part.from_text(
                        text=text.strip()
                    )
                ]
            )

            response = self.client.models.embed_content(
                model=self.model,
                contents=content,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=self.dimension,
                ),
            )

            if not response.embeddings:
                raise RuntimeError(
                    "Gemini returned no embedding."
                )

            values = response.embeddings[0].values

            if not values:
                raise RuntimeError(
                    "Gemini returned an empty embedding vector."
                )

            return list(values)

        except Exception:
            logger.exception(
                "Failed to generate text embedding."
            )
            raise

    # ============================================================
    # Multiple Document Embeddings
    # ============================================================

    def embed_documents(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Generate one embedding for every document chunk.
        """

        if not texts:
            return []

        cleaned_texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not cleaned_texts:
            raise ValueError(
                "No valid texts provided for embedding."
            )

        embeddings: List[List[float]] = []

        try:

            batch_size = 32

            for start in range(
                0,
                len(cleaned_texts),
                batch_size,
            ):

                batch = cleaned_texts[
                    start:start + batch_size
                ]

                contents = [
                    types.Content(
                        parts=[
                            types.Part.from_text(
                                text=text
                            )
                        ]
                    )
                    for text in batch
                ]

                response = self.client.models.embed_content(
                    model=self.model,
                    contents=contents,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=self.dimension,
                    ),
                )

                if not response.embeddings:
                    raise RuntimeError(
                        "Gemini returned no embeddings."
                    )

                batch_embeddings = []

                for embedding in response.embeddings:

                    if not embedding.values:
                        raise RuntimeError(
                            "Gemini returned an empty embedding."
                        )

                    batch_embeddings.append(
                        list(embedding.values)
                    )

                if len(batch_embeddings) != len(batch):
                    raise RuntimeError(
                        "Gemini returned "
                        f"{len(batch_embeddings)} embeddings "
                        f"for {len(batch)} chunks."
                    )

                embeddings.extend(
                    batch_embeddings
                )

                logger.info(
                    "Generated embeddings for %d/%d chunks.",
                    len(embeddings),
                    len(cleaned_texts),
                )

            if len(embeddings) != len(cleaned_texts):
                raise RuntimeError(
                    "Final embedding count "
                    f"({len(embeddings)}) does not match "
                    f"chunk count ({len(cleaned_texts)})."
                )

            return embeddings

        except Exception:
            logger.exception(
                "Failed to generate document embeddings."
            )
            raise

    # ============================================================
    # Query Embedding
    # ============================================================

    def embed_query(
        self,
        query: str,
    ) -> List[float]:
        """
        Generate an embedding specifically for a user's
        retrieval query.

        Documents use:
            RETRIEVAL_DOCUMENT

        User queries use:
            RETRIEVAL_QUERY
        """

        if not query or not query.strip():
            raise ValueError(
                "Cannot generate embedding for an empty query."
            )

        try:

            content = types.Content(
                parts=[
                    types.Part.from_text(
                        text=query.strip()
                    )
                ]
            )

            response = self.client.models.embed_content(
                model=self.model,
                contents=content,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                    output_dimensionality=self.dimension,
                ),
            )

            if not response.embeddings:
                raise RuntimeError(
                    "Gemini returned no query embedding."
                )

            values = response.embeddings[0].values

            if not values:
                raise RuntimeError(
                    "Gemini returned an empty query embedding."
                )

            return list(values)

        except Exception:
            logger.exception(
                "Failed to generate query embedding."
            )
            raise


# ================================================================
# Singleton instance
# ================================================================

embedding_service = EmbeddingService()