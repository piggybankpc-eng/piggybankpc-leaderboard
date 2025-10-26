# 🏆 Official PiggyBankPC Builds Feature

## What's New?

You now have a **separate Official Builds leaderboard** that showcases your PiggyBankPC channel builds while ALSO populating the community leaderboard!

## Key Features

### 1. Separate Official Builds Page
- **URL:** https://piggybankpc.uk/official-builds
- Beautiful card-based layout showcasing each build
- Shows hardware specs, performance metrics, and YouTube videos
- Only displays builds you've marked as "official"

### 2. Dual Leaderboard Presence
Your official builds appear in **TWO places:**
- ✅ **Official Builds page** - Dedicated showcase
- ✅ **Community Leaderboard** - With special "Official" badge

This means:
- Viewers can compare their systems to yours
- Community leaderboard isn't empty when starting out
- Your builds are highlighted and stand out

### 3. YouTube Integration
- Each official build can have a YouTube video link
- Red YouTube icon appears next to build on leaderboards
- Click icon → opens your build/testing video
- Drives traffic to @piggybankpc channel

### 4. Admin-Only Access
- Only admins can submit official builds
- Protected submission route
- Delete button for managing builds

## How to Use

### Step 1: Make Yourself Admin

```bash
cd /home/john/Desktop/piggybankpc-leaderboard
source venv/bin/activate
python make_admin.py YOUR_USERNAME
```

### Step 2: Submit Official Build

1. **Log in** to your account
2. Click **"Official Builds"** in navigation
3. Click **"Submit a new official build"** (only visible to admins)
4. Fill in the form:
   - **Build Name** (optional): "Budget Beast 2024", "Ultimate Gaming Rig", etc.
   - **YouTube URL**: Link to your build video
   - **Benchmark File**: Upload the .pbr file from your benchmark
5. **Submit!**

### Step 3: View Your Builds

**Official Builds Page:** https://piggybankpc.uk/official-builds
- Shows all your official builds in rich cards
- YouTube button prominent
- Full specs and performance stats

**Community Leaderboard:** https://piggybankpc.uk/leaderboard
- Your builds appear with red "Official" badge
- YouTube icon clickable
- Mixed with community submissions for comparison

## What Happens Behind the Scenes

### Database
New fields added to `submissions` table:
- `is_official` (BOOLEAN) - Marks official builds
- `youtube_video_url` (VARCHAR 500) - YouTube video link
- `build_name` (VARCHAR 200) - Custom build name

### Code
- **New route:** `/official-builds` (view all official builds)
- **Admin route:** `/official-builds/submit` (admin only)
- **Delete route:** `/official-builds/<id>/delete` (admin only)
- **Badge logic:** Community leaderboard shows badge when `is_official=True`
- **YouTube icon:** Shows when `youtube_video_url` is not null

## Benefits for Your Channel

1. **Content Showcase:** Every build you feature gets a permanent spot
2. **Video Views:** Direct links drive traffic to your videos
3. **Authority:** Official badge establishes you as the expert
4. **Comparison:** Viewers benchmark against YOUR builds
5. **Engagement:** Users try to beat your scores
6. **SEO:** Rich build pages with specs help search rankings

## Example Workflow

```
1. Build a PC for video (e.g., "£500 Budget Gaming PC")
2. Film build process + testing for YouTube
3. Run PiggyBankPC Benchmark Tool on the system
4. Upload video to YouTube
5. Submit official build:
   - Name: "£500 Budget Gaming Beast"
   - YouTube: https://youtube.com/watch?v=...
   - Benchmark: Upload .pbr file
6. Build appears on both leaderboards
7. Viewers watch video → subscribe → try to beat your score
```

## Managing Official Builds

### View All Builds
https://piggybankpc.uk/official-builds

### Delete a Build (Admin Only)
- Click the red "Delete" button on any build card
- Confirm deletion
- Build removed from both leaderboards

### Edit Build (Not Yet Implemented)
Currently, you need to delete and re-submit to change details.
Could add edit functionality if needed!

## Technical Details

### Migration Script
File: `migrate_add_official_builds.py`
- Adds new columns to database
- Sets `is_official=FALSE` for all existing submissions
- Creates index on `is_official` for fast queries

### Admin Helper
File: `make_admin.py`
- Quick script to grant admin access
- Usage: `python make_admin.py USERNAME`

### Routes
- `GET /official-builds` - View official builds (public)
- `GET /official-builds/submit` - Submit form (admin only)
- `POST /official-builds/submit` - Process submission (admin only)
- `POST /official-builds/<id>/delete` - Delete build (admin only)

### Templates
- `templates/official_builds.html` - Official builds showcase
- `templates/official_builds_submit.html` - Submission form
- `templates/leaderboard.html` - Updated with badge logic
- `templates/base.html` - Updated navigation

## Future Enhancements

Potential additions:
- **Edit official builds** (currently delete + re-submit)
- **Build categories** (Budget, Mid-Range, High-End)
- **Featured build** (highlight one build on homepage)
- **Build comparisons** (side-by-side comparison tool)
- **Build galleries** (photo carousel for each build)
- **Parts list integration** (with Amazon affiliate links)
- **Build guides** (PDF download for each build)

## Deployment Status

✅ **LIVE** at https://piggybankpc.uk

- Database migration: **COMPLETE**
- Code deployment: **COMPLETE**
- Production server: **RUNNING**
- Feature: **ACTIVE**

Current production server PID: 501283

## Questions?

Check `IMPORTANT_FILES.md` for complete server management documentation.

---

**Built with:** Flask, SQLAlchemy, Bootstrap 5
**Deployed:** October 26, 2025
**Status:** ✅ Production Ready
