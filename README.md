# Agentic Systems Lab

An extensible workspace for building and testing agentic applications. It currently starts with the two tasks from the NAGP Agentic AI assignment:

- **Task 1 - Hostel Concierge:** a multi-agent application with an orchestrator, Booking and Kitchen specialists, MCP tools, approval gates, and mock hostel data.
- **Task 2 - Smart Incident Response:** an n8n workflow that routes incidents using a team directory and incident history.

## Project layout

```text
.
|-- task1/
|   |-- data/                       # Mock guests, menu, and kitchen hours
|   |-- src/hostel_concierge/
|   |   |-- agents/                 # Orchestrator and specialist agents
|   |   `-- mcp/                    # MCP server and tool integration
|   |-- tests/                      # Automated behavior and access-control tests
|   `-- traces/                     # Reference-prompt outputs for the assignment
`-- task2/
    |-- workflow/                   # n8n workflow export
    `-- demo/                       # Demo materials
```

## Getting started

We will implement **Task 1** first. Its README and run instructions will be expanded once the language, agent framework, and MCP SDK are selected. Task 2 will be built and exported separately from n8n.

Use fictional data only. Keep API keys and other credentials in local environment configuration; do not commit secrets.
