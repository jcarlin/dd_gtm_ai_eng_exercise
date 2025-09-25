# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This repository serves as a template for multi-agent workflows using Claude Code, specifically designed around a four-agent system for collaborative development projects. The repository name suggests it's intended for drone deployment applications but currently contains workflow templates.

## Repository Structure
```
drone-deploy/
├── memory/multi-agent-template.md      # Template for agent memory/roles
├── usermemory/multi-agent-template.md  # User memory template (duplicate)
└── .claude/settings.local.json        # Claude Code permissions config
```

## Multi-Agent Workflow System

### Four-Agent Architecture
This repository implements a structured multi-agent approach with defined roles:

1. **Agent 1 (Architect)**: Research & Planning
   - System exploration and requirements analysis
   - Architecture planning and design documents
   - Focus on understanding the big picture

2. **Agent 2 (Builder)**: Core Implementation
   - Feature development and main implementation work
   - Core functionality development
   - Building solutions based on Architect's plans

3. **Agent 3 (Validator)**: Testing & Validation
   - Writing tests and validation scripts
   - Quality assurance and debugging
   - **Restriction**: Cannot edit source code, only tests
   - Reports issues to Builder for resolution

4. **Agent 4 (Scribe)**: Documentation & Refinement
   - Documentation creation and maintenance
   - Code refinement and optimization
   - Usage guides and examples

### Agent Communication Protocol
- Each agent must acknowledge their role at the beginning of work
- Agents operate in separate terminal instances
- Clear handoffs between agents with documented work products
- Validator reports issues to Builder rather than fixing directly

## Claude Code Configuration
- Repository has specific permissions configured in `.claude/settings.local.json`
- Currently allows bash grep operations
- No build, lint, or test commands configured (repository is template-only)

## Development Notes
This is currently a template repository. When developing actual drone deployment code:
- Add appropriate package.json with build/test/lint scripts
- Implement actual drone deployment logic following the multi-agent pattern
- Each agent should work within their defined scope and responsibilities
- Use the template files in `/memory` and `/usermemory` to establish agent roles