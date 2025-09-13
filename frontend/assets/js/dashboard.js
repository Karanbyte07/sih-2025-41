/**
 * ============================================
 * CMLRE Ocean Intelligence Platform
 * Main Dashboard JavaScript
 * ============================================
 */

class OceanDashboard {
    constructor() {
        this.data = [];
        this.isLoading = false;
        this.apiBaseUrl = '/api';
        this.refreshInterval = 30000; // 30 seconds
        this.autoRefreshEnabled = true;
        
        this.init();
    }

    /**
     * Initialize dashboard
     */
    async init() {
        this.setupEventListeners();
        this.setupViewToggle();
        this.showLoadingState();
        
        try {
            await this.fetchDashboardData();
            this.startAutoRefresh();
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showErrorState('Failed to load dashboard data');
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Button click handlers
        const submitBtn = document.getElementById('submit-otolith');
        const refreshBtn = document.getElementById('refresh-data');
        const insightsBtn = document.getElementById('generate-insights');
        const sampleForm = document.getElementById('sample-form');

        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitNewSample());
        }

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        if (insightsBtn) {
            insightsBtn.addEventListener('click', () => this.generateInsights());
        }

        if (sampleForm) {
            sampleForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Settings and navigation
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.toggleSettings());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Visibility change handler for auto-refresh
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAutoRefresh();
            } else {
                this.resumeAutoRefresh();
            }
        });
    }

    /**
     * Setup view toggle functionality
     */
    setupViewToggle() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-view]')) {
                const view = e.target.dataset.view;
                this.switchView(view, e.target);
            }
        });
    }

    /**
     * Switch between map and list view
     */
    switchView(view, button) {
        // Update button states
        document.querySelectorAll('[data-view]').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        // Toggle containers
        const mapContainer = document.getElementById('map-container');
        const listContainer = document.getElementById('list-container');

        if (view === 'map') {
            mapContainer?.classList.remove('hidden');
            listContainer?.classList.add('hidden');
        } else {
            mapContainer?.classList.add('hidden');
            listContainer?.classList.remove('hidden');
        }

        // Add transition effect
        this.addViewTransition();
    }

    /**
     * Add smooth transition effect for view switching
     */
    addViewTransition() {
        const containers = document.querySelectorAll('#map-container, #list-container');
        containers.forEach(container => {
            container.style.opacity = '0';
            container.style.transform = 'translateY(20px)';
            
            requestAnimationFrame(() => {
                container.style.transition = 'all 0.3s ease';
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            });
        });
    }

    /**
     * Fetch dashboard data from API
     */
    async fetchDashboardData() {
        try {
            this.setLoadingState(true);
            
            const response = await fetch(`${this.apiBaseUrl}/dashboard/data`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.data = Array.isArray(data) ? data : [];
            
            this.renderDashboard();
            this.hideLoadingState();
            
            // Show success message
            this.showStatus('Dashboard data updated successfully', 'success');
            
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            this.hideLoadingState();
            this.showStatus('Failed to fetch dashboard data', 'error');
            
            // Use mock data for demo if API fails
            this.loadMockData();
        }
    }

    /**
     * Load mock data for demonstration
     */
    loadMockData() {
        this.data = [
            {
                image_id: 'sample-demo-001',
                predicted_species: 'Gadus morhua',
                area_px: 1234,
                perimeter_px: 156,
                width_px: 45,
                height_px: 38,
                aspect_ratio: '1.18',
                latitude: 12.45,
                longitude: 75.23,
                analysis_timestamp: new Date().toISOString()
            },
            {
                image_id: 'sample-demo-002',
                predicted_species: 'Salmo salar',
                area_px: 987,
                perimeter_px: 132,
                width_px: 38,
                height_px: 31,
                aspect_ratio: '1.23',
                latitude: 15.67,
                longitude: 73.89,
                analysis_timestamp: new Date(Date.now() - 300000).toISOString()
            }
        ];
        
        this.renderDashboard();
        this.showStatus('Using demo data', 'info');
    }

    /**
     * Render entire dashboard
     */
    renderDashboard() {
        this.updateStatistics();
        this.updateCharts();
        this.updateDataTable();
        this.updateActivityFeed();
    }

    /**
     * Update statistics cards
     */
    updateStatistics() {
        const totalSamples = this.data.length;
        const uniqueSpecies = new Set(
            this.data
                .map(d => d.predicted_species)
                .filter(s => s && s !== 'N/A' && s !== 'Unknown')
        ).size;
        
        const avgArea = totalSamples > 0 
            ? Math.round(this.data.reduce((sum, d) => sum + (d.area_px || 0), 0) / totalSamples)
            : 0;
        
        const latestTime = totalSamples > 0 
            ? this.formatTimestamp(this.data[0].analysis_timestamp)
            : '--:--';

        // Update with count-up animation
        this.animateCountUp('stat-total', totalSamples);
        this.animateCountUp('stat-species', uniqueSpecies);
        this.animateCountUp('stat-avg-area', avgArea);
        
        const latestElement = document.getElementById('stat-latest');
        if (latestElement) {
            latestElement.textContent = latestTime;
        }
    }

    /**
     * Animate count-up for statistics
     */
    animateCountUp(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const currentValue = parseInt(element.textContent) || 0;
        const increment = Math.ceil((targetValue - currentValue) / 20);
        let current = currentValue;

        const timer = setInterval(() => {
            current += increment;
            if (current >= targetValue) {
                current = targetValue;
                clearInterval(timer);
            }
            element.textContent = current;
        }, 50);
    }

    /**
     * Update all charts
     */
    updateCharts() {
        if (window.oceanCharts) {
            window.oceanCharts.updateAllCharts(this.data);
        }
    }

    /**
     * Update data table
     */
    updateDataTable() {
        const tableBody = document.getElementById('samples-table');
        if (!tableBody) return;

        if (this.data.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="px-4 py-8 text-center text-gray-500">
                        <i class="fas fa-search text-2xl mb-2 block"></i>
                        No samples available
                    </td>
                </tr>
            `;
            return;
        }

        const rows = this.data.map((item, index) => {
            const speciesColor = this.getSpeciesColor(item.predicted_species);
            const timestamp = this.formatTimestamp(item.analysis_timestamp);
            
            return `
                <tr class="border-b border-gray-100 hover:bg-blue-50 transition-colors cursor-pointer" 
                    data-sample-id="${item.image_id}"
                    style="animation-delay: ${index * 0.1}s">
                    <td class="px-4 py-3">
                        <span class="font-mono text-sm">${this.truncateText(item.image_id, 12)}</span>
                    </td>
                    <td class="px-4 py-3">
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                              style="background: ${speciesColor}20; color: ${speciesColor}">
                            <i class="fas fa-fish mr-1"></i>
                            ${item.predicted_species || 'Unknown'}
                        </span>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-600">
                        <i class="fas fa-map-marker-alt mr-1"></i>
                        ${item.latitude?.toFixed(2) || '--'}°N, ${item.longitude?.toFixed(2) || '--'}°E
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-600">
                        <i class="fas fa-clock mr-1"></i>
                        ${timestamp}
                    </td>
                </tr>
            `;
        }).join('');

        tableBody.innerHTML = rows;

        // Add click handlers for table rows
        this.setupTableRowHandlers();
    }

    /**
     * Setup table row click handlers
     */
    setupTableRowHandlers() {
        const rows = document.querySelectorAll('[data-sample-id]');
        rows.forEach(row => {
            row.addEventListener('click', () => {
                const sampleId = row.dataset.sampleId;
                this.showSampleDetails(sampleId);
            });
        });
    }

    /**
     * Show detailed view of a sample
     */
    showSampleDetails(sampleId) {
        const sample = this.data.find(item => item.image_id === sampleId);
        if (!sample) return;

        const modal = this.createSampleModal(sample);
        document.body.appendChild(modal);
        
        // Animate modal in
        requestAnimationFrame(() => {
            modal.classList.add('opacity-100');
            modal.classList.remove('opacity-0');
        });
    }

    /**
     * Create sample detail modal
     */
    createSampleModal(sample) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 opacity-0 transition-opacity duration-300';
        
        modal.innerHTML = `
            <div class="bg-white rounded-2xl p-6 max-w-md mx-4 transform scale-95 transition-transform duration-300">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-xl font-bold text-gray-900">Sample Details</h3>
                    <button class="modal-close text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
                
                <div class="space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-blue-50 p-3 rounded-lg">
                            <label class="text-sm font-medium text-gray-600">Species</label>
                            <p class="text-lg font-bold text-blue-600">${sample.predicted_species || 'Unknown'}</p>
                        </div>
                        <div class="bg-green-50 p-3 rounded-lg">
                            <label class="text-sm font-medium text-gray-600">Area</label>
                            <p class="text-lg font-bold text-green-600">${sample.area_px?.toFixed(0) || '--'} px²</p>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-yellow-50 p-3 rounded-lg">
                            <label class="text-sm font-medium text-gray-600">Perimeter</label>
                            <p class="text-lg font-bold text-yellow-600">${sample.perimeter_px?.toFixed(0) || '--'} px</p>
                        </div>
                        <div class="bg-purple-50 p-3 rounded-lg">
                            <label class="text-sm font-medium text-gray-600">Aspect Ratio</label>
                            <p class="text-lg font-bold text-purple-600">${sample.aspect_ratio || '--'}</p>
                        </div>
                    </div>
                    
                    <div class="bg-gray-50 p-3 rounded-lg">
                        <label class="text-sm font-medium text-gray-600">Location</label>
                        <p class="font-mono text-sm">${sample.latitude?.toFixed(4) || '--'}°N, ${sample.longitude?.toFixed(4) || '--'}°E</p>
                    </div>
                    
                    <div class="bg-gray-50 p-3 rounded-lg">
                        <label class="text-sm font-medium text-gray-600">Analysis Time</label>
                        <p class="text-sm">${this.formatFullTimestamp(sample.analysis_timestamp)}</p>
                    </div>
                </div>
                
                <div class="flex gap-3 mt-6">
                    <button class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition">
                        <i class="fas fa-download mr-2"></i>Export Data
                    </button>
                    <button class="modal-close flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg hover:bg-gray-300 transition">
                        Close
                    </button>
                </div>
            </div>
        `;

        // Add close handlers
        modal.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                modal.classList.add('opacity-0');
                setTimeout(() => modal.remove(), 300);
            });
        });

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('opacity-0');
                setTimeout(() => modal.remove(), 300);
            }
        });

        return modal;
    }

    /**
     * Update activity feed
     */
    updateActivityFeed() {
        const feed = document.getElementById('activity-feed');
        if (!feed) return;

        if (this.data.length === 0) {
            feed.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-stream text-3xl mb-2 block opacity-50"></i>
                    <p>No recent activity</p>
                </div>
            `;
            return;
        }

        // Get recent items (last 5)
        const recentItems = this.data.slice(0, 5);
        
        const activities = recentItems.map((item, index) => {
            const speciesColor = this.getSpeciesColor(item.predicted_species);
            const timeAgo = this.getTimeAgo(item.analysis_timestamp);
            
            return `
                <div class="activity-item" style="animation-delay: ${index * 0.1}s">
                    <div class="activity-icon" style="background: ${speciesColor}">
                        <i class="fas fa-microscope"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">
                            ${item.predicted_species || 'Unknown'} sample analyzed
                        </div>
                        <div class="activity-subtitle">
                            ${timeAgo} • Area: ${Math.round(item.area_px || 0)}px² • ID: ${this.truncateText(item.image_id, 8)}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        feed.innerHTML = activities;
    }

    /**
     * Submit new sample for analysis
     */
    async submitNewSample() {
        const submitBtn = document.getElementById('submit-otolith');
        if (!submitBtn || this.isLoading) return;

        const originalText = submitBtn.innerHTML;
        this.setButtonLoading(submitBtn, 'Analyzing...');

        try {
            const sampleId = `sample-${Date.now()}`;
            const sampleData = {
                image_data: this.getSampleImageData(),
                image_id: sampleId,
                latitude: this.getRandomLatitude(),
                longitude: this.getRandomLongitude()
            };

            const response = await fetch(`${this.apiBaseUrl}/ingest/otolith`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sampleData)
            });

            if (response.ok) {
                this.showStatus('Sample submitted successfully! Processing in background...', 'success');
                
                // Refresh data after a delay
                setTimeout(() => {
                    this.fetchDashboardData();
                }, 3000);
            } else {
                throw new Error('Failed to submit sample');
            }
        } catch (error) {
            console.error('Error submitting sample:', error);
            this.showStatus('Failed to submit sample. Please try again.', 'error');
        } finally {
            this.setButtonLoading(submitBtn, originalText, false);
        }
    }

    /**
     * Generate AI insights
     */
    async generateInsights() {
        const insightsBtn = document.getElementById('generate-insights');
        const insightsContent = document.getElementById('insights-content');
        
        if (!insightsBtn || !insightsContent || this.data.length === 0) {
            this.showStatus('No data available for analysis', 'error');
            return;
        }

        const originalText = insightsBtn.innerHTML;
        this.setButtonLoading(insightsBtn, 'Generating...');

        // Show loading state in insights panel
        insightsContent.innerHTML = `
            <div class="flex items-center justify-center py-12">
                <div class="text-center">
                    <div class="loading-spinner mx-auto mb-4"></div>
                    <p class="text-blue-600 font-medium">Analyzing marine data...</p>
                    <p class="text-sm text-gray-500">AI is processing ${this.data.length} samples</p>
                </div>
            </div>
        `;

        try {
            // Simulate AI processing time
            await this.delay(2000);
            
            const insights = this.generateMockInsights();
            this.displayInsights(insights);
            
        } catch (error) {
            console.error('Error generating insights:', error);
            this.showInsightsError();
        } finally {
            this.setButtonLoading(insightsBtn, originalText, false);
        }
    }

    /**
     * Generate mock AI insights based on current data
     */
    generateMockInsights() {
        const totalSamples = this.data.length;
        const species = [...new Set(this.data.map(d => d.predicted_species).filter(s => s && s !== 'N/A'))];
        const avgArea = Math.round(this.data.reduce((sum, d) => sum + (d.area_px || 0), 0) / totalSamples);
        const dominantSpecies = this.getDominantSpecies();

        return {
            summary: `Analysis of ${totalSamples} otolith samples reveals an average morphometric area of ${avgArea}px² with variations indicating diverse age groups and growth patterns across the sampled marine population.`,
            
            biodiversity: `${species.length} distinct species identified through AI classification. ${dominantSpecies} appears to be the predominant species, showing typical morphometric characteristics consistent with regional marine biodiversity patterns.`,
            
            patterns: `Morphometric analysis indicates seasonal growth patterns and environmental adaptations. The aspect ratio distribution suggests diverse habitat utilization across the sampled species.`,
            
            recommendations: `Continue temporal sampling across different depths and seasons to capture ecological variations. Consider expanding analysis to include additional morphometric parameters for enhanced species differentiation and population dynamics assessment.`
        };
    }

    /**
     * Display insights in the panel
     */
    displayInsights(insights) {
        const insightsContent = document.getElementById('insights-content');
        if (!insightsContent) return;

        const insightsHTML = `
            <div class="space-y-6">
                <div class="insight-card bg-gradient-to-r from-blue-50 to-cyan-50 border-l-4 border-blue-400 p-4 rounded-lg">
                    <h4 class="font-bold text-blue-800 mb-2 flex items-center">
                        <i class="fas fa-chart-line mr-2"></i>
                        Data Summary
                    </h4>
                    <p class="text-blue-700 text-sm leading-relaxed">${insights.summary}</p>
                </div>
                
                <div class="insight-card bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-400 p-4 rounded-lg">
                    <h4 class="font-bold text-green-800 mb-2 flex items-center">
                        <i class="fas fa-leaf mr-2"></i>
                        Biodiversity Analysis
                    </h4>
                    <p class="text-green-700 text-sm leading-relaxed">${insights.biodiversity}</p>
                </div>
                
                <div class="insight-card bg-gradient-to-r from-purple-50 to-violet-50 border-l-4 border-purple-400 p-4 rounded-lg">
                    <h4 class="font-bold text-purple-800 mb-2 flex items-center">
                        <i class="fas fa-project-diagram mr-2"></i>
                        Pattern Recognition
                    </h4>
                    <p class="text-purple-700 text-sm leading-relaxed">${insights.patterns}</p>
                </div>
                
                <div class="insight-card bg-gradient-to-r from-amber-50 to-yellow-50 border-l-4 border-amber-400 p-4 rounded-lg">
                    <h4 class="font-bold text-amber-800 mb-2 flex items-center">
                        <i class="fas fa-lightbulb mr-2"></i>
                        Recommendations
                    </h4>
                    <p class="text-amber-700 text-sm leading-relaxed">${insights.recommendations}</p>
                </div>
            </div>
        `;

        insightsContent.innerHTML = insightsHTML;

        // Add animation to insight cards
        const cards = insightsContent.querySelectorAll('.insight-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 200);
        });
    }

    /**
     * Show insights error state
     */
    showInsightsError() {
        const insightsContent = document.getElementById('insights-content');
        if (!insightsContent) return;

        insightsContent.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
                <h4 class="text-lg font-medium text-gray-900 mb-2">Analysis Failed</h4>
                <p class="text-gray-500 mb-4">Unable to generate AI insights at this time.</p>
                <button class="btn-primary" onclick="this.generateInsights()">
                    <i class="fas fa-retry mr-2"></i>Try Again
                </button>
            </div>
        `;
    }

    /**
     * Handle form submission
     */
    handleFormSubmit(e) {
        e.preventDefault();
        this.submitNewSample();
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + R: Refresh data
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            this.refreshData();
        }
        
        // Ctrl/Cmd + N: New sample
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            this.submitNewSample();
        }
        
        // Escape: Close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.fixed.inset-0');
            modals.forEach(modal => modal.remove());
        }
    }

    /**
     * Refresh dashboard data
     */
    async refreshData() {
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            const originalText = refreshBtn.innerHTML;
            this.setButtonLoading(refreshBtn, 'Refreshing...');
            
            await this.fetchDashboardData();
            
            this.setButtonLoading(refreshBtn, originalText, false);
        } else {
            await this.fetchDashboardData();
        }
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        if (this.autoRefreshEnabled) {
            this.refreshTimer = setInterval(() => {
                if (!document.hidden && this.autoRefreshEnabled) {
                    this.fetchDashboardData();
                }
            }, this.refreshInterval);
        }
    }

    /**
     * Pause auto-refresh
     */
    pauseAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    /**
     * Resume auto-refresh
     */
    resumeAutoRefresh() {
        if (this.autoRefreshEnabled && !this.refreshTimer) {
            this.startAutoRefresh();
        }
    }

    /**
     * Toggle settings panel
     */
    toggleSettings() {
        // Implementation for settings panel
        console.log('Settings panel toggled');
    }

    /**
     * Utility Methods
     */
    
    setLoadingState(isLoading) {
        this.isLoading = isLoading;
        // Update UI loading indicators
    }

    showLoadingState() {
        const cards = document.querySelectorAll('.ocean-card');
        cards.forEach(card => {
            card.style.opacity = '0.7';
        });
    }

    hideLoadingState() {
        const cards = document.querySelectorAll('.ocean-card');
        cards.forEach(card => {
            card.style.opacity = '1';
        });
    }

    setButtonLoading(button, text, isLoading = true) {
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = `<div class="loading-spinner mr-2"></div>${text}`;
        } else {
            button.disabled = false;
            button.innerHTML = text;
        }
    }

    showStatus(message, type = 'info') {
        const alert = document.getElementById('status-alert');
        if (!alert) return;

        const icon = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
            warning: 'fas fa-exclamation-triangle'
        }[type] || 'fas fa-info-circle';

        alert.className = `status-alert ${type}`;
        alert.querySelector('.status-icon').className = `status-icon ${icon}`;
        alert.querySelector('.status-message').textContent = message;
        alert.classList.remove('hidden');

        setTimeout(() => {
            alert.classList.add('hidden');
        }, 5000);
    }

    showErrorState(message) {
        this.showStatus(message, 'error');
    }

    getSpeciesColor(species) {
        return window.oceanCharts ? window.oceanCharts.getSpeciesColor(species) : '#3B82F6';
    }

    formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleTimeString('en-US', {
            hour12: true,
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatFullTimestamp(timestamp) {
        return new Date(timestamp).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInMinutes = Math.floor((now - time) / 60000);

        if (diffInMinutes < 1) return 'Just now';
        if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
        if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
        return `${Math.floor(diffInMinutes / 1440)}d ago`;
    }

    truncateText(text, length) {
        return text && text.length > length ? text.substring(0, length) + '...' : text;
    }

    getDominantSpecies() {
        const speciesCounts = this.data.reduce((acc, item) => {
            const species = item.predicted_species || 'Unknown';
            acc[species] = (acc[species] || 0) + 1;
            return acc;
        }, {});

        return Object.keys(speciesCounts).reduce((a, b) => 
            speciesCounts[a] > speciesCounts[b] ? a : b
        );
    }

    getSampleImageData() {
        // Return base64 encoded sample image
        return 'iVBORw0KGgoAAAANSUhEUgAAAGAAAAA8CAYAAAD2a2KkAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGVSURBVHhe7dJBCsNADADBi/T/d7ZDIgo+sRQEkl3b2Y//AY6gQBYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRYkQRa8A3oDk/oBEJt3AAAAAElFTkSuQmCC';
    }

    getRandomLatitude() {
        return Math.random() * 15 + 5; // 5°N to 20°N
    }

    getRandomLongitude() {
        return Math.random() * 15 + 70; // 70°E to 85°E
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Cleanup method
     */
    destroy() {
        this.pauseAutoRefresh();
        // Remove event listeners and cleanup
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.ocean-bg')) {
        window.oceanDashboard = new OceanDashboard();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { OceanDashboard };
}