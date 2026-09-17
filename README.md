<div align="center">

# 🎯 RDT · Revenue-Driven Triage

### Motor de triaje de incidencias asistido por LLM con razonamiento ReAct

Clasificación automática · Cálculo de riesgo determinista · Human-in-the-loop · Multi-proveedor

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local-000000?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-external-F55036?style=flat-square)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)

</div>

---

## 📌 Overview

**RDT** recibe reportes de incidencias en texto libre, los clasifica automáticamente por **categoría, urgencia y departamento** usando un LLM que razona paso a paso (framework **ReAct**), calcula de forma **determinista** el riesgo económico y de abandono asociado, decide una **prioridad operacional**, y presenta todo en un dashboard donde un **operador humano** aprueba o rechaza la clasificación antes de que sea definitiva.

> 💡 **Problema de negocio:** los sistemas de triage tradicionales priorizan solo por severidad técnica u orden de llegada. RDT añade contexto económico (Financial Risk) y conductual (Churn Risk) al triage, permitiendo priorizar incidencias que realmente ponen en riesgo ingresos o retención de clientes — sin dejar que el LLM decida datos financieros ni ejecute acciones por sí solo.

---

## 🏗️ Arquitectura

```
Frontend (HTML/CSS/JS)
   shop.html / orders.html  →  escenarios de demo
        │
        ▼  fetch()
FastAPI (/triage)
        │
        ▼  Pydantic valida input
Provider Abstraction
   ├── OllamaProvider   (local)
   └── ExternalProvider (Groq)
        │
        ▼  Prompt ReAct: Thought → Action → Observation → Final Answer
Extracción y validación del JSON (Pydantic)
        │
        ▼
Risk Engine       →  Financial Risk · Churn Risk (heurístico)
Decision Engine   →  Prioridad · Acción recomendada
        │
        ▼
Respuesta + métricas (latencia, tokens, coste)
        │
        ▼
confirmation.html → Revisión humana (✓ Aprobar / ✗ Rechazar)
```


---

## 🤖 LLM Providers

| Proveedor | Modelo | Tipo | Latencia típica | Coste |
|---|---|---|---|---|
| **Ollama** | `llama3.2:3b` | Local (`localhost:11434`) | Depende del hardware (puede superar 2 min en equipos con RAM limitada) | Gratuito |
| **Groq** | `openai/gpt-oss-20b` | Externo (cloud) | 1-2 segundos | ~$0.0001/petición |

> ⚠️ **Nota de mantenimiento:** Groq deprecó `llama-3.1-8b-instant` del tier gratuito el 16 de agosto de 2026. Se migró a `openai/gpt-oss-20b`, el reemplazo recomendado oficialmente por Groq.

---

## 🧠 Prompt Engineering

El prompt implementa el framework **ReAct**:

Thought → Action → Observation (repetido al menos 2 veces)
↓
Final Answer (JSON)


**Incluye:**
- ✅ Ejemplos *few-shot* (casos de urgencia crítica y baja)
- ✅ Reglas explícitas anti-sesgo (ignora género, etnia, nivel socioeconómico o barrio al determinar urgencia)
- ✅ Instrucción de no inventar datos no presentes en el reporte

📄 Ver: `backend/app/prompts/triage_prompt.py`

---

## ⚖️ Risk Engine

Cálculo **100% determinista** — sin intervención del LLM en ningún número financiero.

| Factor | Cómo se calcula |
|---|---|
| **Financial Risk** | Monto de la transacción normalizado sobre un techo de 1000€ |
| **Churn Risk** | Heurística basada en `failed_attempts`, `recent_errors`, `checkout_blocked` — *declarado explícitamente como heurístico, no como Machine Learning* |
| **Incident Impact** | Urgencia del LLM traducida a escala numérica (LOW=0.25 · MEDIUM=0.5 · HIGH=0.75 · CRITICAL=1.0) |

**Risk Score** = promedio ponderado de los tres factores (pesos iguales, 1/3 cada uno). Se eligió sobre la multiplicación de la propuesta inicial por ser más interpretable y facilitar thresholds intuitivos.

📄 Ver: `backend/app/services/risk_engine.py`

---

## 🎯 Decision Engine

| Risk Score | Prioridad | Acción |
|:---:|:---:|---|
| `≥ 0.7` | 🔴 **P1** | Intervención humana prioritaria inmediata |
| `0.4 – 0.69` | 🟡 **P2** | Escalado a cola prioritaria |
| `< 0.4` | 🟢 **P3** | Atención estándar |

> Todas las prioridades requieren revisión humana en este MVP — el sistema nunca actúa de forma completamente autónoma.

📄 Ver: `backend/app/services/decision_engine.py`

---

