# Prompts — Example Prompts Library

This directory contains example AI prompts for the AI Prompt System.

## Status

These prompts were originally created for the **CodeShift** project and serve as **examples** of how to write effective AI agent prompts.

## Using These Prompts

1. **Copy** a prompt that matches your use case
2. **Customize** the content for your project
3. **Add** to your own prompt registry

## Prompt Structure

Each prompt follows the frontmatter format:

```yaml
---
name: promt-example
version: "1.0"
type: your-project-type
layer: Operations|Design|Implementation|Meta
status: active
tags: [tag1, tag2]
---
```

## Layers

| Layer | Description |
|-------|-------------|
| Operations | Verification, testing, quality |
| Design | Architecture, planning |
| Implementation | Feature add, bug fix |
| Meta | System, governance |

## Customization Guide

To adapt these prompts for your project:

1. Update `type:` to your project name
2. Modify project-specific paths and references
3. Adjust layer and tags as needed
4. Update version and date
