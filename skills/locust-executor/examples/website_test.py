from locust import HttpUser, task, between, tag
import json


class WebsiteUser(HttpUser):
    wait_time = between(2, 5)
    host = "https://example.com"

    def on_start(self):
        self.client.headers["User-Agent"] = "LocustLoadTest/1.0"

    @task(5)
    @tag("website", "homepage")
    def homepage(self):
        with self.client.get("/", name="/", catch_response=True) as response:
            if response.status_code == 200:
                if len(response.content) > 1000:
                    response.success()
                else:
                    response.failure("Homepage content too short")
            else:
                response.failure(f"Homepage returned {response.status_code}")

    @task(3)
    @tag("website", "navigation")
    def about_page(self):
        self.client.get("/about", name="/about")

    @task(3)
    @tag("website", "navigation")
    def contact_page(self):
        self.client.get("/contact", name="/contact")

    @task(2)
    @tag("website", "content")
    def blog_page(self):
        self.client.get("/blog", name="/blog")

    @task(2)
    @tag("website", "content")
    def pricing_page(self):
        self.client.get("/pricing", name="/pricing")

    @task(1)
    @tag("website", "api")
    def api_status(self):
        with self.client.get("/api/status", name="/api/status", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "ok":
                        response.success()
                    else:
                        response.failure("Status not ok")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON")
            else:
                response.failure(f"API returned {response.status_code}")

    @task(1)
    @tag("website", "static")
    def static_assets(self):
        self.client.get("/static/css/main.css", name="/static/css/main.css")
        self.client.get("/static/js/app.js", name="/static/js/app.js")

    @task(1)
    @tag("website", "forms")
    def submit_contact_form(self):
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "This is a test message from Locust load testing."
        }
        with self.client.post("/contact", data=payload, name="/contact [POST]", catch_response=True) as response:
            if response.status_code in [200, 201, 302]:
                response.success()
            else:
                response.failure(f"Form submission returned {response.status_code}")
