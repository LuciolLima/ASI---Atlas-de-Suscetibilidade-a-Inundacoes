/* ============================================================
   ASI Landing — Background Canvas + Interações + Modal
   Vanilla JS, sem dependências, ~3KB gzipped
   ============================================================ */

(() => {
  'use strict';

  // ====== Configuração ======
  const CFG = {
    particleCount: 55,
    particleColor: 'rgba(0, 180, 216, 0.35)',
    lineColor: 'rgba(46, 134, 193, 0.06)',
    maxDist: 130,
    speed: 0.12,
    parallaxStrength: 12
  };

  // ====== Estado ======
  const canvas = document.getElementById('bg-canvas');
  const ctx = canvas.getContext('2d');
  let width = 0, height = 0, particles = [], animationId = null;
  let prefersReducedMotion = false;

  // ====== Utilitários ======
  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  const lerp = (a, b, t) => a + (b - a) * t;

  // ====== NAV TABS — Troca de painéis ======
  function initNavTabs() {
    const tabButtons = document.querySelectorAll('.nav-tab');
    const panels = document.querySelectorAll('.panel-content');

    function switchTab(target) {
      // Atualizar botões
      tabButtons.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      const activeBtn = document.querySelector('.nav-tab[data-target="' + target + '"]');
      if (activeBtn) {
        activeBtn.classList.add('active');
        activeBtn.setAttribute('aria-selected', 'true');
      }

      // Atualizar painéis
      panels.forEach(panel => {
        if (panel.id === 'panel-' + target) {
          panel.hidden = false;
          panel.classList.add('active');
        } else {
          panel.hidden = true;
          panel.classList.remove('active');
        }
      });

      // Scroll suave para o topo do conteúdo
      const targetPanel = document.getElementById('panel-' + target);
      if (targetPanel) {
        targetPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    tabButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-target');
        switchTab(target);
      });
    });

    // Footer links que disparam tabs
    document.querySelectorAll('.footer-tab-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = link.getAttribute('data-tab');
        switchTab(target);
      });
    });
  }

  // ====== Canvas ======
  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  // ====== Partículas ======
  class Particle {
    constructor() { this.reset(true); }
    reset(init = false) {
      this.x = init ? Math.random() * width : Math.random() * width;
      this.y = init ? Math.random() * height : (Math.random() > 0.5 ? -10 : height + 10);
      this.vx = (Math.random() - 0.5) * CFG.speed;
      this.vy = (Math.random() - 0.5) * CFG.speed;
      this.radius = Math.random() * 1.4 + 0.4;
      this.alpha = Math.random() * 0.35 + 0.08;
    }
    update() {
      this.x += this.vx; this.y += this.vy;
      if (this.x < -15 || this.x > width + 15 || this.y < -15 || this.y > height + 15) {
        this.reset();
      }
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = CFG.particleColor.replace('0.35', this.alpha.toFixed(3));
      ctx.fill();
    }
  }

  function initParticles() {
    particles = Array.from({ length: CFG.particleCount }, () => new Particle());
  }

  function drawConnections() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const distSq = dx * dx + dy * dy;
        if (distSq < CFG.maxDist * CFG.maxDist) {
          const dist = Math.sqrt(distSq);
          const opacity = (1 - dist / CFG.maxDist) * 0.09;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = CFG.lineColor.replace('0.06', opacity.toFixed(4));
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach(p => { p.update(); p.draw(); });
    drawConnections();
    animationId = requestAnimationFrame(animate);
  }

  // ====== Modal Termos de Uso ======
  const modal = document.getElementById('terms-modal');
  const enterBtn = document.getElementById('enter-btn');
  const proceedBtn = document.getElementById('terms-proceed');
  const closeButtons = document.querySelectorAll('.modal-close');
  const tabButtons = document.querySelectorAll('.terms-tab');
  const tabPanels = document.querySelectorAll('.terms-panel');
  const countdownEl = document.getElementById('countdown-timer');

  const STREAMLIT_URL = 'https://asi---atlas-de-suscetibilidade-a-inundacoes.streamlit.app/?from_landing=1&v=3.0';

  let countdownInterval = null;
  let countdownSeconds = 10;
  let modalInitialized = false;

  function startCountdown() {
    countdownSeconds = 10;
    if (countdownEl) countdownEl.textContent = countdownSeconds;
    if (proceedBtn) {
      proceedBtn.disabled = true;
      proceedBtn.setAttribute('aria-describedby', 'countdown-timer');
    }

    countdownInterval = setInterval(() => {
      countdownSeconds--;
      if (countdownEl) countdownEl.textContent = countdownSeconds;
      if (countdownSeconds <= 0) {
        clearInterval(countdownInterval);
        countdownInterval = null;
        if (proceedBtn) {
          proceedBtn.disabled = false;
          proceedBtn.removeAttribute('aria-describedby');
          proceedBtn.focus();
        }
      }
    }, 1000);
  }

  function stopCountdown() {
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
  }

  function openModal() {
    if (!modal) return;
    // Reset state before opening
    stopCountdown();
    if (proceedBtn) proceedBtn.disabled = true;
    // Show modal with animation class
    modal.showModal();
    // Force reflow for animation
    modal.offsetWidth;
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    startCountdown();
  }

  function closeModal() {
    if (!modal) return;
    stopCountdown();
    // Animate out
    modal.classList.remove('is-open');
    // Wait for animation then close
    setTimeout(() => {
      if (!modal.classList.contains('is-open')) {
        modal.close();
        document.body.style.overflow = '';
        if (proceedBtn) proceedBtn.disabled = true;
      }
    }, 200); // match CSS animation duration
  }

  function handleTabClick(e) {
    const tab = e.currentTarget;
    const target = tab.getAttribute('aria-controls');

    tabButtons.forEach(btn => {
      btn.classList.remove('active');
      btn.setAttribute('aria-selected', 'false');
    });
    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');

    tabPanels.forEach(panel => {
      if (panel.id === target) {
        panel.hidden = false;
        panel.classList.add('active');
      } else {
        panel.hidden = true;
        panel.classList.remove('active');
      }
    });
  }

  function handleProceedClick(e) {
    e.preventDefault();
    e.stopPropagation();
    if (proceedBtn.disabled) return;
    closeModal();
    window.open(STREAMLIT_URL, '_blank', 'noopener,noreferrer');
  }

  function handleKeydown(e) {
    if (e.key === 'Escape' && modal?.open) {
      closeModal();
    }
  }

  // ====== Inicialização ======
  function init() {
    prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    resize(); 
    initParticles(); 
    
    if (!prefersReducedMotion) {
      animate();
    } else {
      particles.forEach(p => p.draw());
      drawConnections();
    }

    window.addEventListener('resize', () => { 
      resize(); 
      if (prefersReducedMotion) {
        ctx.clearRect(0, 0, width, height);
        particles.forEach(p => p.draw());
        drawConnections();
      }
    }, { passive: true });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        cancelAnimationFrame(animationId);
      } else if (!prefersReducedMotion) {
        animate();
      }
    });

    // ====== Event Listeners ======
    
    // Nav Tabs
    initNavTabs();

    // Botão "Iniciar ASI" abre modal
    if (enterBtn) {
      enterBtn.addEventListener('click', openModal);
      enterBtn.addEventListener('mouseenter', () => {
        if (!prefersReducedMotion) enterBtn.style.transform = 'translateY(-2px) scale(1.02)';
      });
      enterBtn.addEventListener('mouseleave', () => { enterBtn.style.transform = ''; });
      enterBtn.addEventListener('mousedown', () => { enterBtn.style.transform = 'scale(0.98)'; });
      enterBtn.addEventListener('mouseup', () => { 
        if (!prefersReducedMotion) enterBtn.style.transform = 'translateY(-2px) scale(1.02)'; 
        else enterBtn.style.transform = '';
      });
      enterBtn.addEventListener('focus', () => { enterBtn.style.transform = ''; });
    }

    // Modal events
    if (proceedBtn) proceedBtn.addEventListener('click', handleProceedClick);
    
    // Modal events
    if (proceedBtn) proceedBtn.addEventListener('click', handleProceedClick);
    closeButtons.forEach(btn => btn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeModal();
    }));

    // Fechar clicando no backdrop (apenas no backdrop real, não no conteúdo)
    if (modal) {
      modal.addEventListener('click', (e) => {
        // e.target === modal pega clique no próprio <dialog> (o fundo)
        // mas NÃO pega clique nos filhos (conteúdo do modal)
        if (e.target === modal) {
          closeModal();
        }
      });
    }

    tabButtons.forEach(btn => btn.addEventListener('click', handleTabClick));
    
    document.addEventListener('keydown', handleKeydown);

    // ====== Parallax sutil no hero ======
    const hero = document.querySelector('.hero');
    if (hero && !prefersReducedMotion) {
      let rafId = null;
      let targetX = 0, targetY = 0;
      let currentX = 0, currentY = 0;

      function parallaxLoop() {
        currentX = lerp(currentX, targetX, 0.08);
        currentY = lerp(currentY, targetY, 0.08);
        hero.style.transform = `translate(${currentX}px, ${currentY}px)`;
        rafId = requestAnimationFrame(parallaxLoop);
      }

      document.addEventListener('mousemove', (e) => {
        const { innerWidth, innerHeight } = window;
        targetX = clamp((e.clientX - innerWidth / 2) / innerWidth * CFG.parallaxStrength, -CFG.parallaxStrength, CFG.parallaxStrength);
        targetY = clamp((e.clientY - innerHeight / 2) / innerHeight * CFG.parallaxStrength, -CFG.parallaxStrength, CFG.parallaxStrength);
      }, { passive: true });

      document.addEventListener('mouseleave', () => {
        targetX = 0; targetY = 0;
      });

      parallaxLoop();

      window.addEventListener('beforeunload', () => cancelAnimationFrame(rafId));
    }

    // ====== IntersectionObserver para animação de entrada dos cards ======
    const cards = document.querySelectorAll('.info-card');
    if (cards.length && !prefersReducedMotion && 'IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, idx) => {
          if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

      cards.forEach((card, idx) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `opacity 0.5s ease ${idx * 0.08}s, transform 0.5s ease ${idx * 0.08}s`;
        observer.observe(card);
      });
    }

    // Animação das novas seções
    const devSection = document.querySelector('.dev-section');
    const ackSection = document.querySelector('.ack-section');
    const sectionsToAnimate = [devSection, ackSection].filter(Boolean);
    
    if (sectionsToAnimate.length && !prefersReducedMotion && 'IntersectionObserver' in window) {
      const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            sectionObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });
      
      sectionsToAnimate.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        sectionObserver.observe(section);
      });
    }

    // ====== Smooth scroll para âncoras internas ======
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', (e) => {
        const targetId = anchor.getAttribute('href');
        if (targetId === '#') return;
        const target = document.querySelector(targetId);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          target.focus({ preventScroll: true });
        }
      });
    });
  }
  
  // ====== Inicia ======
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();