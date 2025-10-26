"""
PiggyBankPC Leaderboard - Leaderboard Routes
"""
from flask import Blueprint, render_template, request
from sqlalchemy import desc, asc
from models import db, Submission, User
from datetime import datetime, timedelta

leaderboard_bp = Blueprint('leaderboard', __name__)


@leaderboard_bp.route('/leaderboard')
def index():
    """Main leaderboard page with filtering and sorting"""

    # Get filter parameters
    sort_by = request.args.get('sort', 'fps_avg')
    order = request.args.get('order', 'desc')
    price_filter = request.args.get('price', 'all')
    gpu_brand = request.args.get('gpu_brand', 'all')
    time_period = request.args.get('time', 'all')
    page = request.args.get('page', 1, type=int)

    # Start with base query - exclude unpublished official builds (anti-spoiler)
    query = Submission.query.filter_by(verified=True, published=True)

    # Apply price filter
    if price_filter == 'under100':
        query = query.filter(Submission.gpu_price < 100)
    elif price_filter == '100-200':
        query = query.filter(Submission.gpu_price >= 100, Submission.gpu_price <= 200)
    elif price_filter == 'over200':
        query = query.filter(Submission.gpu_price > 200)

    # Apply GPU brand filter
    if gpu_brand != 'all':
        if gpu_brand == 'nvidia':
            query = query.filter(
                (Submission.gpu_model.ilike('%nvidia%')) |
                (Submission.gpu_model.ilike('%gtx%')) |
                (Submission.gpu_model.ilike('%rtx%'))
            )
        elif gpu_brand == 'amd':
            query = query.filter(
                (Submission.gpu_model.ilike('%amd%')) |
                (Submission.gpu_model.ilike('%radeon%')) |
                (Submission.gpu_model.ilike('%rx%'))
            )
        elif gpu_brand == 'intel':
            query = query.filter(Submission.gpu_model.ilike('%intel%'))

    # Apply time period filter
    if time_period == 'week':
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = query.filter(Submission.submission_date >= week_ago)
    elif time_period == 'month':
        month_ago = datetime.utcnow() - timedelta(days=30)
        query = query.filter(Submission.submission_date >= month_ago)

    # Apply sorting
    if sort_by == 'tokens':
        sort_column = Submission.ai_tokens_per_sec
    elif sort_by == 'fps':
        sort_column = Submission.fps_avg
    else:
        sort_column = getattr(Submission, sort_by, Submission.fps_avg)

    if order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Add secondary sort by submission date
    query = query.order_by(desc(Submission.submission_date))

    # Paginate results
    per_page = 20
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    submissions = pagination.items

    # Get statistics - exclude unpublished submissions
    total_submissions = Submission.query.filter_by(verified=True, published=True).count()
    unique_users = db.session.query(Submission.user_id).filter(
        Submission.verified == True,
        Submission.published == True
    ).distinct().count()
    avg_fps = db.session.query(db.func.avg(Submission.fps_avg)).filter(
        Submission.verified == True,
        Submission.published == True
    ).scalar() or 0
    avg_tokens = db.session.query(db.func.avg(Submission.ai_tokens_per_sec)).filter(
        Submission.ai_tokens_per_sec.isnot(None),
        Submission.verified == True,
        Submission.published == True
    ).scalar() or 0

    stats = {
        'total_submissions': total_submissions,
        'unique_users': unique_users,
        'avg_fps': round(avg_fps, 1),
        'avg_tokens': round(avg_tokens, 1)
    }

    return render_template(
        'leaderboard.html',
        submissions=submissions,
        pagination=pagination,
        stats=stats,
        sort_by=sort_by,
        order=order,
        price_filter=price_filter,
        gpu_brand=gpu_brand,
        time_period=time_period
    )
