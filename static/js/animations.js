// GSAP Animations
document.addEventListener('DOMContentLoaded', () => {
    if (typeof window.gsap === 'undefined') return;
    
    if (typeof window.ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    }

    // Анимация хедера
    gsap.from("header", { y: -20, opacity: 0, duration: 0.6, ease: "power2.out", clearProps: "all" });

    // Анимация логотипа (только на главной странице)
    const logoSvg = document.getElementById('logo-svg');
    const isHomePage = window.location.pathname === '/' || window.location.pathname === '/home/' || window.location.pathname === '';
    
    if (logoSvg && isHomePage) {
        const hammer = document.getElementById('logo-hammer');
        const letters = document.querySelectorAll('.logo-letter');
        
        if (hammer && letters.length > 0) {
            const logoTl = gsap.timeline({ delay: 0.5 });
            
            // Скрываем буквы в начале
            gsap.set(letters, { opacity: 0, scale: 0, transformOrigin: "center center" });
            
            // Анимация молотка: замах и удар
            logoTl.fromTo(hammer, 
                { rotation: -60, x: -20, opacity: 0, transformOrigin: "20% 90%" }, 
                { rotation: 0, x: 0, opacity: 1, duration: 0.6, ease: "power3.out" }
            )
            .to(hammer, { rotation: -30, duration: 0.3, ease: "power1.inOut" })
            .to(hammer, { rotation: 0, duration: 0.15, ease: "power2.in" })
            
            // Эффект удара (встряска)
            .to(logoSvg, { x: 1, y: 1, duration: 0.05, repeat: 5, yoyo: true })
            
            // Появление букв по очереди
            .to(letters, { 
                opacity: 1, 
                scale: 1, 
                duration: 0.4, 
                stagger: 0.07, 
                ease: "back.out(2)" 
            }, "-=0.2");
        }
    }
    
    // Скролл-анимации для секций
    gsap.utils.toArray('.section-reveal').forEach(section => {
        gsap.to(section, {
            y: 0,
            opacity: 1,
            duration: 1.2,
            ease: "expo.out",
            force3D: true,
            scrollTrigger: {
                trigger: section,
                start: "top 90%",
                toggleActions: "play none none none"
            }
        });
    });
    
    // Скролл-анимации для Bento-карточек
    gsap.utils.toArray('.bento-card').forEach((card, i) => {
        gsap.to(card, {
            y: 0,
            opacity: 1,
            duration: 1.4,
            delay: i * 0.1,
            ease: "expo.out",
            force3D: true,
            scrollTrigger: {
                trigger: card,
                start: "top 95%",
                toggleActions: "play none none none"
            }
        });
    });

    // Скролл-анимации для преимуществ
    gsap.utils.toArray('.highlight-card').forEach(card => {
        gsap.from(card, {
            y: 30,
            opacity: 0,
            duration: 0.6,
            ease: "power2.out",
               force3D: true,
            scrollTrigger: {
                trigger: card,
                start: "top 90%",
                toggleActions: "play none none none"
            }
        });
    });

    // Анимации для карточек товаров (product_list.html / favorites_list.html)
    const productCards = document.querySelectorAll('.grid > .group');
    if (productCards.length > 0) {
        if (typeof ScrollTrigger !== 'undefined') {
            ScrollTrigger.batch(productCards, {
                onEnter: batch => gsap.from(batch, { y: 50, opacity: 0, duration: 0.6, stagger: 0.1, ease: "power3.out", clearProps: "all" }),
                once: true
            });
        } else {
            gsap.from(productCards, { y: 30, opacity: 0, duration: 0.5, stagger: 0.1, ease: "power2.out", delay: 0.1, clearProps: "all" });
        }
    }

    // Анимации для детальной страницы товара (product_detail.html)
    const detailCols = document.querySelectorAll('.container.grid.lg\\:grid-cols-2 > div');
    if (detailCols.length > 0) {
        gsap.from(detailCols, { 
            y: 30, 
            opacity: 0, 
            duration: 0.8, 
            stagger: 0.2, 
            ease: "power3.out", 
            clearProps: "all",
            scrollTrigger: typeof ScrollTrigger !== 'undefined' ? {
                trigger: detailCols[0].parentElement,
                start: "top 85%"
            } : null
        });
    }

    // Анимации для страницы корзины (cart.html)
    const cartCols = document.querySelectorAll('.container.lg\\:grid.lg\\:grid-cols-\\[1fr_400px\\] > div');
    if (cartCols.length > 0) {
        gsap.from(cartCols, { 
            y: 30, 
            opacity: 0, 
            duration: 0.8, 
            stagger: 0.2, 
            ease: "power3.out", 
            clearProps: "all",
            scrollTrigger: typeof ScrollTrigger !== 'undefined' ? {
                trigger: cartCols[0].parentElement,
                start: "top 85%"
            } : null
        });
    }

    // Ensure hero interactive container uses preserve-3d
    gsap.set('#hero-interactive, #float-card', { transformStyle: 'preserve-3d' });

    // Refresh ScrollTrigger after images load to fix incorrect trigger positions
    if (typeof ScrollTrigger !== 'undefined') {
        window.addEventListener('load', () => {
            ScrollTrigger.refresh();
        });
    }

});

