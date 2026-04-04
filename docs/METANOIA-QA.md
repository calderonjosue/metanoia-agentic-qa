# Metanoia-QA: Autonomous Agentic STLC Framework

> **Metanoia** (del griego μετάνοια): transformación profunda, un cambio de mente o corazón. Este sistema transforma radicalmente la manera en que las organizaciones abordan la calidad del software.

---

## 🎯 Filosofía del Proyecto

Los sistemas de QA actuales automatizan la ejecución, pero requieren intervención humana exhaustiva para la planificación y el mantenimiento. Metanoia-QA introduce el concepto de **QA Agentics**: un departamento de calidad corporativo modelado en código.

Los agentes, dotados de System Prompts basados en metodologías como **ISTQB** y **DevSecOps**, razonan sobre:
- El historial del software
- Los nuevos requerimientos del negocio
- Generan estrategias de calidad dinámicas y adaptativas

---

## 🚀 Vision

Metanoia-QA no es un framework de automatización tradicional; es un **Sistema de Calidad Autónomo**. Utiliza una arquitectura jerárquica de grafos de agentes y Modelos de Lenguaje Grande (LLMs) para orquestar de forma nativa el **Ciclo de Vida del Testing de Software (STLC)** completo.

Su mayor innovación radica en la **Conciencia Histórica**: antes de planificar un nuevo ciclo, el sistema explora activamente el pasado del proyecto para predecir riesgos y optimizar la cobertura.

---

## 🏛️ Arquitectura Multi-Agente (Mapeada al STLC)

El sistema opera sobre un grafo de estados dirigido (LangGraph), donde cada nodo representa una fase del STLC liderada por un Agente Especializado.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      NIVEL 1: INTELIGENCIA ESTRATÉGICA                  │
├─────────────────────────────────────────────────────────────────────────┤
│  📊 Context & Regression Analyzer    │  🎯 Test Strategy Manager        │
│  Pre-Requirement Analysis            │  Test Planning                   │
│  Exploración de memoria histórica    │  Distribución dinámica de esfuerzo│
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    NIVEL 2: DISEÑO Y EJECUCIÓN TÉCNICA                  │
├─────────────────────────────────────────────────────────────────────────┤
│  📝 Test Design Lead    │  🎭 UI Automation    │  ⚡ Performance     │  🔒 │
│  Test Design           │  Engineer           │  Test Engineer     │  Sec│
│  & Environment Setup   │  (Playwright)       │  (k6/JMeter)       │     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       NIVEL 3: AUDITORÍA Y CIERRE                       │
├─────────────────────────────────────────────────────────────────────────┤
│  🔮 QA Release Analyst                                                  │
│  Test Execution Analysis & Test Closure                                │
│  Veredicto de Release con certificación de riesgo                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agentes por Nivel

#### Nivel 1: Inteligencia de Contexto y Estrategia

| Agente | Nombre Corporativo | Fase STLC | Función |
|--------|-------------------|-----------|---------|
| **Context & Regression Analyzer** | `ContextAnalyst` | Pre-Requirement Analysis | Antes de iniciar el Sprint, extrae el "Scope" anterior, revisa los reportes del Sprint N-1, identifica flaky tests históricos, módulos con alta densidad de defectos y deuda técnica acumulada |
| **Test Strategy Manager** | `StrategyManager` | Test Planning | Toma los hallazgos del Context Analyst y el nuevo alcance del Sprint. Aplica el principio ISTQB de **Defect Clustering** para decidir dinámicamente qué porcentaje de esfuerzo irá a pruebas funcionales, de regresión, rendimiento o seguridad |

#### Nivel 2: Diseño y Ejecución (Domain Leads + Tool Specialists)

| Agente | Rol | Fase STLC | Función |
|--------|-----|-----------|---------|
| **Test Design Lead** | `DesignLead` | Test Design & Environment Setup | Genera escenarios de prueba que cubren los "Happy Paths" y utiliza razonamiento LLM para inferir **Edge Cases** no documentados. Prepara la data de prueba sintética |
| **UI Automation Engineer** | `PlaywrightAgent` | Test Execution | Genera y ejecuta scripts de Playwright. Utiliza capacidades **multimodales** para aplicar **auto-curación (self-healing) visual** si los selectores del DOM cambian |
| **Performance Test Engineer** | `K6Agent` / `JMeterAgent` | Test Design & Execution | Infiere cuellos de botella y delega a sub-agentes la escritura de scripts de carga (k6 o JMeter) enfocados en los endpoints alterados en el Sprint actual |
| **Security Test Engineer** | `ZAPAgent` | Dynamic Analysis (DAST) | Realiza análisis dinámico (DAST) y **fuzzing lógico** sobre la API para prevenir vulnerabilidades (OWASP Top 10) |

