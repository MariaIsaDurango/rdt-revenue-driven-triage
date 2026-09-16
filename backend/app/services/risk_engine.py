"""
Risk Engine: deterministic calculation of financial risk, churn risk,
and incident impact, combined into a single risk score.

This module contains NO LLM calls. Every number here comes from code,
not from model interpretation, per the separation-of-concerns principle:
LLM = interpretation, code = calculation and decision.
"""

from app.models.schemas import TransactionContext, BehaviorContext, RiskAssessment

# --- Configuration (documented, adjustable, NOT hardcoded silently) ---

FINANCIAL_RISK_CEILING = 1000.0  # amount (in transaction currency) considered "maximum exposure"

CHURN_WEIGHT_FAILED_ATTEMPT = 0.20
CHURN_WEIGHT_RECENT_ERROR = 0.15
CHURN_WEIGHT_CHECKOUT_BLOCKED = 0.30

URGENCY_TO_IMPACT = {
    "LOW": 0.25,
    "MEDIUM": 0.50,
    "HIGH": 0.75,
    "CRITICAL": 1.0,
}

# Weighted average weights for the final risk score (must sum to 1.0)
WEIGHT_FINANCIAL = 1 / 3
WEIGHT_CHURN = 1 / 3
WEIGHT_IMPACT = 1 / 3


def calculate_financial_risk(transaction: TransactionContext) -> float:
    """Normalizes transaction amount to a 0-1 scale using a fixed ceiling."""
    if transaction.amount <= 0:
        return 0.0
    normalized = transaction.amount / FINANCIAL_RISK_CEILING
    return min(normalized, 1.0)


def calculate_churn_risk(behavior: BehaviorContext) -> float:
    """
    Heuristic churn risk based on observed behavioral signals.
    NOT a trained ML model — see RiskAssessment.risk_note.
    """
    score = 0.0
    score += behavior.failed_attempts * CHURN_WEIGHT_FAILED_ATTEMPT
    score += behavior.recent_errors * CHURN_WEIGHT_RECENT_ERROR
    if behavior.checkout_blocked:
        score += CHURN_WEIGHT_CHECKOUT_BLOCKED
    return min(score, 1.0)


def calculate_incident_impact(urgency: str) -> float:
    """Maps the LLM-determined urgency label to a numeric impact score."""
    return URGENCY_TO_IMPACT.get(urgency, 0.5)


def assess_risk(
    transaction: TransactionContext,
    behavior: BehaviorContext,
    urgency: str,
) -> RiskAssessment:
    """
    Combines the three risk factors into a single weighted risk score.
    Weighted average was chosen over multiplication for interpretability:
    see project decision log (README) for the trade-off discussion.
    """
    financial_risk = calculate_financial_risk(transaction)
    churn_risk = calculate_churn_risk(behavior)
    incident_impact = calculate_incident_impact(urgency)

    risk_score = (
        financial_risk * WEIGHT_FINANCIAL
        + churn_risk * WEIGHT_CHURN
        + incident_impact * WEIGHT_IMPACT
    )

    return RiskAssessment(
        financial_risk=round(financial_risk, 4),
        churn_risk=round(churn_risk, 4),
        incident_impact=round(incident_impact, 4),
        risk_score=round(risk_score, 4),
    )
