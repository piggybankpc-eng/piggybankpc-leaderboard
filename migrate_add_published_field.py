#!/usr/bin/env python3
"""
Database Migration: Add Published Field to Submissions
Adds 'published' field to control visibility of official submissions (anti-spoiler)
"""
import sqlite3
from pathlib import Path

def migrate():
    """Add published field to submissions table"""

    db_path = Path(__file__).parent / 'instance' / 'database.db'

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("   Please run the app first to create the database.")
        return False

    print(f"📊 Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   Tables found: {', '.join(tables)}")

        # Find submissions table
        if 'submissions' not in tables:
            print("❌ No submissions table found in database!")
            conn.close()
            return False

        # Check if published column already exists
        cursor.execute("PRAGMA table_info(submissions)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'published' in columns:
            print("✅ 'published' field already exists!")
            conn.close()
            return True

        print(f"📝 Adding 'published' column to submissions table...")

        # Add published column (default TRUE for existing submissions)
        cursor.execute("""
            ALTER TABLE submissions
            ADD COLUMN published BOOLEAN DEFAULT 1
        """)
        print("   ✓ Added 'published' column")

        # Set all existing submissions to published
        cursor.execute("""
            UPDATE submissions
            SET published = 1
            WHERE published IS NULL
        """)
        print("   ✓ Set existing submissions to published")

        # Commit changes
        conn.commit()

        # Verify the changes
        cursor.execute("PRAGMA table_info(submissions)")
        columns_after = [col[1] for col in cursor.fetchall()]

        print("\n📋 Submissions table now has 'published' field!")

        # Get count of published vs unpublished
        cursor.execute("SELECT COUNT(*) FROM submissions WHERE published = 1")
        published_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM submissions WHERE published = 0 OR published IS NULL")
        unpublished_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM submissions")
        total_count = cursor.fetchone()[0]

        print(f"\n📊 Submissions: {published_count} published, {unpublished_count} unpublished ({total_count} total)")

        conn.close()

        print("\n✅ Migration completed successfully!")
        print("\n🎬 Anti-Spoiler Feature is now enabled:")
        print("   • Official submissions can be marked as unpublished")
        print("   • Unpublished submissions are hidden from leaderboards")
        print("   • Add YouTube URL to publish and reveal results")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("🔄 PiggyBankPC Leaderboard - Anti-Spoiler Migration")
    print("=" * 60)
    migrate()
