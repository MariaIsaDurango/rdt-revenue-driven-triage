const API_URL = "http://127.0.0.1:8000";

const PRODUCTS = [
  { id: 1, name: "Auriculares Pro X", category: "Audio", price: 129, emoji: "🎧" },
  { id: 2, name: "Smartwatch Fit 5", category: "Wearables", price: 320, emoji: "⌚" },
  { id: 3, name: "UltraBook 14\"", category: "Portátiles", price: 850, emoji: "💻" },
  { id: 4, name: "Mochila Urban", category: "Accesorios", price: 75, emoji: "🎒" },
  { id: 5, name: "Cámara Compact Z", category: "Foto", price: 410, emoji: "📷" },
  { id: 6, name: "Teclado Mecánico", category: "Periféricos", price: 95, emoji: "⌨️" },
];

const failedAttempts = {};

const grid = document.getElementById("product-grid");
const modal = document.getElementById("payment-modal");
const modalProcessing = document.getElementById("modal-processing");
const modalFailed = document.getElementById("modal-failed");
const modalProductName = document.getElementById("modal-product-name");
const complaintText = document.getElementById("complaint-text");
const complaintStatus = document.getElementById("complaint-status");

let currentProduct = null;
let debounceTimer = null;

function renderProducts() {
  grid.innerHTML = PRODUCTS.map(p => `
    <div class="product-card">
      <div class="product-image">${p.emoji}</div>
      <div class="product-body">
        <p class="product-category">${p.category}</p>
        <p class="product-name">${p.name}</p>
        <div class="product-price-row">
          <span class="product-price">${p.price}€</span>
        </div>
        <button class="buy-btn" data-id="${p.id}">Comprar ahora</button>
      </div>
    </div>
  `).join("");

  grid.querySelectorAll(".buy-btn").forEach(btn => {
    btn.addEventListener("click", () => startCheckout(Number(btn.dataset.id)));
  });
}

function startCheckout(productId) {
  currentProduct = PRODUCTS.find(p => p.id === productId);
  failedAttempts[productId] = (failedAttempts[productId] || 0) + 1;

  modal.hidden = false;
  modalProcessing.hidden = false;
  modalFailed.hidden = true;
  complaintText.value = "";
  complaintStatus.textContent = "";

  setTimeout(() => {
    modalProcessing.hidden = true;
    modalFailed.hidden = false;
    modalProductName.textContent = `${currentProduct.name} · ${currentProduct.price}€`;
    complaintText.focus();
  }, 1400);
}

complaintText.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  const text = complaintText.value.trim();
  if (text.length < 10) {
    complaintStatus.textContent = "";
    return;
  }
  complaintStatus.textContent = "Escribiendo...";
  debounceTimer = setTimeout(() => submitReport(text), 1200);
});

async function submitReport(feedbackText) {
  complaintStatus.textContent = "Enviando reporte...";

  const payload = {
    feedback_text: feedbackText,
    provider: "external",
    transaction: { amount: currentProduct.price, currency: "EUR" },
    behavior: {
      failed_attempts: failedAttempts[currentProduct.id],
      recent_errors: failedAttempts[currentProduct.id],
      checkout_blocked: true,
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
      product_name: currentProduct.name,
    }));
    window.location.href = "confirmation.html";
  } catch (err) {
    complaintStatus.textContent = `Error: ${err.message}`;
  }
}

renderProducts();
