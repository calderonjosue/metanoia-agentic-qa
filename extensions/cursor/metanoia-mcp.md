# Metanoia-QA MCP Server

Configure Cursor to use Metanoia-QA as an AI agent.

## Setup

1. Copy this file to `.cursor/mcp.json`
2. Update the command path
3. Restart Cursor

## Configuration

```json
{
  "mcpServers": {
    "metanoia-qa": {
      "command": "npx",
      "args": ["metanoia-qa", "mcp"]
    }
  }
}
```

## Features

- Inline test status
- One-click sprint start
- Real-time agent monitoring