> **Nota**: Los agentes de Nivel 2 son "Domain Leads" que orquestan **sub-agentes especializados en herramientas** (Playwright, k6, JMeter, OWASP ZAP).

#### Nivel 3: Cierre y Auditoría

| Agente | Nombre Corporativo | Fase STLC | Función |
|--------|-------------------|-----------|---------|
| **QA Release Analyst** | `ReleaseAnalyst` | Test Execution Analysis & Test Closure | Evalúa los resultados de todos los Domain Leads. No emite un simple Pass/Fail; **cruza los errores técnicos con el impacto en el flujo de valor del negocio** y genera el reporte de certificación del Release |

---

## 🧠 Sistema de Memoria (Arquitectura Final)

Tras evaluar opciones (Engram, Mem0, soluciones propias), la arquitectura de memoria seleccionada para Metanoia-QA es:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAPAS DE MEMORÍA                            │
├─────────────────────────────────────────────────────────────────┤
│  1. Memoria de Ejecución      │  LangGraph Checkpointers       │
│     (Short-Term / Thread)     │  PostgreSQL                    │
├─────────────────────────────────────────────────────────────────┤
│  2. Memoria Arqueológica      │  Supabase + pgvector           │
│     (Long-Term / Historical)  │  Self-hosted, empresa          │
├─────────────────────────────────────────────────────────────────┤
│  3. Memoria de Aprendizaje    │  Tablas de Lecciones           │
│     (Procedural)              │  Aprendizaje procedimental     │
└─────────────────────────────────────────────────────────────────┘
```

### 1. Memoria de Ejecución (Short-Term)

- **Herramienta**: `LangGraph Checkpointers` (PostgreSQL)
- **Función**: Mantiene el estado de la ejecución actual (thread). Permite que si un proceso de prueba de carga largo se interrumpe, el Performance Test Engineer pueda retomar exactamente donde quedó, manteniendo la integridad de los datos recogidos.
- **Alcance**: Temporal, ligada al `thread_id` del Sprint actual.

### 2. Memoria Arqueológica (Long-Term)

- **Herramienta**: `Supabase + pgvector` (RAG)
- **Función**: Almacena el historial de calidad de la organización:
  - Reportes de Sprints pasados
  - Logs de errores históricos y su resolución
  - Documentación técnica del software (Swagger, Arquitectura)
- **Mecanismo**: Búsqueda de similitud vectorial para recuperar contextos similares a la tarea actual y predecir puntos de falla.
- **Seguridad**: Self-hosted, soberanía de datos. Sin dependencias de nube de terceros.

### 3. Memoria de Aprendizaje (Procedural)

- **Herramienta**: Tabla `agent_lessons_learned` en Supabase
- **Función**: Optimiza la interacción entre agentes y herramientas. Si el Security Test Engineer descubre que un firewall específico bloquea sus escaneos, guarda esa "lección" para ajustar sus headers en futuras ejecuciones sin intervención humana.

### Flujo del Context & Regression Analyzer

```
1. TRIGGER: Inicio de fase Test Planning
2. QUERY: El Context Analyst ejecuta búsqueda vectorial:
   "Traer los últimos 5 fallos críticos relacionados con pagos"
3. SYNTHESIS: Gemini analiza los resultados y genera una directriz:
   "Históricamente, los cambios en este módulo afectan el tiempo 
    de respuesta del login. Priorizar Performance Test Engineer."
4. DECISION: El Strategy Manager asigna más peso de prueba a los 
   módulos históricamente problemáticos basándose en el principio 
   ISTQB de Defect Clustering.
```

---

## 🔄 Flujo de Trabajo (Workflow Autónomo)

```
┌──────────────────────────────────────────────────────────────────────┐
│  1. SPRINT INGESTION & HISTORICAL MINING                            │
│     El sistema recibe el webhook del nuevo Sprint.                   │
│     El Context Analyst revisa la base de datos vectorial             │
│     buscando el contexto del Sprint anterior y el historial de fallos│
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  2. CONTEXT RETRIEVAL & PLANNING                                    │
│     El Strategy Manager cruza el historial con metodologías          │
│     inyectadas (System Prompts ISTQB) y diseña el Test Plan          │
│     priorizado por riesgo.                                           │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  3. AUTONOMOUS DESIGN                                               │
│     El Design Lead genera escenarios de prueba y datos sintéticos    │
│     estructurados de forma autónoma.                                 │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  4. MULTI-LEVEL EXECUTION                                           │
│     Despliegue en paralelo de pruebas:                               │
│     • UI Automation Engineer (Playwright con vision healing)        │
│     • Performance Test Engineer (k6/JMeter)                         │
│     • Security Test Engineer (OWASP ZAP)                            │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│  5. VEREDICTO Y SELF-HEALING                                        │
│     El Release Analyst emite el análisis final.                      │
│     Si hubo fallos de UI por cambios cosméticos, los sub-agentes     │
│     generan un Pull Request reparando los selectores automáticamente.│
└──────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Tech Stack

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Core Framework | Python 3.12+ | Runtime principal |
| Agent Orchestration | LangGraph / LangChain | Grafo de agentes con estado y checkpointing |
| LLM Engine | Google Gemini 1.5 Pro & Flash | Vision + Reasoning + Code Generation |
| Backend / API | FastAPI | Orquestación y coordinación de agentes |
| Knowledge Base | Supabase (pgvector) | Memoria institucional vectorial (self-hosted) |
| UI Testing | Playwright | Automatización visual con self-healing multimodal |
| Performance | k6 / JMeter | Test de carga y estrés |
| Security | OWASP ZAP | DAST scanning y fuzzing lógico |
| Dashboard UI | Next.js + Tremor | Visualización y monitoreo en tiempo real |

