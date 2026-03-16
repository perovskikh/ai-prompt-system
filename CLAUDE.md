# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Prompt System is an MCP (Model Context Protocol) server for managing AI prompts through their full lifecycle: from idea to production implementation. It provides 8 MCP tools for prompt execution, chaining, versioning, and project memory management.

## Commands

### Run the Server

```bash
# Local development
pip install -e .
python -m src.api.server

# Docker (recommended for full stack)
docker compose up -d
```

### Testing

```bash
# Run tests (pytest configured in pyproject.toml)
pytest

# Inside Docker container
docker exec <container> pytest
```

### Linting

```bash
# Black formatting
black src/

# Ruff linting
ruff check src/
```

## Architecture

The system follows an MCP server architecture with the following key components:

```
src/api/server.py    # FastMCP server with 8 tools (main entry point)
prompts/              # 28 markdown prompt files organized by category
memory/               # Project context/memory storage (per-project JSON files)
config/               # YAML configs for settings and API keys
docker/               # Dockerfile and docker-compose.yml
```

### MCP Tools (8 total)

1. `run_prompt` - Execute a single prompt
2. `run_prompt_chain` - Execute multi-stage prompt chain (ideation → finish)
3. `list_prompts` - List available prompts from registry
4. `get_project_memory` - Get project context/memory
5. `save_project_memory` - Save project context
6. `adapt_to_project` - Auto-detect project stack (Python/JS, frameworks, DB)
7. `clean_context` - Clean context when token limit exceeded
8. `get_available_mcp_tools` - List all available tools

### Data Flow

- **Prompts**: Stored as `.md` files in `prompts/` directory, registered in `prompts/registry.json`
- **Memory**: Per-project JSON files stored in `memory/{project_id}/context.json`
- **API Keys**: Environment-based (`API_KEYS__SYSTEM`, `API_KEYS__PROJECT_{n}`)
- **Rate Limiting**: 60-second sliding window per API key

### Storage Strategy

- **PostgreSQL** (port 5432): Persistent data (prompts, versions, projects, audit logs)
- **Redis** (port 6379): Hot data, cache, pub/sub, rate limiting

The MCP server runs on port 8000 with SSE transport.

### Key Classes

- `APIKeyManager` - Manages API keys with rate limiting (60s window)
- `AuditLogger` - Tracks all API actions in memory
- `PromptExecutor` - Executes prompts through LLM (Z.ai by default)
- `LLMClient` - Multi-provider LLM client (Z.ai, Anthropic, OpenRouter, MiniMax)
- FastMCP server instance created in `src/api/server.py`

### LLM Integration

The system now executes prompts through LLM providers. Default provider is Z.ai (Anthropic-compatible):
- Provider auto-detection based on available API keys in `.env`
- Priority: Z.ai → OpenRouter → Anthropic → MiniMax
- Streaming support for real-time output

API keys are loaded from `.env`:
- `ZAI_API_KEY` - Primary (Anthropic-compatible)
- `ANTHROPIC_API_KEY` - Anthropic direct
- `OPENROUTER_API_KEY` - OpenRouter fallback
- `MINIMAX_API_KEY` - MiniMax fallback

## Integration with Claude Code

To use with Claude Code, add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "ai-prompt-system": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "perovskikh/ai-prompt-system"]
    }
  }
}
```

## Documentation

- `README.md` - Project overview and quick start
- `prompts/README.md` - Guide to using prompts
- `MCP_INTEGRATION.md` - Claude Code integration details
- `SYSTEM_ARCHITECTURE.md` - Full system diagram