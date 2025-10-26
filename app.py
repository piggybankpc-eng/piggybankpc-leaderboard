"""
PiggyBankPC Leaderboard - Main Application
"""
from flask import Flask
from flask_login import LoginManager
from models import db, User
from config import config
import os
import logging

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID"""
    return User.query.get(int(user_id))


def create_app(config_name=None):
    """Application factory"""

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Configure logging
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.leaderboard import leaderboard_bp
    from routes.submit import submit_bp
    from routes.profile import profile_bp
    # Phase 2: Diagnostic & Revenue Generation
    from routes.diagnostics import diagnostics_bp
    from routes.most_improved import most_improved_bp
    from routes.analytics import analytics_bp
    # Official PiggyBankPC Builds
    from routes.official_builds import official_builds_bp
    # Admin Dashboard
    from routes.admin import admin_bp
    # Best All-Rounder
    from routes.best_all_rounder import best_all_rounder_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(submit_bp)
    app.register_blueprint(profile_bp)
    # Phase 2 blueprints
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(most_improved_bp)
    app.register_blueprint(analytics_bp)
    # Official builds blueprint
    app.register_blueprint(official_builds_bp)
    # Admin blueprint
    app.register_blueprint(admin_bp)
    # Best all-rounder blueprint
    app.register_blueprint(best_all_rounder_bp)

    # Health check endpoint for Docker/Kubernetes/Coolify monitoring
    @app.route('/health')
    def health_check():
        """Health check endpoint for container orchestration"""
        from datetime import datetime
        from flask import jsonify

        try:
            # Check database connectivity
            db.session.execute(db.text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'

        return jsonify({
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'database': db_status,
            'version': '2.0.0'  # Phase 2 complete!
        }), 200 if db_status == 'healthy' else 503

    # Create database tables
    with app.app_context():
        db.create_all()

    # Add custom template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """Format datetime for display"""
        if value is None:
            return ''
        return value.strftime(format)

    @app.template_filter('relative_time')
    def relative_time(value):
        """Convert datetime to relative time (e.g., '2 hours ago')"""
        if value is None:
            return ''

        from datetime import datetime
        now = datetime.utcnow()
        diff = now - value

        seconds = diff.total_seconds()

        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f'{days} day{"s" if days != 1 else ""} ago'
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f'{weeks} week{"s" if weeks != 1 else ""} ago'
        elif seconds < 31536000:
            months = int(seconds / 2592000)
            return f'{months} month{"s" if months != 1 else ""} ago'
        else:
            years = int(seconds / 31536000)
            return f'{years} year{"s" if years != 1 else ""} ago'

    return app


# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    # Development server only (use Gunicorn in production!)
    app.run(host='0.0.0.0', port=5555, debug=True)
