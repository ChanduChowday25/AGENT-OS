"""
Central LLM service for AgentOS.

All LLM communication goes through this service.

The rest of AgentOS does not need to know whether the
underlying model is Groq, Gemini, Claude, etc.

To switch providers later, we only change this file
and the corresponding settings/.env values.
"""

import logging
import time

from groq import Groq

from config.settings import get_settings


settings = get_settings()

logger = logging.getLogger(__name__)


class LLMService:
    """
    Central service responsible for communicating with the LLM.

    Agents should only call:

        llm_service.generate(prompt)

    They should NOT know which provider is being used.
    """

    def __init__(self):

        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        # ========================================================
        # Groq client
        # ========================================================

        self.client = Groq(
            api_key=self.api_key,
        )

        logger.info(
            "LLMService initialized | "
            "provider=groq | model=%s",
            self.model,
        )

    # ============================================================
    # Generate
    # ============================================================

    def generate(
        self,
        prompt: str,
        structured: bool = False,
    ) -> str:
        """
        Generate a response from the configured LLM.

        Parameters:
            prompt:
                Prompt sent to the LLM.

            structured:
                If True, request a JSON object from Groq.

                If False, use the normal text response behavior.

        Agents only interact with this method.
        """

        if not prompt or not prompt.strip():
            raise ValueError(
                "LLM prompt cannot be empty."
            )

        start_time = time.perf_counter()

        logger.info(
            "LLM request started | "
            "provider=groq | model=%s | structured=%s",
            self.model,
            structured,
        )

        try:

            # ====================================================
            # Build Groq request
            # ====================================================

            request_kwargs = {
                "model": self.model,

                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],

                "temperature": 0.2,

                "max_tokens": 500,
            }

            # ====================================================
            # Structured JSON response
            # ====================================================

            if structured:

                request_kwargs[
                    "response_format"
                ] = {
                    "type": "json_object"
                }

                logger.info(
                    "Groq JSON response mode enabled."
                )

            # ====================================================
            # Groq request
            # ====================================================

            response = (
                self.client
                .chat
                .completions
                .create(
                    **request_kwargs
                )
            )

            elapsed = (
                time.perf_counter()
                - start_time
            )

            logger.info(
                "LLM request completed | "
                "provider=groq | time=%.2fs",
                elapsed,
            )

            # ====================================================
            # Extract response
            # ====================================================

            content = (
                response
                .choices[0]
                .message
                .content
            )

            if not content:

                raise RuntimeError(
                    "LLM returned an empty response."
                )

            return content.strip()

        # ========================================================
        # Error handling
        # ========================================================

        except Exception as e:

            elapsed = (
                time.perf_counter()
                - start_time
            )

            logger.exception(
                "LLM request failed | "
                "provider=groq | time=%.2fs",
                elapsed,
            )

            error = str(e)
            error_upper = error.upper()

            # ----------------------------------------------------
            # Invalid API key
            # ----------------------------------------------------

            if (
                "401" in error
                or "API KEY" in error_upper
                or "INVALID_API_KEY" in error_upper
            ):

                raise Exception(
                    "Invalid Groq API key."
                ) from e

            # ----------------------------------------------------
            # Rate limit / quota
            # ----------------------------------------------------

            if (
                "429" in error
                or "RATE_LIMIT" in error_upper
            ):

                raise Exception(
                    "Groq API rate limit or quota "
                    "has been exceeded."
                ) from e

            # ----------------------------------------------------
            # Timeout
            # ----------------------------------------------------

            if "TIMEOUT" in error_upper:

                raise Exception(
                    "Groq request timed out."
                ) from e

            # ----------------------------------------------------
            # Generic error
            # ----------------------------------------------------

            raise Exception(
                f"LLM request failed: {error}"
            ) from e


# ================================================================
# Singleton
# ================================================================

llm_service = LLMService()