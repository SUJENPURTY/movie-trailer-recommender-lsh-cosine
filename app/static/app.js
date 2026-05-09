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
        initCarousels();
        initModals();
        initSearchAutocomplete();
        initCounters();
        initSmoothScroll();
        initToast();
    }

    function initLoader() {
        const loader = document.getElementById('loader');
        if (!loader) return;

        window.addEventListener('load', function() {
            setTimeout(function() {
                loader.classList.add('hidden');
                document.body.style.overflow = 'auto';
            }, 800);
        });

        if (document.readyState === 'complete') {
            setTimeout(function() {
                loader.classList.add('hidden');
            }, 500);
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

            lastScroll = currentScroll;
        });

        document.querySelectorAll('.nav-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        const offset = 80;
                        const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
                        window.scrollTo({ top: top, behavior: 'smooth' });
                    }
                }
            });
        });
    }

    function initMouseGlow() {
        const glow = document.createElement('div');
        glow.className = 'mouse-glow';
        glow.style.display = 'none';
        document.body.appendChild(glow);

        document.addEventListener('mousemove', function(e) {
            if (e.target.closest('.navbar, .btn-cta, .movie-card, .toggle-btn, .switch-btn')) {
                glow.style.display = 'block';
                glow.style.left = e.clientX + 'px';
                glow.style.top = e.clientY + 'px';
            }
        });

        document.addEventListener('mouseout', function(e) {
            if (e.relatedTarget === null) {
                glow.style.display = 'none';
            }
        });
    }

    function initParticles() {
        const container = document.getElementById('particles');
        if (!container) return;

        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 15 + 's';
            particle.style.animationDuration = (15 + Math.random() * 10) + 's';
            container.appendChild(particle);
        }
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
                AOS.refresh();
            });
        }
    }

    function initGSAP() {
        if (typeof gsap !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);

            gsap.utils.toArray('.hero-title').forEach(function(el) {
                gsap.from(el, {
                    scrollTrigger: {
                        trigger: el,
                        start: 'top 80%'
                    },
                    y: 50,
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
                    y: 30,
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
                    y: 40,
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
        }
    }

    function initCarousels() {
        document.querySelectorAll('.carousel-section').forEach(function(section) {
            const container = section.querySelector('.carousel-container');
            const prevBtn = section.querySelector('.carousel-nav.prev');
            const nextBtn = section.querySelector('.carousel-nav.next');

            if (!container || !prevBtn || !nextBtn) return;

            const scrollAmount = 250;

            prevBtn.addEventListener('click', function() {
                container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
            });

            nextBtn.addEventListener('click', function() {
                container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            });

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
        });
    }

    function initModals() {
        const modal = document.getElementById('trailerModal');
        if (!modal) return;

        const closeBtn = modal.querySelector('.modal-close');

        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal);
        }

        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                closeModal();
            }
        });

        window.openTrailerModal = function(videoId) {
            const iframe = modal.querySelector('iframe');
            if (iframe) {
                iframe.src = 'https://www.youtube.com/embed/' + videoId + '?autoplay=1';
            }
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        };

        window.closeTrailerModal = closeModal;

        function closeModal() {
            const iframe = modal.querySelector('iframe');
            if (iframe) {
                iframe.src = '';
            }
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
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
        });

        searchInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
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
                    window.scrollTo({ top: top, behavior: 'smooth' });
                }
            });
        });
    }

    function initToast() {
        window.showToast = function(message, type) {
            const container = document.getElementById('toast-container');
            if (!container) return;

            const toast = document.createElement('div');
            toast.className = 'toast ' + (type || 'success');

            const iconClass = type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle';
            toast.innerHTML = '<i class="fas ' + iconClass + '"></i><span>' + message + '</span>';

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

    window.addEventListener('scroll', function() {
        const reveals = document.querySelectorAll('.reveal-on-scroll');
        
        reveals.forEach(function(el) {
            const windowHeight = window.innerHeight;
            const elementTop = el.getBoundingClientRect().top;
            const revealPoint = 150;

            if (elementTop < windowHeight - revealPoint) {
                el.classList.add('revealed');
            }
        });
    });

    window.addEventListener('resize', function() {
        if (typeof AOS !== 'undefined') {
            AOS.refresh();
        }
    });

    document.addEventListener('click', function(e) {
        const movieCards = document.querySelectorAll('.movie-card');
        movieCards.forEach(function(card) {
            if (card.contains(e.target) && !e.target.closest('a') && !e.target.closest('button')) {
                card.classList.add('active');
                setTimeout(function() {
                    card.classList.remove('active');
                }, 300);
            }
        });
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
        .movie-card.active {
            transform: scale(0.98);
        }
    `;
    document.head.appendChild(style);

})();