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

  /* reveal-on-scroll — progressive enhancement.
     The stylesheet keeps `.reveal` visible by default and only hides it once
     `html.js` is set, so we opt in ONLY when IntersectionObserver is available.
     Elements fade/slide in the first time they enter the viewport. */
  if ('IntersectionObserver' in window) {
    document.documentElement.classList.add('js');
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          obs.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
  }
})();
