document.addEventListener('DOMContentLoaded', () => {
 
  /* ---------- Navbar: sombra al hacer scroll ---------- */
  const navEl = document.getElementById('siteNav');
  const toggleBtn = document.getElementById('navToggle');
 
  if (navEl) {
    window.addEventListener('scroll', () => {
      navEl.classList.toggle('scrolled', window.scrollY > 8);
    }, { passive: true });
  }
 
  if (toggleBtn && navEl) {
    toggleBtn.addEventListener('click', () => {
      const open = navEl.classList.toggle('open');
      toggleBtn.setAttribute('aria-expanded', String(open));
    });
    document.querySelectorAll('nav.links a').forEach(a => {
      a.addEventListener('click', () => {
        navEl.classList.remove('open');
        toggleBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }
 
  /* ---------- Resalta el link activo según la página actual ---------- */
  const current = document.body.dataset.page;
  if (current) {
    document.querySelectorAll('nav.links a[data-page]').forEach(a => {
      if (a.dataset.page === current) a.classList.add('active');
    });
  }
 
  /* ---------- Carrito simple (contador persistente) ---------- */
  const CART_KEY = 'craftbeer_cart_count';
  const cartCountEls = document.querySelectorAll('.cart-count');
 
  function getCartCount() {
    try { return parseInt(localStorage.getItem(CART_KEY) || '0', 10); }
    catch (e) { return 0; }
  }
  function setCartCount(n) {
    cartCountEls.forEach(el => { el.textContent = n; });
    try { localStorage.setItem(CART_KEY, String(n)); } catch (e) { /* noop */ }
  }
  setCartCount(getCartCount());
 
  document.querySelectorAll('.add-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      setCartCount(getCartCount() + 1);
      const original = btn.textContent;
      btn.classList.add('added');
      btn.textContent = 'Agregado ✓';
      setTimeout(() => {
        btn.classList.remove('added');
        btn.textContent = original;
      }, 1200);
    });
  });
 
  /* ---------- Filtro de catálogo por categoría ---------- */
  const chips = document.querySelectorAll('.chip[data-filter]');
  const products = document.querySelectorAll('.product[data-category]');
 
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const filter = chip.dataset.filter;
 
      products.forEach(p => {
        const show = filter === 'todas' || p.dataset.category === filter;
        p.style.display = show ? '' : 'none';
      });
    });
  });
 
});