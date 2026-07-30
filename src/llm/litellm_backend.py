"""LiteLLM generation backend wrapper."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.llm.generation_backend import (
    GenerationBackend,
    GenerationCapabilities,
    GenerationResult,
)

LiteLLMCallable = Callable[..., tuple[str, str, dict[str, Any]]]


def _provider_from_model(model: str) -> str:
    if not model:
        return ""
    if "/" in model:
        return model.split("/", 1)[0]
    return "openai"


class LiteLLMGenerationBackend(GenerationBackend):
    """Thin adapter around the existing LiteLLM analyzer call path."""

    backend_id = "litellm"
    capabilities = GenerationCapabilities(
        supports_json=True,
        supports_tools=True,
        supports_stream=True,
        supports_vision=False,
        supports_health_check=False,
        supports_smoke_test=False,
    )

    def __init__(self, completion_callable: LiteLLMCallable):
        self._completion_callable = completion_callable

    def generate(
        self,
        prompt: str,
        generation_config: dict[str, Any],
        *,
        system_prompt: str | None = None,
        stream: bool = False,
        stream_progress_callback: Callable[[int], None] | None = None,
        response_validator: Callable[[str], None] | None = None,
        audit_context: dict[str, Any] | None = None,
    ) -> GenerationResult:
        text, model, usage = self._completion_callable(
            prompt,
            generation_config,
            system_prompt=system_prompt,
            stream=stream,
            stream_progress_callback=stream_progress_callback,
            response_validator=response_validator,
            audit_context=audit_context,
        )
        provider = str((usage or {}).get("provider") or _provider_from_model(model))
        return GenerationResult(
            text=text,
            model=model,
            provider=provider,
            backend=self.backend_id,
            usage=usage or {},
            raw=None,
            diagnostics={},
        )
