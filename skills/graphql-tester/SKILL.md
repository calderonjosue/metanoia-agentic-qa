---
name: graphql-tester
description: GraphQL API testing skill. Test queries, mutations, schema introspection, variables, and authentication. Trigger: When testing GraphQL APIs, running GraphQL queries/mutations, validating schemas, or setting up GraphQL test automation.
---

# GraphQL Tester Skill

Execute GraphQL API tests with query/mutation validation, schema introspection, variable support, and authentication headers.

## Usage

```python
from graphql_tester import GraphQLTester

client = GraphQLTester(endpoint="https://api.example.com/graphql")

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
print(result)

result = client.mutation(
    query="""
    mutation CreateUser($name: String!, $email: String!) {
        createUser(name: $name, email: $email) {
            id
            name
        }
    }
    """,
    variables={"name": "Alice", "email": "alice@example.com"}
)
```

## Components

- `executor.py` - GraphQLTester class
- `schema.json` - Introspection result cache
- `examples/schema_test.py` - Schema validation example
