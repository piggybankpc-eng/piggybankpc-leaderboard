"""
PiggyBankPC Leaderboard - Authentication Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse as url_parse
from models import db, User
from utils.email import send_verification_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []

        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        if not email or '@' not in email:
            errors.append('Valid email address required')
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        if password != confirm_password:
            errors.append('Passwords do not match')

        # Check if username exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken')

        # Check if email exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)

        # Generate verification token
        user.generate_verification_token()

        db.session.add(user)
        db.session.commit()

        # Send verification email
        try:
            send_verification_email(user)
            flash(f'Registration successful! Please check {email} for verification link.', 'success')
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
            flash('Registration successful! However, we couldn\'t send the verification email. Please contact support.', 'warning')

        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) |
            (User.email == username_or_email.lower())
        ).first()

        if user is None or not user.check_password(password):
            flash('Invalid username/email or password', 'danger')
            return render_template('login.html')

        # Check if email is verified
        if not user.email_verified:
            flash('Please verify your email address before logging in. Check your inbox for the verification link.', 'warning')
            return render_template('login.html')

        login_user(user, remember=remember)

        # Redirect to next page or index
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify user email with token"""

    # Find user with this token
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('auth.login'))

    # Verify the token
    if user.verify_email_token(token):
        db.session.commit()
        flash('Email verified successfully! You can now log in.', 'success')
    else:
        flash('Verification link has expired. Please contact support.', 'danger')

    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """Resend verification email"""

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        user = User.query.filter_by(email=email).first()

        if not user:
            # Don't reveal if email exists or not
            flash('If that email is registered, a verification link has been sent.', 'info')
            return redirect(url_for('auth.login'))

        if user.email_verified:
            flash('This email is already verified. You can log in.', 'info')
            return redirect(url_for('auth.login'))

        # Generate new token
        user.generate_verification_token()
        db.session.commit()

        # Send verification email
        try:
            send_verification_email(user)
            flash('Verification email sent! Please check your inbox.', 'success')
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
            flash('Failed to send email. Please try again later.', 'danger')

        return redirect(url_for('auth.login'))

    return render_template('resend_verification.html')
