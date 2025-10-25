"""
PiggyBankPC Leaderboard - Achievement System
Gamification to encourage users to improve their builds!
"""

from models import db, Achievement, Improvement


# Achievement Definitions
ACHIEVEMENTS = {
    'thermal_hero': {
        'title': '🔥 Thermal Hero',
        'description': 'Fixed thermal issues and gained 15+ FPS',
        'badge': '🔥',
        'criteria': {
            'min_fps_gain': 15,
            'issue_fixed': 'thermal_throttling'
        }
    },

    'performance_boost': {
        'title': '⚡ Performance Booster',
        'description': 'Improved performance by 20%+',
        'badge': '⚡',
        'criteria': {
            'min_percent_gain': 20
        }
    },

    'dedicated_tuner': {
        'title': '🔧 Dedicated Tuner',
        'description': 'Submitted 5+ benchmarks of same hardware',
        'badge': '🔧',
        'criteria': {
            'min_submissions': 5,
            'same_hardware': True
        }
    },

    'mega_improvement': {
        'title': '🚀 Mega Improvement',
        'description': 'Gained 30+ FPS in a single upgrade',
        'badge': '🚀',
        'criteria': {
            'min_fps_gain': 30
        }
    },

    'optimizer': {
        'title': '💎 Optimizer',
        'description': 'Watched tutorial video and improved score by 10+ FPS',
        'badge': '💎',
        'criteria': {
            'video_watched': True,
            'min_fps_gain': 10
        }
    },

    'first_submission': {
        'title': '🎯 First Steps',
        'description': 'Submitted your first benchmark!',
        'badge': '🎯',
        'criteria': {
            'first_submission': True
        }
    },

    'value_champion': {
        'title': '💰 Value Champion',
        'description': 'Achieved best price-per-FPS in your price range',
        'badge': '💰',
        'criteria': {
            'best_value_in_range': True
        }
    }
}


def check_and_award_achievements(improvement=None, user_id=None):
    """
    Check if a user qualifies for any achievements
    Award them automatically

    Args:
        improvement: Improvement object (for improvement-based achievements)
        user_id: User ID (for submission-based achievements)

    Returns:
        list: List of newly awarded Achievement objects
    """
    awarded = []

    if improvement:
        # Check improvement-based achievements
        for achievement_id, achievement in ACHIEVEMENTS.items():
            criteria = achievement['criteria']
            qualifies = True

            # Check min FPS gain
            if 'min_fps_gain' in criteria:
                if improvement.fps_gain < criteria['min_fps_gain']:
                    qualifies = False

            # Check percent gain
            if 'min_percent_gain' in criteria:
                if improvement.fps_gain_percent < criteria['min_percent_gain']:
                    qualifies = False

            # Check if specific issue was fixed
            if 'issue_fixed' in criteria:
                if not improvement.fixes_applied or criteria['issue_fixed'] not in improvement.fixes_applied:
                    qualifies = False

            # Award if qualifies and user doesn't already have it
            if qualifies:
                existing = Achievement.query.filter_by(
                    user_id=improvement.user_id,
                    achievement_type=achievement_id
                ).first()

                if not existing:
                    new_achievement = Achievement(
                        user_id=improvement.user_id,
                        achievement_type=achievement_id,
                        title=achievement['title'],
                        description=achievement['description'],
                        badge_emoji=achievement['badge'],
                        improvement_id=improvement.id
                    )
                    db.session.add(new_achievement)
                    awarded.append(new_achievement)

    if user_id:
        # Check user-based achievements
        from models import Submission

        # First submission achievement
        user_submissions = Submission.query.filter_by(user_id=user_id, verified=True).count()
        if user_submissions == 1:
            existing = Achievement.query.filter_by(
                user_id=user_id,
                achievement_type='first_submission'
            ).first()

            if not existing:
                new_achievement = Achievement(
                    user_id=user_id,
                    achievement_type='first_submission',
                    title=ACHIEVEMENTS['first_submission']['title'],
                    description=ACHIEVEMENTS['first_submission']['description'],
                    badge_emoji=ACHIEVEMENTS['first_submission']['badge']
                )
                db.session.add(new_achievement)
                awarded.append(new_achievement)

        # Dedicated tuner achievement (5+ submissions of same hardware)
        # Get user's submission grouped by hardware fingerprint
        from sqlalchemy import func
        hardware_counts = db.session.query(
            Submission.hardware_fingerprint,
            func.count(Submission.id).label('count')
        ).filter_by(user_id=user_id, verified=True).group_by(
            Submission.hardware_fingerprint
        ).having(func.count(Submission.id) >= 5).all()

        if hardware_counts:
            existing = Achievement.query.filter_by(
                user_id=user_id,
                achievement_type='dedicated_tuner'
            ).first()

            if not existing:
                new_achievement = Achievement(
                    user_id=user_id,
                    achievement_type='dedicated_tuner',
                    title=ACHIEVEMENTS['dedicated_tuner']['title'],
                    description=ACHIEVEMENTS['dedicated_tuner']['description'],
                    badge_emoji=ACHIEVEMENTS['dedicated_tuner']['badge']
                )
                db.session.add(new_achievement)
                awarded.append(new_achievement)

    # Commit all new achievements
    if awarded:
        db.session.commit()

    return awarded


def get_user_achievements(user_id):
    """
    Get all achievements for a user

    Args:
        user_id: User ID

    Returns:
        list: List of Achievement objects
    """
    return Achievement.query.filter_by(user_id=user_id).order_by(
        Achievement.unlocked_at.desc()
    ).all()


def get_achievement_progress(user_id):
    """
    Get user's progress towards locked achievements

    Args:
        user_id: User ID

    Returns:
        dict: Progress data for each achievement
    """
    from models import Submission

    progress = {}

    # Get user's unlocked achievements
    unlocked = {a.achievement_type for a in Achievement.query.filter_by(user_id=user_id).all()}

    # Calculate progress for locked achievements
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id not in unlocked:
            criteria = achievement['criteria']
            progress_data = {
                'title': achievement['title'],
                'description': achievement['description'],
                'badge': achievement['badge'],
                'progress': 0,
                'target': 100
            }

            # Calculate specific progress
            if 'min_submissions' in criteria:
                hardware_counts = db.session.query(
                    func.count(Submission.id)
                ).filter_by(user_id=user_id, verified=True).group_by(
                    Submission.hardware_fingerprint
                ).all()

                max_count = max([c[0] for c in hardware_counts], default=0)
                progress_data['progress'] = max_count
                progress_data['target'] = criteria['min_submissions']

            progress[achievement_id] = progress_data

    return progress
