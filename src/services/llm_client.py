# src/services/llm_client.py
"""
LLM Client - Multi-provider support (MiniMax, Z.ai, Anthropic, OpenRouter)

Provides async client for executing prompts through various LLM providers.
"""

import os
import json
import logging
from typing import Optional, AsyncGenerator
import httpx

logger = logging.getLogger(__name__)

# Provider configurations (updated March 2026)
PROVIDERS = {
    "minimax": {
        "base_url": "https://api.minimax.chat/v1",
        "endpoint": "/text/chatcompletion_pro",
        "model": "abab6.5s-chat",
        "env_key": "MINIMAX_API_KEY",
    },
    "zai": {
        "base_url": "https://api.z.ai/api",
        "endpoint": "/anthropic/v1/messages",
        "model": "claude-sonnet-4-6",  # Updated to 4.6
        "env_key": "ZAI_API_KEY",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "endpoint": "/v1/messages",
        "model": "claude-sonnet-4-6",  # Updated to 4.6 (March 2026)
        "env_key": "ANTHROPIC_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "endpoint": "/chat/completions",
        "model": "google/gemini-2.0-flash-exp",  # Updated model
        "env_key": "OPENROUTER_API_KEY",
    },
    # Free models from OpenRouter
    "openrouter_free": {
        "base_url": "https://openrouter.ai/api/v1",
        "endpoint": "/chat/completions",
        "model": "minimax/minimax-m2.5:free",
        "env_key": "OPENROUTER_API_KEY",
    },
    "glm": {
        "base_url": "https://openrouter.ai/api/v1",
        "endpoint": "/chat/completions",
        "model": "z-ai/glm-4.5-air:free",
        "env_key": "OPENROUTER_API_KEY",
    },
}


class LLMClient:
    """Async client for multiple LLM providers."""

    def __init__(
        self,
        provider: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Auto-detect provider based on available keys
        if provider == "auto":
            provider = self._detect_provider()

        self.provider = provider
        config = PROVIDERS.get(provider, PROVIDERS["zai"])

        self.base_url = config["base_url"]
        self.endpoint = config["endpoint"]
        self.default_model = config["model"]

        # Use provided key or fall back to env
        self.api_key = api_key or os.getenv(config["env_key"])
        self.model = model or self.default_model

        if not self.api_key:
            logger.warning(f"No API key for provider: {provider}")

    def _detect_provider(self) -> str:
        """Detect best available provider."""
        # Priority: Z.ai (has working Anthropic API), then OpenRouter, then Anthropic
        if os.getenv("ZAI_API_KEY"):
            return "zai"
        if os.getenv("OPENROUTER_API_KEY"):
            return "openrouter"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.getenv("MINIMAX_API_KEY"):
            return "minimax"
        return "zai"  # fallback to zai as primary

    def _get_headers(self) -> dict:
        """Get provider-specific headers."""
        if self.provider == "anthropic":
            return {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
        elif self.provider == "zai":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        else:
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

    def _build_payload(
        self,
        messages: list[dict],
        temperature: Optional[float],
        max_tokens: Optional[int],
        stream: bool,
    ) -> dict:
        """Build provider-specific payload."""
        temp = temperature or self.temperature
        tokens = max_tokens or self.max_tokens

        if self.provider in ("anthropic", "zai"):
            return {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
            }
        else:
            # OpenRouter, MiniMax use OpenAI-like format
            return {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
                "stream": stream,
            }

    def _parse_response(self, response: dict) -> dict:
        """Parse provider-specific response format."""
        if self.provider in ("anthropic", "zai"):
            # Anthropic format: {"content": [...], "stop_reason": "..."}
            content = response.get("content", [])
            if content and isinstance(content, list):
                text = content[0].get("text", "") if content[0].get("type") == "text" else str(content[0])
            else:
                text = ""
            return {
                "choices": [{"message": {"content": text}}],
                "usage": response.get("usage", {}),
            }
        else:
            # OpenRouter, MiniMax use OpenAI format
            return response

    async def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> dict | AsyncGenerator[str, None]:
        """
        Send chat request to LLM provider.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            stream: Enable streaming response

        Returns:
            dict response or async generator for streaming
        """
        if not self.api_key:
            return {"error": "No API key configured"}

        headers = self._get_headers()
        payload = self._build_payload(messages, temperature, max_tokens, stream)
        endpoint = f"{self.base_url}{self.endpoint}"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                if stream:
                    return self._stream_response(client, endpoint, headers, payload)
                else:
                    response = await client.post(endpoint, headers=headers, json=payload)
                    response.raise_for_status()
                    return self._parse_response(response.json())
        except httpx.HTTPStatusError as e:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"API error: {e.response.status_code}", "details": e.response.text[:200]}
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            return {"error": str(e)}

    async def _stream_response(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        headers: dict,
        payload: dict,
    ) -> AsyncGenerator[str, None]:
        """Handle streaming response from provider."""
        async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    if self.provider in ("anthropic", "zai"):
                        # SSE format: data: {"type":"content_block_delta"...}
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if chunk.get("type") == "content_block_delta":
                                    delta = chunk.get("delta", {})
                                    if delta.get("text"):
                                        yield delta["text"]
                            except json.JSONDecodeError:
                                continue
                    else:
                        # OpenAI format: data: {"choices":[...]}
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if delta.get("content"):
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Optional[dict] = None,
    ) -> dict:
        """
        Generate response from prompt.

        Args:
            system_prompt: System instructions
            user_prompt: User input
            context: Additional context data

        Returns:
            dict with generated text and metadata
        """
        messages = []

        # Build system message with context if provided
        if context:
            context_str = self._format_context(context)
            full_system = f"{system_prompt}\n\n## Context\n{context_str}"
        else:
            full_system = system_prompt

        # Some providers don't support system role - combine with first user message
        if self.provider in ("zai",):
            # For Z.ai: system becomes part of user message
            messages.append({
                "role": "user",
                "content": f"[System: {full_system}]\n\nUser request: {user_prompt}"
            })
        else:
            messages.append({"role": "system", "content": full_system})
            messages.append({"role": "user", "content": user_prompt})

        result = await self.chat(messages)

        if "error" in result:
            return {
                "status": "error",
                "error": result["error"],
            }

        try:
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "status": "success",
                "content": content,
                "model": self.model,
                "usage": result.get("usage", {}),
            }
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse response: {e}, result: {result}")
            return {
                "status": "error",
                "error": "Invalid response format",
            }

    def _format_context(self, context: dict) -> str:
        """Format context dict as string for prompt."""
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"### {key}")
                for k, v in value.items():
                    lines.append(f"- {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"### {key}")
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)


def get_llm_client() -> LLMClient:
    """Get configured LLM client from environment."""
    return LLMClient()