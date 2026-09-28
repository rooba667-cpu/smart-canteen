/* ============================================================
   Smart Canteen — JavaScript
   ============================================================ */

/* ═══════════════════════════════════
   CART STATE  (localStorage)
═══════════════════════════════════ */
const CART_KEY = 'sc_cart';

function getCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
  catch { return []; }
}
function saveCart(cart) { localStorage.setItem(CART_KEY, JSON.stringify(cart)); }
function clearCart()    { localStorage.removeItem(CART_KEY); }

function updateCartBadge() {
  const cart  = getCart();
  const total = cart.reduce((s, i) => s + i.quantity, 0);
  document.querySelectorAll('.cart-count').forEach(el => {
    el.textContent = total;
    el.style.display = total > 0 ? 'flex' : 'none';
  });
}

/* ═══════════════════════════════════
   ADD TO CART
═══════════════════════════════════ */
function addToCart(itemId, name, price, emoji) {
  const cart = getCart();
  const idx  = cart.findIndex(i => i.food_item_id === itemId);
  if (idx >= 0) {
    cart[idx].quantity++;
  } else {
    cart.push({ food_item_id: itemId, name, price, emoji, quantity: 1 });
  }
  saveCart(cart);
  updateCartBadge();
  showToast(`${name} added to cart 🛒`, 'success');
}

/* ═══════════════════════════════════
   TOAST NOTIFICATION
═══════════════════════════════════ */
function showToast(msg, type = 'success') {
  let toast = document.getElementById('sc-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'sc-toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✅' : '❌'}</span> ${msg}`;
  toast.classList.add('show');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('show'), 3000);
}

/* ═══════════════════════════════════
   HAMBURGER MENU
═══════════════════════════════════ */
function initHamburger() {
  const btn = document.querySelector('.hamburger');
  const nav = document.querySelector('.navbar-nav');
  if (!btn || !nav) return;
  btn.addEventListener('click', () => nav.classList.toggle('open'));
  document.addEventListener('click', e => {
    if (!btn.contains(e.target) && !nav.contains(e.target)) nav.classList.remove('open');
  });
}

/* ═══════════════════════════════════
   AUTO-DISMISS ALERTS
═══════════════════════════════════ */
function initAlerts() {
  document.querySelectorAll('.alert').forEach(a => {
    setTimeout(() => a.style.opacity = '0', 4000);
    setTimeout(() => a.remove(), 4500);
  });
}

/* ═══════════════════════════════════
   MENU PAGE
═══════════════════════════════════ */
function initMenuPage() {
  if (!document.querySelector('.food-grid')) return;

  /* Tab filter */
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.dataset.cat;
      document.querySelectorAll('.category-section').forEach(sec => {
        sec.style.display = (cat === 'all' || sec.dataset.cat === cat) ? 'block' : 'none';
      });
    });
  });

  /* Search */
  const searchInput = document.getElementById('menu-search');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase().trim();
      document.querySelectorAll('.food-card').forEach(card => {
        const text = card.querySelector('h4').textContent.toLowerCase();
        card.closest('.col-item').style.display = text.includes(q) ? '' : 'none';
      });
    });
  }
}

/* ═══════════════════════════════════
   CART PAGE
═══════════════════════════════════ */
function initCartPage() {
  const cartContainer = document.getElementById('cart-items-container');
  if (!cartContainer) return;
  renderCart();
}

