const API_URL = "http://127.0.0.1:8000";

const ORDERS = [
  { id: 101, product: "Auriculares Pro X", emoji: "🎧", date: "12 sep 2026", price: 129 },
  { id: 102, product: "UltraBook 14\"", emoji: "💻", date: "8 sep 2026", price: 850 },
  { id: 103, product: "Cámara Compact Z", emoji: "📷", date: "3 sep 2026", price: 410 },
];

const reportCount = {};

const list = document.getElementById("orders-list");
const modal = document.getElementById("report-modal");
const modalChecking = document.getElementById("modal-checking");
const modalMismatch = document.getElementById("modal-mismatch");
const modalOrderName = document.getElementById("modal-order-name");
const modalDeliveryDate = document.getElementById("modal-delivery-date");
const reportText = document.getElementById("report-text");
const reportStatus = document.getElementById("report-status");

let currentOrder = null;
let debounceTimer = null;

function renderOrders() {
  list.innerHTML = ORDERS.map(o => `
    <div class="order-card">
      <div class="order-info">
        <span class="order-emoji">${o.emoji}</span>
        <div>
          <div class="order-name">${o.product}</div>
          <div class="order-date">Pedido el ${o.date}</div>
          <div class="order-status">✓ Entregado</div>
        </div>
      </div>
      <div class="order-actions">
        <span class="order-price">${o.price}€</span>
        <button class="report-btn" data-id="${o.id}">No recibí este pedido</button>
      </div>
    </div>
  `).join("");

  list.querySelectorAll(".report-btn").forEach(btn => {
    btn.addEventListener("click", () => openReport(Number(btn.dataset.id)));
  });
}

function openReport(orderId) {
  currentOrder = ORDERS.find(o => o.id === orderId);
  reportCount[orderId] = (reportCount[orderId] || 0) + 1;

  modal.hidden = false;
  modalChecking.hidden = false;
  modalMismatch.hidden = true;
  reportText.value = "";
  reportStatus.textContent = "";

  setTimeout(() => {
    modalChecking.hidden = true;
    modalMismatch.hidden = false;
    modalOrderName.textContent = `${currentOrder.product} · ${currentOrder.price}€`;
    modalDeliveryDate.textContent = currentOrder.date;
    reportText.focus();
  }, 1400);
}

reportText.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  const text = reportText.value.trim();
  if (text.length < 10) {
    reportStatus.textContent = "";
    return;
  }
  reportStatus.textContent = "Escribiendo...";
  debounceTimer = setTimeout(() => submitReport(text), 1200);
});

async function submitReport(feedbackText) {
  reportStatus.textContent = "Enviando reporte...";

  const payload = {
    feedback_text: feedbackText,
    provider: "external",
    transaction: { amount: currentOrder.price, currency: "EUR" },
    behavior: {
      failed_attempts: 0,
      recent_errors: reportCount[currentOrder.id],
      checkout_blocked: false,
    },
  };

  try {
    const response = await fetch(`${API_URL}/triage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok) throw new Error(data.detail || "Error del servidor");

    sessionStorage.setItem("rdt_last_result", JSON.stringify({
      ...data,
      product_name: currentOrder.product,
    }));
    window.location.href = "confirmation.html";
  } catch (err) {
    reportStatus.textContent = `Error: ${err.message}`;
  }
}

renderOrders();
