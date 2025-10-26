"""
PiggyBankPC Leaderboard - Official Builds Routes
Admin-only routes for managing official PiggyBankPC builds
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Submission, DiagnosticIssue
from security import BenchmarkSecurity
from utils.diagnostics import analyze_submission
from pathlib import Path
from functools import wraps

official_builds_bp = Blueprint('official_builds', __name__)


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


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def extract_submission_data(validated_results):
    """
    Extract submission data from validated results
    (Shared with submit.py - could be refactored to utils)
    """
    try:
        results = validated_results.get('results', {})
        system_info = results.get('system_info', {})
        fps_data = results.get('fps', {})
        ai_data = results.get('ai', {})
        cpu_data = results.get('cpu', {})

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

        # Extract GPU metrics
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
            if cpu_data.get('benchmark_type') == 'geekbench':
                data['cpu_score'] = cpu_data.get('multi_core_score', 0.0)
            else:
                data['cpu_score'] = cpu_data.get('events_per_second', 0.0)

        return data

    except Exception as e:
        current_app.logger.error(f"Failed to extract submission data: {str(e)}")
        return None


@official_builds_bp.route('/official-builds')
def index():
    """Display official PiggyBankPC builds leaderboard"""

    # Get only official builds
    query = Submission.query.filter_by(is_official=True, verified=True)

    # Sort by FPS (highest first)
    query = query.order_by(Submission.fps_avg.desc())

    submissions = query.all()

    # Calculate stats for official builds
    total_builds = len(submissions)
    avg_fps = sum(s.fps_avg for s in submissions if s.fps_avg) / total_builds if total_builds > 0 else 0
    avg_tokens = sum(s.ai_tokens_per_sec for s in submissions if s.ai_tokens_per_sec) / len([s for s in submissions if s.ai_tokens_per_sec]) if any(s.ai_tokens_per_sec for s in submissions) else 0

    stats = {
        'total_builds': total_builds,
        'avg_fps': round(avg_fps, 1),
        'avg_tokens': round(avg_tokens, 1)
    }

    return render_template(
        'official_builds.html',
        submissions=submissions,
        stats=stats
    )


@official_builds_bp.route('/official-builds/submit', methods=['GET', 'POST'])
@admin_required
def submit():
    """Admin-only submission for official PiggyBankPC builds"""

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

        # Get YouTube URL and build name from form
        youtube_url = request.form.get('youtube_url', '').strip()
        build_name = request.form.get('build_name', '').strip()

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
                flash('Invalid submission file. The signature verification failed.', 'danger')
                return redirect(request.url)

            # Extract data
            submission_data = extract_submission_data(validated_results)

            if not submission_data:
                flash('Failed to extract benchmark data from submission.', 'danger')
                return redirect(request.url)

            # Save file
            filename = secure_filename(file.filename)
            upload_path = Path(current_app.config['UPLOAD_FOLDER'])
            upload_path.mkdir(exist_ok=True, parents=True)

            unique_filename = f"official_{current_user.id}_{submission_data['hardware_fingerprint'][:8]}_{filename}"
            filepath = upload_path / unique_filename

            with open(filepath, 'w') as f:
                f.write(file_content)

            # Create official submission record
            submission = Submission(
                user_id=current_user.id,
                pbr_filename=unique_filename,
                is_official=True,  # Mark as official build
                youtube_video_url=youtube_url if youtube_url else None,
                build_name=build_name if build_name else None,
                **submission_data
            )

            db.session.add(submission)
            db.session.commit()

            # Run diagnostic analysis
            issues = analyze_submission(submission)
            current_app.logger.info(f"Official build submitted: {len(issues)} issues detected")

            flash(f'Official build "{build_name or "Untitled"}" submitted successfully!', 'success')
            return redirect(url_for('official_builds.index'))

        except Exception as e:
            current_app.logger.error(f"Official build submission error: {str(e)}")
            flash('An error occurred while processing your submission. Please try again.', 'danger')
            return redirect(request.url)

    return render_template('official_builds_submit.html')


@official_builds_bp.route('/official-builds/<int:submission_id>/delete', methods=['POST'])
@admin_required
def delete(submission_id):
    """Admin-only deletion of official builds"""

    submission = Submission.query.get_or_404(submission_id)

    if not submission.is_official:
        flash('This is not an official build.', 'danger')
        return redirect(url_for('official_builds.index'))

    try:
        # Delete associated file if it exists
        if submission.pbr_filename:
            filepath = Path(current_app.config['UPLOAD_FOLDER']) / submission.pbr_filename
            if filepath.exists():
                filepath.unlink()

        db.session.delete(submission)
        db.session.commit()

        flash('Official build deleted successfully.', 'success')
    except Exception as e:
        current_app.logger.error(f"Delete error: {str(e)}")
        flash('Error deleting build.', 'danger')

    return redirect(url_for('official_builds.index'))
