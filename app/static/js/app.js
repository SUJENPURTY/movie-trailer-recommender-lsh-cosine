(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', init);

    function init() {
        initLoader();
        initNavbar();
        initMouseGlow();
        initParticles();
        initAOS();
        initGSAP();
        initSmoothScroll();
        initCarousels();
        initModals();
        initSearchAutocomplete();
        initCounters();
        initToast();
        initKeyboardShortcuts();
        initHoverEffects();
    }

    function initLoader() {
        const loader = document.getElementById('loader');
        if (!loader) return;

        window.addEventListener('load', function() {
            setTimeout(function() {
                loader.style.opacity = '0';
                loader.style.visibility = 'hidden';
                document.body.style.overflow = 'auto';
                initHeroAnimation();
            }, 800);
        });

        if (document.readyState === 'complete') {
            setTimeout(function() {
                loader.style.opacity = '0';
                loader.style.visibility = 'hidden';
            }, 500);
        }

        window.addEventListener('beforeunload', function() {
            loader.style.opacity = '1';
            loader.style.visibility = 'visible';
        });
    }

    function initHeroAnimation() {
        const heroBadge = document.querySelector('.hero-badge');
        const heroTitle = document.querySelector('.hero-title');
        const heroSubtitle = document.querySelector('.hero-subtitle');
        const heroSearch = document.querySelector('.hero-search');
        const trendingChips = document.querySelector('.trending-chips');
        const trustBadges = document.querySelector('.trust-badges');

        const tl = window.gsap ? window.gsap.timeline() : null;

        if (tl) {
            if (heroBadge) tl.fromTo(heroBadge, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, 0);
            if (heroTitle) tl.fromTo(heroTitle, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }, 0.1);
            if (heroSubtitle) tl.fromTo(heroSubtitle, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, 0.2);
            if (heroSearch) tl.fromTo(heroSearch, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, 0.3);
            if (trendingChips) tl.fromTo(trendingChips, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, 0.4);
            if (trustBadges) tl.fromTo(trustBadges, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }, 0.5);
        } else {
            const elements = [heroBadge, heroTitle, heroSubtitle, heroSearch, trendingChips, trustBadges];
            elements.forEach(function(el, i) {
                if (el) {
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(20px)';
                    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                    el.style.transitionDelay = (i * 0.1) + 's';
                    setTimeout(function() {
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    }, 100);
                }
            });
        }
    }

    function initNavbar() {
        const navbar = document.getElementById('mainNav');
        if (!navbar) return;

        const toggler = document.querySelector('.navbar-toggler');
        const collapse = document.querySelector('.navbar-collapse');

        if (toggler && collapse) {
            toggler.addEventListener('click', function() {
                collapse.classList.toggle('show');
                const icon = toggler.querySelector('i');
                if (icon) {
                    icon.classList.toggle('fa-bars');
                    icon.classList.toggle('fa-times');
                }
            });

            document.addEventListener('click', function(e) {
                if (!collapse.contains(e.target) && !toggler.contains(e.target)) {
                    collapse.classList.remove('show');
                    const icon = toggler.querySelector('i');
                    if (icon && !icon.classList.contains('fa-bars')) {
                        icon.classList.add('fa-bars');
                        icon.classList.remove('fa-times');
                    }
                }
            });
        }

        let lastScroll = 0;
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;

            if (currentScroll > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            if (currentScroll > 100 && currentScroll > lastScroll) {
                navbar.style.transform = 'translateY(-100%)';
            } else {
                navbar.style.transform = 'translateY(0)';
            }

            lastScroll = currentScroll;
        });

        document.querySelectorAll('.nav-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href && href.startsWith('#') && href.length > 1) {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        const offset = 80;
                        const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
                        window.scrollTo({ top: top, behavior: 'smooth' });

                        if (collapse && collapse.classList.contains('show')) {
                            collapse.classList.remove('show');
                        }
                    }
                }
            });
        });
    }

    function initMouseGlow() {
        const glow = document.getElementById('mouseGlow') || createMouseGlow();
        
        let throttleTimeout;
        document.addEventListener('mousemove', function(e) {
            if (throttleTimeout) return;
            
            throttleTimeout = setTimeout(function() {
                throttleTimeout = null;
                
                const target = e.target;
                const isInteractive = target.closest('.navbar, .btn, .movie-card, .toggle-btn, .switch-btn, a, button, input');
                
                if (isInteractive) {
                    glow.style.display = 'block';
                    glow.style.left = (e.clientX - 200) + 'px';
                    glow.style.top = (e.clientY - 200) + 'px';
                    glow.style.opacity = '0.3';
                } else {
                    glow.style.opacity = '0';
                    setTimeout(function() {
                        if (glow.style.opacity === '0') {
                            glow.style.display = 'none';
                        }
                    }, 300);
                }
            }, 50);
        });

        document.addEventListener('mouseout', function(e) {
            if (e.relatedTarget === null) {
                glow.style.opacity = '0';
                setTimeout(function() {
                    glow.style.display = 'none';
                }, 300);
            }
        });
    }

    function createMouseGlow() {
        const glow = document.createElement('div');
        glow.id = 'mouseGlow';
        glow.className = 'mouse-glow';
        glow.style.cssText = 'position:fixed;width:400px;height:400px;border-radius:50%;background:radial-gradient(circle,rgba(255,45,85,0.4),transparent 70%);pointer-events:none;z-index:0;display:none;transition:opacity 0.3s ease;';
        document.body.appendChild(glow);
        return glow;
    }

    function initParticles() {
        const container = document.getElementById('particles');
        if (!container) return;

        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = 'position:absolute;width:4px;height:4px;background:#ff2d55;border-radius:50%;opacity:0.3;left:' + Math.random() * 100 + '%;animation:particleFloat ' + (15 + Math.random() * 10) + 's linear infinite;animation-delay:' + Math.random() * 15 + 's;';
            container.appendChild(particle);
        }

        const style = document.createElement('style');
        style.textContent = '@keyframes particleFloat{0%{transform:translateY(100vh) rotate(0deg);opacity:0}10%{opacity:0.3}90%{opacity:0.3}100%{transform:translateY(-100vh) rotate(720deg);opacity:0}}';
        document.head.appendChild(style);
    }

    function initAOS() {
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-out-cubic',
                once: true,
                offset: 100,
                disable: function() {
                    return window.innerWidth < 768;
                }
            });

            window.addEventListener('scroll', function() {
                AOS.refreshHard();
            });

            window.addEventListener('resize', function() {
                AOS.refresh();
            });
        }
    }

    function initGSAP() {
        if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);

            gsap.utils.toArray('.section-title').forEach(function(el) {
                gsap.from(el, {
                    scrollTrigger: {
                        trigger: el,
                        start: 'top 80%'
                    },
                    y: 30,
                    opacity: 0,
                    duration: 1,
                    ease: 'power3.out'
                });
            });

            gsap.utils.toArray('.metric-card').forEach(function(card, i) {
                gsap.from(card, {
                    scrollTrigger: {
                        trigger: card,
                        start: 'top 85%'
                    },
                    y: 40,
                    opacity: 0,
                    duration: 0.8,
                    delay: i * 0.1,
                    ease: 'power3.out'
                });
            });

            gsap.utils.toArray('.movie-card').forEach(function(card, i) {
                gsap.from(card, {
                    scrollTrigger: {
                        trigger: card,
                        start: 'top 90%'
                    },
                    y: 50,
                    opacity: 0,
                    duration: 0.6,
                    delay: i * 0.05,
                    ease: 'power3.out'
                });
            });

            gsap.from('.chart-wrapper', {
                scrollTrigger: {
                    trigger: '.chart-wrapper',
                    start: 'top 80%'
                },
                scale: 0.95,
                opacity: 0,
                duration: 1,
                ease: 'power3.out'
            });

            gsap.utils.toArray('.feature-card').forEach(function(card, i) {
                gsap.from(card, {
                    scrollTrigger: {
                        trigger: card,
                        start: 'top 85%'
                    },
                    y: 40,
                    opacity: 0,
                    duration: 0.8,
                    delay: i * 0.15,
                    ease: 'power3.out'
                });
            });

            gsap.utils.toArray('.insight-card').forEach(function(card, i) {
                gsap.from(card, {
                    scrollTrigger: {
                        trigger: card,
                        start: 'top 90%'
                    },
                    y: 30,
                    opacity: 0,
                    duration: 0.6,
                    delay: i * 0.1,
                    ease: 'power3.out'
                });
            });

            ScrollTrigger.create({
                trigger: '.navbar',
                start: 'top -50',
                onUpdate: function(self) {
                    const navbar = document.getElementById('mainNav');
                    if (navbar) {
                        if (self.direction === 1 && self.scroll() > 50) {
                            navbar.style.transform = 'translateY(-100%)';
                        } else {
                            navbar.style.transform = 'translateY(0)';
                        }
                    }
                }
            });
        }
    }

    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const offset = 80;
                    const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
                    
                    if (window.gsap) {
                        gsap.to(window, { duration: 0.8, scrollTo: { y: top }, ease: 'power3.out' });
                    } else {
                        window.scrollTo({ top: top, behavior: 'smooth' });
                    }
                }
            });
        });

        document.documentElement.style.scrollBehavior = 'smooth';
    }

    function initCarousels() {
        document.querySelectorAll('.carousel-section').forEach(function(section) {
            const container = section.querySelector('.carousel-container');
            const prevBtn = section.querySelector('.carousel-nav.prev');
            const nextBtn = section.querySelector('.carousel-nav.next');

            if (!container) return;

            const scrollAmount = container.querySelector('.carousel-item')?.offsetWidth + 24 || 250;

            if (prevBtn) {
                prevBtn.addEventListener('click', function() {
                    container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
                });
            }

            if (nextBtn) {
                nextBtn.addEventListener('click', function() {
                    container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
                });
            }

            let isDown = false;
            let startX;
            let scrollLeft;

            container.addEventListener('mousedown', function(e) {
                isDown = true;
                container.style.cursor = 'grabbing';
                startX = e.pageX - container.offsetLeft;
                scrollLeft = container.scrollLeft;
            });

            container.addEventListener('mouseleave', function() {
                isDown = false;
                container.style.cursor = 'grab';
            });

            container.addEventListener('mouseup', function() {
                isDown = false;
                container.style.cursor = 'grab';
            });

            container.addEventListener('mousemove', function(e) {
                if (!isDown) return;
                e.preventDefault();
                const x = e.pageX - container.offsetLeft;
                const walk = (x - startX) * 2;
                container.scrollLeft = scrollLeft - walk;
            });

            container.style.cursor = 'grab';

            let touchStartX = 0;
            let touchScrollLeft = 0;

            container.addEventListener('touchstart', function(e) {
                touchStartX = e.touches[0].pageX - container.offsetLeft;
                touchScrollLeft = container.scrollLeft;
            }, { passive: true });

            container.addEventListener('touchmove', function(e) {
                const x = e.touches[0].pageX - container.offsetLeft;
                const walk = (x - touchStartX) * 1.5;
                container.scrollLeft = touchScrollLeft - walk;
            }, { passive: true });
        });
    }

    function initModals() {
        const modal = document.getElementById('trailerModal');
        if (!modal) return;

        const closeBtn = modal.querySelector('.modal-close');

        if (closeBtn) {
            closeBtn.addEventListener('click', closeTrailerModal);
        }

        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeTrailerModal();
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                closeTrailerModal();
            }
        });

        window.openTrailerModal = function(videoId) {
            const iframe = document.getElementById('trailerIframe');
            if (iframe) {
                iframe.src = 'https://www.youtube.com/embed/' + videoId + '?autoplay=1&rel=0';
            }
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            document.body.style.overflow = 'hidden';
            
            if (window.gsap) {
                gsap.fromTo(modal, 
                    { opacity: 0 }, 
                    { opacity: 1, duration: 0.3, ease: 'power2.out' }
                );
                gsap.fromTo(modal.querySelector('.modal-content'),
                    { scale: 0.95, opacity: 0 },
                    { scale: 1, opacity: 1, duration: 0.3, ease: 'power2.out' }
                );
            }
        };

        window.closeTrailerModal = function() {
            const iframe = document.getElementById('trailerIframe');
            if (iframe) {
                iframe.src = '';
            }
            
            if (window.gsa ? false : true) {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            } else {
                gsap.to(modal, {
                    opacity: 0,
                    duration: 0.2,
                    ease: 'power2.in',
                    onComplete: function() {
                        modal.classList.add('hidden');
                        modal.classList.remove('flex');
                        modal.style.opacity = '';
                    }
                });
            }
            
            document.body.style.overflow = '';
        };
    }

    function initSearchAutocomplete() {
        const searchInput = document.getElementById('movieSearchInput');
        if (!searchInput) return;

        let debounceTimer;

        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function() {
                const value = searchInput.value.trim();
                if (value.length > 0) {
                    searchInput.parentElement.classList.add('searching');
                } else {
                    searchInput.parentElement.classList.remove('searching');
                }
            }, 300);
        });

        searchInput.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
            if (window.gsap) {
                gsap.to(this, { scale: 1.02, duration: 0.2, ease: 'power2.out' });
            }
        });

        searchInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
            if (window.gsap) {
                gsap.to(this, { scale: 1, duration: 0.2, ease: 'power2.out' });
            }
        });

        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const form = document.getElementById('movieSearchForm');
                if (form) form.submit();
            }
        });

        document.querySelectorAll('.chip').forEach(function(chip) {
            chip.addEventListener('click', function() {
                if (searchInput) {
                    searchInput.value = this.textContent.trim();
                    searchInput.focus();
                }
            });
        });
    }

    function initCounters() {
        const counters = document.querySelectorAll('.metric-value');
        if (counters.length === 0) return;

        const animateCounter = function(el) {
            const text = el.textContent;
            const match = text.match(/([\d.]+)/);

            if (!match) return;

            const target = parseFloat(match[1]);
            const suffix = text.replace(match[1], '');
            const duration = 2000;
            const startTime = performance.now();

            function update(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeProgress = 1 - Math.pow(1 - progress, 3);
                const current = target * easeProgress;

                el.textContent = current.toFixed(1) + suffix;

                if (progress < 1) {
                    requestAnimationFrame(update);
                }
            }

            requestAnimationFrame(update);
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(function(counter) {
            observer.observe(counter);
        });
    }

    function initToast() {
        window.showToast = function(message, type) {
            const container = document.getElementById('toast-container');
            if (!container) return;

            const toast = document.createElement('div');
            toast.className = 'toast ' + (type || 'success');
            toast.style.cssText = 'padding:1rem 1.5rem;background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:12px;color:var(--text-primary);font-weight:500;box-shadow:0 16px 48px rgba(0,0,0,0.5);animation:toast-in 0.3s ease;display:flex;align-items:center;gap:0.75rem;';

            const iconClass = type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle';
            const iconColor = type === 'error' ? '#ff2d55' : '#10b981';
            toast.innerHTML = '<i class="fas ' + iconClass + '" style="color:' + iconColor + ';"></i><span>' + message + '</span>';

            container.appendChild(toast);

            setTimeout(function() {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                setTimeout(function() {
                    toast.remove();
                }, 300);
            }, 4000);
        };
    }

    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
                const searchInput = document.getElementById('movieSearchInput');
                if (searchInput && document.activeElement !== searchInput) {
                    e.preventDefault();
                    searchInput.focus();
                }
            }

            if (e.key === 'Escape') {
                const modal = document.getElementById('trailerModal');
                if (modal && !modal.classList.contains('hidden')) {
                    closeTrailerModal();
                }
            }
        });
    }

    function initHoverEffects() {
        document.querySelectorAll('.movie-card').forEach(function(card) {
            card.addEventListener('mouseenter', function() {
                const poster = this.querySelector('.poster-wrapper img');
                if (poster && window.gsap) {
                    gsap.to(poster, { scale: 1.1, duration: 0.5, ease: 'power2.out' });
                }
            });

            card.addEventListener('mouseleave', function() {
                const poster = this.querySelector('.poster-wrapper img');
                if (poster && window.gsap) {
                    gsap.to(poster, { scale: 1, duration: 0.5, ease: 'power2.out' });
                }
            });
        });

        document.querySelectorAll('.toggle-btn, .switch-btn').forEach(function(btn) {
            btn.addEventListener('mouseenter', function() {
                if (window.gsap) {
                    gsap.to(this, { scale: 1.05, duration: 0.2, ease: 'power2.out' });
                }
            });

            btn.addEventListener('mouseleave', function() {
                if (window.gtap) return;
                this.style.transform = '';
            });
        });

        document.querySelectorAll('.btn-cta, .search-btn').forEach(function(btn) {
            btn.addEventListener('mouseenter', function() {
                if (window.gsap) {
                    gsap.to(this, { y: -2, boxShadow: '0 12px 40px rgba(255,45,85,0.5)', duration: 0.2, ease: 'power2.out' });
                }
            });

            btn.addEventListener('mouseleave', function() {
                if (window.gsap) {
                    gsap.to(this, { y: 0, boxShadow: '', duration: 0.2, ease: 'power2.out' });
                }
            });
        });

        document.querySelectorAll('.feature-card, .insight-card').forEach(function(card) {
            card.addEventListener('mouseenter', function() {
                if (window.gsap) {
                    gsap.to(this, { y: -4, duration: 0.3, ease: 'power2.out' });
                }
            });

            card.addEventListener('mouseleave', function() {
                if (window.gsap) {
                    gsap.to(this, { y: 0, duration: 0.3, ease: 'power2.out' });
                }
            });
        });

        const socialIcons = document.querySelectorAll('.social-icon, .btn-ghost-nav');
        socialIcons.forEach(function(icon) {
            icon.addEventListener('mouseenter', function() {
                if (window.gsap) {
                    gsap.to(this, { scale: 1.1, duration: 0.2, ease: 'back.out(1.7)' });
                }
            });

            icon.addEventListener('mouseleave', function() {
                if (window.gsap) {
                    gsap.to(this, { scale: 1, duration: 0.2, ease: 'power2.out' });
                }
            });
        });
    }

    window.addEventListener('scroll', function() {
        const reveals = document.querySelectorAll('.reveal-on-scroll, [data-aos]');
        
        reveals.forEach(function(el) {
            const windowHeight = window.innerHeight;
            const elementTop = el.getBoundingClientRect().top;
            const revealPoint = 150;

            if (elementTop < windowHeight - revealPoint) {
                el.classList.add('revealed');
            }
        });

        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-link');

        let currentSection = '';
        sections.forEach(function(section) {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 200) {
                currentSection = section.getAttribute('id');
            }
        });

        navLinks.forEach(function(link) {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + currentSection) {
                link.classList.add('active');
            }
        });
    });

    window.addEventListener('resize', function() {
        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
        if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
            ScrollTrigger.refresh();
        }
    });

    window.addEventListener('popstate', function() {
        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
    });

    const style = document.createElement('style');
    style.textContent = `
        .reveal-on-scroll {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.8s ease-out;
        }
        .reveal-on-scroll.revealed {
            opacity: 1;
            transform: translateY(0);
        }
        @keyframes toast-in {
            from { opacity: 0; transform: translateX(100%); }
            to { opacity: 1; transform: translateX(0); }
        }
        .movie-card { overflow: hidden; }
        .movie-card .poster-wrapper img { will-change: transform; }
        .glass-panel { backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
    `;
    document.head.appendChild(style);

    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
    }

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (prefersReducedMotion.matches) {
        document.documentElement.style.setProperty('--transition-base', '0ms');
        document.documentElement.style.setProperty('--transition-smooth', '0ms');
    }

    window.addEventListener('error', function(e) {
        console.warn('Script error:', e.message);
    });

})();