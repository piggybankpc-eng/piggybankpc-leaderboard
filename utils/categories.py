"""
PiggyBankPC Leaderboard - Category System
Defines valid resolution/quality combinations for fair competition
"""

# Valid leaderboard categories
# Format: (resolution, quality)
VALID_CATEGORIES = [
    # 720p
    ('1280x720', 'Low'),
    ('1280x720', 'Ultra'),

    # 1080p
    ('1920x1080', 'Low'),
    ('1920x1080', 'Medium'),
    ('1920x1080', 'High'),
    ('1920x1080', 'Ultra'),

    # 1440p
    ('2560x1440', 'Low'),
    ('2560x1440', 'Medium'),
    ('2560x1440', 'High'),
    ('2560x1440', 'Ultra'),
]

# Category display names
CATEGORY_NAMES = {
    ('1280x720', 'Low'): '720p Low',
    ('1280x720', 'Ultra'): '720p Ultra',
    ('1920x1080', 'Low'): '1080p Low',
    ('1920x1080', 'Medium'): '1080p Medium',
    ('1920x1080', 'High'): '1080p High',
    ('1920x1080', 'Ultra'): '1080p Ultra',
    ('2560x1440', 'Low'): '1440p Low',
    ('2560x1440', 'Medium'): '1440p Medium',
    ('2560x1440', 'High'): '1440p High',
    ('2560x1440', 'Ultra'): '1440p Ultra',
}

# Official/main category (most competitive)
OFFICIAL_CATEGORY = ('1920x1080', 'High')


def is_valid_category(resolution, quality):
    """Check if resolution/quality combination is valid"""
    if not resolution or not quality:
        return False
    return (resolution, quality) in VALID_CATEGORIES


def get_category_name(resolution, quality):
    """Get display name for category"""
    return CATEGORY_NAMES.get((resolution, quality), f"{resolution} {quality}")


def get_all_categories():
    """Get list of all valid categories with display names"""
    return [
        {
            'resolution': res,
            'quality': qual,
            'name': get_category_name(res, qual),
            'is_official': (res, qual) == OFFICIAL_CATEGORY
        }
        for res, qual in VALID_CATEGORIES
    ]


def validate_submission_category(resolution, quality):
    """
    Validate submission category and return error message if invalid

    Returns:
        None if valid, error message string if invalid
    """
    if not resolution or not quality:
        return "Missing resolution or quality settings"

    if not is_valid_category(resolution, quality):
        return (
            f"Invalid category: {resolution} {quality}. "
            f"Only the following categories are allowed:\n"
            f"720p: Low, Ultra\n"
            f"1080p: Low, Medium, High, Ultra\n"
            f"1440p: Low, Medium, High, Ultra"
        )

    return None
