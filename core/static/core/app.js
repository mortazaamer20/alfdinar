/* مبادرة ألف دينار — تفاعلات الواجهة */
(function () {
  'use strict';

  /* close mobile nav on link click */
  document.querySelectorAll('.nav-links a').forEach((a) =>
    a.addEventListener('click', () =>
      document.querySelector('.nav-links')?.classList.remove('open')
    )
  );

  /* mark nav toggle accessible state (no-op enhancement) */
  const toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const open = document.querySelector('.nav-links')?.classList.contains('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
})();
