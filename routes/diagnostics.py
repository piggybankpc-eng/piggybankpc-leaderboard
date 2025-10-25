"""
PiggyBankPC Leaderboard - Diagnostic Results Routes
"""

from flask import Blueprint, render_template, abort
from flask_login import current_user
from models import db, Submission, DiagnosticIssue, Improvement
from sqlalchemy import func

diagnostics_bp = Blueprint('diagnostics', __name__)


@diagnostics_bp.route('/submission/<int:submission_id>/diagnostics')
def view_diagnostics(submission_id):
    """
    View diagnostic results for a submission
    Shows detected issues, YouTube videos, affiliate products, and improvements
    """
    submission = Submission.query.get_or_404(submission_id)

    # Get detected issues for this submission
    issues = DiagnosticIssue.query.filter_by(
        submission_id=submission_id
    ).order_by(
        # Order by severity: high -> medium -> low
        db.case(
            (DiagnosticIssue.severity == 'high', 1),
            (DiagnosticIssue.severity == 'medium', 2),
            else_=3
        )
    ).all()

    # Get leaderboard rank for this submission
    rank = Submission.query.filter(
        Submission.verified == True,
        Submission.fps_avg > submission.fps_avg
    ).count() + 1

    total_submissions = Submission.query.filter_by(verified=True).count()

    # Check if this submission is an improvement over a previous one
    improvement = None
    if submission.is_improvement and submission.parent_submission_id:
        improvement = Improvement.query.filter_by(
            after_submission_id=submission.id
        ).first()

    return render_template(
        'diagnostics.html',
        submission=submission,
        issues=issues,
        rank=rank,
        total_submissions=total_submissions,
        improvement=improvement
    )


@diagnostics_bp.route('/submission/<int:submission_id>/diagnostics/raw')
def view_diagnostics_raw(submission_id):
    """
    API endpoint: Return diagnostic data as JSON
    Useful for PEGGY AI agent or external integrations
    """
    from flask import jsonify

    submission = Submission.query.get_or_404(submission_id)

    issues = DiagnosticIssue.query.filter_by(
        submission_id=submission_id
    ).all()

    return jsonify({
        'submission_id': submission.id,
        'user': submission.user.username,
        'fps_avg': submission.fps_avg,
        'issues_count': len(issues),
        'issues': [
            {
                'type': issue.issue_type,
                'severity': issue.severity,
                'title': issue.title,
                'description': issue.description,
                'potential_fps_gain': issue.potential_fps_gain,
                'fix_difficulty': issue.fix_difficulty,
                'fix_time': issue.fix_time,
                'fix_cost': issue.fix_cost
            }
            for issue in issues
        ],
        'is_improvement': submission.is_improvement,
        'improvement_percent': submission.improvement_percent
    })
