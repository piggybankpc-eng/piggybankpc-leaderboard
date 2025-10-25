"""
PiggyBankPC Leaderboard - Most Improved Routes
"""

from flask import Blueprint, render_template
from models import db, Improvement, User, Submission
from sqlalchemy import desc

most_improved_bp = Blueprint('most_improved', __name__)


@most_improved_bp.route('/leaderboard/most-improved')
def most_improved():
    """
    Most Improved leaderboard - shows users who gained the most FPS
    Celebrates improvements and motivates users to optimize their builds
    """
    # Get top improvements ordered by absolute FPS gain
    improvements = db.session.query(Improvement).join(
        Improvement.after_submission
    ).join(
        Submission.user
    ).filter(
        Submission.verified == True
    ).order_by(
        desc(Improvement.fps_gain)
    ).limit(50).all()

    return render_template(
        'most_improved.html',
        improvements=improvements
    )


@most_improved_bp.route('/leaderboard/most-improved/percent')
def most_improved_percent():
    """
    Most Improved by percentage - shows users who gained the most %
    Good for showcasing low-end builds that doubled performance
    """
    improvements = db.session.query(Improvement).join(
        Improvement.after_submission
    ).join(
        Submission.user
    ).filter(
        Submission.verified == True
    ).order_by(
        desc(Improvement.fps_gain_percent)
    ).limit(50).all()

    return render_template(
        'most_improved.html',
        improvements=improvements
    )
