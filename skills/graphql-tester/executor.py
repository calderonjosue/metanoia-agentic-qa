import json
from typing import Any, Optional

import requests


class GraphQLTester:
    def __init__(
        self,
        endpoint: str,
        headers: Optional[dict] = None,
        timeout: int = 30
    ):
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout
        self._schema = None

    def query(
        self,
        query: str,
        variables: Optional[dict] = None,
        operation_name: Optional[str] = None
    ) -> dict:
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name

        response = requests.post(
            self.endpoint,
            json=payload,
            headers=self.headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        result = response.json()

        if "errors" in result:
            raise GraphQLError(result["errors"])

        return result.get("data", {})

    def mutation(
        self,
        query: str,
        variables: Optional[dict] = None,
        operation_name: Optional[str] = None
    ) -> dict:
        return self.query(query, variables, operation_name)

    def introspect(self) -> dict:
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    ...FullType
                }
                directives {
                    name
                    description
                    locations
                    args {
                        ...InputValue
                    }
                }
            }
        }

        fragment FullType on __Type {
            kind
            name
            description
            fields(includeDeprecated: true) {
                name
                description
                args {
                    ...InputValue
                }
                type {
                    ...TypeRef
                }
                isDeprecated
                deprecationReason
            }
            inputFields {
                ...InputValue
            }
            interfaces {
                ...TypeRef
            }
            enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
            }
            possibleTypes {
                ...TypeRef
            }
        }

        fragment InputValue on __InputValue {
            name
            description
            type {
                ...TypeRef
            }
            defaultValue
        }

        fragment TypeRef on __Type {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                    ofType {
                                        kind
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        response = requests.post(
            self.endpoint,
            json={"query": introspection_query},
            headers=self.headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        result = response.json()

        if "errors" in result:
            raise GraphQLError(result["errors"])

        self._schema = result.get("data", {})
        return self._schema

    def validate_schema(self) -> dict:
        if self._schema is None:
            self.introspect()

        schema = self._schema
        validation_results = {
            "has_query_type": schema.get("__schema", {}).get("queryType") is not None,
            "types_count": len(schema.get("__schema", {}).get("types", [])),
            "directives_count": len(schema.get("__schema", {}).get("directives", [])),
            "valid": True
        }

        if not validation_results["has_query_type"]:
            validation_results["valid"] = False
            validation_results["error"] = "No query type found"

        return validation_results

    def get_schema_json(self) -> str:
        if self._schema is None:
            self.introspect()
        return json.dumps(self._schema, indent=2)


class GraphQLError(Exception):
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(str(errors))
