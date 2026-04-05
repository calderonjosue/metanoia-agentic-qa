"""Provider-side Pact verification example.

This demonstrates how to use PactExecutor to verify a provider
against consumer contracts, including Docker-based testing.
"""

import asyncio
from metanoia.skills.pact_executor.executor import PactExecutor


async def verify_user_service():
    """Verify the user service against consumer contracts."""
    executor = PactExecutor()
    
    result = await executor.execute({
        "mode": "provider",
        "provider": "user-service",
        "pact_url": "./pacts/web-frontend-user-service.json",
        "provider_base_url": "http://localhost:8080",
        "state_handlers": {
            "user 123 exists": "http://localhost:8089/setup/user/123",
            "user 999 does not exist": "http://localhost:8089/setup/user/999"
        }
    })
    
    print(f"Status: {result['status']}")
    
    if result['verification_result']:
        verified = result['verification_result'].get('verified', False)
        print(f"Verified: {verified}")
        print(f"Output: {result['verification_result'].get('output', '')[:500]}")
    
    if result['error']:
        print(f"Error: {result['error']}")
    
    return result


async def verify_with_docker():
    """Verify the user service running in Docker."""
    executor = PactExecutor()
    
    result = await executor.execute({
        "mode": "provider",
        "provider": "user-service",
        "pact_url": "./pacts/web-frontend-user-service.json",
        "provider_base_url": "http://localhost:8080",
        "docker": {
            "enabled": True,
            "image": "my-user-service:latest",
            "port": 8080,
            "health_check": "/health",
            "startup_timeout": 30
        }
    })
    
    print(f"Docker verification status: {result['status']}")
    print(f"Verified: {result.get('verification_result', {}).get('verified', False)}")
    
    return result


async def verify_from_broker():
    """Verify against a contract retrieved from the Pact Broker."""
    executor = PactExecutor()
    
    result = await executor.execute({
        "mode": "provider",
        "provider": "user-service",
        "pact_url": "pact://web-frontend/user-service:latest",
        "provider_base_url": "http://localhost:8080"
    })
    
    return result


async def main():
    """Run all verification examples."""
    print("=== Local Provider Verification ===")
    await verify_user_service()
    
    print("\n=== Docker-Based Verification ===")
    await verify_with_docker()
    
    print("\n=== Broker-Based Verification ===")
    await verify_from_broker()


if __name__ == "__main__":
    asyncio.run(main())
