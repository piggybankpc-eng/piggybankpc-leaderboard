// PiggyBankPC Leaderboard - Custom JavaScript

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');

    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href !== '') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Add confirmation for delete actions
document.querySelectorAll('form[onsubmit*="confirm"]').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
});

// Table row highlighting
document.querySelectorAll('.table-hover tbody tr').forEach(row => {
    row.addEventListener('click', function() {
        // Optional: Add click handler for table rows
    });
});
