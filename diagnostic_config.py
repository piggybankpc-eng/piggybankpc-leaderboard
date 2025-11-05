"""
PiggyBankPC Leaderboard - Diagnostic Configuration
Configure YouTube videos and affiliate links for revenue generation
"""

# YouTube Video IDs or Channel URL - UPDATE THESE WITH YOUR ACTUAL VIDEO IDs!
# For now, using channel URL is fine - users will see your channel
# When you create specific videos, replace with video IDs like: 'dQw4w9WgXcQ'
YOUTUBE_VIDEOS = {
    'thermal_throttling': '@piggybankpc',  # Channel URL (will link to your channel)
    'gpu_repaste': '@piggybankpc',         # GPU thermal paste application video
    'cpu_thermal_paste': '@piggybankpc',   # CPU thermal paste application video
    'cpu_bottleneck': '@piggybankpc',      # Replace with video ID when you make the video
    'low_ram': '@piggybankpc',             # Replace with video ID when you make the video
    'old_drivers': '@piggybankpc',         # Replace with video ID when you make the video
}

# Affiliate Links - UPDATE WITH YOUR ACTUAL AFFILIATE LINKS!
# Amazon Associates, eBay Partner Network, etc.
AFFILIATE_LINKS = {
    'Noctua NT-H1': 'https://amzn.to/4nj7P1z',  # GPU thermal paste
    'Noctua_NT-H2': 'https://amzn.to/4hiHuiA',
    'Arctic MX-4': 'https://amzn.to/PLACEHOLDER_CPU_PASTE',  # TODO: Add your affiliate link
    'thermal_pads': 'https://amzn.to/4ht4USI',  # Thermal pads kit
    'gelid_pads': 'https://amzn.to/PLACEHOLDER_GELID',  # TODO: Add your affiliate link
    'ram_ddr4_16gb': 'https://amzn.to/4oCK31x',
    'ram_ddr3_16gb': 'https://amzn.to/4htTgqC',
    'noctua_cooler': 'https://amzn.to/PLACEHOLDER_COOLER',  # TODO: Add your affiliate link
    'arctic_fan': 'https://amzn.to/PLACEHOLDER_FAN',  # TODO: Add your affiliate link
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
    },
    'Arctic MX-4 4g': {
        'name': 'Arctic MX-4 Thermal Paste (4g)',
        'price': 6.99,
        'currency': '£',
        'affiliate_link_key': 'Arctic MX-4',
        'why_recommend': 'Cheapest fix for CPU temps! Easy to apply, lasts 8+ years. Try this FIRST before buying a new cooler.',
        'image_url': '/static/images/products/arctic-mx4.jpg'
    },
    'Noctua NH-U12S': {
        'name': 'Noctua NH-U12S CPU Cooler',
        'price': 49.99,
        'currency': '£',
        'affiliate_link_key': 'noctua_cooler',
        'why_recommend': 'Excellent budget tower cooler, quiet, fits most cases. Big upgrade over stock coolers.',
        'image_url': '/static/images/products/noctua-cooler.jpg'
    },
    'Gelid GP-Extreme 1.0mm': {
        'name': 'Gelid GP-Extreme Thermal Pads (1.0mm)',
        'price': 8.99,
        'currency': '£',
        'affiliate_link_key': 'gelid_pads',
        'why_recommend': 'Best thermal pads for GPU memory chips. Multiple thicknesses available (get 1.0mm, 1.5mm, 2.0mm).',
        'image_url': '/static/images/products/gelid-pads.jpg'
    },
    'Arctic P12 120mm': {
        'name': 'Arctic P12 120mm Case Fan',
        'price': 7.99,
        'currency': '£',
        'affiliate_link_key': 'arctic_fan',
        'why_recommend': 'Cheap, quiet, moves lots of air. Add 1-2 intake fans to improve overall cooling.',
        'image_url': '/static/images/products/arctic-fan.jpg'
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
