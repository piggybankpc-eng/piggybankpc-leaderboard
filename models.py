"""
PiggyBankPC Leaderboard - Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    submissions = db.relationship('Submission', backref='user', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Submission.user_id')
    improvements = db.relationship('Improvement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Submission(db.Model):
    """Benchmark submission model"""
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    hardware_fingerprint = db.Column(db.String(64), nullable=False, index=True)

    # System Info
    cpu_model = db.Column(db.String(255))
    gpu_model = db.Column(db.String(255), index=True)
    gpu_price = db.Column(db.Float)
    ram_total = db.Column(db.String(50))

    # Benchmark Results
    fps_avg = db.Column(db.Float, index=True)
    fps_min = db.Column(db.Float)
    fps_max = db.Column(db.Float)
    ai_tokens_per_sec = db.Column(db.Float)
    cpu_score = db.Column(db.Float)

    # GPU Metrics for Diagnostics (Phase 2)
    gpu_temp_max = db.Column(db.Float)
    gpu_temp_avg = db.Column(db.Float)
    gpu_load_avg = db.Column(db.Float)  # Average GPU utilization %

    # Improvement Tracking (Phase 2)
    parent_submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=True)
    is_improvement = db.Column(db.Boolean, default=False)
    improvement_percent = db.Column(db.Float)

    # Metadata
    submission_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    verified = db.Column(db.Boolean, default=True)
    pbr_filename = db.Column(db.String(255))
    benchmark_version = db.Column(db.String(20))
    benchmark_timestamp = db.Column(db.String(50))

    # Official PiggyBankPC Build tracking
    is_official = db.Column(db.Boolean, default=False, index=True)
    youtube_video_url = db.Column(db.String(500))  # YouTube video link for official builds
    build_name = db.Column(db.String(200))  # Optional custom name for official builds (e.g., "Budget Beast 2024")

    @property
    def price_per_fps(self):
        """Calculate price-per-FPS performance metric"""
        if self.fps_avg and self.gpu_price and self.fps_avg > 0:
            return round(self.gpu_price / self.fps_avg, 2)
        return None

    @property
    def gpu_brand(self):
        """Extract GPU brand from model"""
        if not self.gpu_model:
            return 'Unknown'
        model_upper = self.gpu_model.upper()
        if 'NVIDIA' in model_upper or 'GTX' in model_upper or 'RTX' in model_upper:
            return 'NVIDIA'
        elif 'AMD' in model_upper or 'RADEON' in model_upper or 'RX' in model_upper:
            return 'AMD'
        elif 'INTEL' in model_upper:
            return 'Intel'
        return 'Unknown'

    # Relationships
    parent_submission = db.relationship('Submission', remote_side=[id], backref='child_submissions', foreign_keys=[parent_submission_id])
    issues = db.relationship('DiagnosticIssue', backref='submission', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Submission {self.id} by {self.user.username}>'


class DiagnosticIssue(db.Model):
    """Detected issues for each submission"""
    __tablename__ = 'diagnostic_issues'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False, index=True)

    # Issue details
    issue_type = db.Column(db.String(50), index=True)  # 'thermal_throttling', 'cpu_bottleneck', etc.
    severity = db.Column(db.String(20))  # 'high', 'medium', 'low'
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    impact = db.Column(db.Text)
    potential_fps_gain = db.Column(db.String(50))

    # Fix details
    fix_difficulty = db.Column(db.String(20))
    fix_time = db.Column(db.String(50))
    fix_cost = db.Column(db.String(50))
    youtube_video_id = db.Column(db.String(50))
    youtube_title = db.Column(db.String(200))

    # Product recommendations (stored as JSON)
    products = db.Column(db.JSON)

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DiagnosticIssue {self.issue_type} for Submission {self.submission_id}>'


class Improvement(db.Model):
    """Track before/after improvements"""
    __tablename__ = 'improvements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    hardware_fingerprint = db.Column(db.String(64), index=True)

    # Before/After submissions
    before_submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    after_submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'))

    # Improvement metrics
    fps_before = db.Column(db.Float)
    fps_after = db.Column(db.Float)
    fps_gain = db.Column(db.Float, index=True)  # Absolute gain
    fps_gain_percent = db.Column(db.Float, index=True)  # Percentage gain

    # What they fixed (stored as JSON array)
    fixes_applied = db.Column(db.JSON)  # ['thermal_paste', 'thermal_pads', 'ram_upgrade']

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    before_submission = db.relationship('Submission', foreign_keys=[before_submission_id], backref='improvements_as_before')
    after_submission = db.relationship('Submission', foreign_keys=[after_submission_id], backref='improvements_as_after')

    def __repr__(self):
        return f'<Improvement {self.id}: +{self.fps_gain} FPS ({self.fps_gain_percent}%)>'


class Achievement(db.Model):
    """User achievements/badges"""
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Achievement details
    achievement_type = db.Column(db.String(50), index=True)  # 'thermal_hero', 'performance_boost', etc.
    title = db.Column(db.String(100))  # '🔥 Thermal Hero'
    description = db.Column(db.Text)
    badge_emoji = db.Column(db.String(10))  # '🔥'

    # Associated improvement
    improvement_id = db.Column(db.Integer, db.ForeignKey('improvements.id'), nullable=True)

    # Timestamps
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    improvement = db.relationship('Improvement', backref='achievement')

    def __repr__(self):
        return f'<Achievement {self.title} for User {self.user_id}>'


class AnalyticsEvent(db.Model):
    """Track user interactions for analytics"""
    __tablename__ = 'analytics_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=True, index=True)

    # Event details
    event_type = db.Column(db.String(50), index=True)  # 'video_click', 'affiliate_click', 'improvement_submitted'
    event_data = db.Column(db.JSON)  # Additional context

    # Metadata
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship('User', backref='analytics_events')
    submission = db.relationship('Submission', backref='analytics_events')

    def __repr__(self):
        return f'<AnalyticsEvent {self.event_type} at {self.created_at}>'


class DiagnosticConfig(db.Model):
    """Store diagnostic configuration (YouTube videos, affiliate links)"""
    __tablename__ = 'diagnostic_config'

    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.JSON)  # Flexible JSON storage
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    updater = db.relationship('User', backref='config_updates')

    def __repr__(self):
        return f'<DiagnosticConfig {self.config_key}>'
