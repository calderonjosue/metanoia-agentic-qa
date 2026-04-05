from locust import HttpUser, task, between, tag
import json


class APILoadUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.headers["Content-Type"] = "application/json"
        self.client.headers["Accept"] = "application/json"

    @task(3)
    @tag("api", "products")
    def list_products(self):
        with self.client.get("/api/products", name="/api/products", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response.success()
                    else:
                        response.failure("Expected list response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status {response.status_code}")

    @task(2)
    @tag("api", "products")
    def get_product(self):
        product_id = 1
        with self.client.get(f"/api/products/{product_id}", name="/api/products/[id]", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()

    @task(2)
    @tag("api", "orders")
    def create_order(self):
        payload = {
            "product_id": 1,
            "quantity": 1,
            "customer_id": 123
        }
        with self.client.post("/api/orders", json=payload, name="/api/orders", catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            elif response.status_code == 400:
                response.failure("Bad request - invalid payload")
            else:
                response.failure(f"Unexpected status {response.status_code}")

    @task(1)
    @tag("api", "customers")
    def get_customer(self):
        customer_id = 1
        with self.client.get(f"/api/customers/{customer_id}", name="/api/customers/[id]", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()

    @task(1)
    @tag("api", "health")
    def health_check(self):
        self.client.get("/api/health", name="/api/health")

    @task(1)
    @tag("api", "search")
    def search_products(self):
        with self.client.get("/api/products?search=example", name="/api/products?search", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
