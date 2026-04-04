"""Sample test scenarios for e-commerce demo."""

TEST_SCENARIOS = {
    "checkout_flow": {
        "name": "Complete Checkout Flow",
        "description": "Test complete purchase journey from cart to confirmation",
        "tool": "playwright",
        "steps": [
            {
                "action": "goto",
                "url": "http://localhost:3000/products"
            },
            {
                "action": "click",
                "target": ".product-card:first-child"
            },
            {
                "action": "click",
                "target": "#add-to-cart"
            },
            {
                "action": "goto",
                "url": "http://localhost:3000/cart"
            },
            {
                "action": "click",
                "target": "#checkout-button"
            },
            {
                "action": "fill",
                "target": "#email",
                "value": "test@example.com"
            },
            {
                "action": "fill",
                "target": "#card-number",
                "value": "4242424242424242"
            },
            {
                "action": "click",
                "target": "#pay-now"
            },
            {
                "action": "wait_for",
                "target": ".order-confirmation"
            }
        ],
        "assertions": [
            {
                "type": "element_visible",
                "target": ".order-confirmation",
                "message": "Order confirmation should appear"
            },
            {
                "type": "text_contains",
                "target": ".order-id",
                "pattern": "ORD-"
            }
        ]
    },
    "product_search": {
        "name": "Product Search",
        "description": "Search for products and verify results",
        "tool": "playwright",
        "steps": [
            {
                "action": "goto",
                "url": "http://localhost:3000"
            },
            {
                "action": "fill",
                "target": "#search-input",
                "value": "laptop"
            },
            {
                "action": "click",
                "target": "#search-button"
            },
            {
                "action": "wait_for",
                "target": ".search-results"
            }
        ],
        "assertions": [
            {
                "type": "element_count",
                "target": ".product-card",
                "min": 1,
                "message": "At least one product should appear"
            }
        ]
    }
}

API_ENDPOINTS = [
    {"method": "GET", "path": "/api/products"},
    {"method": "GET", "path": "/api/products/{id}"},
    {"method": "GET", "path": "/api/categories"},
    {"method": "POST", "path": "/api/orders", "body": {"items": [], "total": 0}},
    {"method": "GET", "path": "/api/orders/{id}"},
]
