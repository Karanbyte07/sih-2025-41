/**
 * ============================================
 * CMLRE Ocean Intelligence Platform
 * Ocean Effects & Animations JavaScript
 * ============================================
 */

class OceanEffects {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.startAnimations();
    }

    init() {
        this.isAnimating = true;
        this.particles = [];
        this.waves = [];
        this.bubbles = document.querySelectorAll('.bubble');
        this.createOceanParticles();
        this.initializeScrollAnimations();
    }

    /**
     * Create floating ocean particles
     */
    createOceanParticles() {
        const particleContainer = document.querySelector('.ocean-particles');
        if (!particleContainer) return;

        // Create additional bubbles dynamically
        for (let i = 0; i < 8; i++) {
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.style.cssText = `
                width: ${Math.random() * 10 + 5}px;
                height: ${Math.random() * 10 + 5}px;
                left: ${Math.random() * 100}%;
                animation-delay: ${Math.random() * 8}s;
                animation-duration: ${Math.random() * 6 + 8}s;
            `;
            particleContainer.appendChild(bubble);
        }

        // Create current particles
        this.createCurrentParticles();
    }

    /**
     * Create flowing current particles
     */
    createCurrentParticles() {
        const body = document.body;
        
        setInterval(() => {
            if (!this.isAnimating) return;
            
            const particle = document.createElement('div');
            particle.className = 'current-particle';
            particle.style.cssText = `
                top: ${Math.random() * window.innerHeight}px;
                left: -10px;
                animation-delay: 0s;
                animation-duration: ${Math.random() * 4 + 8}s;
            `;
            
            body.appendChild(particle);
            
            // Remove particle after animation
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 12000);
        }, 3000);
    }

    /**
     * Initialize scroll-based animations
     */
    initializeScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, observerOptions);

        // Observe elements with reveal-on-scroll class
        document.querySelectorAll('.reveal-on-scroll').forEach(el => {
            observer.observe(el);
        });

        // Staggered animations for cards
        this.setupStaggeredAnimations();
    }

    /**
     * Setup staggered animations for card elements
     */
    setupStaggeredAnimations() {
        const cards = document.querySelectorAll('.ocean-card, .stat-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('animate-fade-in');
        });
    }

    /**
     * Setup event listeners for interactive effects
     */
    setupEventListeners() {
        // Button click ripple effects
        this.setupRippleEffects();
        
        // Card hover effects
        this.setupCardHoverEffects();
        
        // Scroll effects
        this.setupScrollEffects();
        
        // Resize handling
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    /**
     * Setup ripple effects for buttons
     */
    setupRippleEffects() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-primary, .btn-secondary')) {
                this.createRipple(e);
            }
        });
    }

    /**
     * Create ripple effect on button click
     */
    createRipple(event) {
        const button = event.target.closest('.btn-primary, .btn-secondary');
        if (!button) return;

        const ripple = button.querySelector('.btn-ripple');
        if (!ripple) return;

        const rect = button.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        ripple.style.width = '0';
        ripple.style.height = '0';

        // Trigger animation
        requestAnimationFrame(() => {
            ripple.style.width = '300px';
            ripple.style.height = '300px';
        });

        // Reset after animation
        setTimeout(() => {
            ripple.style.width = '0';
            ripple.style.height = '0';
        }, 600);
    }

    /**
     * Setup hover effects for cards
     */
    setupCardHoverEffects() {
        const cards = document.querySelectorAll('.ocean-card, .stat-card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.addFloatingEffect(card);
            });
            
            card.addEventListener('mouseleave', () => {
                this.removeFloatingEffect(card);
            });
        });
    }

    /**
     * Add floating effect to element
     */
    addFloatingEffect(element) {
        element.style.transform = 'translateY(-8px)';
        element.style.boxShadow = '0 20px 40px rgba(30, 64, 175, 0.15)';
    }

    /**
     * Remove floating effect from element
     */
    removeFloatingEffect(element) {
        element.style.transform = 'translateY(0)';
        element.style.boxShadow = '';
    }

    /**
     * Setup scroll-based effects
     */
    setupScrollEffects() {
        let ticking = false;

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.updateScrollEffects();
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    /**
     * Update scroll-based effects
     */
    updateScrollEffects() {
        const scrollY = window.scrollY;
        const windowHeight = window.innerHeight;

        // Parallax effect for hero section
        const hero = document.querySelector('.ocean-hero');
        if (hero) {
            const offset = scrollY * 0.5;
            hero.style.transform = `translateY(${offset}px)`;
        }

        // Wave animation disabled - waves stay static
        // const waves = document.querySelectorAll('.wave-path');
        // waves.forEach(wave => {
        //     const speed = Math.max(0.5, 1 - scrollY / windowHeight);
        //     wave.style.animationDuration = `${6 / speed}s`;
        // });
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Recalculate particle positions
        this.repositionParticles();
    }

    /**
     * Reposition particles on resize
     */
    repositionParticles() {
        const bubbles = document.querySelectorAll('.bubble');
        bubbles.forEach(bubble => {
            bubble.style.left = `${Math.random() * 100}%`;
        });
    }

    /**
     * Start continuous animations
     */
    startAnimations() {
        this.animateWaves();
        this.animateCompass();
        this.setupLoadingAnimations();
    }

    /**
     * Animate wave elements - DISABLED
     */
    animateWaves() {
        // Wave animation disabled - waves stay static
        // const waves = document.querySelectorAll('.wave-path');
        // waves.forEach((wave, index) => {
        //     wave.style.animationDelay = `${index * 0.5}s`;
        // });
    }

    /**
     * Animate compass rotation
     */
    animateCompass() {
        const compass = document.querySelector('.compass');
        if (compass) {
            let rotation = 0;
            const rotateCompass = () => {
                rotation += 0.5;
                compass.style.transform = `rotate(${rotation}deg)`;
                if (this.isAnimating) {
                    requestAnimationFrame(rotateCompass);
                }
            };
            rotateCompass();
        }
    }

    /**
     * Setup loading animations
     */
    setupLoadingAnimations() {
        // Create loading spinner component
        this.createLoadingSpinner();
        
        // Setup skeleton loaders
        this.setupSkeletonLoaders();
    }

    /**
     * Create animated loading spinner
     */
    createLoadingSpinner() {
        const style = document.createElement('style');
        style.textContent = `
            .ocean-loading {
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            
            .ocean-loading::after {
                content: '';
                width: 20px;
                height: 20px;
                border: 3px solid rgba(59, 130, 246, 0.3);
                border-top: 3px solid #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Setup skeleton loading effects
     */
    setupSkeletonLoaders() {
        const skeletons = document.querySelectorAll('.skeleton');
        skeletons.forEach(skeleton => {
            skeleton.style.background = `
                linear-gradient(90deg, 
                    rgba(240, 249, 255, 0.8) 25%, 
                    rgba(219, 234, 254, 0.8) 50%, 
                    rgba(240, 249, 255, 0.8) 75%)
            `;
            skeleton.style.backgroundSize = '200px 100%';
            skeleton.style.animation = 'shimmer 1.5s infinite';
        });
    }

    /**
     * Show loading state
     */
    showLoading(element, text = 'Loading...') {
        const loadingHTML = `
            <div class="ocean-loading">
                <span>${text}</span>
            </div>
        `;
        element.innerHTML = loadingHTML;
    }

    /**
     * Hide loading state
     */
    hideLoading(element, content) {
        element.innerHTML = content;
    }

    /**
     * Create typewriter effect
     */
    typeWriter(element, text, speed = 50) {
        let i = 0;
        element.innerHTML = '';
        
        const typing = () => {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(typing, speed);
            }
        };
        
        typing();
    }

    /**
     * Create count-up animation for numbers
     */
    countUp(element, target, duration = 2000) {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }

    /**
     * Pause all animations
     */
    pauseAnimations() {
        this.isAnimating = false;
        document.body.style.animationPlayState = 'paused';
    }

    /**
     * Resume all animations
     */
    resumeAnimations() {
        this.isAnimating = true;
        document.body.style.animationPlayState = 'running';
    }

    /**
     * Toggle animations based on performance
     */
    toggleAnimationsForPerformance() {
        // Check if device prefers reduced motion
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        if (prefersReducedMotion) {
            this.pauseAnimations();
        } else {
            this.resumeAnimations();
        }
    }

    /**
     * Cleanup method
     */
    destroy() {
        this.pauseAnimations();
        
        // Remove event listeners
        window.removeEventListener('scroll', this.updateScrollEffects);
        window.removeEventListener('resize', this.handleResize);
        
        // Clear particles
        const particles = document.querySelectorAll('.current-particle');
        particles.forEach(particle => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        });
    }
}

// Utility functions for ocean effects
const OceanUtils = {
    /**
     * Generate random ocean color
     */
    getRandomOceanColor() {
        const colors = [
            '#1E40AF', '#3B82F6', '#60A5FA', '#0EA5E9', '#06B6D4'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    },

    /**
     * Create wave path data
     */
    generateWavePath(width, height, amplitude = 20, frequency = 2) {
        let path = `M0,${height}`;
        
        for (let x = 0; x <= width; x += 10) {
            const y = height + Math.sin((x / width) * frequency * Math.PI) * amplitude;
            path += ` L${x},${y}`;
        }
        
        path += ` L${width},${height + 100} L0,${height + 100} Z`;
        return path;
    },

    /**
     * Calculate distance between two points
     */
    distance(x1, y1, x2, y2) {
        return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    },

    /**
     * Linear interpolation
     */
    lerp(start, end, factor) {
        return start + (end - start) * factor;
    },

    /**
     * Easing function
     */
    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
    }
};

// Initialize ocean effects when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on the ocean platform page
    if (document.querySelector('.ocean-bg')) {
        window.oceanEffects = new OceanEffects();
        
        // Performance monitoring
        if ('requestIdleCallback' in window) {
            requestIdleCallback(() => {
                window.oceanEffects.toggleAnimationsForPerformance();
            });
        }
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { OceanEffects, OceanUtils };
}