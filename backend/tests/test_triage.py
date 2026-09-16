"""
Tests for the /triage endpoint.
LLM calls are mocked — these tests never hit Ollama or Groq,
following the assignment's requirement that tests not depend on a real LLM.
"""

from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# A well-formed response, exactly as we expect a healthy LLM to produce it.
VALID_LLM_OUTPUT = """Thought: The report mentions a service disruption.
Action: Classify the incident.
Observation: This is a utility service issue.
Final Answer: {"category": "Infrastructure", "urgency": "MEDIUM", "summary": "Sin agua caliente por varios dias sin respuesta", "department": "Utilities", "reasoning": "Interrupcion de servicio basico sin atencion."}
"""

# A malformed response simulating the model hallucinating / breaking format.
MALFORMED_LLM_OUTPUT = "Lo siento, no puedo procesar esta solicitud en este momento."


def test_health_check():
    """Sanity check: the API is up and responding."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.providers.ollama_provider.OllamaProvider.generate", new_callable=AsyncMock)
def test_triage_valid_input(mock_generate):
    """
    Simulates a healthy LLM response and checks the endpoint returns
    a correctly structured 200 response with the expected fields.
    """
    mock_generate.return_value = (VALID_LLM_OUTPUT, 100, 50)

    response = client.post("/triage", json={
        "feedback_text": "Llevo 3 dias sin agua caliente y nadie me responde",
        "provider": "ollama"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["triage"]["category"] == "Infrastructure"
    assert data["triage"]["urgency"] == "MEDIUM"
    assert data["metrics"]["input_tokens"] == 100
    assert data["metrics"]["output_tokens"] == 50
    assert data["metrics"]["provider"] == "ollama"


@patch("app.providers.ollama_provider.OllamaProvider.generate", new_callable=AsyncMock)
def test_triage_malformed_llm_output(mock_generate):
    """
    Simulates the LLM hallucinating / not following the expected format.
    The API must catch this and return a controlled 422 error,
    not crash the service.
    """
    mock_generate.return_value = (MALFORMED_LLM_OUTPUT, 20, 15)

    response = client.post("/triage", json={
        "feedback_text": "Cualquier reporte de prueba",
        "provider": "ollama"
    })

    assert response.status_code == 422
    assert "schema validation" in response.json()["detail"]


def test_triage_invalid_request_body():
    """
    Sends a request missing the required 'feedback_text' field.
    Pydantic should reject this before it ever reaches the LLM provider.
    """
    response = client.post("/triage", json={"provider": "ollama"})

    assert response.status_code == 422
