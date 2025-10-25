/**
 * PiggyBankPC Analytics Tracking
 * Tracks video clicks and affiliate clicks for revenue monitoring
 */

/**
 * Track YouTube video clicks
 * Called when user clicks "Watch Tutorial" button
 *
 * @param {string} issueType - Type of issue (thermal_throttling, cpu_bottleneck, etc)
 * @param {string} videoId - YouTube video ID
 */
function trackVideoClick(issueType, videoId) {
    fetch('/api/analytics/event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event_type: 'video_click',
            event_data: {
                issue_type: issueType,
                video_id: videoId,
                timestamp: new Date().toISOString()
            }
        })
    }).catch(error => {
        console.error('Analytics tracking error:', error);
    });
}

/**
 * Track affiliate product clicks
 * Called when user clicks "Buy on Amazon" button
 *
 * @param {string} productName - Name of product (e.g., "Arctic MX-5")
 * @param {string} issueType - Type of issue this product solves
 */
function trackAffiliateClick(productName, issueType) {
    fetch('/api/analytics/event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event_type: 'affiliate_click',
            event_data: {
                product: productName,
                issue_type: issueType,
                timestamp: new Date().toISOString()
            }
        })
    }).catch(error => {
        console.error('Analytics tracking error:', error);
    });
}

/**
 * Track page views (optional - for engagement metrics)
 * Call this on diagnostic page load
 */
function trackPageView(pageType, submissionId) {
    fetch('/api/analytics/event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event_type: 'page_view',
            event_data: {
                page_type: pageType,
                submission_id: submissionId,
                timestamp: new Date().toISOString()
            }
        })
    }).catch(error => {
        console.error('Analytics tracking error:', error);
    });
}

// Auto-track diagnostic page views when loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a diagnostic page
    const diagnosticPage = document.querySelector('[data-page="diagnostics"]');
    if (diagnosticPage) {
        const submissionId = diagnosticPage.dataset.submissionId;
        trackPageView('diagnostics', submissionId);
    }
});
