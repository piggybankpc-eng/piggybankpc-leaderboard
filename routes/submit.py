"""
PiggyBankPC Leaderboard - Submission Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Submission, DiagnosticIssue, Improvement
from security import BenchmarkSecurity
from utils.diagnostics import analyze_submission, get_submission_rank
from utils.improvements import track_improvement, detect_fixes_from_diagnostics, detect_improvement_opportunity
from utils.achievements import check_and_award_achievements
import os
from pathlib import Path

submit_bp = Blueprint('submit', __name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def extract_submission_data(validated_results):
    """
    Extract submission data from validated results

    Args:
        validated_results: Validated benchmark results from security module

    Returns:
        dict: Extracted data ready for database
    """
    try:
        results = validated_results.get('results', {})
        system_info = results.get('system_info', {})
        fps_data = results.get('fps', {})
        ai_data = results.get('ai', {})
        cpu_data = results.get('cpu', {})

        # Extract system information
        cpu = system_info.get('cpu', {})
        gpu = system_info.get('gpu', {})
        ram = system_info.get('ram', {})

        data = {
            'hardware_fingerprint': validated_results.get('hardware_fingerprint', ''),
            'cpu_model': cpu.get('model', 'Unknown'),
            'gpu_model': gpu.get('model', 'Unknown'),
            'gpu_price': system_info.get('gpu_price', 0.0),
            'ram_total': ram.get('total', 'Unknown'),
            'benchmark_version': validated_results.get('version', '1.0.0'),
            'benchmark_timestamp': validated_results.get('timestamp', '')
        }

        # Extract FPS benchmark results
        if fps_data.get('status') == 'completed':
            data['fps_avg'] = fps_data.get('average_fps', 0.0)
            data['fps_min'] = fps_data.get('min_fps', 0.0)
            data['fps_max'] = fps_data.get('max_fps', 0.0)

        # Phase 2: Extract GPU metrics for diagnostic analysis
        gpu_metrics = fps_data.get('gpu_metrics', {})
        if gpu_metrics:
            data['gpu_temp_max'] = gpu_metrics.get('temp_max', 0.0)
            data['gpu_temp_avg'] = gpu_metrics.get('temp_avg', 0.0)
            data['gpu_load_avg'] = gpu_metrics.get('load_avg', 0.0)

        # Extract AI benchmark results
        if ai_data.get('status') == 'completed':
            data['ai_tokens_per_sec'] = ai_data.get('tokens_per_second', 0.0)

        # Extract CPU benchmark results
        if cpu_data.get('status') == 'completed':
            # Support different CPU benchmark types
            if cpu_data.get('benchmark_type') == 'geekbench':
                data['cpu_score'] = cpu_data.get('multi_core_score', 0.0)
            else:
                data['cpu_score'] = cpu_data.get('events_per_second', 0.0)

        return data

    except Exception as e:
        current_app.logger.error(f"Failed to extract submission data: {str(e)}")
        return None


@submit_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    """Handle benchmark submission uploads"""

    if request.method == 'POST':
        # Check if file was uploaded
        if 'pbr_file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)

        file = request.files['pbr_file']

        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a .pbr file', 'danger')
            return redirect(request.url)

        try:
            # Read file content
            file_content = file.read().decode('utf-8')

            # Initialize security module
            security = BenchmarkSecurity(
                base_dir=current_app.config['BASE_DIR'],
                signing_key=current_app.config['BENCHMARK_SECURITY_KEY']
            )

            # Validate submission
            validated_results = security.validate_submission_content(file_content)

            if not validated_results:
                flash('Invalid submission file. The signature verification failed. '
                      'This file may have been tampered with or corrupted.', 'danger')
                return redirect(request.url)

            # Extract data
            submission_data = extract_submission_data(validated_results)

            if not submission_data:
                flash('Failed to extract benchmark data from submission.', 'danger')
                return redirect(request.url)

            # Save file to uploads directory
            filename = secure_filename(file.filename)
            upload_path = Path(current_app.config['UPLOAD_FOLDER'])
            upload_path.mkdir(exist_ok=True, parents=True)

            # Add user ID and timestamp to filename to ensure uniqueness
            unique_filename = f"{current_user.id}_{submission_data['hardware_fingerprint'][:8]}_{filename}"
            filepath = upload_path / unique_filename

            # Write the file
            with open(filepath, 'w') as f:
                f.write(file_content)

            # Create submission record
            submission = Submission(
                user_id=current_user.id,
                pbr_filename=unique_filename,
                **submission_data
            )

            db.session.add(submission)
            db.session.commit()

            # ========== PHASE 2: DIAGNOSTIC ANALYSIS & IMPROVEMENT TRACKING ==========

            # Check for previous submissions (improvement tracking)
            previous = detect_improvement_opportunity(
                current_user.id,
                submission_data['hardware_fingerprint']
            )

            improvement_obj = None
            if previous:
                # This is a re-submission - track improvement!
                current_app.logger.info(f"Detected re-submission for user {current_user.id}")

                # Get diagnostic issues from previous submission
                before_issues = DiagnosticIssue.query.filter_by(
                    submission_id=previous['id']
                ).all()

                # Auto-detect which fixes were applied
                fixes = detect_fixes_from_diagnostics(before_issues, submission)

                # Track the improvement
                improvement_obj = track_improvement(
                    before_submission_id=previous['id'],
                    after_submission=submission,
                    fixes_applied=fixes
                )

                current_app.logger.info(f"Improvement tracked: +{improvement_obj.fps_gain:.1f} FPS")

            # Run diagnostic analysis on this submission
            issues = analyze_submission(submission)
            current_app.logger.info(f"Diagnostic analysis complete: {len(issues)} issues detected")

            # Award "First Submission" achievement if this is their first
            check_and_award_achievements(user_id=current_user.id)

            # If there was an improvement, check for improvement-based achievements
            if improvement_obj:
                check_and_award_achievements(
                    user_id=current_user.id,
                    improvement=improvement_obj
                )

            # ========== END PHASE 2 ==========

            # Redirect to diagnostic results page (the money-maker!)
            flash('Submission successful! View your diagnostic report below.', 'success')
            return redirect(url_for('diagnostics.view_diagnostics', submission_id=submission.id))

        except Exception as e:
            current_app.logger.error(f"Submission processing error: {str(e)}")
            flash('An error occurred while processing your submission. Please try again.', 'danger')
            return redirect(request.url)

    return render_template('submit.html')
