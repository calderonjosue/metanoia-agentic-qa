"""Consumer-side Pact contract testing example.

This demonstrates how to use PactExecutor to create consumer-driven contracts.
"""

import asyncio
from metanoia.skills.pact_executor.executor import PactExecutor


async def test_user_service_contract():
    """Create a contract for the user service."""
    executor = PactExecutor()
    
    result = await executor.execute({
        "mode": "consumer",
        "consumer": "web-frontend",
        "provider": "user-service",
        "version": "1.0.0",
        "interactions": [
            {
                "description": "a request to get user by ID",
                "request": {
                    "method": "GET",
                    "path": "/users/123",
                    "headers": {
                        "Accept": "application/json"
                    }
                },
                "response": {
                    "status": 200,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "id": 123,
                        "name": "John Doe",
                        "email": "john@example.com",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                },
                "provider_state": "user 123 exists"
            },
            {
                "description": "a request to get user that does not exist",
                "request": {
                    "method": "GET",
                    "path": "/users/999",
                    "headers": {
                        "Accept": "application/json"
                    }
                },
                "response": {
                    "status": 404,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "error": "User not found",
                        "code": "USER_404"
                    }
                },
                "provider_state": "user 999 does not exist"
            },
            {
                "description": "a request to create a new user",
                "request": {
                    "method": "POST",
                    "path": "/users",
                    "headers": {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    "body": {
                        "name": "Jane Smith",
                        "email": "jane@example.com"
                    }
                },
                "response": {
                    "status": 201,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "id": 456,
                        "name": "Jane Smith",
                        "email": "jane@example.com",
                        "created_at": "2024-01-15T11:00:00Z"
                    }
                }
            }
        ]
    })
    
    print(f"Status: {result['status']}")
    print(f"Pact file: {result['pact_file']}")
    
    if result['error']:
        print(f"Error: {result['error']}")
    
    return result


async def test_product_service_contract():
    """Create a contract for the product catalog service."""
    executor = PactExecutor()
    
    result = await executor.execute({
        "mode": "consumer",
        "consumer": "mobile-app",
        "provider": "product-service",
        "version": "2.1.0",
        "interactions": [
            {
                "description": "get all products",
                "request": {
                    "method": "GET",
                    "path": "/products",
                    "query": {
                        "page": "1",
                        "limit": "20"
                    }
                },
                "response": {
                    "status": 200,
                    "body": {
                        "products": [
                            {"id": 1, "name": "Widget", "price": 9.99},
                            {"id": 2, "name": "Gadget", "price": 29.99}
                        ],
                        "total": 2,
                        "page": 1
                    }
                }
            },
            {
                "description": "get product by ID",
                "request": {
                    "method": "GET",
                    "path": "/products/1"
                },
                "response": {
                    "status": 200,
                    "body": {
                        "id": 1,
                        "name": "Widget",
                        "price": 9.99,
                        "in_stock": True,
                        "categories": ["electronics", "tools"]
                    }
                }
            }
        ]
    })
    
    return result


if __name__ == "__main__":
    asyncio.run(test_user_service_contract())
    asyncio.run(test_product_service_contract())
