# Landing Agents Platform

This repository contains the scaffold for the Landing Agents Platform described in the solution architecture document. It provides a Python-based implementation skeleton organised around the conversation engine and the FastMCP-driven tool servers that power the agentic workflows.

## Repository layout

```
.
├── docs/
│   └── architecture.md        # Solution architecture document
├── pyproject.toml             # Project metadata and dependencies
└── src/
    └── landing_agents/
        ├── conversation/      # Conversation engine domain logic
        └── mcp/               # FastMCP server implementations
```

## Getting started

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

> **Note:** `fastmcp` is declared as a dependency but is not vendored in this repository. Install it from PyPI or your internal package index before running the MCP servers.

## Running MCP servers

Each MCP server module exposes an `app` instance that can be started with FastMCP's CLI:

```bash
python -m landing_agents.mcp.rag_server
```

Replace `rag_server` with the server you want to run (`crm_server`, `calendar_server`, `messaging_server`, `analytics_server`, or `experiment_server`).

## Conversation engine

The conversation engine modules provide domain models (state, agents, phases) and a `ConversationEngine` class capable of routing user turns to specialist agents. Integrate this package into your application server or orchestration layer to connect the conversational runtime with the MCP tools.

## Next steps

* Flesh out the placeholder tool implementations with real integrations.
* Extend the conversation engine logic with actual LLM prompts and policy enforcement.
* Add tests and evaluation harnesses as the implementation matures.

