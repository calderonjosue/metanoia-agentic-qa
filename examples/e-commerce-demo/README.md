# E-Commerce Demo

Run a complete quality mission on a sample e-commerce application in 5 minutes.

## 🏃 Quick Start

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be ready
sleep 10

# 3. Verify the application is running
curl http://localhost:3000/health

# 4. Start Metanoia-QA
uvicorn src.api.main:app --reload --port 8000
```

## 📋 What This Includes

- **Sample E-Commerce App**: Next.js storefront
- **Backend API**: FastAPI product/order service
- **Database**: PostgreSQL with test data
- **Metanoia-QA**: Configured for this demo

## 🚀 Running a Quality Mission

### Via API

```bash
curl -X POST http://localhost:8000/v1/metanoia/sprint/start \
  -H "Content-Type: application/json" \
  -d '{
    "sprint_id": "DEMO-01",
    "sprint_goal": "Test checkout flow with payment integration",
    "risk_tolerance": "Medium",
    "historical_lookback_sprints": 2
  }'
```

### Via Dashboard

Open http://localhost:3000/dashboard and create a new sprint.

## 📁 Project Structure

```
e-commerce-demo/
├── docker-compose.yml      # All services
├── metanoia.yaml           # Metanoia-QA configuration
├── app/                    # Sample Next.js app
├── api/                    # Sample FastAPI backend
├── tests/                  # Test scenarios
└── data/                   # Test data
```

## ⚙️ Configuration

The `metanoia.yaml` configures:

```yaml
sprint:
  default_risk_tolerance: Medium
  historical_lookback: 3

agents:
  context_analyzer:
    enabled: true
    vector_store: supabase
  
  playwright:
    browsers: [chromium, firefox]
    visual_healing: true
  
  k6:
    default_vus: 50
    default_duration: 30s

knowledge:
  provider: supabase
  connection: postgresql://postgres:demo@localhost:5432/metanoia
```

## 🧪 Test Scenarios

| Scenario | Description | Tool |
|----------|-------------|------|
| `checkout-flow` | Complete purchase journey | Playwright |
| `product-search` | Search and filter products | Playwright |
| `api-load` | Product API load test | k6 |
| `security-scan` | OWASP Top 10 scan | ZAP |

## 🔧 Services

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Next.js storefront |
| API | http://localhost:8000 | FastAPI backend |
| Dashboard | http://localhost:3000/dashboard | Metanoia-QA UI |
| PostgreSQL | localhost:5432 | Database |
| Supabase | localhost:5432 | Vector storage |

## 🛑 Stopping

```bash
# Stop all services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

## ⚠️ Demo Credentials

| Service | Username | Password |
|---------|----------|----------|
| PostgreSQL | postgres | demo |
| Supabase | postgres | demo |
| Dashboard | admin | admin |

## 💡 Tips

- Services may take 30-60 seconds to fully initialize
- If tests fail, check that all services are healthy first
- Use `docker-compose logs -f` to debug issues
- For fresh data, run: `docker-compose restart -v`

---

*This demo is for educational purposes. See docs/ for production deployment.*