function renderCart() {
  const cart = getCart();
  const container = document.getElementById('cart-items-container');
  const emptyMsg  = document.getElementById('cart-empty');
  const summaryEl = document.getElementById('cart-summary');
  if (!container) return;

  if (cart.length === 0) {
    container.innerHTML = '';
    if (emptyMsg)  emptyMsg.style.display  = 'block';
    if (summaryEl) summaryEl.style.display = 'none';
    updateCartTotals(0, 0);
    return;
  }

  if (emptyMsg)  emptyMsg.style.display  = 'none';
  if (summaryEl) summaryEl.style.display = 'block';

  container.innerHTML = cart.map((item, idx) => `
    <div class="cart-item" data-idx="${idx}">
      <div class="cart-item-emoji">${item.emoji || '🍽️'}</div>
      <div class="cart-item-info">
        <h4>${item.name}</h4>
        <span>₹${(item.price * item.quantity).toFixed(2)}</span>
        <div style="font-size:.78rem;color:#999">₹${item.price} each</div>
      </div>
      <div class="cart-controls">
        <button class="qty-btn" onclick="changeQty(${idx}, -1)">−</button>
        <span class="qty-display">${item.quantity}</span>
        <button class="qty-btn" onclick="changeQty(${idx}, 1)">+</button>
        <button class="remove-item" onclick="removeItem(${idx})" title="Remove">🗑</button>
      </div>
    </div>
  `).join('');

  const totalQty    = cart.reduce((s, i) => s + i.quantity, 0);
  const totalAmount = cart.reduce((s, i) => s + i.price * i.quantity, 0);
  updateCartTotals(totalQty, totalAmount);
}

function updateCartTotals(qty, amount) {
  const el = (id) => document.getElementById(id);
  if (el('cart-qty'))    el('cart-qty').textContent    = qty;
  if (el('cart-subtotal')) el('cart-subtotal').textContent = `₹${amount.toFixed(2)}`;
  if (el('cart-total'))  el('cart-total').textContent  = `₹${amount.toFixed(2)}`;

  /* Prep time estimate */
  let prep = '';
  if (qty === 0)       prep = '—';
  else if (qty <= 2)   prep = '5 – 10 minutes';
  else if (qty <= 4)   prep = '10 – 15 minutes';
  else                 prep = '15 – 20 minutes';
  if (el('prep-time')) el('prep-time').textContent = prep;

  const placeBtn = document.getElementById('place-order-btn');
  if (placeBtn) placeBtn.disabled = qty === 0;
}

function changeQty(idx, delta) {
  const cart = getCart();
  cart[idx].quantity += delta;
  if (cart[idx].quantity <= 0) cart.splice(idx, 1);
  saveCart(cart);
  updateCartBadge();
  renderCart();
}

function removeItem(idx) {
  const cart = getCart();
  const name = cart[idx].name;
  cart.splice(idx, 1);
  saveCart(cart);
  updateCartBadge();
  renderCart();
  showToast(`${name} removed from cart`, 'error');
}

/* ═══════════════════════════════════
   PLACE ORDER
═══════════════════════════════════ */
function placeOrder() {
  const cart        = getCart();
  const pickupTime  = document.getElementById('pickup-time')?.value;
  const placeBtn    = document.getElementById('place-order-btn');

  if (!pickupTime) { showToast('Please select a pickup time.', 'error'); return; }
  if (cart.length === 0) { showToast('Your cart is empty!', 'error'); return; }

  placeBtn.disabled = true;
  placeBtn.innerHTML = '<span class="spinner" style="width:20px;height:20px;border-width:2px;display:inline-block"></span> Placing Order…';

  fetch('/place-order', {
    method:  'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ items: cart, pickup_time: pickupTime })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      clearCart();
      updateCartBadge();
      window.location.href = `/order-confirmation/${data.order_id}`;
    } else {
      showToast(data.message || 'Order failed. Try again.', 'error');
      placeBtn.disabled = false;
      placeBtn.innerHTML = '🛒 Place Order';
    }
  })
  .catch(() => {
    showToast('Network error. Please try again.', 'error');
    placeBtn.disabled = false;
    placeBtn.innerHTML = '🛒 Place Order';
  });
}

