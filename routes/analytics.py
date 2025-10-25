"""
PiggyBankPC Leaderboard - Analytics & Revenue Tracking Routes
"""

from flask import Blueprint, jsonify, request
from flask_login import current_user
from models import db, AnalyticsEvent
from datetime import datetime
import json

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/api/analytics/event', methods=['POST'])
def track_event():
    """
    Track user interaction events (video clicks, affiliate clicks)
    This is the MONEY-MAKER - tracks every potential revenue action!

    Expected JSON:
    {
        "event_type": "video_click" | "affiliate_click",
        "event_data": {
            "issue_type": "thermal_throttling",
            "video_id": "ABC123" | "product": "Arctic MX-5"
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'event_type' not in data:
            return jsonify({'status': 'error', 'message': 'Missing event_type'}), 400

        event = AnalyticsEvent(
            user_id=current_user.id if current_user.is_authenticated else None,
            event_type=data.get('event_type'),
            event_data=json.dumps(data.get('event_data', {})),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        db.session.add(event)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'event_id': event.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@analytics_bp.route('/api/analytics/stats', methods=['GET'])
def analytics_stats():
    """
    Get analytics statistics (for admin dashboard)
    Shows video views, affiliate clicks, conversion potential
    """
    from flask_login import login_required
    from functools import wraps

    # Simple admin check
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403

    # Count events by type
    video_clicks = AnalyticsEvent.query.filter_by(event_type='video_click').count()
    affiliate_clicks = AnalyticsEvent.query.filter_by(event_type='affiliate_click').count()

    # Estimated revenue (conservative)
    # Video clicks: £0.003 per view (£3 CPM)
    # Affiliate clicks: 20% conversion rate × £1 average commission
    estimated_video_revenue = video_clicks * 0.003
    estimated_affiliate_revenue = affiliate_clicks * 0.20 * 1.00

    return jsonify({
        'status': 'success',
        'stats': {
            'video_clicks': video_clicks,
            'affiliate_clicks': affiliate_clicks,
            'estimated_video_revenue': round(estimated_video_revenue, 2),
            'estimated_affiliate_revenue': round(estimated_affiliate_revenue, 2),
            'total_estimated_revenue': round(estimated_video_revenue + estimated_affiliate_revenue, 2)
        }
    })


@analytics_bp.route('/api/analytics/events/recent', methods=['GET'])
def recent_events():
    """
    Get recent analytics events (for admin dashboard)
    Shows last 100 events with user info
    """
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403

    events = AnalyticsEvent.query.order_by(
        AnalyticsEvent.created_at.desc()
    ).limit(100).all()

    return jsonify({
        'status': 'success',
        'events': [
            {
                'id': event.id,
                'event_type': event.event_type,
                'event_data': json.loads(event.event_data) if event.event_data else {},
                'user_id': event.user_id,
                'created_at': event.created_at.isoformat(),
                'ip_address': event.ip_address
            }
            for event in events
        ]
    })
