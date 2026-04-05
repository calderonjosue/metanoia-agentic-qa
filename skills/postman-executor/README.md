# Postman Executor

Execute Postman API tests and collection runners for automated API testing.

## Overview

The Postman Executor enables automated API testing by running Postman collections, individual requests, and collection runners using the Newman CLI.

## Installation

### Prerequisites

- Node.js and npm installed
- Newman CLI installed globally

### Install Newman

```bash
npm install -g newman
```

Verify installation:

```bash
newman --version
```

## Quick Start

### Basic Usage

```python
import asyncio
from postman_executor.executor import PostmanExecutor

async def main():
    executor = PostmanExecutor()
    
    result = await executor.execute({
        "collection": "./my_collection.json",
        "environment": "./dev_env.json"
    })
    
    print(f"Status: {result['status']}")
    print(f"Passed: {result['summary']['passed']}")
    print(f"Failed: {result['summary']['failed']}")

asyncio.run(main())
```

### Running with Iterations

```python
result = await executor.execute({
    "collection": "./api_tests.json",
    "environment": "./staging_env.json",
    "iteration_count": 10,
    "delay_request": 500,
    "report_format": "json"
})
```

## Input Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `collection` | string | Yes | - | Path to Postman collection JSON |
| `environment` | string | No | - | Path to environment JSON |
| `iteration_count` | integer | No | 1 | Number of iterations |
| `iteration_data` | string | No | - | CSV/JSON data file path |
| `delay_request` | integer | No | 0 | Delay between requests (ms) |
| `report_format` | string | No | json | Output format: json, html, cli, junit |
| `folder` | string | No | - | Run specific folder in collection |

## Output Format

```json
{
  "status": "success",
  "summary": {
    "total": 25,
    "passed": 23,
    "failed": 2,
    "skipped": 0
  },
  "results": {
    "summary": {...},
    "raw_output": "..."
  },
  "error": null
}
```

## Examples

See `examples/api_test.js` for a Postman collection example.

## File Structure

```
postman-executor/
├── SKILL.md          # Skill definition
├── executor.py       # Executor implementation
├── schema.json       # Input/output schema
├── examples/
│   └── api_test.js  # Example collection
└── README.md         # This file
```

## Requirements

- Newman CLI >= 5.0.0
- Valid Postman collection JSON
- Optional: Postman environment JSON

## Troubleshooting

### Newman not found

```bash
npm install -g newman
```

### Collection validation failed

Ensure your collection follows Postman Collection v2.1 format.

### Environment not loading

Check that environment JSON has `values` array with key-value pairs.
