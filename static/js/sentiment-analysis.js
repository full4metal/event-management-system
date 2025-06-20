// Sentiment Analysis Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get analysis data from hidden script tags
    const analysisDataElement = document.getElementById('analysisData');
    
    let analysisData = {};
    
    try {
        analysisData = JSON.parse(analysisDataElement.textContent);
    } catch (e) {
        console.error('Error parsing analysis data:', e);
    }
    
    // Initialize charts
    initializeCharts();
    
    // Auto-hide flash messages
    setTimeout(hideFlashMessages, 5000);
    
    function initializeCharts() {
        // Sentiment Distribution Chart
        const sentimentCtx = document.getElementById('sentimentChart');
        if (sentimentCtx && analysisData.aggregate_metrics) {
            const sentimentData = analysisData.aggregate_metrics.sentiment_distribution;
            
            new Chart(sentimentCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                        data: [
                            sentimentData.positive || 0,
                            (analysisData.aggregate_metrics.total_feedback || 0) - (sentimentData.positive || 0) - (sentimentData.negative || 0),
                            sentimentData.negative || 0
                        ],
                        backgroundColor: [
                            '#28a745',
                            '#ffc107',
                            '#dc3545'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                                    return `${context.label}: ${context.parsed} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    window.updateAnalysis = function() {
        const eventFilter = document.getElementById('event-filter').value;
        const timeFilter = document.getElementById('time-filter').value;
        
        // Show loading state
        showLoading();
        
        // Make API call to get filtered analysis
        const params = new URLSearchParams({
            event_id: eventFilter,
            time_filter: timeFilter
        });
        
        fetch(`/organizer/api/sentiment-analysis?${params}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Update global data
                analysisData = data.analysis_results;
                
                // Update UI
                updateOverviewCards(data.analysis_results);
                updateCharts(data.analysis_results);
                updateInsights(data.analysis_results);
                updateThemes(data.analysis_results);
                
                hideLoading();
                showToast('Analysis updated successfully', 'success');
            })
            .catch(error => {
                console.error('Error updating analysis:', error);
                hideLoading();
                showToast('Error updating analysis: ' + error.message, 'error');
            });
    };
    
    function updateOverviewCards(analysis) {
        const metrics = analysis.aggregate_metrics || {};
        const distribution = metrics.sentiment_distribution || {};
        
        // Update sentiment score
        const sentimentScore = document.getElementById('overall-sentiment-score');
        if (sentimentScore) {
            sentimentScore.textContent = `${(metrics.average_sentiment_score || 0).toFixed(1)}%`;
        }
        
        // Update positive percentage
        const positivePercentage = document.getElementById('positive-percentage');
        if (positivePercentage) {
            positivePercentage.textContent = `${(distribution.positive_percentage || 0).toFixed(1)}%`;
        }
        
        // Update negative percentage
        const negativePercentage = document.getElementById('negative-percentage');
        if (negativePercentage) {
            negativePercentage.textContent = `${(distribution.negative_percentage || 0).toFixed(1)}%`;
        }
        
        // Update total feedback
        const totalFeedback = document.getElementById('total-feedback');
        if (totalFeedback) {
            totalFeedback.textContent = metrics.total_feedback || 0;
        }
        
        // Update trend
        const sentimentTrend = document.getElementById('sentiment-trend');
        if (sentimentTrend && analysis.trends) {
            const trend = analysis.trends.trend || 'stable';
            sentimentTrend.className = `card-trend trend-${trend === 'improving' ? 'up' : trend === 'declining' ? 'down' : 'stable'}`;
            
            let trendText = 'Stable';
            let trendIcon = 'fas fa-minus';
            
            if (trend === 'improving') {
                trendText = 'Improving';
                trendIcon = 'fas fa-arrow-up';
            } else if (trend === 'declining') {
                trendText = 'Declining';
                trendIcon = 'fas fa-arrow-down';
            }
            
            sentimentTrend.innerHTML = `<i class="${trendIcon}"></i> ${trendText}`;
        }
    }
    
    function updateCharts(analysis) {
        // Update sentiment chart
        const sentimentCtx = document.getElementById('sentimentChart');
        if (sentimentCtx && analysis.aggregate_metrics) {
            const chart = Chart.getChart(sentimentCtx);
            if (chart) {
                const distribution = analysis.aggregate_metrics.sentiment_distribution;
                const total = analysis.aggregate_metrics.total_feedback || 0;
                const neutral = total - (distribution.positive || 0) - (distribution.negative || 0);
                
                chart.data.datasets[0].data = [
                    distribution.positive || 0,
                    neutral,
                    distribution.negative || 0
                ];
                chart.update();
            }
        }
    }
    
    function updateInsights(analysis) {
        const insights = analysis.insights || {};
        
        // Update urgent concerns
        const urgentConcerns = document.getElementById('urgent-concerns');
        if (urgentConcerns) {
            if (insights.urgent_concerns && insights.urgent_concerns.length > 0) {
                urgentConcerns.innerHTML = insights.urgent_concerns.map(concern => 
                    `<li class="insight-item priority-${concern.priority || 'medium'}">${concern.description}</li>`
                ).join('');
            } else {
                urgentConcerns.innerHTML = '<li class="insight-item">No urgent concerns identified - great job!</li>';
            }
        }
        
        // Update opportunities
        const opportunities = document.getElementById('opportunities');
        if (opportunities) {
            if (insights.improvement_opportunities && insights.improvement_opportunities.length > 0) {
                opportunities.innerHTML = insights.improvement_opportunities.map(opportunity => 
                    `<li class="insight-item">${opportunity.description}</li>`
                ).join('');
            } else {
                opportunities.innerHTML = '<li class="insight-item">Keep monitoring feedback for improvement opportunities</li>';
            }
        }
    }
    
    function updateThemes(analysis) {
        const themes = analysis.themes || {};
        
        // Update positive themes
        const positiveThemes = document.querySelector('.positive-themes .theme-list');
        if (positiveThemes) {
            if (themes.top_positive_themes && themes.top_positive_themes.length > 0) {
                positiveThemes.innerHTML = themes.top_positive_themes.slice(0, 5).map(([theme, count]) => 
                    `<li class="theme-item">
                        <span class="theme-text">${theme.charAt(0).toUpperCase() + theme.slice(1)}</span>
                        <span class="theme-count">${count}</span>
                    </li>`
                ).join('');
            } else {
                positiveThemes.innerHTML = '<li class="theme-item"><span class="theme-text">No positive themes identified yet</span></li>';
            }
        }
        
        // Update negative themes
        const negativeThemes = document.querySelector('.negative-themes .theme-list');
        if (negativeThemes) {
            if (themes.top_negative_themes && themes.top_negative_themes.length > 0) {
                negativeThemes.innerHTML = themes.top_negative_themes.slice(0, 5).map(([theme, count]) => 
                    `<li class="theme-item">
                        <span class="theme-text">${theme.charAt(0).toUpperCase() + theme.slice(1)}</span>
                        <span class="theme-count">${count}</span>
                    </li>`
                ).join('');
            } else {
                negativeThemes.innerHTML = '<li class="theme-item"><span class="theme-text">No negative themes identified - excellent!</span></li>';
            }
        }
    }
    
    window.exportAnalysis = function() {
        // Generate CSV export
        const csvData = generateCSVReport();
        downloadFile(csvData, 'sentiment-analysis-report.csv', 'text/csv');
        showToast('Analysis report exported successfully', 'success');
    };
    
    function generateCSVReport() {
        const headers = [
            'Metric',
            'Value',
            'Notes'
        ];
        
        const metrics = analysisData.aggregate_metrics || {};
        const distribution = metrics.sentiment_distribution || {};
        
        const rows = [
            ['Overall Sentiment Score', `${(metrics.average_sentiment_score || 0).toFixed(1)}%`, 'Higher is better'],
            ['Positive Feedback', `${(distribution.positive_percentage || 0).toFixed(1)}%`, `${distribution.positive || 0} reviews`],
            ['Negative Feedback', `${(distribution.negative_percentage || 0).toFixed(1)}%`, `${distribution.negative || 0} reviews`],
            ['Total Feedback', metrics.total_feedback || 0, 'Total analyzed reviews'],
            ['Average Rating', (metrics.average_rating || 0).toFixed(1), 'Out of 5 stars']
        ];
        
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');
        
        return csvContent;
    }
    
    function downloadFile(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }
    
    function showLoading() {
        // Add loading overlays to charts and sections
        document.querySelectorAll('.chart-container, .dashboard-section, .overview-grid').forEach(section => {
            if (!section.querySelector('.loading-overlay')) {
                const overlay = document.createElement('div');
                overlay.className = 'loading-overlay';
                overlay.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(255, 255, 255, 0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 100;
                `;
                overlay.innerHTML = `
                    <div class="loading-spinner" style="text-align: center; color: #4caf50;">
                        <i class="fas fa-spinner fa-spin" style="font-size: 24px; margin-bottom: 10px;"></i>
                        <p>Updating analysis...</p>
                    </div>
                `;
                section.style.position = 'relative';
                section.appendChild(overlay);
            }
        });
    }
    
    function hideLoading() {
        document.querySelectorAll('.loading-overlay').forEach(overlay => {
            overlay.remove();
        });
    }
    
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add toast styles if not already present
        if (!document.querySelector('#toast-styles')) {
            const styles = document.createElement('style');
            styles.id = 'toast-styles';
            styles.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                }
                .toast-success { border-left: 4px solid #4caf50; }
                .toast-error { border-left: 4px solid #f44336; }
                .toast-info { border-left: 4px solid #2196f3; }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    function hideFlashMessages() {
        const flashMessages = document.querySelector('.flash-messages');
        if (flashMessages) {
            flashMessages.style.opacity = '0';
            setTimeout(() => {
                flashMessages.style.display = 'none';
            }, 300);
        }
    }
});