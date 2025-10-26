"""
PiggyBankPC Leaderboard - Admin Dashboard Routes
Admin-only routes for user management and analytics
"""
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from models import db, User, Submission, Improvement, Achievement
from functools import wraps
from datetime import datetime
import csv
import io

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/admin')
@admin_required
def dashboard():
    """Admin dashboard with user management and analytics"""

    # Get all users with their stats
    users = User.query.order_by(User.created_at.desc()).all()

    user_data = []
    for user in users:
        submission_count = Submission.query.filter_by(user_id=user.id).count()
        official_count = Submission.query.filter_by(user_id=user.id, is_official=True).count()
        improvement_count = Improvement.query.filter_by(user_id=user.id).count()
        achievement_count = Achievement.query.filter_by(user_id=user.id).count()

        # Get best FPS
        best_submission = Submission.query.filter_by(user_id=user.id)\
            .order_by(Submission.fps_avg.desc()).first()
        best_fps = best_submission.fps_avg if best_submission else 0

        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'created_at': user.created_at,
            'submissions': submission_count,
            'official_builds': official_count,
            'improvements': improvement_count,
            'achievements': achievement_count,
            'best_fps': best_fps
        })

    # Platform stats
    total_users = len(users)
    total_submissions = Submission.query.count()
    total_official = Submission.query.filter_by(is_official=True).count()
    total_community = total_submissions - total_official
    total_improvements = Improvement.query.count()

    stats = {
        'total_users': total_users,
        'total_submissions': total_submissions,
        'official_builds': total_official,
        'community_submissions': total_community,
        'total_improvements': total_improvements,
        'admin_users': len([u for u in users if u.is_admin])
    }

    return render_template(
        'admin_dashboard.html',
        users=user_data,
        stats=stats
    )


@admin_bp.route('/admin/users/export')
@admin_required
def export_users():
    """Export all user data to CSV"""

    users = User.query.order_by(User.created_at.desc()).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'ID',
        'Username',
        'Email',
        'Is Admin',
        'Created Date',
        'Total Submissions',
        'Official Builds',
        'Improvements',
        'Achievements',
        'Best FPS'
    ])

    # Write user data
    for user in users:
        submission_count = Submission.query.filter_by(user_id=user.id).count()
        official_count = Submission.query.filter_by(user_id=user.id, is_official=True).count()
        improvement_count = Improvement.query.filter_by(user_id=user.id).count()
        achievement_count = Achievement.query.filter_by(user_id=user.id).count()

        best_submission = Submission.query.filter_by(user_id=user.id)\
            .order_by(Submission.fps_avg.desc()).first()
        best_fps = best_submission.fps_avg if best_submission else 0

        writer.writerow([
            user.id,
            user.username,
            user.email,
            'Yes' if user.is_admin else 'No',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            submission_count,
            official_count,
            improvement_count,
            achievement_count,
            round(best_fps, 1) if best_fps else 'N/A'
        ])

    # Prepare file for download
    output.seek(0)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f'piggybankpc_users_{timestamp}.csv'

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@admin_bp.route('/admin/submissions/export')
@admin_required
def export_submissions():
    """Export all submission data to CSV"""

    submissions = Submission.query.order_by(Submission.submission_date.desc()).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'ID',
        'Username',
        'Email',
        'Is Official',
        'Build Name',
        'YouTube URL',
        'CPU',
        'GPU',
        'GPU Price',
        'RAM',
        'FPS Average',
        'FPS Min',
        'FPS Max',
        'AI Tokens/sec',
        'CPU Score',
        'GPU Temp Max',
        'Submission Date'
    ])

    # Write submission data
    for sub in submissions:
        writer.writerow([
            sub.id,
            sub.user.username,
            sub.user.email,
            'Yes' if sub.is_official else 'No',
            sub.build_name or 'N/A',
            sub.youtube_video_url or 'N/A',
            sub.cpu_model,
            sub.gpu_model,
            round(sub.gpu_price, 2) if sub.gpu_price else 'N/A',
            sub.ram_total,
            round(sub.fps_avg, 1) if sub.fps_avg else 'N/A',
            round(sub.fps_min, 1) if sub.fps_min else 'N/A',
            round(sub.fps_max, 1) if sub.fps_max else 'N/A',
            round(sub.ai_tokens_per_sec, 1) if sub.ai_tokens_per_sec else 'N/A',
            round(sub.cpu_score, 0) if sub.cpu_score else 'N/A',
            round(sub.gpu_temp_max, 1) if sub.gpu_temp_max else 'N/A',
            sub.submission_date.strftime('%Y-%m-%d %H:%M:%S')
        ])

    # Prepare file for download
    output.seek(0)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f'piggybankpc_submissions_{timestamp}.csv'

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@admin_bp.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""

    user = User.query.get_or_404(user_id)

    # Don't allow removing your own admin status
    if user.id == current_user.id:
        flash('You cannot change your own admin status.', 'warning')
        return redirect(url_for('admin.dashboard'))

    user.is_admin = not user.is_admin
    db.session.commit()

    status = 'admin' if user.is_admin else 'regular user'
    flash(f'{user.username} is now a {status}.', 'success')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user and all their data"""

    user = User.query.get_or_404(user_id)

    # Don't allow deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account from admin panel.', 'danger')
        return redirect(url_for('admin.dashboard'))

    username = user.username

    try:
        # User deletion will cascade to submissions, improvements, achievements
        db.session.delete(user)
        db.session.commit()
        flash(f'User {username} and all their data have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}")
        flash('Error deleting user. Please try again.', 'danger')

    return redirect(url_for('admin.dashboard'))
