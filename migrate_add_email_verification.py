#!/usr/bin/env python3
"""
Database Migration: Add Email Verification Fields
Adds email_verified, verification_token, and verification_token_expires to User table
"""
import sqlite3
from pathlib import Path

def migrate():
    """Add email verification fields to User table"""

    db_path = Path(__file__).parent / 'instance' / 'database.db'

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("   Please run the app first to create the database.")
        return False

    print(f"📊 Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # First, check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   Tables found: {', '.join(tables)}")

        # Find the user table (might be 'user', 'User', 'users', or 'Users')
        user_table = None
        for table in tables:
            if table.lower() in ['user', 'users']:
                user_table = table
                break

        if not user_table:
            print("❌ No user table found in database!")
            print("   Please ensure the app has been run to create tables.")
            conn.close()
            return False

        print(f"   Using table: {user_table}")

        # Check if columns already exist
        cursor.execute(f"PRAGMA table_info({user_table})")
        columns = [col[1] for col in cursor.fetchall()]

        migrations_needed = []

        if 'email_verified' not in columns:
            migrations_needed.append('email_verified')

        if 'verification_token' not in columns:
            migrations_needed.append('verification_token')

        if 'verification_token_expires' not in columns:
            migrations_needed.append('verification_token_expires')

        if not migrations_needed:
            print("✅ All email verification fields already exist!")
            conn.close()
            return True

        print(f"📝 Adding columns: {', '.join(migrations_needed)}")

        # Add email_verified column (default FALSE for new users)
        if 'email_verified' in migrations_needed:
            cursor.execute(f"""
                ALTER TABLE {user_table}
                ADD COLUMN email_verified BOOLEAN DEFAULT 0
            """)
            print("   ✓ Added email_verified column")

            # Set existing users to verified (grandfather them in)
            cursor.execute(f"""
                UPDATE {user_table}
                SET email_verified = 1
                WHERE email_verified IS NULL OR email_verified = 0
            """)
            print("   ✓ Set existing users to verified")

        # Add verification_token column (can't add UNIQUE constraint in SQLite ALTER TABLE)
        if 'verification_token' in migrations_needed:
            cursor.execute(f"""
                ALTER TABLE {user_table}
                ADD COLUMN verification_token VARCHAR(100)
            """)
            print("   ✓ Added verification_token column")

        # Add verification_token_expires column
        if 'verification_token_expires' in migrations_needed:
            cursor.execute(f"""
                ALTER TABLE {user_table}
                ADD COLUMN verification_token_expires DATETIME
            """)
            print("   ✓ Added verification_token_expires column")

        # Commit changes
        conn.commit()

        # Verify the changes
        cursor.execute(f"PRAGMA table_info({user_table})")
        columns_after = [col[1] for col in cursor.fetchall()]

        print("\n📋 User table columns after migration:")
        for col in columns_after:
            print(f"   • {col}")

        # Get count of verified users
        cursor.execute(f"SELECT COUNT(*) FROM {user_table} WHERE email_verified = 1")
        verified_count = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {user_table}")
        total_count = cursor.fetchone()[0]

        print(f"\n👥 Users: {verified_count}/{total_count} verified")

        conn.close()

        print("\n✅ Migration completed successfully!")
        print("\n📧 Email verification is now enabled:")
        print("   • New users must verify their email before logging in")
        print("   • Existing users are automatically verified")
        print("   • Verification emails will be sent upon registration")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("🔄 PiggyBankPC Leaderboard - Email Verification Migration")
    print("=" * 60)
    migrate()
