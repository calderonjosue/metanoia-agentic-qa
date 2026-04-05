# GraphQL Tester

GraphQL API testing toolkit with query/mutation support, schema introspection, and authentication.

## Installation

```bash
pip install requests
```

## Quick Start

```python
from graphql_tester import GraphQLTester

client = GraphQLTester(
    endpoint="https://api.example.com/graphql",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

# Query
result = client.query(
    query="""
    query GetUser($id: ID!) {
        user(id: $id) {
            id
            name
            email
        }
    }
    """,
    variables={"id": "123"}
)

# Mutation
result = client.mutation(
    query="""
    mutation CreateUser($name: String!, $email: String!) {
        createUser(name: $name, email: $email) {
            id
        }
    }
    """,
    variables={"name": "Alice", "email": "alice@example.com"}
)
```

## Features

- **Query Testing** - Execute GraphQL queries with variables
- **Mutation Testing** - Execute GraphQL mutations
- **Schema Introspection** - Fetch and validate schema
- **Variable Support** - JSON variables for parameterized queries
- **Authentication** - Custom headers (Bearer, API keys, etc.)

## API

### GraphQLTester

| Parameter | Type | Description |
|-----------|------|-------------|
| `endpoint` | str | GraphQL endpoint URL |
| `headers` | dict | Optional authentication headers |
| `timeout` | int | Request timeout in seconds (default: 30) |

### Methods

- `query(query, variables=None)` - Execute a query
- `mutation(query, variables=None)` - Execute a mutation
- `introspect()` - Fetch full schema introspection
- `validate_schema()` - Validate schema structure

## Examples

See `examples/` directory for detailed examples.