---

## 📂 Estructura del Proyecto

```
metanoia-qa/
├── src/
│   ├── agents/                           # Domain Leads (LangGraph nodes)
│   │   ├── context_analyst/             # Context & Regression Analyzer
│   │   ├── strategy_manager/             # Test Strategy Manager
│   │   ├── design_lead/                 # Test Design Lead
│   │   ├── ui_automation/               # UI Automation Engineer + Playwright sub-agent
│   │   ├── performance/                  # Performance Test Engineer + k6/JMeter sub-agents
│   │   ├── security/                     # Security Test Engineer + ZAP sub-agent
│   │   └── release_analyst/             # QA Release Analyst
│   ├── orchestrator/                     # LangGraph StateGraph
│   │   ├── state.py                      # Pydantic state classes por agente
│   │   ├── graph.py                       # Definición del grafo STLC
│   │   └── checkpointing.py              # PostgreSQL checkpointers
│   ├── knowledge/                        # Supabase + pgvector
│   │   ├── client.py                     # Cliente de base de datos
│   │   ├── schemas.sql                   # Schema de tablas vectoriales
│   │   └── rag.py                        # Retrieval-Augmented Generation
│   ├── executors/                        # Sub-agentes especializados en herramientas
│   │   ├── playwright/                  # Playwright runner + vision healing
│   │   ├── k6/                           # k6 script generation & execution
│   │   ├── jmeter/                       # JMeter integration
│   │   └── zap/                          # OWASP ZAP wrapper
│   ├── api/                              # FastAPI
│   │   ├── routes/
│   │   │   ├── sprint.py                # Sprint lifecycle endpoints
│   │   │   ├── agents.py                # Agent status & control
│   │   │   └── reports.py               # Certification reports
│   │   └── main.py
│   └── dashboard/                        # Next.js + Tremor
│       ├── components/
│       ├── pages/
│       └── lib/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   └── METANOIA-QA.md                   # Este documento
├── openspec/                             # SDD artifacts
│   └── changes/
└── requirements.txt
```

---

## 🗄️ Schema de Base de Datos (Supabase)

```sql
-- Memoria Histórica de Testing
-- Almacena hallazgos de Sprints anteriores para el Context Analyst
CREATE TABLE qa_historical_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sprint_id TEXT NOT NULL,
  module_name TEXT,
  description TEXT,
  defect_density FLOAT,
  critical_bugs_found INT,
  embedding VECTOR(768),              -- Embeddings de Gemini
  metadata JSONB,                     -- Contexto adicional
  created_at TIMESTAMP DEFAULT NOW()
);

-- Lecciones Aprendidas por Agente
-- Memoria procedimental para optimización continua
CREATE TABLE agent_lessons_learned (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_role TEXT,                    -- ej: 'performance_engineer'
  tool_used TEXT,                     -- ej: 'k6', 'playwright', 'zap'
  issue_encountered TEXT,
  resolution_applied TEXT,
  embedding VECTOR(768),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para búsqueda vectorial eficiente
CREATE INDEX idx_historical_memory_embedding ON qa_historical_memory 
  USING HNSW(embedding vector_cosine_ops);
  
CREATE INDEX idx_agent_lessons_embedding ON agent_lessons_learned 
  USING HNSW(embedding vector_cosine_ops);

-- Función de búsqueda semántica para el Context Analyst
CREATE OR REPLACE FUNCTION match_historical_testing(
  query_embedding VECTOR(768),
  match_threshold FLOAT,
  match_count INT
)
RETURNS TABLE(
  id UUID,
  sprint_id TEXT,
  module_name TEXT,
  description TEXT,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    qa_historical_memory.id,
    qa_historical_memory.sprint_id,
    qa_historical_memory.module_name,
    qa_historical_memory.description,
    1 - (qa_historical_memory.embedding <=> query_embedding) AS similarity
  FROM qa_historical_memory
  WHERE 1 - (qa_historical_memory.embedding <=> query_embedding) > match_threshold
  ORDER BY qa_historical_memory.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

---

## 🚀 Instalación y Uso Rápido

```bash
# Clonar el repositorio
git clone https://github.com/tu-organizacion/metanoia-qa.git
cd metanoia-qa

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar navegadores de Playwright
playwright install

