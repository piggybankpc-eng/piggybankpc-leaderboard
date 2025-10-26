"""
PiggyBankPC Leaderboard - Best All-Rounder Routes
Shows systems with best balanced performance for gaming + AI
"""
from flask import Blueprint, render_template
from sqlalchemy import desc
from models import Submission

best_all_rounder_bp = Blueprint('best_all_rounder', __name__)


@best_all_rounder_bp.route('/best-all-rounder')
def index():
    """Best All-Rounder leaderboard - balanced gaming + AI performance"""

    # Get all submissions with both FPS and AI scores
    submissions = Submission.query.filter(
        Submission.verified == True,
        Submission.fps_avg.isnot(None),
        Submission.ai_tokens_per_sec.isnot(None)
    ).all()

    # Calculate all-rounder scores and sort
    scored_submissions = []
    for sub in submissions:
        score = sub.all_rounder_score
        if score:
            scored_submissions.append({
                'submission': sub,
                'score': score
            })

    # Sort by score (highest first)
    scored_submissions.sort(key=lambda x: x['score'], reverse=True)

    # Calculate stats
    total_all_rounders = len(scored_submissions)
    avg_score = sum(s['score'] for s in scored_submissions) / total_all_rounders if total_all_rounders > 0 else 0

    # Get best in each category
    best_fps = max((s['submission'].fps_avg for s in scored_submissions), default=0)
    best_tokens = max((s['submission'].ai_tokens_per_sec for s in scored_submissions), default=0)

    stats = {
        'total_all_rounders': total_all_rounders,
        'avg_score': round(avg_score, 1),
        'best_fps': round(best_fps, 1),
        'best_tokens': round(best_tokens, 1)
    }

    return render_template(
        'best_all_rounder.html',
        submissions=scored_submissions,
        stats=stats
    )
