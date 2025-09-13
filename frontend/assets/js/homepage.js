/**
 * ============================================
 * Homepage Controller JavaScript
 * Enhanced Navigation & Hero Interactions
 * ============================================
 */

class HomepageController {
    constructor() {
        this.navbar = document.getElementById('navbar');
        this.mobileMenuBtn = document.getElementById('mobile-menu-btn');
        this.mobileMenu = document.getElementById('mobile-menu');
        this.particlesContainer = document.getElementById('particles-container');
        
        this.init();
    }

    /**
     * Initialize homepage functionality
     */
    init() {
        this.setupNavigationScroll();
        this.setupMobileMenu();
        this.animateStatistics();
        this.createFloatingParticles();
        this.setupScrollAnimations();
        this.setupButtonEffects();
    }

    /**
     * Setup navigation scroll effects
     */
    setupNavigationScroll() {
        let lastScroll = 0;
        
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            // Change navbar appearance on scroll
            if (currentScroll > 100) {
                this.navbar.classList.add('scrolled');
                this.navbar.style.background = 'rgba(255, 255, 255, 0.98)';
                this.navbar.style.backdropFilter = 'blur(20px)';
                this.navbar.style.borderBottom = '1px solid rgba(59, 130, 246, 0.1)';
            } else {
                this.navbar.classList.remove('scrolled');
                this.navbar.style.background = 'rgba(255, 255, 255, 0.95)';
                this.navbar.style.backdropFilter = 'blur(10px)';
                this.navbar.style.borderBottom = '1px solid rgba(59, 130, 246, 0.1)';
            }
            
            // Hide/show navbar on scroll
            if (currentScroll > lastScroll && currentScroll > 200) {
                this.navbar.style.transform = 'translateY(-100%)';
            } else {
                this.navbar.style.transform = 'translateY(0)';
            }
            
            lastScroll = currentScroll;
        });
    }

    /**
     * Setup mobile menu functionality
     */
    setupMobileMenu() {
        if (!this.mobileMenuBtn || !this.mobileMenu) return;

        this.mobileMenuBtn.addEventListener('click', () => {
            this.toggleMobileMenu();
        });

        // Close mobile menu when clicking nav links
        const mobileNavLinks = this.mobileMenu.querySelectorAll('a');
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.closeMobileMenu();
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.navbar.contains(e.target)) {
                this.closeMobileMenu();
            }
        });
    }

    /**
     * Toggle mobile menu
     */
    toggleMobileMenu() {
        const isOpen = !this.mobileMenu.classList.contains('hidden');
        
        if (isOpen) {
            this.closeMobileMenu();
        } else {
            this.openMobileMenu();
        }
    }

    /**
     * Open mobile menu
     */
    openMobileMenu() {
        this.mobileMenu.classList.remove('hidden');
        this.mobileMenuBtn.classList.add('active');
        
        // Animate menu items
        const menuItems = this.mobileMenu.querySelectorAll('.mobile-nav-link');
        menuItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                item.style.transition = 'all 0.3s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }

    /**
     * Close mobile menu
     */
    closeMobileMenu() {
        this.mobileMenu.classList.add('hidden');
        this.mobileMenuBtn.classList.remove('active');
    }

    /**
     * Animate statistics counter
     */
    animateStatistics() {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        const animateCounter = (element, target) => {
            const duration = 2000; // 2 seconds
            const steps = 60;
            const increment = target / steps;
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                
                // Format number based on target
                let displayValue;
                if (target >= 10000) {
                    displayValue = (current / 1000).toFixed(1) + 'K';
                } else if (target >= 1000) {
                    displayValue = current.toFixed(0);
                } else {
                    displayValue = current.toFixed(0) + '%';
                }
                
                element.textContent = displayValue;
            }, duration / steps);
        };

        // Observe stats for animation trigger
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = parseInt(entry.target.dataset.count);
                    animateCounter(entry.target, target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        statNumbers.forEach(stat => {
            observer.observe(stat);
        });
    }

    /**
     * Create floating particles effect
     */
    createFloatingParticles() {
        if (!this.particlesContainer) return;

        const createParticle = () => {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Random size and position
            const size = Math.random() * 6 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.bottom = '-10px';
            
            // Random animation duration
            const duration = Math.random() * 6 + 8;
            particle.style.animationDuration = duration + 's';
            particle.style.animationDelay = Math.random() * 2 + 's';
            
            this.particlesContainer.appendChild(particle);
            
            // Remove particle after animation
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, (duration + 2) * 1000);
        };

        // Create particles periodically
        setInterval(createParticle, 300);
        
        // Create initial batch
        for (let i = 0; i < 10; i++) {
            setTimeout(createParticle, i * 200);
        }
    }

    /**
     * Setup scroll-triggered animations
     */
    setupScrollAnimations() {
        const animatedElements = document.querySelectorAll('.intro-card, .feature-highlight, .visual-card');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, { 
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        animatedElements.forEach((element, index) => {
            // Initial state
            element.style.opacity = '0';
            element.style.transform = 'translateY(40px)';
            element.style.transition = `all 0.8s ease ${index * 0.1}s`;
            
            observer.observe(element);
        });
    }

    /**
     * Setup button ripple effects
     */
    setupButtonEffects() {
        const rippleButtons = document.querySelectorAll('.btn-hero-primary, .btn-hero-secondary');
        
        rippleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const ripple = button.querySelector('.btn-ripple');
                if (ripple) {
                    ripple.style.width = '0';
                    ripple.style.height = '0';
                    
                    setTimeout(() => {
                        ripple.style.width = '300px';
                        ripple.style.height = '300px';
                        
                        setTimeout(() => {
                            ripple.style.width = '0';
                            ripple.style.height = '0';
                        }, 600);
                    }, 10);
                }
            });
        });

        // Add hover effects to all buttons
        const allButtons = document.querySelectorAll('.btn-primary, .btn-hero-primary, .btn-hero-secondary, .btn-cta-primary, .btn-cta-secondary');
        
        allButtons.forEach(button => {
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'translateY(-2px)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = 'translateY(0)';
            });
        });
    }

    /**
     * Smooth scroll to section
     */
    scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            const offsetTop = section.offsetTop - 80; // Account for fixed navbar
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    }

    /**
     * Handle page visibility change
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // Pause animations when page is hidden
            this.pauseAnimations();
        } else {
            // Resume animations when page becomes visible
            this.resumeAnimations();
        }
    }

    /**
     * Pause animations
     */
    pauseAnimations() {
        const animatedElements = document.querySelectorAll('.wave-layer, .particle');
        animatedElements.forEach(element => {
            element.style.animationPlayState = 'paused';
        });
    }

    /**
     * Resume animations
     */
    resumeAnimations() {
        const animatedElements = document.querySelectorAll('.wave-layer, .particle');
        animatedElements.forEach(element => {
            element.style.animationPlayState = 'running';
        });
    }

    /**
     * Initialize live data updates (for demo)
     */
    initializeLiveData() {
        const dataValues = document.querySelectorAll('.data-value');
        
        setInterval(() => {
            dataValues.forEach(value => {
                const current = parseFloat(value.textContent);
                if (!isNaN(current)) {
                    const variation = (Math.random() - 0.5) * 0.2;
                    const newValue = (current + variation).toFixed(1);
                    value.textContent = newValue + (value.textContent.includes('°') ? '°C' : 
                                                   value.textContent.includes('PSU') ? ' PSU' : '');
                }
            });
        }, 3000);
    }

    /**
     * Add keyboard navigation
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // ESC key closes mobile menu
            if (e.key === 'Escape') {
                this.closeMobileMenu();
            }
            
            // Enter key on buttons triggers click
            if (e.key === 'Enter' && e.target.matches('button, .btn-primary, .btn-hero-primary, .btn-hero-secondary')) {
                e.target.click();
            }
        });
    }

    /**
     * Setup performance monitoring
     */
    setupPerformanceMonitoring() {
        // Monitor scroll performance
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            scrollTimeout = setTimeout(() => {
                // Perform any cleanup or optimization after scroll stops
                this.optimizeAnimations();
            }, 150);
        });
    }

    /**
     * Optimize animations based on performance
     */
    optimizeAnimations() {
        const isSlowDevice = window.devicePixelRatio < 1.5 || navigator.hardwareConcurrency < 4;
        
        if (isSlowDevice) {
            // Reduce animation complexity for slower devices
            const particles = document.querySelectorAll('.particle');
            if (particles.length > 20) {
                particles.forEach((particle, index) => {
                    if (index % 2 === 0) {
                        particle.remove();
                    }
                });
            }
        }
    }

    /**
     * Cleanup method
     */
    destroy() {
        // Remove event listeners and cleanup
        window.removeEventListener('scroll', this.setupNavigationScroll);
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        
        // Clear any intervals
        clearInterval(this.particleInterval);
        clearInterval(this.dataUpdateInterval);
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.homepageController = new HomepageController();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { HomepageController };
}