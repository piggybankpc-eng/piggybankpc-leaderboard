"""
PiggyBankPC Leaderboard - Profile Routes
"""
from flask import Blueprint, render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from models import db, User, Submission

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile/<username>')
def view_profile(username):
    """View user profile"""
    user = User.query.filter_by(username=username).first_or_404()

    # Get user's submissions
    submissions = Submission.query.filter_by(
        user_id=user.id,
        verified=True
    ).order_by(desc(Submission.submission_date)).all()

    # Calculate statistics
    stats = {}

    if submissions:
        # Average FPS
        avg_fps = db.session.query(
            func.avg(Submission.fps_avg)
        ).filter_by(user_id=user.id, verified=True).scalar()

        # Best price-per-FPS
        best_value = None
        for sub in submissions:
            if sub.price_per_fps:
                if best_value is None or sub.price_per_fps < best_value:
                    best_value = sub.price_per_fps

        # Total submissions
        total_subs = len(submissions)

        # Best FPS
        best_fps = max((s.fps_avg for s in submissions if s.fps_avg), default=0)

        stats = {
            'avg_fps': round(avg_fps, 1) if avg_fps else 0,
            'best_price_per_fps': round(best_value, 2) if best_value else None,
            'total_submissions': total_subs,
            'best_fps': round(best_fps, 1)
        }
    else:
        stats = {
            'avg_fps': 0,
            'best_price_per_fps': None,
            'total_submissions': 0,
            'best_fps': 0
        }

    # Check if viewing own profile
    is_own_profile = current_user.is_authenticated and current_user.id == user.id

    return render_template(
        'profile.html',
        user=user,
        submissions=submissions,
        stats=stats,
        is_own_profile=is_own_profile
    )


@profile_bp.route('/profile/<username>/delete/<int:submission_id>', methods=['POST'])
@login_required
def delete_submission(username, submission_id):
    """Delete a submission (own submissions only)"""

    # Get the submission
    submission = Submission.query.get_or_404(submission_id)

    # Check authorization
    if submission.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    # Delete the submission
    db.session.delete(submission)
    db.session.commit()

    flash('Submission deleted successfully.', 'success')
    return redirect(url_for('profile.view_profile', username=current_user.username))
