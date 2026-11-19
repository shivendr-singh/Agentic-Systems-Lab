# Task 1: Hostel Concierge

A mock-data hostel concierge with Booking and Kitchen specialist tools served over MCP. The app supplies guest identity and room context; neither is intended to be chosen by the model or overridden by guest text.

## Current implementation

- Mock guest bookings, menu, stock, allergens, and kitchen hours are in `data/`.
- Deterministic booking and kitchen rules prepare approval-required proposals and reject invalid requests.
- The MCP server exposes four tools. Booking and Kitchen MCP clients each receive only their own allow-listed tools, with trusted guest context injected by the client adapter.
- Unit and in-memory MCP tests cover core rules, tool isolation, and guest-context validation.

The LLM agents, conversation orchestration, approval pause/resume, and per-request call limits are the next implementation steps. Proposal tools do not yet execute actions.

## Setup

Requires Python 3.11 or newer.

From this directory, install the package and MCP SDK:

```powershell
python -m pip install -e .
```

Run the tests:

```powershell
python -m unittest discover -s tests -v
```

Run the local MCP server:

```powershell
python -m hostel_concierge.mcp.server
```

The VS Code MCP server entry is in the workspace-level `.vscode/mcp.json`.