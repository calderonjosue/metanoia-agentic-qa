#!/usr/bin/env python3
"""
WireMock Stateful Mock Examples - Multi-step API scenarios.
"""

from skills.wiremock_executor import WireMockExecutor, Scenario


def user_registration_flow():
    """Simulate a user registration flow with multiple states."""
    with WireMockExecutor() as executor:
        executor.reset()

        scenario = Scenario("user_registration")

        scenario.stub_post("/api/register", {"sessionId": "abc123"})
        scenario.in_state("Started")
        scenario.will_set_state_to("AwaitingEmailVerification")

        scenario.stub_post("/api/verify-email", {"verified": True})
        scenario.in_state("AwaitingEmailVerification")
        scenario.will_set_state_to("EmailVerified")

        scenario.stub_get("/api/profile", {"id": 1, "name": "New User", "verified": True})
        scenario.in_state("EmailVerified")

        executor.add_scenario_stub(scenario)

        print("User registration flow created")
        print(f"Mappings: {executor.get_mappings()}")


def shopping_cart_flow():
    """Simulate a shopping cart checkout flow."""
    with WireMockExecutor() as executor:
        executor.reset()

        cart_scenario = Scenario("shopping_cart")

        cart_scenario.stub_post("/api/cart", {"cartId": "cart-1", "items": []})
        cart_scenario.in_state("CartCreated")
        cart_scenario.will_set_state_to("EmptyCart")

        cart_scenario.stub_post("/api/cart/cart-1/items", {"itemId": "item-1", "name": "Widget"})
        cart_scenario.in_state("EmptyCart")
        cart_scenario.will_set_state_to("HasItems")

        cart_scenario.stub_get("/api/cart/cart-1", {"cartId": "cart-1", "items": ["item-1"]})
        cart_scenario.in_state("HasItems")

        cart_scenario.stub_delete("/api/cart/cart-1/items/item-1", {"removed": True})
        cart_scenario.in_state("HasItems")
        cart_scenario.will_set_state_to("EmptyCart")

        cart_scenario.stub_post("/api/checkout", {"orderId": "order-1", "status": "paid"})
        cart_scenario.in_state("HasItems")
        cart_scenario.will_set_state_to("CheckedOut")

        executor.add_scenario_stub(cart_scenario)

        print("Shopping cart flow created")


def multi_state_auth_flow():
    """Simulate authentication with token refresh."""
    with WireMockExecutor() as executor:
        executor.reset()

        auth = Scenario("auth_flow")

        auth.stub_post("/api/login", {"accessToken": "token-123", "refreshToken": "refresh-abc"})
        auth.in_state("LoggedOut")
        auth.will_set_state_to("LoggedIn")

        auth.stub_get("/api/me", {"id": 1, "name": "User"})
        auth.in_state("LoggedIn")

        auth.stub_post("/api/refresh", {"accessToken": "token-456", "refreshToken": "refresh-def"})
        auth.in_state("LoggedIn")
        auth.will_set_state_to("LoggedIn")

        auth.stub_post("/api/logout", {"success": True})
        auth.in_state("LoggedIn")
        auth.will_set_state_to("LoggedOut")

        executor.add_scenario_stub(auth)

        print("Auth flow created")


def conditional_responses():
    """Stub that returns different responses based on request body."""
    with WireMockExecutor() as executor:
        executor.reset()

        scenario = Scenario("price_lookup")

        scenario.stub_matching(
            url_path="/api/prices",
            method="POST",
            body_pattern=r'\{"productId": "basic"\}',
            response_status=200,
            response_body={"productId": "basic", "price": 9.99}
        )
        scenario.in_state("Started")

        scenario.stub_matching(
            url_path="/api/prices",
            method="POST",
            body_pattern=r'\{"productId": "premium"\}',
            response_status=200,
            response_body={"productId": "premium", "price": 29.99}
        )
        scenario.in_state("Started")

        scenario.stub_matching(
            url_path="/api/prices",
            method="POST",
            body_pattern=r'\{"productId": "enterprise"\}',
            response_status=200,
            response_body={"productId": "enterprise", "price": 99.99}
        )
        scenario.in_state("Started")

        executor.add_scenario_stub(scenario)

        print("Conditional responses scenario created")


def paginated_api():
    """Simulate paginated API responses."""
    with WireMockExecutor() as executor:
        executor.reset()

        scenario = Scenario("paginated_users")

        scenario.stub_matching(
            url_path="/api/users",
            method="GET",
            headers={"Accept": "application/json"},
            response_status=200,
            response_body={
                "data": [{"id": 1}, {"id": 2}],
                "page": 1,
                "totalPages": 3,
                "hasMore": True
            }
        )
        scenario.in_state("Page1")

        scenario.stub_matching(
            url_path="/api/users",
            method="GET",
            headers={"Accept": "application/json"},
            response_status=200,
            response_body={
                "data": [{"id": 3}, {"id": 4}],
                "page": 2,
                "totalPages": 3,
                "hasMore": True
            }
        )
        scenario.in_state("Page1")

        scenario.stub_matching(
            url_path="/api/users",
            method="GET",
            headers={"Accept": "application/json"},
            response_status=200,
            response_body={
                "data": [{"id": 5}],
                "page": 3,
                "totalPages": 3,
                "hasMore": False
            }
        )
        scenario.in_state("Page2")

        executor.add_scenario_stub(scenario)

        print("Paginated API scenario created")


def state_transitions():
    """Example showing how state transitions work."""
    with WireMockExecutor() as executor:
        executor.reset()

        executor.stub_matching(
            url_path="/api/step1",
            method="POST",
            response_status=200,
            response_body={"step": 1, "next": "step2"},
            scenario_name="workflow",
            new_state="Step1Complete"
        )

        executor.stub_matching(
            url_path="/api/step2",
            method="POST",
            response_status=200,
            response_body={"step": 2, "next": "step3"},
            scenario_name="workflow",
            required_state="Step1Complete",
            new_state="Step2Complete"
        )

        executor.stub_matching(
            url_path="/api/step3",
            method="POST",
            response_status=200,
            response_body={"step": 3, "complete": True},
            scenario_name="workflow",
            required_state="Step2Complete",
            new_state="WorkflowComplete"
        )

        print("State transition workflow created")


if __name__ == "__main__":
    print("=== User Registration Flow ===")
    user_registration_flow()

    print("\n=== Shopping Cart Flow ===")
    shopping_cart_flow()

    print("\n=== Auth Flow ===")
    multi_state_auth_flow()

    print("\n=== Conditional Responses ===")
    conditional_responses()

    print("\n=== Paginated API ===")
    paginated_api()

    print("\n=== State Transitions ===")
    state_transitions()
