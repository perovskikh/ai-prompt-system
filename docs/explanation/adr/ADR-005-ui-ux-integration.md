# ADR-005: UI/UX Integration Strategy

## Status
**Proposed** | 2026-03-22

## Context

Need to support beautiful UI/UX generation for web apps, CLI tools, and mobile applications through p9i MCP server.

## Decision

We will integrate with modern UI/UX frameworks and tools to enable prompt-driven UI generation.

### Web UI Integration

| Framework | Purpose | Env Variable |
|-----------|---------|--------------|
| TailwindCSS | Utility-first CSS generation | `TAILWIND_API_KEY` |
| shadcn/ui | Component library | - |
| Radix UI | Headless primitives | - |
| Figma API | Design imports | `FIGMA_TOKEN` |

### CLI UI Integration

| Framework | Purpose | Language |
|-----------|---------|----------|
| Textual | Rich CLI interfaces | Python |
| Bubble Tea | TUI framework | Go |
| Blinks | Modern TUI | Rust |

### Desktop/Mobile Integration

| Framework | Purpose | Env Variable |
|-----------|---------|--------------|
| Tauri | Lightweight desktop apps | `TAURI_TOKEN` |
| Electron | Cross-platform desktop | - |
| Flutter | Mobile apps | `FLUTTER_TOKEN` |

## Consequences

- New prompts for UI/UX generation
- Support for multiple frameworks
- Design token integration
- Theme customization

## Required Environment Variables

```bash
# UI/UX
TAILwind_API_KEY=your_key      # Optional: Tailwind AI
FIGMA_TOKEN=your_token         # Figma API for design import
TUI_THEME=dark                 # CLI theme (dark/light)

# Desktop
TAURI_TOKEN=your_token         # Tauri authentication

# Mobile
FLUTTER_TOKEN=your_token       # Flutter/Expo authentication
```

## Alternatives Considered

- Use only TailwindCSS (rejected - need component libraries)
- Generate raw HTML/CSS (rejected - need modern frameworks)
- Skip CLI support (rejected - CLI is important use case)
