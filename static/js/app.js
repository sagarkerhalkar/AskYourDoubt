(() => {
  const qs = (selector, root = document) => root.querySelector(selector);
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
  window.AYD = { qs, qsa };

  const toast = (message, type = 'success') => {
    let box = qs('#aydToast');
    if (!box) {
      box = document.createElement('div');
      box.id = 'aydToast';
      Object.assign(box.style, {
        position: 'fixed', right: '18px', bottom: '18px', zIndex: '9999',
        maxWidth: 'min(360px, calc(100vw - 36px))', padding: '12px 15px',
        borderRadius: '13px', color: '#fff', fontWeight: '800', fontSize: '.88rem',
        boxShadow: '0 16px 40px rgba(15,23,42,.24)', opacity: '0',
        transform: 'translateY(10px)', transition: '.2s ease'
      });
      document.body.appendChild(box);
    }
    box.textContent = message;
    box.style.background = type === 'error' ? '#d92d20' : '#3448d8';
    box.style.opacity = '1';
    box.style.transform = 'translateY(0)';
    clearTimeout(box._timer);
    box._timer = setTimeout(() => {
      box.style.opacity = '0';
      box.style.transform = 'translateY(10px)';
    }, 1800);
  };

  const menu = qs('[data-mobile-menu]');
  const sidebar = qs('.sidebar');
  if (menu && sidebar) {
    menu.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (event) => {
      if (window.innerWidth <= 1024 && sidebar.classList.contains('open') &&
          !sidebar.contains(event.target) && !menu.contains(event.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  const navToggle = qs('[data-nav-toggle]');
  const nav = qs('.navlinks');
  if (navToggle && nav) navToggle.addEventListener('click', () => nav.classList.toggle('open'));

  const fallbackCopy = (value) => {
    const area = document.createElement('textarea');
    area.value = value;
    area.setAttribute('readonly', '');
    Object.assign(area.style, { position: 'fixed', opacity: '0', pointerEvents: 'none' });
    document.body.appendChild(area);
    area.select();
    area.setSelectionRange(0, value.length);
    let copied = false;
    try { copied = document.execCommand('copy'); } catch (_) { copied = false; }
    area.remove();
    return copied;
  };

  qsa('[data-copy], [data-copy-target]').forEach((button) => {
    button.addEventListener('click', async () => {
      const targetSelector = button.dataset.copyTarget || '';
      const target = targetSelector ? qs(targetSelector) : null;
      const value = (button.dataset.copy || target?.value || target?.textContent || '').trim();
      if (!value) {
        toast('Nothing to copy.', 'error');
        return;
      }
      const original = button.textContent;
      let copied = false;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(value);
          copied = true;
        }
      } catch (_) { copied = false; }
      if (!copied) copied = fallbackCopy(value);
      if (!copied) {
        window.prompt('Copy this link:', value);
        return;
      }
      button.textContent = 'Copied ✓';
      toast('Join link copied.');
      setTimeout(() => { button.textContent = original || 'Copy Link'; }, 1400);
    });
  });

  qsa('[data-collapse]').forEach((button) => button.addEventListener('click', () => {
    const box = qs(button.dataset.collapse);
    if (!box) return;
    box.classList.toggle('open');
    button.setAttribute('aria-expanded', String(box.classList.contains('open')));
  }));

  qsa('[data-tab]').forEach((button) => button.addEventListener('click', () => {
    const root = button.closest('[data-tabs]') || document;
    qsa('[data-tab]', root).forEach((item) => item.classList.remove('active'));
    qsa('[data-tab-panel]', root).forEach((panel) => panel.classList.remove('active'));
    button.classList.add('active');
    qs(`[data-tab-panel="${button.dataset.tab}"]`, root)?.classList.add('active');
  }));

  qsa('[data-emoji]').forEach((button) => button.addEventListener('click', () => {
    const target = qs(button.dataset.target || '#question');
    if (!target) return;
    const start = target.selectionStart ?? target.value.length;
    const end = target.selectionEnd ?? start;
    target.value = target.value.slice(0, start) + button.dataset.emoji + target.value.slice(end);
    target.focus();
    target.selectionStart = target.selectionEnd = start + button.dataset.emoji.length;
  }));

  qsa('[data-countdown]').forEach((element) => {
    const end = new Date(element.dataset.countdown).getTime();
    const tick = () => {
      const diff = Math.max(0, end - Date.now());
      const hours = Math.floor(diff / 3600000);
      const minutes = Math.floor((diff % 3600000) / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      element.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    };
    tick();
    setInterval(tick, 1000);
  });
})();

/* Premium motion layer: progressive enhancement only. */
(() => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  document.querySelectorAll('.hero-grid > *, .role-card, .feature-strip > *, .auth-card, .auth-visual > *, .page-head, .stat, .panel, .resource-form, .question-bank-card').forEach((element, index) => {
    if (!element.hasAttribute('data-reveal')) element.setAttribute('data-reveal', '');
    element.style.transitionDelay = `${Math.min(index % 8, 7) * 45}ms`;
  });

  if (!reduceMotion && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll('[data-reveal]').forEach((element) => observer.observe(element));
  } else {
    document.querySelectorAll('[data-reveal]').forEach((element) => element.classList.add('revealed'));
  }

  if (!reduceMotion && window.matchMedia('(pointer:fine)').matches) {
    document.querySelectorAll('.role-card, .auth-card, .stat, .resource-form').forEach((card) => {
      card.setAttribute('data-tilt', '');
      card.addEventListener('pointermove', (event) => {
        const rect = card.getBoundingClientRect();
        const px = (event.clientX - rect.left) / rect.width - 0.5;
        const py = (event.clientY - rect.top) / rect.height - 0.5;
        card.style.transform = `perspective(900px) rotateX(${(-py * 3.5).toFixed(2)}deg) rotateY(${(px * 4).toFixed(2)}deg) translateY(-3px)`;
      });
      card.addEventListener('pointerleave', () => { card.style.transform = ''; });
    });
  }

  const animateValue = (element) => {
    const raw = (element.textContent || '').trim();
    if (!/^\d+$/.test(raw)) return;
    const target = Number(raw);
    if (target <= 0 || reduceMotion) return;
    const duration = Math.min(900, 350 + target * 12);
    const start = performance.now();
    const tick = (now) => {
      const progress = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      element.textContent = String(Math.round(target * eased));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  document.querySelectorAll('.stat strong').forEach(animateValue);
})();

/* QR download/share: native share on supported devices, safe fallback everywhere. */
(() => {
  const buttons = [...document.querySelectorAll('[data-share-qr]')];
  if (!buttons.length) return;

  const notify = (message) => {
    let box = document.querySelector('#aydQrToast');
    if (!box) {
      box = document.createElement('div');
      box.id = 'aydQrToast';
      Object.assign(box.style, {
        position: 'fixed', right: '18px', bottom: '18px', zIndex: '10000',
        maxWidth: 'min(380px, calc(100vw - 36px))', padding: '12px 15px',
        borderRadius: '13px', color: '#fff', background: '#315cf5',
        fontWeight: '800', fontSize: '.86rem', boxShadow: '0 18px 44px rgba(31,49,120,.24)',
        opacity: '0', transform: 'translateY(10px)', transition: '.2s ease'
      });
      document.body.appendChild(box);
    }
    box.textContent = message;
    box.style.opacity = '1';
    box.style.transform = 'translateY(0)';
    clearTimeout(box._timer);
    box._timer = setTimeout(() => {
      box.style.opacity = '0';
      box.style.transform = 'translateY(10px)';
    }, 2300);
  };

  const copyText = (value) => {
    const area = document.createElement('textarea');
    area.value = value || '';
    area.setAttribute('readonly', '');
    Object.assign(area.style, { position: 'fixed', opacity: '0', pointerEvents: 'none' });
    document.body.appendChild(area);
    area.select();
    area.setSelectionRange(0, area.value.length);
    let copied = false;
    try { copied = document.execCommand('copy'); } catch (_) { copied = false; }
    area.remove();
    return copied;
  };

  const downloadFile = (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'AskYourDoubt_QR.png';
    link.rel = 'noopener';
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  buttons.forEach((button) => {
    button.addEventListener('click', async () => {
      const qrUrl = button.dataset.qrUrl;
      const joinUrl = button.dataset.joinUrl;
      const filename = button.dataset.fileName || 'AskYourDoubt_QR.png';
      const original = button.textContent;
      button.disabled = true;
      button.textContent = 'Preparing…';

      try {
        let file = null;
        try {
          const response = await fetch(qrUrl, { cache: 'no-store' });
          if (response.ok) {
            const blob = await response.blob();
            file = new File([blob], filename, { type: blob.type || 'image/png' });
          }
        } catch (_) { file = null; }

        if (navigator.share && file && (!navigator.canShare || navigator.canShare({ files: [file] }))) {
          await navigator.share({
            title: 'AskYourDoubt — Join Session',
            text: 'Scan this QR code or use the session link to join the live doubt session.',
            url: joinUrl,
            files: [file],
          });
          notify('QR shared successfully.');
          return;
        }

        if (navigator.share) {
          await navigator.share({
            title: 'AskYourDoubt — Join Session',
            text: 'Join the live doubt session using this link.',
            url: joinUrl,
          });
          notify('Session link shared.');
          return;
        }

        downloadFile(qrUrl, filename);
        if (joinUrl) copyText(joinUrl);
        notify('QR downloaded and join link copied.');
      } catch (error) {
        if (error && error.name === 'AbortError') return;
        downloadFile(qrUrl, filename);
        if (joinUrl) copyText(joinUrl);
        notify('QR downloaded. Share it from your Downloads folder.');
      } finally {
        button.disabled = false;
        button.textContent = original;
      }
    });
  });
})();
