"""
PiggyBankPC Leaderboard - Diagnostic Analysis Engine
Detect performance issues and recommend fixes (with YouTube videos + affiliate products!)
"""

from models import db, DiagnosticIssue
from diagnostic_config import YOUTUBE_VIDEOS, get_product_with_link


def calculate_thermal_gain(temp_max):
    """
    Estimate performance loss from thermal throttling
    Based on typical GPU boost behavior

    Args:
        temp_max: Maximum GPU temperature reached

    Returns:
        int: Estimated performance loss percentage
    """
    if temp_max >= 90:
        return 25  # 25-35% loss
    elif temp_max >= 85:
        return 20  # 20-30% loss
    elif temp_max >= 83:
        return 15  # 15-25% loss
    else:
        return 0


def analyze_submission(submission):
    """
    Analyze a submission for common issues and improvement opportunities
    This is the MONEY-MAKER - detects issues and links to YouTube videos + products!

    Args:
        submission: Submission object

    Returns:
        list: List of detected issues (also saved to database)
    """
    issues = []

    # 1. THERMAL THROTTLING (High Priority) 🔥💰
    if submission.gpu_temp_max and submission.gpu_temp_max >= 83:
        severity = 'high' if submission.gpu_temp_max >= 85 else 'medium'
        potential_gain = calculate_thermal_gain(submission.gpu_temp_max)

        # Calculate potential FPS gain
        fps_gain_min = int(submission.fps_avg * potential_gain / 100)
        fps_gain_max = int(submission.fps_avg * (potential_gain + 10) / 100)

        # Check if user has Intel 13th/14th gen - add BIOS warning
        cpu_lower = submission.cpu_model.lower()
        intel_bios_note = ""
        if any(gen in cpu_lower for gen in ['13th', '14th', 'i9-13', 'i9-14', 'i7-13', 'i7-14', 'i5-13', 'i5-14']):
            intel_bios_note = " 🔴 IMPORTANT: You have an Intel 13th/14th gen CPU. High temps could be a sign of CPU degradation. Update your BIOS with Intel's latest microcode patch ASAP!"

        issue = DiagnosticIssue(
            submission_id=submission.id,
            issue_type='thermal_throttling',
            severity=severity,
            title='🔥 Thermal Throttling Detected!',
            description=f'Your GPU reached {submission.gpu_temp_max}°C and is throttling performance to protect itself.{intel_bios_note}',
            impact=f'You\'re losing approximately {potential_gain}% of your GPU\'s potential!',
            potential_fps_gain=f'+{fps_gain_min}-{fps_gain_max} FPS',
            fix_difficulty='Easy',
            fix_time='30-45 minutes',
            fix_cost='£15-25',
            youtube_video_id=YOUTUBE_VIDEOS.get('thermal_throttling'),
            youtube_title='How to Repaste Your GPU - Complete Guide',
            products=[
                get_product_with_link('Noctua NT-H1 3.5g'),
                get_product_with_link('thermal_pads 13w')
            ]
        )
        db.session.add(issue)
        issues.append(issue)

    # 2. CPU BOTTLENECK (Medium Priority) ⚠️💰
    if submission.gpu_load_avg and submission.gpu_load_avg < 85:
        # GPU not being fully utilized - CPU can't keep up
        potential_gain = (95 - submission.gpu_load_avg) * 0.5
        fps_gain_min = int(submission.fps_avg * potential_gain / 100)
        fps_gain_max = int(submission.fps_avg * (potential_gain + 15) / 100)

        # Build CPU recommendation based on current hardware
        cpu_recommendation = f"Consider upgrading to a faster CPU for your platform. Your current CPU: {submission.cpu_model}"

        # Add warning for Intel 13th/14th gen instability issues
        intel_13_14_warning = ""
        cpu_lower = submission.cpu_model.lower()
        if any(gen in cpu_lower for gen in ['13th', '14th', 'i9-13', 'i9-14', 'i7-13', 'i7-14', 'i5-13', 'i5-14']):
            intel_13_warning = " ⚠️ WARNING: Some Intel 13th/14th gen CPUs have known instability issues. If buying used, ask seller for proof of stability testing or consider older generations (12th gen or earlier). 🔴 CRITICAL: If you already have a 13th/14th gen CPU, UPDATE YOUR BIOS IMMEDIATELY with Intel's microcode fix to prevent permanent damage! Check your motherboard manufacturer's website."

        issue = DiagnosticIssue(
            submission_id=submission.id,
            issue_type='cpu_bottleneck',
            severity='medium',
            title='⚠️ CPU Bottleneck Detected',
            description=f'Your GPU is only at {submission.gpu_load_avg}% average utilization during gaming. {cpu_recommendation}{intel_13_14_warning}',
            impact='Your CPU can\'t feed data fast enough to keep your GPU busy! Check eBay or Facebook Marketplace for budget upgrades. AVOID Intel 13th/14th gen unless seller can prove stability. 🔴 If you have 13th/14th gen: Update BIOS NOW with Intel microcode patch!',
            potential_fps_gain=f'+{fps_gain_min}-{fps_gain_max} FPS',
            fix_difficulty='Medium',
            fix_time='1-2 hours',
            fix_cost='£40-150 (used market)',
            youtube_video_id=YOUTUBE_VIDEOS.get('cpu_bottleneck'),
            youtube_title='Is Your CPU Bottlenecking Your GPU? How to Tell',
            products=[]  # No affiliate program for CPUs - recommend checking used market
        )
        db.session.add(issue)
        issues.append(issue)

    # 3. LOW RAM (Low Priority) 📊💰
    if submission.ram_total:
        try:
            # Extract GB from string like "16GB" or "16 GB"
            ram_gb = int(''.join(filter(str.isdigit, submission.ram_total.split('GB')[0])))

            if ram_gb < 16:
                issue = DiagnosticIssue(
                    submission_id=submission.id,
                    issue_type='low_ram',
                    severity='low',
                    title='📊 More RAM Recommended',
                    description=f'You have {ram_gb}GB RAM. Modern games benefit from 16GB+ for smoother performance.',
                    impact='May experience stuttering in memory-heavy games, longer load times',
                    potential_fps_gain='+5-15 FPS in some games',
                    fix_difficulty='Easy',
                    fix_time='10 minutes',
                    fix_cost='£18-25',
                    youtube_video_id=YOUTUBE_VIDEOS.get('low_ram'),
                    youtube_title='RAM Upgrade Guide - Does More RAM = More FPS?',
                    products=[
                        get_product_with_link('ram_ddr4_16gb'),
                        get_product_with_link('ram_ddr3_16gb')
                    ]
                )
                db.session.add(issue)
                issues.append(issue)
        except (ValueError, IndexError):
            pass  # Couldn't parse RAM, skip this check

    # Save all issues to database
    if issues:
        db.session.commit()

    return issues


def get_submission_rank(submission):
    """
    Calculate submission's rank on the leaderboard

    Args:
        submission: Submission object

    Returns:
        int: Rank (1 = best)
    """
    from models import Submission

    # Count submissions with higher FPS
    rank = Submission.query.filter(
        Submission.verified == True,
        Submission.fps_avg > submission.fps_avg
    ).count() + 1

    return rank


def detect_improvement_opportunity(user_id, hardware_fingerprint):
    """
    Check if user has submitted this hardware before
    If yes, link submissions for improvement tracking

    Args:
        user_id: User ID
        hardware_fingerprint: Hardware fingerprint

    Returns:
        dict: Previous submission data if found, None otherwise
    """
    from models import Submission

    previous = Submission.query.filter_by(
        user_id=user_id,
        hardware_fingerprint=hardware_fingerprint,
        verified=True
    ).order_by(Submission.submission_date.desc()).first()

    if previous:
        return {
            'id': previous.id,
            'fps_avg': previous.fps_avg,
            'submission_date': previous.submission_date,
            'gpu_temp_max': previous.gpu_temp_max,
            'gpu_load_avg': previous.gpu_load_avg
        }

    return None
