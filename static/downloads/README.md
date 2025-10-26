# PiggyBankPC Benchmark AppImage

## How to Add the AppImage

1. Build or obtain the `PiggyBankPC-Benchmark.AppImage` file
2. Place it in this directory: `/home/john/Desktop/piggybankpc-leaderboard/static/downloads/`
3. The download link will automatically work: `/download`

## AppImage Filename
The download page expects: `PiggyBankPC-Benchmark.AppImage`

## Alternative: External Hosting
If hosting the AppImage elsewhere (GitHub Releases, etc.), update the download link in:
`templates/download.html` - line with `url_for('static', filename='downloads/...')`

Replace with direct URL:
```html
<a href="https://github.com/YOUR_REPO/releases/latest/download/PiggyBankPC-Benchmark.AppImage"
   class="btn btn-primary btn-lg"
   download>
```
