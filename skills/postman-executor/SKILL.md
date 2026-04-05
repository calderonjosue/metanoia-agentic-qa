---
name: postman-executor
version: 1.0.0
author: Metanoia-QA Team
description: Execute Postman API tests and collection runners for automated API testing
triggers:
  - postman:test
  - postman:run
  - postman:execute
  - api:test
  - api:automation
---

# Postman Executor

Execute Postman API tests and collection runners with this skill.

## Overview

The Postman Executor enables automated API testing by running Postman collections, individual requests, and collection runners. It supports both Newman CLI execution and Postman API integration.

## Features

- Run Postman collections via Newman CLI
- Execute collection runners with environment configurations
- Support for JSON/CSV data files
- Configurable iteration counts and delays
- Export test results in multiple formats

## Structure

```
postman-executor/
├── SKILL.md          # This file
├── executor.py       # Main executor implementation
├── schema.json       # Input/output contract
├── examples/        # Example usage
│   └── api_test.js  # API test example
└── README.md         # Documentation
```

## Usage

### Basic Collection Run

```python
from postman_executor.executor import PostmanExecutor

executor = PostmanExecutor()
result = await executor.execute({
    "collection": "./my_collection.json",
    "environment": "./dev_env.json"
})
```

### With Iterations

```python
result = await executor.execute({
    "collection": "./collection.json",
    "environment": "./env.json",
    "iterations": 10,
    "delay": 1000
})
```

## Requirements

- [Newman](https://www.npmjs.com/package/newman) installed (`npm install -g newman`)
- Postman collection JSON file
- Optional: environment JSON file

## Input Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `collection` | string | Yes | Path to Postman collection JSON |
| `environment` | string | No | Path to environment JSON |
| `iterations` | number | No | Number of iterations (default: 1) |
| `delay` | number | No | Delay between requests in ms |
| `export_results` | boolean | No | Export results to file |
| `report_format` | string | No | Output format: json, html, cli |

## Output Schema

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "success" or "error" |
| `summary` | object | Run summary with passed/failed counts |
| `results` | object | Detailed test results |
| `error` | string | Error message if status is error |

## API Reference

See `executor.py` for full implementation details.
