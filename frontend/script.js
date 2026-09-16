const API_URL = "http://127.0.0.1:8000";

const form = document.getElementById("triage-form");
const submitBtn = document.getElementById("submit-btn");
const statusMessage = document.getElementById("status-message");
const resultPanel = document.getElementById("result-panel");
const hitlStatus = document.getElementById("hitl-status");

const urgencyColors = {
  LOW: "#d1fae5",
  MEDIUM: "#fef3c7",
  HIGH: "#fed7aa",
  CRITICAL: "#fecaca",
};

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const feedback_text = document.getElementById("feedback_text").value;
  const provider = document.getElementById("provider").value;

  submitBtn.disabled = true;
  statusMessage.textContent =
    provider === "ollama"
      ? "Analizando con Ollama local... esto puede tardar varios minutos en hardware limitado."
      : "Analizando con Groq...";
  resultPanel.hidden = true;
  hitlStatus.textContent = "";

  try {
    const response = await fetch(`${API_URL}/triage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ feedback_text, provider }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Error desconocido del servidor");
    }

    renderResult(data);
    statusMessage.textContent = "";
  } catch (err) {
    statusMessage.textContent = `Error: ${err.message}`;
  } finally {
    submitBtn.disabled = false;
  }
});

function renderResult(data) {
  const { triage, metrics } = data;

  document.getElementById("r-category").textContent = triage.category;
  document.getElementById("r-department").textContent = triage.department;
  document.getElementById("r-summary").textContent = triage.summary;
  document.getElementById("r-reasoning").textContent = triage.reasoning;

  const urgencyEl = document.getElementById("r-urgency");
  urgencyEl.textContent = triage.urgency;
  urgencyEl.style.background = urgencyColors[triage.urgency] || "#e5e7eb";

  document.getElementById("m-latency").textContent = `${metrics.latency_ms} ms`;
  document.getElementById("m-tokens").textContent = `${metrics.input_tokens} / ${metrics.output_tokens}`;
  document.getElementById("m-cost").textContent = `$${metrics.estimated_cost}`;
  document.getElementById("m-provider").textContent = `${metrics.provider} · ${metrics.model}`;

  resultPanel.hidden = false;
}

// Human-in-the-loop: approve/reject only update local UI state in the MVP.
// No persistence yet — that belongs to a later phase (see roadmap).
document.getElementById("approve-btn").addEventListener("click", () => {
  hitlStatus.textContent = "✓ Incidencia aprobada por el operador.";
  hitlStatus.style.color = "#16a34a";
});

document.getElementById("reject-btn").addEventListener("click", () => {
  hitlStatus.textContent = "✗ Incidencia rechazada por el operador.";
  hitlStatus.style.color = "#dc2626";
});
