(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- mobile nav ---- */

  function initNav() {
    var toggle = document.querySelector('.nav-toggle');
    var list = document.getElementById('nav-list');
    if (!toggle || !list) return;

    function setOpen(open) {
      toggle.setAttribute('aria-expanded', String(open));
      list.dataset.open = String(open);
    }

    toggle.addEventListener('click', function () {
      setOpen(toggle.getAttribute('aria-expanded') !== 'true');
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        toggle.focus();
      }
    });

    document.addEventListener('click', function (e) {
      if (toggle.getAttribute('aria-expanded') !== 'true') return;
      if (!toggle.contains(e.target) && !list.contains(e.target)) setOpen(false);
    });

    // the menu is only a menu below the breakpoint; leaving it "open" past that
    // point strands aria-expanded in the wrong state
    window.matchMedia('(min-width: 761px)').addEventListener('change', function (e) {
      if (e.matches) setOpen(false);
    });
  }

  /* ---- copy buttons on code snippets ---- */

  function initCopyButtons() {
    if (!navigator.clipboard) return;

    document.querySelectorAll('.snippet').forEach(function (snippet) {
      var bar = snippet.querySelector('.snippet-bar');
      var pre = snippet.querySelector('pre');
      if (!bar || !pre) return;

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'copy-btn';
      btn.textContent = 'copy';
      btn.setAttribute('aria-label', 'Copy snippet to clipboard');

      var reset;
      btn.addEventListener('click', function () {
        clearTimeout(reset);
        navigator.clipboard.writeText(pre.innerText).then(function () {
          btn.textContent = 'copied';
          btn.dataset.state = 'done';
        }, function () {
          btn.textContent = 'failed';
          btn.dataset.state = 'fail';
        }).then(function () {
          reset = setTimeout(function () {
            btn.textContent = 'copy';
            delete btn.dataset.state;
          }, 1800);
        });
      });

      bar.appendChild(btn);
    });
  }

  /* ---- table of contents, built from the article's own headings ---- */

  function slugify(text) {
    return text.toLowerCase().trim()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-');
  }

  function initToc() {
    var toc = document.querySelector('.toc');
    var prose = document.querySelector('.prose');
    if (!toc || !prose) return;

    var headings = prose.querySelectorAll('h2, h3');
    if (headings.length < 3) {
      toc.remove();
      return;
    }

    var list = document.createElement('ol');
    var used = Object.create(null);

    headings.forEach(function (h) {
      if (!h.id) {
        var base = slugify(h.textContent) || 'section';
        used[base] = (used[base] || 0) + 1;
        h.id = used[base] > 1 ? base + '-' + used[base] : base;
      }

      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;

      var li = document.createElement('li');
      li.className = 'lvl-' + h.tagName[1];
      li.appendChild(a);
      list.appendChild(li);
    });

    toc.appendChild(list);

    // highlight whichever heading the reader is currently under
    var links = {};
    list.querySelectorAll('a').forEach(function (a) {
      links[a.getAttribute('href').slice(1)] = a;
    });

    var active = null;
    var seen = new Set();

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) seen.add(entry.target.id);
        else seen.delete(entry.target.id);
      });

      var current = null;
      headings.forEach(function (h) {
        if (seen.has(h.id) && !current) current = h.id;
      });
      if (!current || current === active) return;

      if (active && links[active]) links[active].classList.remove('is-current');
      links[current].classList.add('is-current');
      active = current;
    }, { rootMargin: '-80px 0px -70% 0px' });

    headings.forEach(function (h) { observer.observe(h); });
  }

  /* ---- reading progress ---- */

  function initProgress() {
    var prose = document.querySelector('.prose');
    if (!prose || reduceMotion) return;

    var bar = document.createElement('div');
    bar.className = 'progress';
    document.body.appendChild(bar);

    var start = 0;
    var span = 1;
    var queued = false;

    function measure() {
      var box = prose.getBoundingClientRect();
      start = box.top + window.scrollY;
      // the last viewport of the article is visible without scrolling past it,
      // so the scrollable distance is the article height minus one screen
      span = Math.max(1, box.height - window.innerHeight);
    }

    function draw() {
      queued = false;
      var ratio = (window.scrollY - start) / span;
      bar.style.transform = 'scaleX(' + Math.min(1, Math.max(0, ratio)) + ')';
    }

    function onScroll() {
      if (queued) return;
      queued = true;
      requestAnimationFrame(draw);
    }

    measure();
    draw();

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', function () { measure(); onScroll(); }, { passive: true });

    // late-loading webfonts reflow the article and invalidate the measurement
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { measure(); draw(); });
    }
  }

  function init() {
    initNav();
    initCopyButtons();
    initToc();
    initProgress();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