# Configurar variables de entorno
cp .env.example .env
# Editar .env y añadir:
# - GEMINI_API_KEY
# - SUPABASE_URL
# - SUPABASE_SERVICE_KEY

# Iniciar el motor de orquestación (FastAPI)
uvicorn src.api.main:app --reload
```

### Ejecutar una "Misión de Calidad"

Envía el alcance de tu Sprint y permite que el Context Analyst haga su trabajo antes de planificar:

```bash
POST /v1/metanoia/sprint/start
{
  "sprint_id": "SP-45",
  "sprint_goal": "Implementar checkout multi-tenant con integración de pasarela de pagos.",
  "risk_tolerance": "Low",
  "historical_lookback_sprints": 3
}
```

---

## 📋 Roadmap

| Fase | Estado | Descripción |
|------|--------|-------------|
| [x] Arquitectura jerárquica base de LangGraph | ✅ Completado | Grafo de 8 agentes mapeado al STLC |
| [x] Integración del Context Analyst | ✅ En diseño | Exploración de memoria histórica vía pgvector |
| [ ] Integración de Gemini Vision | 🔲 Pendiente | Auto-curación visual de UI (Playwright) |
| [ ] Sub-grafos dedicados para k6/JMeter | 🔲 Pendiente | Delegación a herramientas de performance |
| [ ] Integración OWASP ZAP | 🔲 Pendiente | Security scanning y fuzzing lógico |
| [ ] Integración GitHub Actions | 🔲 Pendiente | Aprobación/bloqueo automático de PRs |

---

## 🌐 API Endpoints

### Sprint Lifecycle

```bash
# Iniciar una misión de calidad
POST /v1/metanoia/sprint/start
Content-Type: application/json

{
  "sprint_id": "SP-45",
  "sprint_goal": "Implementar checkout multi-tenant con pasarela de pagos",
  "risk_tolerance": "Low",
  "historical_lookback_sprints": 3
}

# Consultar estado del Sprint
GET /v1/metanoia/sprint/{sprint_id}/status

# Obtener Test Plan generado por Strategy Manager
GET /v1/metanoia/sprint/{sprint_id}/test-plan

# Obtener reporte de certificación del Release Analyst
GET /v1/metanoia/sprint/{sprint_id}/certification
```

### Agent Control

```bash
# Listar estado de todos los agentes
GET /v1/metanoia/agents/status

# Pausar/reanudar agente específico
POST /v1/metanoia/agents/{agent_id}/pause
POST /v1/metanoia/agents/{agent_id}/resume
```

---

## 🎓 Metodologías Inyectadas (System Prompts)

Los agentes de Metanoia-QA operan con System Prompts basados en:

- **ISTQB**: International Software Testing Qualifications Board
  - Principio de Defect Clustering
  - Técnicas de diseño de casos de prueba
  - Gestión de riesgos en testing
  
- **DevSecOps**: Integración de seguridad en el pipeline
  - OWASP Top 10
  - Shift-left security
  - DAST (Dynamic Application Security Testing)

---

## 🛡️ Seguridad y Soberanía de Datos

A diferencia de soluciones basadas en nubes de terceros:

1. **Self-Hosted Memory**: Todo el almacenamiento vectorial reside en infraestructura propia (Supabase/PostgreSQL).
2. **Data Sanitization**: Antes de enviar datos a Gemini, el sistema anonimiza información sensible (PII).
3. **No External Training**: Los datos de QA se utilizan únicamente para contexto en tiempo real, no para entrenar modelos globales.
4. **Prompt Injection Protection**: Validación y sanitización de prompts para prevenir ataques de ingeniería de prompts.

---

## 📚 Inspiración y Referencias

- **[agent-teams-lite](https://github.com/Gentleman-Programming/agent-teams-lite)**: Patrón de orquestación multi-agente con Spec-Driven Development
- **ISTQB**: Metodología de Testing para System Prompts
- **OWASP Top 10**: Guidelines para Security Test Engineer
- **Defect Clustering**: Principio ISTQB para distribución de esfuerzo de testing

---

*Documento versión: 1.0*  
*Actualizado: 2026-04-04*  
*Proyecto: Metanoia-QA: Autonomous Agentic STLC Framework*