## 🚀 Instalación

### Requisitos previos
- Python 3.10+
- [Ollama](https://ollama.com) instalado con el modelo local descargado
- Cuenta gratuita en [Groq](https://console.groq.com)

```bash
ollama pull llama3.2:3b
```

### Backend

```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Crea `backend/.env`:
```env
GROQ_API_KEY=tu_api_key_aqui
```

### Frontend
No requiere instalación — HTML/CSS/JS vanilla, sin dependencias.

---

## ▶️ Ejecución

**Backend:**
```bash
cd backend
source venv/Scripts/activate
uvicorn app.main:app --reload
```
API disponible en `http://127.0.0.1:8000` · Swagger en `http://127.0.0.1:8000/docs`

**Frontend** (con Live Server o similar — el backend debe estar corriendo):

| Página | Descripción |
|---|---|
| `shop.html` | 🛒 Tienda simulada — fallo de pago dispara el triage |
| `orders.html` | 📦 Historial de pedidos — reporte de "no recibido" dispara el triage |
| `confirmation.html` | 👤 Panel del operador — triage + risk + decisión + HITL |
| `index.html` | 🔧 Formulario directo para pruebas manuales del endpoint |

---

## 📡 API — Ejemplo de uso

**Request** `POST /triage`
```json
{
  "feedback_text": "Llevo 3 días sin agua caliente y nadie me responde",
  "provider": "ollama",
  "transaction": { "amount": 850, "currency": "EUR" },
  "behavior": { "failed_attempts": 3, "recent_errors": 4, "checkout_blocked": true }
}
```

**Response**
```json
{
  "triage": {
    "category": "Infrastructure",
    "urgency": "HIGH",
    "summary": "...",
    "department": "Utilities",
    "reasoning": "..."
  },
  "risk": {
    "financial_risk": 0.85,
    "churn_risk": 1.0,
    "incident_impact": 0.75,
    "risk_score": 0.87,
    "risk_note": "churn_risk is a heuristic score based on observed signals, not a trained ML model."
  },
  "decision": {
    "priority": "P1",
    "requires_human_review": true,
    "recommended_action": "Priority human intervention — immediate review required"
  },
  "metrics": {
    "latency_ms": 1854.27,
    "input_tokens": 718,
    "output_tokens": 943,
    "estimated_cost": 0.000111,
    "provider": "external",
    "model": "openai/gpt-oss-20b"
  }
}
```

> `transaction` y `behavior` son opcionales — si se omiten, el Risk Engine calcula con valores neutros.

---

## 🧪 Testing

```bash
cd backend
pytest -v
```

Los tests usan **mocking** (`unittest.mock`) para simular respuestas del LLM — no dependen de Ollama ni Groq disponibles.

| Test | Qué verifica |
|---|---|
| `test_health_check` | El servicio responde |
| `test_triage_valid_input` | Input válido → 200 con estructura correcta |
| `test_triage_malformed_llm_output` | Alucinación del LLM → 422 controlado, sin caída del servicio |
| `test_triage_invalid_request_body` | Request inválido → rechazado por Pydantic antes de llegar al LLM |

⏳ *Pendiente:* tests unitarios dedicados para Risk Engine y Decision Engine.

---

## 👤 Human-in-the-loop

Toda clasificación debe ser revisada por un operador humano (botones ✓ **Aprobar** / ✗ **Rechazar** en `confirmation.html`) antes de considerarse definitiva. En este MVP, la acción solo actualiza el estado visual — la persistencia queda para una fase posterior.

---

## ⚠️ Limitaciones conocidas

- El razonamiento ReAct no está garantizado al 100%; la validación real de estructura la impone **Pydantic**, no el prompt.
- La latencia de Ollama depende del hardware disponible (en esta máquina, 8 GB RAM, puede superar 2 minutos).
- Groq cambia su catálogo de modelos gratuitos con relativa frecuencia.
- Las decisiones de aprobar/rechazar no se persisten aún (sin base de datos).
- Los thresholds del Risk Engine (techo de 1000€, pesos de churn, umbrales de prioridad) son valores iniciales razonables, **no calibrados con datos históricos reales**.
- No incluye aún Domain Adapters para otras industrias ni webhooks de recuperación simulados.

---

## 🗺️ Roadmap futuro

- [ ] Domain Adapters multi-industria (gaming, B2B, fintech)
- [ ] Persistencia de decisiones humanas (base de datos)
- [ ] Webhooks simulados de recuperación automatizada
- [ ] Tests unitarios para Risk Engine y Decision Engine
- [ ] Calibración de thresholds con datos reales

---

<div align="center">

**Proyecto académico — AI Engineering** · Construido con FastAPI, Pydantic, Ollama y Groq

</div>