/**
 * ============================================
 * CMLRE Ocean Intelligence Platform
 * Professional Charts & Visualization JavaScript
 * ============================================
 */

class OceanCharts {
    constructor() {
        this.charts = {};
        this.colorPalette = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
            '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
        ];
        this.speciesColors = {};
        this.initializeCharts();
    }

    /**
     * Initialize all chart configurations
     */
    initializeCharts() {
        this.setupChartDefaults();
        this.createSpeciesChart();
        this.createScatterChart();
        this.createMapChart();
    }

    /**
     * Setup Chart.js default configurations
     */
    setupChartDefaults() {
        Chart.defaults.font.family = 'Inter, sans-serif';
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#64748B';
        Chart.defaults.plugins.legend.position = 'bottom';
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 20;
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(30, 64, 175, 0.9)';
        Chart.defaults.plugins.tooltip.titleColor = '#FFFFFF';
        Chart.defaults.plugins.tooltip.bodyColor = '#FFFFFF';
        Chart.defaults.plugins.tooltip.cornerRadius = 8;
        Chart.defaults.plugins.tooltip.padding = 12;
    }

    /**
     * Get color for species (consistent coloring)
     */
    getSpeciesColor(species) {
        if (!species || species === 'N/A' || species === 'Unknown') {
            return '#9CA3AF';
        }
        
        if (!this.speciesColors[species]) {
            const colorIndex = Object.keys(this.speciesColors).length % this.colorPalette.length;
            this.speciesColors[species] = this.colorPalette[colorIndex];
        }
        
        return this.speciesColors[species];
    }

    /**
     * Create species distribution doughnut chart
     */
    createSpeciesChart() {
        const ctx = document.getElementById('species-chart');
        if (!ctx) return;

        this.charts.species = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [],
                    borderColor: '#FFFFFF',
                    borderWidth: 3,
                    hoverBorderWidth: 4,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 11,
                                weight: '500'
                            },
                            generateLabels: (chart) => {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const meta = chart.getDatasetMeta(0);
                                        const style = meta.controller.getStyle(i);
                                        return {
                                            text: `${label} (${data.datasets[0].data[i]})`,
                                            fillStyle: style.backgroundColor,
                                            strokeStyle: style.borderColor,
                                            lineWidth: style.borderWidth,
                                            pointStyle: 'circle',
                                            hidden: isNaN(data.datasets[0].data[i]) || meta.data[i].hidden,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} samples (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1200,
                    easing: 'easeOutCubic'
                }
            }
        });
    }

    /**
     * Create morphometric scatter plot
     */
    createScatterChart() {
        const ctx = document.getElementById('scatter-chart');
        if (!ctx) return;

        this.charts.scatter = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Area (px²)',
                            font: {
                                size: 14,
                                weight: 'bold'
                            },
                            color: '#1E293B'
                        },
                        grid: {
                            color: 'rgba(59, 130, 246, 0.1)',
                            lineWidth: 1
                        },
                        ticks: {
                            color: '#64748B',
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Perimeter (px)',
                            font: {
                                size: 14,
                                weight: 'bold'
                            },
                            color: '#1E293B'
                        },
                        grid: {
                            color: 'rgba(59, 130, 246, 0.1)',
                            lineWidth: 1
                        },
                        ticks: {
                            color: '#64748B',
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            font: {
                                size: 11,
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: (context) => {
                                return `${context[0].dataset.label}`;
                            },
                            label: (context) => {
                                return [
                                    `Area: ${context.parsed.x.toFixed(0)} px²`,
                                    `Perimeter: ${context.parsed.y.toFixed(0)} px`,
                                    `Aspect Ratio: ${(context.parsed.x / context.parsed.y).toFixed(2)}`
                                ];
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 6,
                        hoverRadius: 8,
                        borderWidth: 2,
                        hoverBorderWidth: 3
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /**
     * Create geospatial map chart
     */
    async createMapChart() {
        try {
            const ctx = document.getElementById('map-chart');
            if (!ctx) return;

            // Load world topology data
            const world = await fetch('https://unpkg.com/world-atlas/countries-110m.json')
                .then(response => response.json());
            
            const countries = ChartGeo.topojson.feature(world, world.objects.countries).features;

            this.charts.map = new Chart(ctx, {
                type: 'choropleth',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Sample Locations',
                        data: [],
                        outline: countries,
                        backgroundColor: [],
                        borderColor: 'rgba(255, 255, 255, 0.8)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    showOutline: true,
                    showGraticule: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                title: (context) => {
                                    return `Sample: ${context[0].label}`;
                                },
                                label: (context) => {
                                    const data = context.raw;
                                    return [
                                        `Species: ${data.species || 'Unknown'}`,
                                        `Location: ${data.latitude?.toFixed(2)}°N, ${data.longitude?.toFixed(2)}°E`,
                                        `Area: ${data.area_px?.toFixed(0)} px²`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        projection: {
                            axis: 'x',
                            projection: 'naturalEarth1',
                            projectionScale: 100,
                            projectionOffset: [0, 0]
                        }
                    },
                    animation: {
                        duration: 2000,
                        easing: 'easeOutCubic'
                    }
                }
            });
        } catch (error) {
            console.error('Error creating map chart:', error);
            this.showMapFallback();
        }
    }

    /**
     * Show fallback when map fails to load
     */
    showMapFallback() {
        const mapContainer = document.getElementById('map-chart').parentElement;
        mapContainer.innerHTML = `
            <div class="flex items-center justify-center h-full text-gray-500 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg">
                <div class="text-center">
                    <i class="fas fa-globe-asia text-4xl mb-4 text-blue-300"></i>
                    <p class="text-lg font-medium">Interactive Map</p>
                    <p class="text-sm">Loading geospatial data...</p>
                </div>
            </div>
        `;
    }

    /**
     * Update species chart with new data
     */
    updateSpeciesChart(data) {
        if (!this.charts.species || !data || data.length === 0) return;

        // Aggregate species data
        const speciesCounts = data.reduce((acc, item) => {
            const species = item.predicted_species && item.predicted_species !== 'N/A' 
                ? item.predicted_species 
                : 'Unknown';
            acc[species] = (acc[species] || 0) + 1;
            return acc;
        }, {});

        const labels = Object.keys(speciesCounts);
        const values = Object.values(speciesCounts);
        const colors = labels.map(species => this.getSpeciesColor(species));

        // Update chart data
        this.charts.species.data.labels = labels;
        this.charts.species.data.datasets[0].data = values;
        this.charts.species.data.datasets[0].backgroundColor = colors;
        
        this.charts.species.update('active');
    }

    /**
     * Update scatter chart with new data
     */
    updateScatterChart(data) {
        if (!this.charts.scatter || !data || data.length === 0) return;

        // Group data by species
        const speciesData = {};
        data.forEach(item => {
            const species = item.predicted_species && item.predicted_species !== 'N/A' 
                ? item.predicted_species 
                : 'Unknown';
            
            if (!speciesData[species]) {
                speciesData[species] = {
                    label: species,
                    data: [],
                    backgroundColor: this.getSpeciesColor(species),
                    borderColor: this.getSpeciesColor(species),
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBorderWidth: 2,
                    pointHoverBorderWidth: 3,
                    pointBorderColor: '#FFFFFF'
                };
            }

            speciesData[species].data.push({
                x: item.area_px,
                y: item.perimeter_px,
                sampleId: item.image_id,
                aspectRatio: item.aspect_ratio
            });
        });

        // Update chart datasets
        this.charts.scatter.data.datasets = Object.values(speciesData);
        this.charts.scatter.update('active');
    }

    /**
     * Update map chart with new data
     */
    updateMapChart(data) {
        if (!this.charts.map || !data || data.length === 0) return;

        const mapData = data.map(item => ({
            feature: this.getCountryFeature(item.latitude, item.longitude),
            value: item.area_px,
            species: item.predicted_species,
            latitude: item.latitude,
            longitude: item.longitude,
            area_px: item.area_px,
            sampleId: item.image_id
        }));

        const colors = data.map(item => this.getSpeciesColor(item.predicted_species));

        this.charts.map.data.labels = data.map(item => item.image_id);
        this.charts.map.data.datasets[0].data = mapData;
        this.charts.map.data.datasets[0].backgroundColor = colors;
        
        this.charts.map.update('active');
    }

    /**
     * Get country feature for coordinates (simplified)
     */
    getCountryFeature(latitude, longitude) {
        // For demo purposes, return India feature for coordinates in Indian Ocean region
        return {
            type: 'Feature',
            properties: { NAME: 'Sample Location' },
            geometry: {
                type: 'Point',
                coordinates: [longitude, latitude]
            }
        };
    }

    /**
     * Create progress chart for loading states
     */
    createProgressChart(containerId, progress = 0) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const canvas = document.createElement('canvas');
        canvas.width = 200;
        canvas.height = 200;
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 80;

        const drawProgress = (percent) => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Background circle
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            ctx.strokeStyle = 'rgba(59, 130, 246, 0.2)';
            ctx.lineWidth = 8;
            ctx.stroke();

            // Progress circle
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, -Math.PI / 2, (-Math.PI / 2) + (2 * Math.PI * percent / 100));
            ctx.strokeStyle = '#3B82F6';
            ctx.lineWidth = 8;
            ctx.lineCap = 'round';
            ctx.stroke();

            // Text
            ctx.fillStyle = '#1E293B';
            ctx.font = 'bold 24px Inter';
            ctx.textAlign = 'center';
            ctx.fillText(`${Math.round(percent)}%`, centerX, centerY + 8);
        };

        // Animate progress
        let currentProgress = 0;
        const animateProgress = () => {
            if (currentProgress < progress) {
                currentProgress += 2;
                drawProgress(currentProgress);
                requestAnimationFrame(animateProgress);
            }
        };

        drawProgress(0);
        animateProgress();
    }

    /**
     * Create real-time chart updates
     */
    startRealTimeUpdates() {
        // Simulate real-time data updates
        setInterval(() => {
            if (Math.random() > 0.7) { // 30% chance of update
                this.simulateDataPoint();
            }
        }, 5000);
    }

    /**
     * Simulate new data point for real-time effect
     */
    simulateDataPoint() {
        const species = ['Gadus morhua', 'Salmo salar', 'Thunnus thynnus', 'Hippoglossus hippoglossus'];
        const randomSpecies = species[Math.floor(Math.random() * species.length)];
        
        const newPoint = {
            predicted_species: randomSpecies,
            area_px: Math.random() * 2000 + 500,
            perimeter_px: Math.random() * 400 + 100,
            latitude: Math.random() * 15 + 5,
            longitude: Math.random() * 15 + 70,
            image_id: `sample-${Date.now()}`,
            aspect_ratio: (Math.random() * 2 + 1).toFixed(2)
        };

        // Add subtle animation for new data point
        this.highlightNewDataPoint(newPoint);
    }

    /**
     * Highlight new data point with animation
     */
    highlightNewDataPoint(dataPoint) {
        // Add visual feedback for new data
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-slide-right';
        notification.innerHTML = `
            <i class="fas fa-plus-circle mr-2"></i>
            New ${dataPoint.predicted_species} sample detected
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    /**
     * Export chart as image
     */
    exportChart(chartName, filename = 'chart.png') {
        const chart = this.charts[chartName];
        if (!chart) return;

        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = filename;
        link.href = url;
        link.click();
    }

    /**
     * Resize charts for responsive design
     */
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }

    /**
     * Destroy all charts
     */
    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        this.charts = {};
    }

    /**
     * Update all charts with new data
     */
    updateAllCharts(data) {
        this.updateSpeciesChart(data);
        this.updateScatterChart(data);
        this.updateMapChart(data);
    }

    /**
     * Get chart statistics
     */
    getChartStats() {
        return {
            totalCharts: Object.keys(this.charts).length,
            speciesCount: Object.keys(this.speciesColors).length,
            activeAnimations: Object.values(this.charts).filter(chart => 
                chart && chart.options && chart.options.animation
            ).length
        };
    }
}

// Chart utility functions
const ChartUtils = {
    /**
     * Generate gradient colors
     */
    generateGradient(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    },

    /**
     * Format large numbers
     */
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    },

    /**
     * Generate chart colors with opacity
     */
    generateColors(baseColor, count, opacity = 1) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            const hue = (i * 360 / count) % 360;
            colors.push(`hsla(${hue}, 70%, 50%, ${opacity})`);
        }
        return colors;
    }
};

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('#species-chart')) {
        window.oceanCharts = new OceanCharts();
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.oceanCharts) {
                window.oceanCharts.resizeCharts();
            }
        });
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { OceanCharts, ChartUtils };
}