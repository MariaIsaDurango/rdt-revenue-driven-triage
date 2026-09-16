"""
Decision Engine: converts a Risk Score into an operational decision
(priority, human review requirement, recommended action).

Separation of concerns: Risk Engine answers "how much risk exists?",
Decision Engine answers "what should we do about it?".
"""

from app.models.schemas import DecisionResult

# --- Thresholds (documented, adjustable — not silently hardcoded) ---
THRESHOLD_P1 = 0.7
THRESHOLD_P2 = 0.4


def decide(risk_score: float) -> DecisionResult:
    """
    Maps a risk score (0-1) to priority, human review requirement,
    and a recommended action. All decisions require human review in
    this MVP per the Human-in-the-loop principle (RDT section 17) —
    the system never acts autonomously on high-risk cases.
    """
    if risk_score >= THRESHOLD_P1:
        return DecisionResult(
            priority="P1",
            requires_human_review=True,
            recommended_action="Priority human intervention — immediate review required",
        )
    elif risk_score >= THRESHOLD_P2:
        return DecisionResult(
            priority="P2",
            requires_human_review=True,
            recommended_action="Escalate to priority queue for human review",
        )
    else:
        return DecisionResult(
            priority="P3",
            requires_human_review=True,
            recommended_action="Standard queue handling",
        )
