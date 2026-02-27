function gbp(n) {
  return new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP", maximumFractionDigits: 0 }).format(n);
}

function dayKey(d) {
  const keys = ["sun","mon","tue","wed","thu","fri","sat"];
  return keys[d.getDay()];
}

(function initGallery(){
  const root = document.querySelector("[data-gallery]");
  if (!root) return;

  const img = root.querySelector("[data-gallery-img]");
  const imagesEl = root.querySelector("[data-gallery-images]");
  const prev = root.querySelector("[data-gallery-prev]");
  const next = root.querySelector("[data-gallery-next]");
  if (!img || !imagesEl || !prev || !next) return;

  const images = JSON.parse(imagesEl.textContent || "[]");
  let idx = 0;

  function render() {
    img.src = images[idx];
  }
  prev.addEventListener("click", () => { idx = (idx - 1 + images.length) % images.length; render(); });
  next.addEventListener("click", () => { idx = (idx + 1) % images.length; render(); });
})();

(function initAvailability(){
  const container = document.querySelector("[data-availability]");
  const dataEl = document.querySelector("[data-availability-json]");
  if (!container || !dataEl) return;

  const availability = JSON.parse(dataEl.textContent || "{}");
  const today = new Date();

  container.innerHTML = "";
  for (let i = 0; i < 7; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() + i);
    const label = d.toLocaleDateString("en-GB", { weekday: "short" });
    const key = dayKey(d);
    const ok = (availability[key] || []).length > 0;

    const span = document.createElement("span");
    span.className = ok ? "avail-chip avail-chip--ok" : "avail-chip";
    span.textContent = label;
    container.appendChild(span);
  }
})();

(function initQuote(){
  const form = document.querySelector("[data-quote-form]");
  const cfgEl = document.querySelector("[data-quote-config]");
  if (!form || !cfgEl) return;

  const cfg = JSON.parse(cfgEl.textContent || "{}");
  const hoursInput = form.querySelector("[data-hours]");

  const baseEl = document.querySelector("[data-quote-base]");
  const feeEl = document.querySelector("[data-quote-fee]");
  const totalEl = document.querySelector("[data-quote-total]");
  const depEl = document.querySelector("[data-quote-deposit]");

  function render() {
    const rawHours = parseInt(hoursInput.value || cfg.min_hours || 1, 10);
    const hours = Math.max(rawHours, cfg.min_hours || 1);

    const base = hours * (cfg.price_per_hour || 0);
    const fee = Math.round(base * (cfg.service_fee_rate || 0));
    const total = base + fee;
    const deposit = Math.round(base * ((cfg.deposit_pct || 0) / 100));

    baseEl.textContent = gbp(base);
    feeEl.textContent = gbp(fee);
    totalEl.textContent = gbp(total);
    depEl.textContent = `${gbp(deposit)} (based on ${cfg.deposit_pct || 0}% of base)`;
  }

  render();
  hoursInput.addEventListener("input", render);
})();
