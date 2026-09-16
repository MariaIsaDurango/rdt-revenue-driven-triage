# RDT · Revenue-Driven Triage

Motor de triaje de incidencias asistido por LLM, con razonamiento ReAct, validación estricta con Pydantic, comparación multi-proveedor (local vs. externo), y revisión humana antes de cualquier decisión final.

## 1. Overview

RDT recibe reportes de incidencias en texto libre, los clasifica automáticamente por categoría, urgencia y departamento usando un LLM que razona paso a paso (framework ReAct) antes de responder, y presenta el resultado en un dashboard donde un operador humano aprueba o rechaza la clasificación.

## 2. Problema de negocio

Los sistemas de triage tradicionales priorizan solo por severidad técnica u orden de llegada, sin contexto adicional. RDT busca incorporar razonamiento explicado y trazable, permitiendo que un humano supervise cada decisión antes de que se registre.

## 3. Arquitectura

Frontend (HTML/CSS/JS)
-> fetch()
FastAPI (/triage)
-> Pydantic (valida input)
-> Provider Abstraction
- OllamaProvider (local)
- ExternalProvider (Groq)
-> Prompt ReAct (Thought -> Action -> Observation -> Final Answer)
-> Extraccion y validacion del JSON (Pydantic)
-> Respuesta + metricas (latencia, tokens, coste)
-> Dashboard -> Revision humana (Aprobar / Rechazar)


## 4. LLM Providers

- **Ollama (local)**: modelo `llama3.2:3b`, corre en `localhost:11434`. Gratuito, sin límite de uso, pero depende del hardware local (en máquinas con RAM limitada, la latencia puede superar los 2 minutos por petición).
- **Groq (externo)**: modelo `openai/gpt-oss-20b`. Nota: Groq deprecó `llama-3.1-8b-instant` del tier gratuito el 16 de agosto de 2026; se migró al modelo recomendado por Groq como reemplazo. Latencia típica: 1-2 segundos.

## 5. Prompt Engineering

El prompt implementa el framework **ReAct** (Thought -> Action -> Observation, repetido al menos dos veces) seguido de un bloque `Final Answer` en JSON. Incluye ejemplos few-shot y reglas explícitas para evitar sesgos (el modelo no debe considerar género, etnia, nivel socioeconómico o barrio al determinar urgencia). Ver `backend/app/prompts/triage_prompt.py`.

## 6. Instalación

### Requisitos previos
- Python 3.10+
- Ollama instalado, con el modelo `llama3.2:3b` descargado (`ollama pull llama3.2:3b`)
- Cuenta gratuita en Groq con API key

### Backend

cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt


Crea el archivo `.env` dentro de `backend/`:

GROQ_API_KEY=tu_api_key_aqui


### Frontend
No requiere instalación, es HTML/CSS/JS vanilla, sin dependencias.

## 7. Ejecución

### Backend

cd backend
source venv/Scripts/activate
uvicorn app.main:app --reload

La API queda disponible en `http://127.0.0.1:8000`. Documentación interactiva (Swagger) en `http://127.0.0.1:8000/docs`.

### Frontend
Abre `frontend/index.html` directamente en el navegador, o sírvelo con una extensión tipo Live Server. El dashboard se conecta automáticamente al backend en `127.0.0.1:8000`.

**Importante:** el backend debe estar corriendo antes de usar el dashboard.

## 8. API - Ejemplo de uso

Request a `POST /triage`:

{
"feedback_text": "Llevo 3 dias sin agua caliente y nadie me responde",
"provider": "ollama"
}


Response:

{
"triage": {
"category": "Infrastructure",
"urgency": "MEDIUM",
"summary": "Falta agua caliente 3 dias sin respuesta, solicitar servicio urgente",
"department": "Utilities",
"reasoning": "..."
},
"metrics": {
"latency_ms": 1741.22,
"input_tokens": 710,
"output_tokens": 785,
"estimated_cost": 0.000098,
"provider": "external",
"model": "openai/gpt-oss-20b"
}
}


## 9. Testing

cd backend
pytest -v


Los tests usan mocking (`unittest.mock`) para simular respuestas del LLM, no dependen de Ollama ni Groq estar disponibles. Cobertura actual:
- Health check del servicio.
- Input válido -> respuesta 200 con estructura correcta.
- Salida del LLM mal formada (alucinación) -> error 422 controlado, sin caída del servicio.
- Request body inválido -> rechazado por Pydantic antes de llegar al LLM.

## 10. Human-in-the-loop

Toda clasificación generada por el LLM debe ser revisada por un operador humano antes de considerarse definitiva, mediante los botones "Aprobar" / "Rechazar" del dashboard. En el MVP actual, esta acción solo actualiza el estado visual, la persistencia de estas decisiones queda para una fase posterior.

## 11. Limitaciones conocidas

- El razonamiento ReAct del LLM no está garantizado al 100%; la validación real de estructura la impone Pydantic, no el prompt.
- La latencia de Ollama depende fuertemente del hardware disponible (en esta máquina, 8 GB RAM, puede superar los 2 minutos por petición).
- Groq cambia su catálogo de modelos gratuitos con relativa frecuencia; el modelo configurado puede requerir actualización en el futuro.
- Las decisiones de aprobar/rechazar no se persisten aún (sin base de datos en el MVP).
- No incluye aún el Risk Engine (Financial Risk / Churn Risk) ni Domain Adapters multi-industria del diseño completo de RDT, quedan planificados como evolución del proyecto.

## 12. Roadmap futuro

- Risk Engine con Financial Risk y Churn Risk heurístico.
- Domain Adapters para múltiples industrias (ecommerce, gaming, B2B, fintech).
- Persistencia de decisiones humanas (base de datos).
- Webhooks simulados de recuperación automatizada.