const raw = sessionStorage.getItem("rdt_last_result");

if (!raw) {
  document.getElementById("result-panel").innerHTML =
    "<h2>No hay ningún resultado reciente</h2><p>Vuelve a la tienda y genera una incidencia.</p><a href='shop.html' class='back-link'>← Volver a la tienda</a>";
} else {
  const data = JSON.parse(raw);
  const { triage, risk, decision, metrics, product_name } = data;

  const urgencyColors = { LOW: "#d1fae5", MEDIUM: "#fef3c7", HIGH: "#fed7aa", CRITICAL: "#fecaca" };
  const priorityColors = { P1: "#fecaca", P2: "#fef3c7", P3: "#d1fae5" };

  document.getElementById("r-product").textContent = product_name || "-";
  document.getElementById("r-category").textContent = triage.category;
  document.getElementById("r-department").textContent = triage.department;
  document.getElementById("r-summary").textContent = triage.summary;
  document.getElementById("r-reasoning").textContent = triage.reasoning;

  const urgencyEl = document.getElementById("r-urgency");
  urgencyEl.textContent = triage.urgency;
  urgencyEl.style.background = urgencyColors[triage.urgency] || "#e5e7eb";

  document.getElementById("risk-financial").textContent = risk.financial_risk;
  document.getElementById("risk-churn").textContent = risk.churn_risk;
  const riskScoreEl = document.getElementById("risk-score");
  riskScoreEl.textContent = risk.risk_score;
  riskScoreEl.style.background = "#e0e7ff";
  document.getElementById("risk-note").textContent = risk.risk_note;

  const priorityEl = document.getElementById("dec-priority");
  priorityEl.textContent = decision.priority;
  priorityEl.style.background = priorityColors[decision.priority] || "#e5e7eb";
  document.getElementById("dec-action").textContent = decision.recommended_action;

  document.getElementById("m-latency").textContent = `${metrics.latency_ms} ms`;
  document.getElementById("m-tokens").textContent = `${metrics.input_tokens} / ${metrics.output_tokens}`;
  document.getElementById("m-cost").textContent = `$${metrics.estimated_cost}`;
  document.getElementById("m-provider").textContent = `${metrics.provider} · ${metrics.model}`;

  document.getElementById("approve-btn").addEventListener("click", () => {
    const el = document.getElementById("hitl-status");
    el.textContent = "✓ Incidencia aprobada por el operador.";
    el.style.color = "#16a34a";
  });
  document.getElementById("reject-btn").addEventListener("click", () => {
    const el = document.getElementById("hitl-status");
    el.textContent = "✗ Incidencia rechazada por el operador.";
    el.style.color = "#dc2626";
  });
}
