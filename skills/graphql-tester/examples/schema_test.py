import json
from pathlib import Path
from executor import GraphQLTester


def load_schema_from_file() -> dict:
    schema_path = Path(__file__).parent.parent / "schema.json"
    with open(schema_path) as f:
        return json.load(f)


def validate_schema_structure():
    schema = load_schema_from_file()

    required_keys = ["__schema"]
    for key in required_keys:
        assert key in schema, f"Missing required key: {key}"

    schema_data = schema["__schema"]
    assert "queryType" in schema_data, "Missing queryType"
    assert "mutationType" in schema_data, "Missing mutationType"
    assert "types" in schema_data, "Missing types"

    print("Schema structure validation: PASSED")


def validate_types():
    schema = load_schema_from_file()
    types = schema["__schema"]["types"]

    type_names = [t["name"] for t in types if t.get("name")]

    required_types = ["Query", "Mutation", "User"]
    for required in required_types:
        assert required in type_names, f"Missing required type: {required}"

    print(f"Found {len(types)} types: {', '.join(required_types)}")
    print("Type validation: PASSED")


def validate_introspection_endpoint(endpoint: str):
    client = GraphQLTester(endpoint=endpoint)

    try:
        schema = client.introspect()
        validation = client.validate_schema()

        print(f"Introspection successful: {validation['valid']}")
        print(f"Types discovered: {validation['types_count']}")
        print(f"Has query type: {validation['has_query_type']}")

        return validation["valid"]
    except Exception as e:
        print(f"Introspection failed: {e}")
        return False


if __name__ == "__main__":
    print("=== Schema Validation Example ===\n")

    print("1. Validating schema structure...")
    validate_schema_structure()

    print("\n2. Validating types...")
    validate_types()

    print("\n3. Schema introspection test (requires running endpoint)...")
    is_valid = validate_introspection_endpoint("http://localhost:4000/graphql")
    if not is_valid:
        print("Note: Set a valid endpoint to test live introspection")
