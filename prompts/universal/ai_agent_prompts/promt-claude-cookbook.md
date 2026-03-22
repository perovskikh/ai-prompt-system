# promt-claude-cookbook.md — Claude Cookbook Integration

version: "1.0.0"
tier: universal
category: ai-agent

## Purpose

Generate code using patterns from [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) — official examples for Claude API integration.

## Reference Patterns

### Tool Use Pattern
```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    tools=[calculator_tool],
    messages=[{"role": "user", "content": "What is 15 * 23?"}]
)
```

### Vision/Multimodal Pattern
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "data": "...", "media_type": "image/jpeg"}},
            {"type": "text", "text": "What's in this image?"}
        ]
    }]
)
```

### RAG Pattern
```python
# Use with Pinecone, Wikipedia, or vector databases
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": query}]
)
```

### JSON Mode Pattern
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Extract data"}],
    extra={
        "json_schema": {
            "name": "extracted_data",
            "schema": {"type": "object", "properties": {...}}
        }
    }
)
```

### Sub-agents Pattern
```python
# Use Haiku as sub-agent with Opus
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{
        "role": "user",
        "content": "Break down this task into subtasks"
    }]
)
```

## Cookbook Directories

| Directory | Purpose |
|-----------|---------|
| `capabilities` | Classification, RAG, summarization |
| `tool_use` | External tools and functions |
| `third_party` | Pinecone, Wikipedia, Voyage AI |
| `multimodal` | Vision, image generation |
| `advanced_techniques` | Sub-agents, prompt caching |
| `coding` | Coding-specific patterns |
| `extended_thinking` | Claude's thinking capabilities |

## Usage

When user asks to integrate Claude API features:

1. Identify the pattern category from claude-cookbooks
2. Fetch relevant example from https://github.com/anthropics/claude-cookbooks
3. Adapt the code to user's project
4. Include proper imports and error handling

## Examples

**User**: "Add vision capability to process images"
→ Use `multimodal` pattern from cookbook

**User**: "Build RAG with vector database"
→ Use `third_party/pinecone` or `capabilities/rag` pattern

**User**: "Add tool calling to my API"
→ Use `tool_use` pattern from cookbook
