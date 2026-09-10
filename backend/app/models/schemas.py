"""
Pydantic schemas for the RDT triage endpoint.
Input schema validates what the client sends.
Output schema validates what the LLM must return.
"""

from pydantic import BaseModel, Field
from typing import Literal


class TriageRequest(BaseModel):
    """Input payload for the /triage endpoint."""
    feedback_text: str = Field(..., min_length=5, description="Raw citizen incident report text")
    provider: Literal["ollama", "external"] = Field(
        default="ollama",
        description="Which LLM provider to use for this request"
    )


class TriageResponse(BaseModel):
    """Structured output the LLM must produce, validated before returning to client."""
    category: str = Field(..., description="Incident category, e.g. 'Infrastructure', 'Payment Failure'")
    urgency: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Urgency level")
    summary: str = Field(..., description="10-word summary of the incident")
    department: str = Field(..., description="Department that should handle this incident")
    reasoning: str = Field(..., description="ReAct-style reasoning trace before the final classification")


class TriageMetrics(BaseModel):
    """Metrics recorded per request, required by the assignment."""
    latency_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    provider: str
    model: str


class TriageFullResponse(BaseModel):
    """Final API response combining triage result and metrics."""
    triage: TriageResponse
    metrics: TriageMetrics
