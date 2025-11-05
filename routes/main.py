"""
PiggyBankPC Leaderboard - Main Routes
"""
from flask import Blueprint, render_template
from sqlalchemy import desc, func
from models import db, Submission
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page"""

    # Get top 5 recent submissions for preview (exclude unpublished official builds - anti-spoiler)
    recent_submissions = Submission.query.filter_by(verified=True, published=True).order_by(
        desc(Submission.submission_date)
    ).limit(5).all()

    # Get best value (price-per-FPS) submissions (exclude unpublished official builds)
    all_submissions = Submission.query.filter_by(verified=True, published=True).filter(
        Submission.fps_avg > 0,
        Submission.gpu_price > 0
    ).all()

    # Calculate price-per-FPS and sort
    best_value_submissions = []
    for sub in all_submissions:
        if sub.price_per_fps:
            best_value_submissions.append(sub)

    best_value_submissions.sort(key=lambda x: x.price_per_fps)
    best_value_submissions = best_value_submissions[:5]

    # Get statistics (exclude unpublished official builds)
    total_submissions = Submission.query.filter_by(verified=True, published=True).count()
    unique_users = db.session.query(Submission.user_id).filter(
        Submission.verified == True,
        Submission.published == True
    ).distinct().count()

    # Get this week's submissions (exclude unpublished official builds)
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_submissions = Submission.query.filter(
        Submission.verified == True,
        Submission.published == True,
        Submission.submission_date >= week_ago
    ).count()

    stats = {
        'total_submissions': total_submissions,
        'unique_users': unique_users,
        'week_submissions': week_submissions
    }

    return render_template(
        'index.html',
        recent_submissions=recent_submissions,
        best_value_submissions=best_value_submissions,
        stats=stats
    )


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@main_bp.route('/download')
def download():
    """Download page for benchmark AppImage"""
    return render_template('download.html')
