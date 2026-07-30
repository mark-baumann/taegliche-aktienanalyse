"""LLM runtime helpers."""

from src.llm.backend_registry import (
    AGENT_CAPABLE_BACKEND_IDS,
    AUTO_AGENT_BACKEND_ID,
    CLAUDE_CODE_CLI_BACKEND_ID,
    CODEX_CLI_BACKEND_ID,
    GENERATION_ONLY_BACKEND_IDS,
    LITELLM_BACKEND_ID,
    LOCAL_CLI_GENERATION_BACKEND_IDS,
    OPENCODE_CLI_BACKEND_ID,
    SUPPORTED_AGENT_GENERATION_BACKENDS,
    SUPPORTED_AGENT_UI_BACKENDS,
    SUPPORTED_GENERATION_BACKENDS,
    SUPPORTED_GENERATION_FALLBACK_BACKENDS,
    resolve_agent_generation_backend_id,
    resolve_generation_backend_id,
    resolve_generation_fallback_backend_id,
)
from src.llm.generation_backend import (
    GenerationBackend,
    GenerationCapabilities,
    GenerationError,
    GenerationErrorCode,
    GenerationResult,
)
from src.llm.litellm_backend import LiteLLMGenerationBackend

__all__ = [
    "AGENT_CAPABLE_BACKEND_IDS",
    "AUTO_AGENT_BACKEND_ID",
    "CLAUDE_CODE_CLI_BACKEND_ID",
    "CODEX_CLI_BACKEND_ID",
    "GENERATION_ONLY_BACKEND_IDS",
    "LITELLM_BACKEND_ID",
    "LOCAL_CLI_GENERATION_BACKEND_IDS",
    "OPENCODE_CLI_BACKEND_ID",
    "SUPPORTED_AGENT_GENERATION_BACKENDS",
    "SUPPORTED_AGENT_UI_BACKENDS",
    "SUPPORTED_GENERATION_BACKENDS",
    "SUPPORTED_GENERATION_FALLBACK_BACKENDS",
    "GenerationBackend",
    "GenerationCapabilities",
    "GenerationError",
    "GenerationErrorCode",
    "GenerationResult",
    "LiteLLMGenerationBackend",
    "resolve_agent_generation_backend_id",
    "resolve_generation_backend_id",
    "resolve_generation_fallback_backend_id",
]
