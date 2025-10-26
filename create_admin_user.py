"""
Create an admin user directly
"""
from app import create_app
from models import db, User

def create_admin(username, email, password):
    """Create a new admin user"""
    app = create_app()

    with app.app_context():
        # Check if user already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f"❌ User '{username}' already exists")
            return

        # Create new admin user
        user = User(
            username=username,
            email=email,
            is_admin=True
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"✅ Admin user '{username}' created successfully!")
        print(f"   Email: {email}")
        print(f"   Admin: Yes")
        print(f"\nYou can now log in at https://piggybankpc.uk/login")


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print("Usage: python create_admin_user.py <username> <email> <password>")
        print("Example: python create_admin_user.py DADDYPIGGY daddy@piggybankpc.uk MyPassword123")
    else:
        create_admin(sys.argv[1], sys.argv[2], sys.argv[3])
