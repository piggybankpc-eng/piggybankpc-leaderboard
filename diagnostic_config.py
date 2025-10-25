"""
PiggyBankPC Leaderboard - Diagnostic Configuration
Configure YouTube videos and affiliate links for revenue generation
"""

# YouTube Video IDs or Channel URL - UPDATE THESE WITH YOUR ACTUAL VIDEO IDs!
# For now, using channel URL is fine - users will see your channel
# When you create specific videos, replace with video IDs like: 'dQw4w9WgXcQ'
YOUTUBE_VIDEOS = {
    'thermal_throttling': '@piggybankpc',  # Channel URL (will link to your channel)
    'cpu_bottleneck': '@piggybankpc',      # Replace with video ID when you make the video
    'low_ram': '@piggybankpc',             # Replace with video ID when you make the video
    'old_drivers': '@piggybankpc',         # Replace with video ID when you make the video
}

# Affiliate Links - UPDATE WITH YOUR ACTUAL AFFILIATE LINKS!
# Amazon Associates, eBay Partner Network, etc.
AFFILIATE_LINKS = {
    'Noctua NT-H1': 'https://amzn.to/4nj7P1z',  # Fixed: removed underscore to match product key
    'Noctua_NT-H2': 'https://amzn.to/4hiHuiA',
    'thermal_pads': 'https://amzn.to/4ht4USI',  # Fixed: removed 'kit' to match product key
    'ram_ddr4_16gb': 'https://amzn.to/4oCK31x',
    'ram_ddr3_16gb': 'https://amzn.to/4htTgqC',
}

# Product Database
PRODUCTS = {
    'Noctua NT-H1 3.5g': {
        'name': 'Noctua NT-H1 Thermal Paste',
        'price': 8.95,
        'currency': '£',
        'affiliate_link_key': 'Noctua NT-H1',
        'why_recommend': 'Easy to apply, non-conductive, great performance. Used on 50+ GPUs!',
        'image_url': '/static/images/products/Noctua NT-H1.jpg'
    },
    'thermal_pads 13w': {
        'name': 'Thermal Pad Set (0.5mm-2mm)',
        'price': 19.99,
        'currency': '£',
        'affiliate_link_key': 'thermal_pads',
        'why_recommend': 'Covers all GPU memory chips, various thicknesses included',
        'image_url': '/static/images/products/thermal-pads.jpg'
    },
    # CPU upgrades removed - no affiliate program available
    # Instead, we'll provide text recommendations based on their current hardware
    'ram_ddr4_16gb': {
        'name': 'Lexar DDR4 16GB (1x16GB) 3200MHz',
        'price': 41.99,
        'currency': '£',
        'affiliate_link_key': 'ram_ddr4_16gb',
        'why_recommend': 'Budget friendly, dual channel performance, reliable brand',
        'image_url': '/static/images/products/ram-ddr4.jpg'
    },
    'ram_ddr3_16gb': {
        'name': 'DDR3 16GB (1x16GB) 1600MHz',
        'price': 14.09,
        'currency': '£',
        'affiliate_link_key': 'ram_ddr3_16gb',
        'why_recommend': 'Perfect for older systems, great value for DDR3 platforms',
        'image_url': '/static/images/products/ram-ddr3.jpg'
    }
}


def get_affiliate_link(product_key):
    """
    Get the full affiliate link for a product

    Args:
        product_key: Product key from PRODUCTS dict

    Returns:
        str: Full affiliate URL
    """
    product = PRODUCTS.get(product_key)
    if not product:
        return '#'

    affiliate_key = product.get('affiliate_link_key')
    return AFFILIATE_LINKS.get(affiliate_key, '#')


def get_product_with_link(product_key):
    """
    Get product data with affiliate link included

    Args:
        product_key: Product key from PRODUCTS dict

    Returns:
        dict: Product data with affiliate_link field
    """
    product = PRODUCTS.get(product_key, {}).copy()
    if product:
        product['affiliate_link'] = get_affiliate_link(product_key)
    return product
