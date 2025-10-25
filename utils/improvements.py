"""
PiggyBankPC Leaderboard - Improvement Tracking
Track before/after benchmarks and calculate gains
"""

from models import db, Improvement, Submission
from utils.achievements import check_and_award_achievements


def detect_improvement_opportunity(user_id, hardware_fingerprint):
    """
    Check if user has previous submissions with same hardware (improvement opportunity)

    Args:
        user_id: User ID
        hardware_fingerprint: Hardware fingerprint from new submission

    Returns:
        dict: Previous submission data if found, None otherwise
    """
    previous = Submission.query.filter_by(
        user_id=user_id,
        hardware_fingerprint=hardware_fingerprint,
        verified=True
    ).order_by(Submission.submission_date.desc()).first()

    if previous:
        return {
            'id': previous.id,
            'fps_avg': previous.fps_avg,
            'submission_date': previous.submission_date
        }
    return None


def track_improvement(before_submission_id, after_submission, fixes_applied=None):
    """
    Create an improvement record linking before and after submissions

    Args:
        before_submission_id: ID of previous submission
        after_submission: New Submission object
        fixes_applied: List of fixes applied (e.g., ['thermal_paste', 'thermal_pads'])

    Returns:
        Improvement: Created improvement object
    """
    before = Submission.query.get(before_submission_id)
    if not before:
        return None

    # Calculate gains
    fps_gain = after_submission.fps_avg - before.fps_avg
    fps_gain_percent = (fps_gain / before.fps_avg) * 100 if before.fps_avg > 0 else 0

    # Create improvement record
    improvement = Improvement(
        user_id=after_submission.user_id,
        hardware_fingerprint=after_submission.hardware_fingerprint,
        before_submission_id=before.id,
        after_submission_id=after_submission.id,
        fps_before=before.fps_avg,
        fps_after=after_submission.fps_avg,
        fps_gain=fps_gain,
        fps_gain_percent=fps_gain_percent,
        fixes_applied=fixes_applied or []
    )

    db.session.add(improvement)
    db.session.commit()

    # Mark after submission as an improvement
    after_submission.is_improvement = True
    after_submission.improvement_percent = fps_gain_percent
    after_submission.parent_submission_id = before.id
    db.session.commit()

    # Check and award achievements
    check_and_award_achievements(improvement=improvement)

    return improvement


def detect_fixes_from_diagnostics(before_issues, after_submission):
    """
    Automatically detect which issues were fixed based on metrics

    Args:
        before_issues: List of DiagnosticIssue objects from before submission
        after_submission: New submission object

    Returns:
        list: List of fix types that were applied
    """
    fixes = []

    for issue in before_issues:
        if issue.issue_type == 'thermal_throttling':
            # Check if thermal issue was fixed
            if after_submission.gpu_temp_max and after_submission.gpu_temp_max < 83:
                fixes.append('thermal_paste')

        elif issue.issue_type == 'cpu_bottleneck':
            # Check if GPU utilization improved
            before_util = issue.submission.gpu_load_avg or 0
            after_util = after_submission.gpu_load_avg or 0
            if after_util > before_util + 10:
                fixes.append('cpu_upgrade')

        elif issue.issue_type == 'low_ram':
            # Check if RAM was upgraded
            try:
                before_ram = int(''.join(filter(str.isdigit, issue.submission.ram_total.split('GB')[0])))
                after_ram = int(''.join(filter(str.isdigit, after_submission.ram_total.split('GB')[0])))
                if after_ram > before_ram:
                    fixes.append('ram_upgrade')
            except:
                pass

    return fixes


def get_user_improvements(user_id, limit=10):
    """
    Get user's improvement history

    Args:
        user_id: User ID
        limit: Max number of improvements to return

    Returns:
        list: List of Improvement objects
    """
    return Improvement.query.filter_by(user_id=user_id).order_by(
        Improvement.created_at.desc()
    ).limit(limit).all()


def get_top_improvements(limit=50):
    """
    Get top improvements for "Most Improved" leaderboard

    Args:
        limit: Number of improvements to return

    Returns:
        list: List of Improvement objects sorted by gain percentage
    """
    return Improvement.query.filter(
        Improvement.fps_gain > 0
    ).order_by(
        Improvement.fps_gain_percent.desc()
    ).limit(limit).all()
