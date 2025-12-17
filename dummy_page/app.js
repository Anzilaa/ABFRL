// Simple products + cart logic for the demo
const DATA_PATH = 'data/products.json';

function fetchProducts(){
  return fetch(DATA_PATH).then(r=>r.json());
}

function getCart(){
  return JSON.parse(localStorage.getItem('cart')||'[]');
}
function saveCart(cart){
  localStorage.setItem('cart', JSON.stringify(cart));
  updateCartCount();
}
function updateCartCount(){
  const count = getCart().reduce((s,i)=>s+i.qty,0);
  const el = document.getElementById('cart-count');
  if(el) el.textContent = count;
}

function addToCart(productId){
  const cart = getCart();
  const found = cart.find(i=>i.id===productId);
  if(found){ found.qty+=1; } else { cart.push({id:productId,qty:1}); }
  saveCart(cart);
}

function renderProducts(){
  const container = document.getElementById('products');
  if(!container) return;
  fetchProducts().then(products=>{
    // fetch recommendations from backend if available
    fetch('/api/recommendations')
      .then(r=>r.json())
      .then(data=>{
        if(data && data.results && data.results.length){
          const recRoot = document.getElementById('recommendations');
          if(recRoot){
            recRoot.innerHTML = '<h3>Recommended for you</h3>' + data.results.map(p=>`<div class="rec">${p.name} — ₹${p.price.toFixed(2)}</div>`).join('');
          }
        }
      }).catch(()=>{});

    const tpl = document.getElementById('product-template');
    products.forEach(p=>{
      const node = tpl.content.cloneNode(true);
      node.querySelector('.thumb').src = p.image;
      node.querySelector('.thumb').alt = p.name;
      node.querySelector('.name').textContent = p.name;
      node.querySelector('.desc').textContent = p.description;
      node.querySelector('.price').textContent = `₹${p.price.toFixed(2)}`;
      const btn = node.querySelector('.add');
      btn.addEventListener('click', ()=>{
        addToCart(p.id);
        btn.textContent = 'Added';
        setTimeout(()=>btn.textContent='Add to cart',800);
      });
      container.appendChild(node);
    });
  });
}

function renderCartPage(){
  const container = document.getElementById('cart-items');
  const summary = document.getElementById('cart-summary');
  if(!container) return;
  fetchProducts().then(products=>{
    const cart = getCart();
    container.innerHTML = '';
    let total = 0;
    if(cart.length===0){ container.innerHTML = '<p>Your cart is empty.</p>'; summary.innerHTML=''; return; }
    cart.forEach(item=>{
      const p = products.find(x=>x.id===item.id);
      if(!p) return;
      total += p.price * item.qty;
      const row = document.createElement('div');
      row.className = 'cart-row';
      row.innerHTML = `
        <img src="${p.image}" alt="${p.name}">
        <div style="flex:1">
          <strong>${p.name}</strong>
          <div>${p.description}</div>
          <div>₹${p.price.toFixed(2)} × <input type="number" min="1" value="${item.qty}" data-id="${p.id}" class="qty" style="width:64px"></div>
        </div>
        <div>
          <button data-remove="${p.id}">Remove</button>
        </div>
      `;
      container.appendChild(row);
    });
    summary.innerHTML = `<strong>Total: ₹${total.toFixed(2)}</strong><br><a href="checkout.html"><button>Proceed to Checkout</button></a>`;

    container.querySelectorAll('button[data-remove]').forEach(b=>{
      b.addEventListener('click', e=>{
        const id = e.currentTarget.getAttribute('data-remove');
        const updated = getCart().filter(i=>i.id!==id);
        saveCart(updated);
        renderCartPage();
      });
    });
    container.querySelectorAll('.qty').forEach(inp=>{
      inp.addEventListener('change', e=>{
        const id = e.target.getAttribute('data-id');
        const qty = parseInt(e.target.value,10)||1;
        const cart = getCart();
        const it = cart.find(i=>i.id===id);
        if(it){ it.qty = qty; saveCart(cart); renderCartPage(); }
      });
    });
  });
}

function renderCheckout(){
  const summary = document.getElementById('checkout-summary');
  if(!summary) return;
  fetchProducts().then(products=>{
    const cart = getCart();
    if(cart.length===0){ summary.innerHTML = '<p>Your cart is empty.</p>'; return; }
    let total = 0;
    const lines = cart.map(i=>{
      const p = products.find(x=>x.id===i.id);
      const line = `${p.name} × ${i.qty} — ₹${(p.price*i.qty).toFixed(2)}`;
      total += p.price*i.qty;
      return `<div>${line}</div>`;
    });
    summary.innerHTML = lines.join('') + `<hr><strong>Total: ₹${total.toFixed(2)}</strong>`;
  });

  const form = document.getElementById('checkout-form');
  if(form){
    form.addEventListener('submit', e=>{
      e.preventDefault();
      // simplistic order handling
      localStorage.removeItem('cart');
      updateCartCount();
      document.getElementById('order-result').textContent = 'Order placed — thank you!';
      form.reset();
    });
  }
}

// Initialize based on page
document.addEventListener('DOMContentLoaded', ()=>{
  updateCartCount();
  const path = location.pathname.split('/').pop();
  if(path==='products.html') renderProducts();
  if(path==='cart.html') renderCartPage();
  if(path==='checkout.html') renderCheckout();
});
