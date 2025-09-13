// Authentication & Session Management
class AuthManager {
    constructor() {
        this.init();
    }

    init() {
        // Check if user is logged in
        this.isLoggedIn = sessionStorage.getItem('isLoggedIn') === 'true';
        this.userEmail = sessionStorage.getItem('userEmail');
        this.loginTime = sessionStorage.getItem('loginTime');
    }

    // Login function
    login(email, password) {
        if (email === 'cmlre@gov.in' && password === '1234') {
            sessionStorage.setItem('isLoggedIn', 'true');
            sessionStorage.setItem('userEmail', email);
            sessionStorage.setItem('loginTime', new Date().toISOString());
            this.init(); // Refresh state
            return true;
        }
        return false;
    }

    // Logout function
    logout() {
        sessionStorage.clear();
        this.init(); // Refresh state
        window.location.href = 'login.html';
    }

    // Check if user is authenticated
    requireAuth() {
        if (!this.isLoggedIn) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    }

    // Get user info
    getUserInfo() {
        return {
            email: this.userEmail,
            loginTime: this.loginTime,
            isLoggedIn: this.isLoggedIn
        };
    }

    // Update navbar for authenticated users
    updateNavbar() {
        const navbar = document.getElementById('universal-navbar');
        if (!navbar) return;

        if (this.isLoggedIn) {
            // Update navigation links for authenticated users
            const desktopNav = navbar.querySelector('.desktop-nav');
            if (desktopNav && !desktopNav.querySelector('[data-page="dashboard"]')) {
                desktopNav.innerHTML = `
                    <a href="dashboard.html" class="nav-link" data-page="dashboard" style="--index: 1">
                        <i class="fas fa-tachometer-alt mr-2"></i>
                        Dashboard
                    </a>
                    <a href="about.html" class="nav-link" data-page="about" style="--index: 2">
                        About
                    </a>
                    <a href="features.html" class="nav-link" data-page="features" style="--index: 3">
                        Features
                    </a>
                `;
            }

            // Update CTA section for authenticated users
            const ctaSection = navbar.querySelector('.cta-section');
            if (ctaSection) {
                ctaSection.innerHTML = `
                    <div class="flex items-center gap-4">
                        <div class="hidden md:flex items-center gap-2 text-gray-700">
                            <i class="fas fa-user-circle text-blue-600"></i>
                            <span class="font-medium">${this.userEmail.split('@')[0]}</span>
                        </div>
                        <button onclick="authManager.logout()" class="btn-primary">
                            <i class="fas fa-sign-out-alt mr-2"></i>
                            Logout
                        </button>
                    </div>
                `;
            }

            // Update mobile menu for authenticated users
            const mobileMenu = navbar.querySelector('.mobile-nav-content');
            if (mobileMenu && !mobileMenu.querySelector('[data-page="dashboard"]')) {
                mobileMenu.innerHTML = `
                    <a href="dashboard.html" class="mobile-nav-link" data-page="dashboard">
                        <i class="fas fa-tachometer-alt mr-2"></i>
                        Dashboard
                    </a>
                    <a href="about.html" class="mobile-nav-link" data-page="about">
                        About
                    </a>
                    <a href="features.html" class="mobile-nav-link" data-page="features">
                        Features
                    </a>
                    <div class="mobile-cta">
                        <button onclick="authManager.logout()" class="btn-primary w-full">
                            <i class="fas fa-sign-out-alt mr-2"></i>
                            Logout
                        </button>
                    </div>
                `;
            }
        }
    }

    // Set active navigation link
    setActiveNavLink() {
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        const pageMapping = {
            'index.html': 'home',
            'dashboard.html': 'dashboard',
            'about.html': 'about',
            'features.html': 'features',
            'login.html': 'login'
        };
        
        const activePage = pageMapping[currentPage] || 'home';
        
        // Remove active class from all links
        document.querySelectorAll('.nav-link, .mobile-nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to current page links
        document.querySelectorAll(`[data-page="${activePage}"]`).forEach(link => {
            link.classList.add('active');
        });
    }
}

// Initialize global auth manager
window.authManager = new AuthManager();

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Update navbar based on auth state
    authManager.updateNavbar();
    
    // Set active nav link
    setTimeout(() => {
        authManager.setActiveNavLink();
    }, 100);
});

// Global logout function for compatibility
function logout() {
    authManager.logout();
}