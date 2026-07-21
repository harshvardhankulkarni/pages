(function () {
  'use strict';

  /* ─── Dark Mode Toggle ─── */
  (function initDarkMode() {
    var saved = localStorage.getItem('chemsol-theme');
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    var theme = saved || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);

    var btn = document.createElement('button');
    btn.id = 'chemsol-dark-toggle';
    btn.setAttribute('aria-label', 'Toggle dark mode');
    btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    btn.style.cssText =
      'position:fixed;bottom:80px;right:24px;z-index:999;width:44px;height:44px;' +
      'border-radius:50%;border:2px solid var(--gray-300,#d1d5db);cursor:pointer;' +
      'font-size:20px;display:flex;align-items:center;justify-content:center;' +
      'background:var(--gray-800,#1f2937);color:#fff;box-shadow:0 2px 12px rgba(0,0,0,0.15);' +
      'transition:opacity 0.4s ease,transform 0.4s ease;opacity:0;transform:translateY(12px);';

    document.body.appendChild(btn);

    requestAnimationFrame(function () {
      btn.style.opacity = '1';
      btn.style.transform = 'translateY(0)';
    });

    btn.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme') || 'light';
      var next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('chemsol-theme', next);
      btn.innerHTML = next === 'dark' ? '☀️' : '🌙';
    });
  })();

  /* ─── Back-to-Top Button ─── */
  (function initBackToTop() {
    var btn = document.createElement('button');
    btn.id = 'chemsol-back-to-top';
    btn.setAttribute('aria-label', 'Scroll to top');
    btn.innerHTML = '&uarr;';
    btn.style.cssText =
      'position:fixed;bottom:24px;right:24px;z-index:998;width:44px;height:44px;' +
      'border-radius:50%;border:2px solid var(--gray-300,#d1d5db);cursor:pointer;' +
      'font-size:20px;font-weight:700;display:flex;align-items:center;justify-content:center;' +
      'background:var(--primary,#1a56db);color:#fff;box-shadow:0 2px 12px rgba(0,0,0,0.15);' +
      'transition:opacity 0.3s ease,visibility 0.3s ease,transform 0.3s ease;' +
      'opacity:0;visibility:hidden;transform:translateY(8px);';

    document.body.appendChild(btn);

    var show = function () {
      btn.style.opacity = '1';
      btn.style.visibility = 'visible';
      btn.style.transform = 'translateY(0)';
    };
    var hide = function () {
      btn.style.opacity = '0';
      btn.style.visibility = 'hidden';
      btn.style.transform = 'translateY(8px)';
    };

    window.addEventListener('scroll', function () {
      if (window.scrollY > 300) { show(); } else { hide(); }
    }, { passive: true });

    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  })();

  /* ─── Copy-to-Clipboard for Code Blocks ─── */
  (function initCopyButtons() {
    var codeBlocks = document.querySelectorAll('.auto-code, .code-block');
    codeBlocks.forEach(function (block) {
      if (block.querySelector('.chemsol-copy-btn')) return;

      var wrapper = block;
      wrapper.style.position = 'relative';

      var btn = document.createElement('button');
      btn.className = 'chemsol-copy-btn';
      btn.textContent = '\uD83D\uDCCB Copy';
      btn.style.cssText =
        'position:absolute;top:8px;right:8px;z-index:5;padding:4px 10px;' +
        'font-size:11px;font-weight:600;border-radius:6px;border:1px solid rgba(255,255,255,0.15);' +
        'cursor:pointer;background:rgba(255,255,255,0.08);color:#e2e8f0;' +
        'transition:background 0.15s,color 0.15s;line-height:1.4;';

      btn.addEventListener('mouseenter', function () {
        btn.style.background = 'rgba(255,255,255,0.18)';
      });
      btn.addEventListener('mouseleave', function () {
        btn.style.background = 'rgba(255,255,255,0.08)';
      });

      btn.addEventListener('click', function () {
        var text = block.textContent || '';
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text.trim()).then(function () {
            btn.textContent = '\u2713 Copied!';
            setTimeout(function () { btn.textContent = '\uD83D\uDCCB Copy'; }, 2000);
          }).catch(function () {
            btn.textContent = '\u2717 Failed';
            setTimeout(function () { btn.textContent = '\uD83D\uDCCB Copy'; }, 2000);
          });
        } else {
          fallbackCopy(text, btn);
        }
      });

      wrapper.appendChild(btn);
    });

    function fallbackCopy(text, btn) {
      var ta = document.createElement('textarea');
      ta.value = text.trim();
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand('copy');
        btn.textContent = '\u2713 Copied!';
      } catch (e) {
        btn.textContent = '\u2717 Failed';
      }
      document.body.removeChild(ta);
      setTimeout(function () { btn.textContent = '\uD83D\uDCCB Copy'; }, 2000);
    }
  })();

  /* ─── Table Search/Filter ─── */
  (function initTableFilters() {
    document.querySelectorAll('.table-wrap').forEach(function (wrap) {
      if (wrap.querySelector('.chemsol-table-filter')) return;

      var table = wrap.querySelector('table');
      if (!table) return;

      var tbody = table.querySelector('tbody');
      if (!tbody) return;

      var rows = tbody.querySelectorAll('tr');
      if (rows.length <= 5) return;

      var filterContainer = document.createElement('div');
      filterContainer.className = 'chemsol-table-filter';
      filterContainer.style.cssText =
        'display:flex;align-items:center;gap:10px;padding:10px 14px;' +
        'border-bottom:1px solid var(--gray-200,#e5e7eb);background:var(--gray-50,#f9fafb);';

      var input = document.createElement('input');
      input.type = 'text';
      input.placeholder = 'Filter table...';
      input.style.cssText =
        'flex:1;padding:6px 10px;font-size:13px;border:1px solid var(--gray-300,#d1d5db);' +
        'border-radius:6px;font-family:inherit;background:#fff;' +
        'color:var(--gray-800,#1f2937);outline:none;transition:border-color 0.15s;';

      input.addEventListener('focus', function () {
        input.style.borderColor = 'var(--primary,#1a56db)';
      });
      input.addEventListener('blur', function () {
        input.style.borderColor = 'var(--gray-300,#d1d5db)';
      });

      var count = document.createElement('span');
      count.style.cssText =
        'font-size:12px;color:var(--gray-500,#6b7280);font-weight:500;white-space:nowrap;';

      function updateCount() {
        var visible = 0;
        rows.forEach(function (r) { if (r.style.display !== 'none') visible++; });
        count.textContent = visible + ' / ' + rows.length + ' rows';
      }

      input.addEventListener('input', function () {
        var q = input.value.toLowerCase().trim();
        rows.forEach(function (row) {
          var match = !q;
          if (q) {
            var cells = row.querySelectorAll('td, th');
            cells.forEach(function (cell) {
              if (cell.textContent.toLowerCase().indexOf(q) !== -1) {
                match = true;
              }
            });
          }
          row.style.display = match ? '' : 'none';
        });
        updateCount();
      });

      filterContainer.appendChild(input);
      filterContainer.appendChild(count);
      wrap.insertBefore(filterContainer, table);
      updateCount();
    });
  })();

  /* ─── Scroll-Triggered Reveal Animations ─── */
  (function initScrollReveal() {
    if (!window.IntersectionObserver) return;

    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    document.querySelectorAll('.reveal, .phase, .impl-card, .auto-card, .dash-card').forEach(function (el) {
      revealObserver.observe(el);
    });
  })();

  /* ─── Smooth Anchor Scrolling ─── */
  (function initSmoothAnchors() {
    document.addEventListener('click', function (e) {
      var target = e.target;
      while (target && target.tagName !== 'A') { target = target.parentElement; }
      if (!target) return;

      var href = target.getAttribute('href');
      if (!href || href.charAt(0) !== '#') return;

      var id = href.slice(1);
      var el = document.getElementById(id);
      if (!el) return;

      e.preventDefault();
      var top = el.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  })();

  /* ─── Progress Bar Animation ─── */
  (function initProgressBars() {
    if (!window.IntersectionObserver) {
      document.querySelectorAll('.dash-progress-fill').forEach(function (bar) {
        var w = bar.getAttribute('data-width') || bar.style.width || '0%';
        bar.style.width = '0%';
        bar.style.width = w;
      });
      return;
    }

    var progressObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var bar = entry.target;
        var target = parseFloat(bar.getAttribute('data-width') || bar.style.width) || 0;
        var startTime = null;
        var duration = 800;

        bar.style.width = '0%';

        function animate(ts) {
          if (!startTime) startTime = ts;
          var elapsed = ts - startTime;
          var progress = Math.min(elapsed / duration, 1);
          var eased = 1 - Math.pow(1 - progress, 3);
          bar.style.width = (target * eased).toFixed(1) + '%';
          if (progress < 1) {
            requestAnimationFrame(animate);
          }
        }

        requestAnimationFrame(animate);
        progressObserver.unobserve(bar);
      });
    }, { threshold: 0.15 });

    document.querySelectorAll('.dash-progress-fill').forEach(function (bar) {
      progressObserver.observe(bar);
    });
  })();

})();
