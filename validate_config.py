#!/usr/bin/env python3
"""
Validate diagnostic_config.py configuration
Shows all your configured products and links
"""

import diagnostic_config

print("=" * 70)
print("✅ DIAGNOSTIC CONFIG VALIDATION")
print("=" * 70)
print()

# Check YouTube videos
print("📺 YOUTUBE VIDEOS:")
print("-" * 70)
for issue_type, video_id in diagnostic_config.YOUTUBE_VIDEOS.items():
    url = f"https://youtube.com/watch?v={video_id}"
    status = "✅ SET" if video_id != 'dQw4w9WgXcQ' else "⚠️  PLACEHOLDER"
    print(f"{status} {issue_type:20s} → {url}")
print()

# Check affiliate links
print("💰 AFFILIATE LINKS:")
print("-" * 70)
for product_key, link in diagnostic_config.AFFILIATE_LINKS.items():
    status = "✅ AMAZON" if 'amzn.to' in link else "⚠️  OTHER"
    print(f"{status} {product_key:20s} → {link}")
print()

# Check products and link matching
print("📦 PRODUCTS & LINK MATCHING:")
print("-" * 70)
errors = []
for product_key, product_data in diagnostic_config.PRODUCTS.items():
    product_name = product_data['name']
    affiliate_key = product_data.get('affiliate_link_key')

    # Test the link resolution
    full_product = diagnostic_config.get_product_with_link(product_key)
    affiliate_link = full_product.get('affiliate_link', '#')

    if affiliate_link == '#':
        status = "❌ NO LINK"
        errors.append(f"Product '{product_key}' has no affiliate link!")
    elif affiliate_key in diagnostic_config.AFFILIATE_LINKS:
        status = "✅ LINKED"
    else:
        status = "⚠️  KEY MISMATCH"
        errors.append(f"Product '{product_key}' affiliate_link_key '{affiliate_key}' not found in AFFILIATE_LINKS")

    price = f"{product_data['currency']}{product_data['price']}"
    print(f"{status} {product_name:35s} {price:10s} → {affiliate_key}")
print()

# Summary
print("=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print(f"YouTube Videos:    {len(diagnostic_config.YOUTUBE_VIDEOS)}")
print(f"Affiliate Links:   {len(diagnostic_config.AFFILIATE_LINKS)}")
print(f"Products:          {len(diagnostic_config.PRODUCTS)}")
print()

if errors:
    print("⚠️  ISSUES FOUND:")
    for error in errors:
        print(f"   - {error}")
    print()
    print("Fix these issues to ensure affiliate links work correctly!")
else:
    print("✅ ALL PRODUCTS HAVE VALID AFFILIATE LINKS!")
    print()
    print("Your configuration is ready to make money! 💰")
    print()
    print("Next steps:")
    print("1. Update YouTube video IDs (currently using placeholder)")
    print("2. Test submission with diagnostic page")
    print("3. Click links to verify tracking works")

print()
print("=" * 70)