/* ═══════════════════════════════════
   ORDER CONFIRMATION – live status poll
═══════════════════════════════════ */
function initOrderConfirmation() {
  const orderId = document.getElementById('order-id-val')?.value;
  if (!orderId) return;

  const STEPS = ['Pending','Accepted','Preparing','Ready','Completed'];

  function refreshStatus() {
    fetch(`/api/order-status/${orderId}`)
    .then(r => r.json())
    .then(data => {
      if (!data.status) return;
      const status = data.status;
      /* Update badge */
      const badge = document.getElementById('live-status-badge');
      if (badge) {
        badge.className = `status-badge ${status}`;
        badge.textContent = status;
      }
      /* Update tracker */
      const stepIdx = STEPS.indexOf(status);
      document.querySelectorAll('.status-step').forEach((step, i) => {
        step.classList.remove('active','completed');
        if (i < stepIdx)  step.classList.add('completed');
        if (i === stepIdx) step.classList.add('active');
      });
      if (status !== 'Completed' && status !== 'Cancelled') {
        setTimeout(refreshStatus, 15000);
      }
    })
    .catch(() => setTimeout(refreshStatus, 20000));
  }

  setTimeout(refreshStatus, 5000);
}

/* ═══════════════════════════════════
   ADMIN — update order status
═══════════════════════════════════ */
function updateOrderStatus(orderId, selectEl) {
  const status  = selectEl.value;
  const btn     = selectEl.closest('.admin-order-bottom')?.querySelector('.update-btn');
  if (btn) { btn.disabled = true; btn.textContent = '…'; }

  fetch('/update-order', {
    method:  'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ order_id: orderId, status })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast(`Order ${orderId} updated to "${status}"`, 'success');
      /* Update visible badge */
      const card  = selectEl.closest('.admin-order-card');
      const badge = card?.querySelector('.status-badge');
      if (badge) { badge.className = `status-badge ${status}`; badge.textContent = status; }
    } else {
      showToast('Update failed.', 'error');
    }
    if (btn) { btn.disabled = false; btn.textContent = 'Update'; }
  })
  .catch(() => { showToast('Network error.', 'error'); if (btn) { btn.disabled = false; btn.textContent = 'Update'; } });
}

/* ═══════════════════════════════════
   ADMIN — filter orders by status
═══════════════════════════════════ */
function filterOrders(status) {
  document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');

  document.querySelectorAll('.admin-order-card').forEach(card => {
    const badge = card.querySelector('.status-badge');
    if (!badge) return;
    const cardStatus = badge.textContent.trim();
    card.style.display = (status === 'all' || cardStatus === status) ? 'block' : 'none';
  });
}

/* ═══════════════════════════════════
   FORM VALIDATION
═══════════════════════════════════ */
function initFormValidation() {
  document.querySelectorAll('form.validated').forEach(form => {
    form.addEventListener('submit', e => {
      let valid = true;
      form.querySelectorAll('[required]').forEach(field => {
        field.classList.remove('invalid');
        if (!field.value.trim()) {
          field.classList.add('invalid');
          valid = false;
        }
      });
      /* Password confirm */
      const pw = form.querySelector('#password');
      const cp = form.querySelector('#confirm_password');
      if (pw && cp && pw.value !== cp.value) {
        cp.classList.add('invalid');
        showToast('Passwords do not match!', 'error');
        valid = false;
      }
      if (!valid) {
        e.preventDefault();
        showToast('Please fill in all required fields.', 'error');
      }
    });
  });
}

/* ═══════════════════════════════════
   GENERATE PICKUP TIME OPTIONS
═══════════════════════════════════ */
function populatePickupTimes() {
  const sel = document.getElementById('pickup-time');
  if (!sel) return;
  const now = new Date();
  now.setMinutes(now.getMinutes() + 15);  // earliest: 15 min from now
  now.setMinutes(Math.ceil(now.getMinutes() / 15) * 15, 0, 0); // round up to 15-min slot

  for (let i = 0; i < 12; i++) {
    const opt = document.createElement('option');
    const hours   = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    opt.value = opt.textContent = `${hours}:${minutes}`;
    sel.appendChild(opt);
    now.setMinutes(now.getMinutes() + 15);
  }
}

/* ═══════════════════════════════════
   INIT ON DOM READY
═══════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  updateCartBadge();
  initHamburger();
  initAlerts();
  initMenuPage();
  initCartPage();
  initOrderConfirmation();
  initFormValidation();
  populatePickupTimes();
});
