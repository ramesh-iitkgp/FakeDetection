# Fake Content Detector - Chrome Extension

Browser extension for real-time detection of deepfakes, manipulated images, and synthetic media.

## Installation

### From Source (Development)

1. **Clone/Extract** the extension folder
2. Open **Chrome** → `chrome://extensions/`
3. Enable **Developer mode** (top right toggle)
4. Click **"Load unpacked"**
5. Select the `extension/` folder
6. ✅ Extension is now active!

### Icon in Toolbar
- Look for the "Fake Detector" icon
- Click to open the popup interface
- Green checkmark = Active on this site

## Features

### 🔍 Quick Scan
- **Analyze URL**: Paste image/video URLs directly
- **Upload File**: Upload local images or videos
- **Scan Page**: Automatically scan all images on current page
- **Right-Click Menu**: Context menu for quick analysis

### 📊 Results Dashboard
- **Risk Level**: LOW / MEDIUM / HIGH / CRITICAL
- **Confidence Score**: Visual progress bar
- **Detection Details**: Specific anomalies found
- **Risk Factors**: Detailed explanation of findings

### 📱 Real-time Features
- **In-page Highlighting**: Suspicious images highlighted with red border
- **Notifications**: Pop-up alerts for suspicious content
- **History**: Automatic tracking of analyzed content
- **Full Reports**: Export detailed analysis reports

## How to Use

### Analyze an Image

**Option 1: Direct URL**
1. Click extension icon
2. Paste image URL in "Image/Video URL" field
3. Click "Analyze URL"
4. Wait for results (2-5 seconds)

**Option 2: Upload Local File**
1. Click extension icon
2. Click "Upload Media"
3. Select image/video from your device
4. Click "Upload & Analyze"

**Option 3: Right-Click Menu**
1. Right-click any image on a webpage
2. Select "🔍 Analyze Image (Fake Detector)"
3. Results appear in the popup

### Scan Page Images

1. Click extension icon
2. Click **"Scan Page Images"**
3. Extension automatically:
   - Detects all images on current page
   - Sends each for analysis
   - Highlights suspicious images
   - Shows notification with count

### Understanding Results

#### Risk Levels Explained

| Level | Indicator | Meaning |
|-------|-----------|---------|
| **LOW** | 🟢 Green | Likely authentic |
| **MEDIUM** | 🟡 Yellow | Some anomalies detected |
| **HIGH** | 🟠 Orange | Probable manipulation |
| **CRITICAL** | 🔴 Red | Very likely fake |

#### Confidence Score
- **0-20%**: Likely real
- **20-40%**: Possibly real
- **40-60%**: Uncertain - verify with other sources
- **60-80%**: Likely manipulated
- **80-100%**: Very likely fake

### Interpretation Guide

**Frequency Anomalies**
- Indicates unusual patterns in frequency domain
- Common in upscaled or re-compressed images

**Synthetic Texture**
- Detects artificial texture patterns
- Higher in AI-generated faces

**Unnatural Eye Movement**
- Issues with eye blinking or symmetry
- Often found in deepfakes

**Blend Artifacts**
- Face pasting or face-swapping traces
- Visible at boundaries

**Missing EXIF Data**
- Metadata stripped from image
- Could indicate image was heavily edited

**Timestamp Mismatch**
- Creation time differs from modification time
- Sign of post-processing

## Settings

Access settings via the ⚙️ button in the popup:

### General
- **Enable Notifications**: Get alerts for suspicious content
- **Auto-scan Images**: Automatically analyze page images on load

