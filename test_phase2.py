#!/usr/bin/env python3
"""
Phase 2 Integration Test Script
Verifies all components are properly installed and importable
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all Phase 2 modules can be imported"""
    print("🧪 Testing Phase 2 imports...\n")

    errors = []

    # Test core models
    try:
        from models import db, User, Submission, DiagnosticIssue, Improvement, Achievement, AnalyticsEvent
        print("✅ Models imported successfully")
        print(f"   - DiagnosticIssue: {DiagnosticIssue.__tablename__}")
        print(f"   - Improvement: {Improvement.__tablename__}")
        print(f"   - Achievement: {Achievement.__tablename__}")
        print(f"   - AnalyticsEvent: {AnalyticsEvent.__tablename__}")
    except Exception as e:
        errors.append(f"❌ Models import failed: {e}")
        print(f"❌ Models import failed: {e}")

    # Test utils
    try:
        from utils.diagnostics import analyze_submission, get_submission_rank
        print("✅ utils.diagnostics imported successfully")
    except Exception as e:
        errors.append(f"❌ utils.diagnostics import failed: {e}")
        print(f"❌ utils.diagnostics import failed: {e}")

    try:
        from utils.achievements import check_and_award_achievements, ACHIEVEMENTS
        print(f"✅ utils.achievements imported successfully")
        print(f"   - {len(ACHIEVEMENTS)} achievements defined")
    except Exception as e:
        errors.append(f"❌ utils.achievements import failed: {e}")
        print(f"❌ utils.achievements import failed: {e}")

    try:
        from utils.improvements import track_improvement, detect_improvement_opportunity
        print("✅ utils.improvements imported successfully")
    except Exception as e:
        errors.append(f"❌ utils.improvements import failed: {e}")
        print(f"❌ utils.improvements import failed: {e}")

    # Test config
    try:
        from config.diagnostic_config import YOUTUBE_VIDEOS, AFFILIATE_LINKS, PRODUCTS
        print(f"✅ config.diagnostic_config imported successfully")
        print(f"   - {len(YOUTUBE_VIDEOS)} video configs")
        print(f"   - {len(AFFILIATE_LINKS)} affiliate links")
        print(f"   - {len(PRODUCTS)} products")
    except Exception as e:
        errors.append(f"❌ config.diagnostic_config import failed: {e}")
        print(f"❌ config.diagnostic_config import failed: {e}")

    # Test routes
    try:
        from routes.diagnostics import diagnostics_bp
        print("✅ routes.diagnostics imported successfully")
    except Exception as e:
        errors.append(f"❌ routes.diagnostics import failed: {e}")
        print(f"❌ routes.diagnostics import failed: {e}")

    try:
        from routes.most_improved import most_improved_bp
        print("✅ routes.most_improved imported successfully")
    except Exception as e:
        errors.append(f"❌ routes.most_improved import failed: {e}")
        print(f"❌ routes.most_improved import failed: {e}")

    try:
        from routes.analytics import analytics_bp
        print("✅ routes.analytics imported successfully")
    except Exception as e:
        errors.append(f"❌ routes.analytics import failed: {e}")
        print(f"❌ routes.analytics import failed: {e}")

    print()
    return errors


def test_files():
    """Test that all required files exist"""
    print("📁 Testing Phase 2 files...\n")

    required_files = [
        'templates/diagnostics.html',
        'templates/most_improved.html',
        'routes/diagnostics.py',
        'routes/most_improved.py',
        'routes/analytics.py',
        'static/js/analytics.js',
        'utils/__init__.py',
        'utils/diagnostics.py',
        'utils/achievements.py',
        'utils/improvements.py',
        'config/__init__.py',
        'config/diagnostic_config.py',
        'PHASE2_COMPLETE.md',
        'PHASE2_DELIVERY.md',
        'PHASE2_FILES.md'
    ]

    missing = []
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing.append(file)

    print()
    return missing


def test_app():
    """Test that app can be created"""
    print("🚀 Testing Flask app creation...\n")

    try:
        from app import create_app
        app = create_app('development')
        print("✅ Flask app created successfully")

        # Check blueprints
        blueprints = list(app.blueprints.keys())
        print(f"✅ {len(blueprints)} blueprints registered:")
        for bp in blueprints:
            print(f"   - {bp}")

        # Check Phase 2 blueprints
        phase2_bps = ['diagnostics', 'most_improved', 'analytics']
        for bp in phase2_bps:
            if bp in blueprints:
                print(f"✅ Phase 2 blueprint '{bp}' registered")
            else:
                print(f"❌ Phase 2 blueprint '{bp}' NOT registered")

        print()
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        print()
        return False


def main():
    print("=" * 60)
    print("🎉 PHASE 2 INTEGRATION TEST")
    print("=" * 60)
    print()

    # Run tests
    import_errors = test_imports()
    missing_files = test_files()
    app_created = test_app()

    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    if not import_errors and not missing_files and app_created:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Phase 2 is fully integrated and ready to launch! 🚀")
        print()
        print("Next steps:")
        print("1. Update config/diagnostic_config.py with YOUR YouTube IDs")
        print("2. Add YOUR affiliate links")
        print("3. Run: python app.py")
        print("4. Test at: http://localhost:5555")
        print("5. Deploy and start making money! 💰")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print()
        if import_errors:
            print(f"Import errors: {len(import_errors)}")
            for error in import_errors:
                print(f"  - {error}")
        if missing_files:
            print(f"Missing files: {len(missing_files)}")
            for file in missing_files:
                print(f"  - {file}")
        if not app_created:
            print("App creation failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
