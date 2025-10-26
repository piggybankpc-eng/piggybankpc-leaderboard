"""
Email utilities for PiggyBankPC Leaderboard
"""
from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")


def send_email(subject, recipients, text_body, html_body):
    """
    Send email with both text and HTML versions

    Args:
        subject: Email subject
        recipients: List of email addresses
        text_body: Plain text version
        html_body: HTML version
    """
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=recipients
    )
    msg.body = text_body
    msg.html = html_body

    # Send asynchronously to avoid blocking
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()


def send_verification_email(user):
    """
    Send email verification link to user

    Args:
        user: User object with email and verification_token
    """
    token = user.verification_token

    # Create verification URL
    verify_url = f"https://{current_app.config['DOMAIN']}/verify-email/{token}"

    # Plain text version
    text_body = f"""
Hello {user.username},

Welcome to PiggyBankPC Leaderboard!

Please verify your email address by clicking the link below:

{verify_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
The PiggyBankPC Team
{current_app.config['YOUTUBE_CHANNEL']}
    """

    # HTML version
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #0d6efd; color: white; padding: 20px; text-center; border-radius: 5px 5px 0 0; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: #0d6efd;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐷 PiggyBankPC Leaderboard</h1>
        </div>
        <div class="content">
            <h2>Hello {user.username}!</h2>
            <p>Welcome to PiggyBankPC Leaderboard - the ultimate platform for gaming FPS and AI/LLM benchmarking!</p>

            <p>Please verify your email address to activate your account:</p>

            <p style="text-align: center;">
                <a href="{verify_url}" class="button">Verify Email Address</a>
            </p>

            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: white; padding: 10px; border-radius: 3px;">
                {verify_url}
            </p>

            <p><strong>This link will expire in 24 hours.</strong></p>

            <div class="footer">
                <p>If you didn't create an account, please ignore this email.</p>
                <p>
                    Best regards,<br>
                    The PiggyBankPC Team<br>
                    <a href="https://youtube.com/{current_app.config['YOUTUBE_CHANNEL']}">{current_app.config['YOUTUBE_CHANNEL']}</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
    """

    send_email(
        subject='Verify your PiggyBankPC Leaderboard account',
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    )


def send_password_reset_email(user, token):
    """
    Send password reset email (for future use)

    Args:
        user: User object
        token: Password reset token
    """
    reset_url = f"https://{current_app.config['DOMAIN']}/reset-password/{token}"

    text_body = f"""
Hello {user.username},

Click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email.

Best regards,
The PiggyBankPC Team
    """

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #dc3545; color: white; padding: 20px; text-center; border-radius: 5px 5px 0 0; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: #dc3545;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Password Reset</h1>
        </div>
        <div class="content">
            <h2>Hello {user.username},</h2>
            <p>You requested a password reset for your PiggyBankPC Leaderboard account.</p>

            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>

            <p><strong>This link will expire in 1 hour.</strong></p>

            <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
        </div>
    </div>
</body>
</html>
    """

    send_email(
        subject='Reset your PiggyBankPC password',
        recipients=[user.email],
        text_body=text_body,
        html_body=html_body
    )
