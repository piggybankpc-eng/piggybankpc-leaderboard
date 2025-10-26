"""
Quick script to make a user an admin
"""
from app import create_app
from models import db, User

def make_admin(username):
    """Make a user an admin"""
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(username=username).first()

        if not user:
            print(f"❌ User '{username}' not found")
            return

        if user.is_admin:
            print(f"✓ {username} is already an admin")
        else:
            user.is_admin = True
            db.session.commit()
            print(f"✅ {username} is now an admin!")


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <username>")
    else:
        make_admin(sys.argv[1])
