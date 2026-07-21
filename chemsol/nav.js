// Enhanced navigation with section 9-14 inclusion
(function() {
  'use strict';

  // ── Accordion toggle ──
  var headers = document.querySelectorAll('.accordion-header');
  for (var i = 0; i < headers.length; i++) {
    headers[i].addEventListener('click', function() {
      this.classList.toggle('open');
      var body = this.nextElementSibling;
      if (body) body.classList.toggle('open');
    });
  }

  // ── Progress bar step click → scroll to section ──
  var steps = document.querySelectorAll('.fp-step');
  for (var s = 0; s < steps.length; s++) {
    steps[s].addEventListener('click', function() {
      var num = this.getAttribute('data-step');
      // Try to open the corresponding accordion section
      var accordionSections = document.querySelectorAll('.accordion-section');
      if (accordionSections[num - 1]) {
        var hdr = accordionSections[num - 1].querySelector('.accordion-header');
        var bdy = accordionSections[num - 1].querySelector('.accordion-body');
        if (hdr && !hdr.classList.contains('open')) {
          hdr.classList.add('open');
          if (bdy) bdy.classList.add('open');
        }
        hdr.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  }

  // ── Auto-detect current page and highlight ──
  var path = window.location.pathname.split('/').pop() || 'index.html';
  var links = document.querySelectorAll('.ab-link');
  for (var j = 0; j < links.length; j++) {
    var href = links[j].getAttribute('href');
    if (href === path || (path === '' && href === 'index.html')) {
      links[j].classList.add('active');
      // Open parent accordion
      var section = links[j].closest('.accordion-body');
      if (section) { section.classList.add('open'); }
      var header = links[j].closest('.accordion-section')?.querySelector('.accordion-header');
      if (header) { header.classList.add('open'); }
    }
  }

  // ── Auto-highlight progress bar step based on current page ──
  var stepMap = {
    'forms.html': 4,
    'flow.html': 4,
    'reports.html': 7,
    'security.html': 7,
    'data-model.html': 8,
    'implementation-plan.html': 8,
    'automation.html': 8
    // Note: Sections 9-14 (Finance, Governance, etc.) now map to step 8 or 9
    // based on current page progress
  };
  var currentStep = stepMap[path] || 0;
  if (currentStep > 0) {
    var circles = document.querySelectorAll('.fp-circle');
    for (var k = 0; k < circles.length; k++) {
      var stepNum = parseInt(circles[k].textContent, 10);
      if (stepNum < currentStep) {
        circles[k].classList.add('completed');
      } else if (stepNum === currentStep) {
        circles[k].classList.add('active');
      }
    }
  }

  // ── Enhanced progress tracking for sections 9-14 ──
  if (path === 'forms.html') {
    // For forms.html, extend progress tracking to cover up to step 10
    var formsSection = document.querySelector('#finance');
    if (formsSection) {
      var formsObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            // When sections 9-14 are visible, extend progress indicator
            document.querySelectorAll('.fp-circle').forEach(function(circle, index) {
              var stepNum = parseInt(circle.textContent, 10);
              // Map sections 9-14 to steps 9-11 in progress bar
              var mappedStep = Math.min(stepNum + 5, 11); // Extended range
              if (stepNum < mappedStep) {
                circle.classList.add('completed');
              } else if (stepNum === mappedStep) {
                circle.classList.add('active');
              }
            });
          }
        });
      }, { threshold: 0.2 });

      formsObserver.observe(formsSection);
    }
  }

  // ── Hamburger menu toggle (for mobile) ──
  document.getElementById('menuToggle')?.addEventListener('click', function() {
    this.classList.toggle('open');
    document.getElementById('sidebarNav')?.classList.toggle('open');
  });
})();