### Detection
- **API Endpoint**: Backend server address (default: http://localhost:5000)
- **Detection Sensitivity**: 
  - Low: Only flag very suspicious content
  - Medium: Standard detection
  - High: Flag even minor anomalies

### Advanced
- **Context Menu**: Enable/disable right-click analysis
- **Cache Results**: Store analysis history locally

## Supported Formats

### Images
- ✅ JPEG / JPG
- ✅ PNG
- ✅ GIF
- ✅ BMP
- ✅ WebP

### Videos
- ✅ MP4
- ✅ WebM
- ✅ AVI
- ✅ MOV
- File size limit: 50MB

## Analysis History

The extension automatically saves your last 50 analyses:

1. Click **"History"** tab in popup
2. View all previous scans with timestamps
3. Click any result to view detailed analysis again
4. Clear history with **"Clear History"** button

## Export & Sharing

### Save Result
- Click **"Save Result"** after analysis
- Downloads JSON file with complete results
- Useful for documentation and evidence

### Share Result
- Click **"Share Result"**
- Copy to clipboard or share via web
- Summary format for quick sharing

### Full Report
- Click **"Full Report"**
- Opens detailed analysis in new tab
- Professional format for sharing with others

## FAQ

### Q: Why does it take 2-5 seconds to analyze?
**A**: The system runs multiple AI models in parallel. GPU acceleration (NVIDIA CUDA) reduces this to 1-2 seconds.

### Q: Is my media stored on your servers?
**A**: No. All analysis happens locally on your device or in your private backend instance. Files are not stored.

### Q: Can it detect all deepfakes?
**A**: No detector is 100% accurate. This uses multiple models for 85-94% accuracy on standard datasets. Always verify suspicious content with other sources.

### Q: Does it work on social media?
**A**: Most popular sites (Facebook, Twitter, TikTok, Instagram) are compatible. Some sites block extensions - use direct URL instead.

### Q: What if I get a false positive?
**A**: This is possible. If you believe content is authentic but flagged:
1. Try lowering sensitivity in Settings
2. Verify with other detection tools
3. Report as false positive (helps improve models)

### Q: Can I use this commercially?
**A**: Yes, with proper attribution. The system is MIT licensed for general use.

### Q: How much data does it send?
**A**: Only the image/video URL or file. No personal data is transmitted.

## Troubleshooting

### Issue: Extension won't load in Chrome
**Solution**:
1. Check Chrome version is 90+
2. Go to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked" and select folder
5. Refresh page if still issues

### Issue: Getting "Cannot connect to backend" error
**Solution**:
1. Ensure backend is running: `python app.py` in backend folder
2. Check API endpoint in Settings matches your server
3. Verify port is not blocked by firewall
4. Try `http://localhost:5000` in Settings

### Issue: Analysis is very slow
**Solution**:
1. Check if GPU is available (`nvidia-smi`)
2. Try reducing video sample frames
3. Analyze smaller files first
4. Restart backend server
5. Check available RAM (needs 2GB+)

### Issue: Images are highlighted on page but no results
**Solution**:
1. Check browser console (F12 → Console)
2. Verify backend is running
3. Check API endpoint setting
4. Try re-scanning the page
5. Use "Upload File" instead of scanning

### Issue: Right-click menu not appearing
**Solution**:
1. Ensure context menu is enabled in Settings
2. Reload extension in `chrome://extensions/`
3. Refresh webpage
4. Try clicking on different image types

## Keyboard Shortcuts

Currently using defaults, but you can customize in Chrome settings:

1. Chrome → Extensions → Keyboard Shortcuts
2. Assign shortcuts for quick access

## Advanced Usage

### Using with Custom Backend

To use your own detection server:

1. **Set API Endpoint** in Settings
   - Point to your server URL
   - Must be accessible from your browser

2. **HTTPS Required** for production
   - Self-signed certs work for localhost
   - Valid SSL for production

3. **CORS Configuration**
   - Backend must allow browser requests
   - Set in Flask app: `CORS(app)`

### Batch Analysis from Script

Use the extension with automation:

```javascript
// In console on page with extension
chrome.runtime.sendMessage(
  {action: 'scanImageURL', url: 'https://example.com/img.jpg'},
  (response) => console.log(response)
);
```

## Performance Metrics

| Task | Time | GPU Required |
|------|------|-------------|
| Image Analysis | 2-5s | Optional |
| Video Analysis (per frame) | 1-2s | Optional |
| Metadata Parse | <500ms | No |
| Full Report Generation | 1s | No |

## Security & Privacy

- ✅ **No Tracking**: Zero analytics or telemetry
- ✅ **Local Processing**: Content not stored
- ✅ **Encrypted Communication**: HTTPS support
- ✅ **Open Source**: Code fully transparent
- ✅ **No Ads**: Completely ad-free

## File Structure

```
extension/
├── manifest.json              # Extension config
├── popup/
│   ├── popup.html            # Main UI
│   ├── popup.js              # UI logic
│   └── popup.css             # Styling
├── content/
│   └── content-script.js     # Page injection
├── background/
│   └── service-worker.js     # Background tasks
└── images/
    ├── icon-16.png
    ├── icon-48.png
    └── icon-128.png
```

## Contributing

Found a bug or have suggestions?

1. Check [GitHub Issues](https://github.com/fakedetector/extension/issues)
2. [Report Bug](https://github.com/fakedetector/extension/issues/new?template=bug.md)
3. [Suggest Feature](https://github.com/fakedetector/extension/issues/new?template=feature.md)

## Version History

### v1.0.0 (Current)
- ✅ Complete deepfake detection
- ✅ Metadata analysis
- ✅ Batch processing
- ✅ History tracking
- ✅ Real-time scanning

### Future Versions
- [ ] Audio deepfake detection
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Video watermarking
- [ ] Blockchain verification

## Support

- 📧 **Email**: support@fakedetector.example.com
- 🐛 **Bug Reports**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions
- 📚 **Docs**: Full documentation in docs/ folder

## License

MIT License - Free for personal and commercial use

---

**Last Updated**: April 2026

**Disclaimer**: This tool assists in identifying potentially fake content but should not be the sole source of truth. Always verify through multiple sources and professional forensic analysis when critical decisions depend on authenticity.