// Экспортируем функции для использования в других файлах (например, base.js)
window.AppAnimations = {
    favoriteAdd: function(btn, e) {
        if (typeof window.gsap === 'undefined') return;
        
        const icon = btn.querySelector('.favorite-icon');
        if (!icon) return;

        // Расчет координат клика относительно иконки
        const rect = icon.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const tl = gsap.timeline();
        
        // 1. Устанавливаем начальный clip-path (невидимый круг в точке клика)
        gsap.set(icon, { 
            clipPath: `circle(0% at ${x}px ${y}px)`,
            webkitClipPath: `circle(0% at ${x}px ${y}px)`
        });

        // 2. Анимация заполнения (радиальное расширение) + Пружинистость
        tl.to(icon, { 
            clipPath: `circle(150% at ${x}px ${y}px)`,
            webkitClipPath: `circle(150% at ${x}px ${y}px)`,
            duration: 0.6, 
            ease: "power2.out"
        })
        .to(icon, { 
            scale: 1.3, 
            duration: 0.2, 
            ease: "back.out(2)" 
        }, 0)
        .to(icon, { 
            scale: 1, 
            duration: 0.5, 
            ease: "elastic.out(1.2, 0.4)",
            clearProps: "clip-path,webkit-clip-path" // Очищаем после анимации
        }, 0.2);

        // 3. Эффект вспышки
        this.createBurst(icon);
    },

    favoriteRemove: function(icon) {
        if (typeof window.gsap === 'undefined') return;
        
        gsap.to(icon, { 
            scale: 0.7, 
            opacity: 0.5,
            duration: 0.15, 
            onComplete: () => {
                gsap.to(icon, { 
                    scale: 1, 
                    opacity: 1,
                    duration: 0.25, 
                    ease: "power2.out" 
                });
            }
        });
    },

    favoriteCardRemove: function(card) {
        if (typeof window.gsap === 'undefined') {
            card.remove();
            return;
        }
        gsap.to(card, { 
            scale: 0.8, 
            opacity: 0, 
            duration: 0.4, 
            ease: "power2.in",
            onComplete: () => card.remove() 
        });
    },

    createBurst: function(el) {
        const rect = el.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2 + window.scrollX;
        const centerY = rect.top + rect.height / 2 + window.scrollY;
        const particlesCount = 8;
        const colors = ['#f59e0b', '#fbbf24', '#f97316', '#fb7185'];

        for (let i = 0; i < particlesCount; i++) {
            const particle = document.createElement('div');
            const size = Math.random() * 6 + 4;
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            Object.assign(particle.style, {
                position: 'absolute',
                left: `${centerX}px`,
                top: `${centerY}px`,
                width: `${size}px`,
                height: `${size}px`,
                backgroundColor: color,
                borderRadius: '50%',
                pointerEvents: 'none',
                zIndex: '9999',
                transform: 'translate(-50%, -50%)'
            });

            document.body.appendChild(particle);

            const angle = (i / particlesCount) * Math.PI * 2;
            const velocity = Math.random() * 60 + 40;
            const x = Math.cos(angle) * velocity;
            const y = Math.sin(angle) * velocity;

            gsap.to(particle, {
                x: x,
                y: y,
                opacity: 0,
                scale: 0,
                duration: Math.random() * 0.5 + 0.5,
                ease: "power2.out",
                onComplete: () => particle.remove()
            });
        }
    }
};
