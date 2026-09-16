"""
Pydantic schemas for the RDT triage endpoint.
Input schema validates what the client sends.
Output schema validates what the LLM must return.
Risk schemas validate the deterministic Risk Engine output (never LLM-generated).
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional


class TransactionContext(BaseModel):
    """Financial context. Comes from the system, never invented by the LLM."""
    amount: float = Field(default=0.0, ge=0, description="Transaction/cart value at risk")
    currency: str = Field(default="EUR")


class BehaviorContext(BaseModel):
    """Behavioral signals used for heuristic churn risk. NOT machine-learned."""
    failed_attempts: int = Field(default=0, ge=0)
    recent_errors: int = Field(default=0, ge=0)
    checkout_blocked: bool = Field(default=False)


class TriageRequest(BaseModel):
    """Input payload for the /triage endpoint."""
    feedback_text: str = Field(..., min_length=5, description="Raw citizen incident report text")
    provider: Literal["ollama", "external"] = Field(default="ollama")
    transaction: Optional[TransactionContext] = Field(default_factory=TransactionContext)
    behavior: Optional[BehaviorContext] = Field(default_factory=BehaviorContext)


class TriageResponse(BaseModel):
    """Structured output the LLM must produce, validated before returning to client."""
    category: str
    urgency: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    summary: str
    department: str
    reasoning: str


class RiskAssessment(BaseModel):
    """
    Output of the deterministic Risk Engine. Never produced by the LLM.
    financial_risk and churn_risk are normalized 0-1 scores.
    churn_risk is explicitly heuristic, not a trained ML model.
    """
    financial_risk: float = Field(..., ge=0, le=1)
    churn_risk: float = Field(..., ge=0, le=1)
    incident_impact: float = Field(..., ge=0, le=1)
    risk_score: float = Field(..., ge=0, le=1)
    risk_note: str = Field(
        default="churn_risk is a heuristic score based on observed signals, not a trained ML model."
    )


class DecisionResult(BaseModel):
    """Output of the deterministic Decision Engine."""
    priority: Literal["P1", "P2", "P3"]
    requires_human_review: bool
    recommended_action: str


class TriageMetrics(BaseModel):
    """Metrics recorded per request, required by the assignment."""
    latency_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    provider: str
    model: str


class TriageFullResponse(BaseModel):
    """Final API response combining triage, risk, decision and metrics."""
    triage: TriageResponse
    risk: RiskAssessment
    decision: DecisionResult
    metrics: TriageMetrics
