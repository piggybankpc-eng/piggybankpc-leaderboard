"""
Database Migration Script: Add Official Builds Support
Adds is_official, youtube_video_url, and build_name fields to submissions table
"""
from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    """Run database migration"""
    app = create_app()

    with app.app_context():
        print("Starting migration...")

        try:
            # Check if columns already exist (SQLite method)
            result = db.session.execute(text("""
                PRAGMA table_info(submissions)
            """))

            existing_columns = [row[1] for row in result]  # Column name is second field
            print(f"Existing columns: {existing_columns}")

            # Add is_official column if it doesn't exist
            if 'is_official' not in existing_columns:
                print("Adding is_official column...")
                db.session.execute(text("""
                    ALTER TABLE submissions
                    ADD COLUMN is_official BOOLEAN DEFAULT FALSE
                """))
                db.session.execute(text("""
                    CREATE INDEX ix_submissions_is_official ON submissions(is_official)
                """))
                print("✓ is_official column added")
            else:
                print("✓ is_official column already exists")

            # Add youtube_video_url column if it doesn't exist
            if 'youtube_video_url' not in existing_columns:
                print("Adding youtube_video_url column...")
                db.session.execute(text("""
                    ALTER TABLE submissions
                    ADD COLUMN youtube_video_url VARCHAR(500)
                """))
                print("✓ youtube_video_url column added")
            else:
                print("✓ youtube_video_url column already exists")

            # Add build_name column if it doesn't exist
            if 'build_name' not in existing_columns:
                print("Adding build_name column...")
                db.session.execute(text("""
                    ALTER TABLE submissions
                    ADD COLUMN build_name VARCHAR(200)
                """))
                print("✓ build_name column added")
            else:
                print("✓ build_name column already exists")

            db.session.commit()
            print("\n✅ Migration completed successfully!")

            # Show summary
            result = db.session.execute(text("SELECT COUNT(*) FROM submissions"))
            total_submissions = result.scalar()
            print(f"\nDatabase Status:")
            print(f"- Total submissions: {total_submissions}")
            print(f"- New fields added: is_official, youtube_video_url, build_name")
            print(f"- All existing submissions have is_official=FALSE by default")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise


if __name__ == '__main__':
    migrate()
