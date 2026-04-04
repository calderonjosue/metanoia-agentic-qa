# Metanoia-QA: Autonomous Agentic STLC Framework

> **Metanoia** (Greek μετάνοια): profound transformation, a shift in mind or heart. This system transforms how organizations approach software quality.

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-green.svg)](https://langchain.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-API%20Framework-red.svg)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini-Vision%20AI-orange.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

---

## 🎯 Vision

Modern QA automation handles execution but still requires extensive human intervention for planning and maintenance. Metanoia-QA introduces **QA Agentics**: a corporate quality department modeled in code.

Equipped with System Prompts based on **ISTQB** and **DevSecOps** methodologies, agents reason about:

- Software history
- New business requirements
- Dynamic, adaptive quality strategies

[📺 Watch Demo Video](https://demo.metanoia-qa.dev)

---

## ✨ Features

| Icon | Feature | Description |
|------|---------|-------------|
| 🤖 | **Multi-Agent Orchestration** | Hierarchical agent graph mapped to STLC phases |
| 🧠 | **Historical Memory** | Vector search over past sprints to predict risks |
| 👁️ | **Vision-Based Self-Healing** | Automatic UI repair when selectors break |
| ⚡ | **Performance Testing** | k6 load generation with ML-optimized scenarios |
| 🔒 | **Security Scanning** | OWASP ZAP integration for DAST analysis |
| 📊 | **Real-Time Dashboard** | Next.js + Tremor for monitoring |
| 🔄 | **Autonomous** | Self-healing PRs for broken tests |

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/metanoia-qa/metanoia-qa.git
cd metanoia-qa

# Install dependencies
pip install -r requirements.txt

# Run the orchestrator
uvicorn src.api.main:app --reload
```

**Start a quality mission:**

```bash
POST /v1/metanoia/sprint/start
{
  "sprint_id": "SP-45",
  "sprint_goal": "Implement multi-tenant checkout with payment gateway",
  "risk_tolerance": "Low"
}
```

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      LEVEL 1: STRATEGIC INTELLIGENCE                    │
├─────────────────────────────────────────────────────────────────────────┤
│  📊 Context & Regression Analyzer  │  🎯 Test Strategy Manager        │
│  Pre-Requirement Analysis          │  Dynamic Effort Distribution       │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    LEVEL 2: DESIGN & TECHNICAL EXECUTION                │
├─────────────────────────────────────────────────────────────────────────┤
│  📝 Test Design Lead    │  🎭 UI Automation    │  ⚡ Performance     │
│  & Environment Setup    │  (Playwright)         │  Test Engineer     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       LEVEL 3: AUDIT & CLOSE                             │
├─────────────────────────────────────────────────────────────────────────┤
│  🔮 QA Release Analyst                                                  │
│  Test Closure & Risk Certification                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agent Roles

| Agent | Corporate Name | STLC Phase | Function |
|-------|---------------|------------|----------|
| **Context & Regression Analyzer** | `ContextAnalyst` | Pre-Requirement | Mines historical data for risk prediction |
| **Test Strategy Manager** | `StrategyManager` | Test Planning | Dynamic effort distribution using Defect Clustering |
| **Test Design Lead** | `DesignLead` | Test Design | Generates scenarios + synthetic test data |
| **UI Automation Engineer** | `PlaywrightAgent` | Test Execution | Playwright with vision-based self-healing |
| **Performance Test Engineer** | `K6Agent` | Test Execution | k6/JMeter load scripts |
| **Security Test Engineer** | `ZAPAgent` | Dynamic Analysis | OWASP ZAP scanning + logical fuzzing |
| **QA Release Analyst** | `ReleaseAnalyst` | Test Closure | Release certification with risk assessment |

---

## 💻 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Core | Python 3.12+ | Runtime |
| Orchestration | LangGraph / LangChain | Stateful agent graphs |
| LLM | Google Gemini 1.5 Pro & Flash | Vision + Reasoning + Code Gen |
| API | FastAPI | Agent coordination |
| Knowledge Base | Supabase (pgvector) | Vector memory (self-hosted) |
| UI Testing | Playwright | Visual automation with self-healing |
| Performance | k6 / JMeter | Load & stress testing |
| Security | OWASP ZAP | DAST scanning |
| Dashboard | Next.js + Tremor | Real-time monitoring |

---

## 📂 Project Structure

```
metanoia-qa/
├── src/
│   ├── agents/                 # Domain Lead agents (LangGraph nodes)
│   │   ├── context_analyst/
│   │   ├── strategy_manager/
│   │   ├── design_lead/
│   │   ├── ui_automation/
│   │   ├── performance/
│   │   ├── security/
│   │   └── release_analyst/
│   ├── orchestrator/           # LangGraph StateGraph
│   │   ├── state.py
│   │   ├── graph.py
│   │   └── checkpointing.py
│   ├── knowledge/              # Supabase + pgvector
│   │   ├── client.py
│   │   └── rag.py
│   ├── executors/              # Tool-specific sub-agents
│   │   ├── playwright/
│   │   ├── k6/
│   │   └── zap/
│   └── api/                    # FastAPI routes
├── skills/                     # Reusable skill modules
│   ├── playwright-executor/
│   ├── k6-executor/
│   └── visual-healing/
├── examples/                   # Demo projects
├── docs/                       # Documentation
└── tests/                      # Unit + integration tests
```

---

## 🔧 Configuration

```bash
# Copy environment template
cp .env.example .env

# Required environment variables
GEMINI_API_KEY=your_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

---

## 📚 Documentation

- [Creating Skills](docs/CREATING_SKILLS.md) - How to build and share skills
- [METANOIA-QA Architecture](docs/METANOIA-QA.md) - Deep dive into the system
- [API Reference](docs/API.md) - Endpoint documentation
- [Examples](examples/) - Demo projects

---

## 🌐 API Endpoints

```bash
# Start a quality mission
POST /v1/metanoia/sprint/start

# Check sprint status
GET /v1/metanoia/sprint/{sprint_id}/status

# Get generated test plan
GET /v1/metanoia/sprint/{sprint_id}/test-plan

# Get release certification
GET /v1/metanoia/sprint/{sprint_id}/certification

# Agent control
GET /v1/metanoia/agents/status
POST /v1/metanoia/agents/{agent_id}/pause
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# With coverage
pytest --cov=src tests/

# Integration tests
pytest tests/integration/ -m integration
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and coding standards.

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

*Metanoia-QA: Autonomous Agentic STLC Framework*  
*Version 1.0.0 | Updated 2026-04-04*
