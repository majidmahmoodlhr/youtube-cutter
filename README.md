# ✂️ YouTube Cutter

> Cut YouTube videos in seconds. No download, no watermark, no hassle.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?style=flat-square)](https://flask.palletsprojects.com/)
[![yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-red?style=flat-square)](https://github.com/yt-dlp/yt-dlp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

A fast, modern web app to download **only the clip you need** from any YouTube video. Paste link → choose quality → set time → download. Built with Flask + yt-dlp + FFmpeg.

**Live Demo:** `http://localhost:5000` after running

![YouTube Cutter Screenshot](https://github.com/majidmahmoodlhr/youtube-cutter/blob/main/Screenshot%202026-09-02%20091047.jpg?raw=true)

---

### ✨ Features

- **⚡ Instant Cutting** - Uses FFmpeg seek for 10x faster cuts
- **🎥 Quality Selector** - Shows real YouTube formats (144p to 1080p, mp4/webm)
- **🎯 Precise Time Control** - Supports `MM:SS` and `HH:MM:SS` with live duration check
- **🔒 Server-Safe** - 10-min max cut, auto-cleanup, FFmpeg timeout
- **💎 Modern UI** - Tailwind CSS, progress bar, responsive, no reload needed
- **🚀 No Watermark** - Clean output with `faststart` for instant playback

### 🛠️ Tech Stack

- **Backend:** Flask, yt-dlp, FFmpeg
- **Frontend:** Tailwind CSS, Vanilla JS
- **Video Processing:** FFmpeg (libx264 + AAC)

### 📦 Installation

**1. Prerequisites - Install FFmpeg**

Windows:
```bash
winget install ffmpeg
```
macOS:
```bash
brew install ffmpeg
```
Linux:
```bash
sudo apt update && sudo apt install ffmpeg
```

**2. Clone & Setup**

```bash
git clone https://github.com/majidmahmoodlhr/youtube-cutter.git
cd youtube-cutter
pip install -r requirements.txt
```

**3. Requirements.txt**

Make sure your `requirements.txt` contains:

```
Flask
yt-dlp
```

**4. Run**

```bash
python app.py
```

Open: `http://localhost:5000`

### 💻 How to Use

1. Paste any YouTube URL
2. Click **Fetch** - app will load thumbnail, title, duration and available qualities
3. Select quality (720p MP4 recommended for speed)
4. Enter Start and End time (e.g., `00:01:10` to `00:01:45`)
5. Click **Cut & Download** - file downloads automatically

### 🔌 API Reference

This app has 2 API endpoints:

#### POST `/fetch`
Fetch video metadata and formats.

Request:
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

Response:
```json
{
  "success": true,
  "title": "Video Title",
  "channel": "Channel Name",
  "duration": 212,
  "duration_text": "00:03:32",
  "thumbnail": "https://...",
  "formats": [
    {"format_id": "22", "height": 720, "ext": "mp4", "has_audio": true, "label": "720p • MP4 + Audio"}
  ]
}
```

#### POST `/cut`
Cut and download video.

Request:
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "start_time": "00:01:10",
  "end_time": "00:01:45",
  "format_id": "22"
}
```

Response: Binary `video/mp4` file download.

### 🗂️ Project Structure

```
youtube-cutter/
├── app.py                 # Main Flask app (with auto-cleanup & safety)
├── templates/
│   └── index.html         # Modern Tailwind UI with progress bar
├── outputs/               # Temp files (auto-deleted)
├── requirements.txt
└── README.md
```

### 🚀 Deployment

**For Production (gunicorn):**

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Deploy to Render / Railway / VPS:**

- Set `FFmpeg` in Dockerfile or build command
- Make sure `outputs/` is writable
- Set env: `PYTHON_VERSION=3.10`

**Dockerfile example:**

```dockerfile
FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

### ⚙️ Configuration

You can change these in `app.py`:

```python
MAX_CUT_DURATION = 600  # seconds - max clip length
FFMPEG_TIMEOUT = 300    # seconds - ffmpeg timeout
MAX_FILE_AGE = 3600     # seconds - auto delete old files
```

### 🛡️ Safety Features (Added)

- ✅ Auto-delete after download (no disk full)
- ✅ 10 min max duration limit
- ✅ FFmpeg timeout protection
- ✅ Old file cleanup every 30 min
- ✅ Duration validation vs actual video length
- ✅ Stable yt-dlp client (`android`) to avoid blocks

### 🤝 Contributing

1. Fork it
2. Create feature branch: `git checkout -b feature/cool-feature`
3. Commit: `git commit -m 'Add cool feature'`
4. Push: `git push origin feature/cool-feature`
5. Open PR

### 📝 License

MIT License - see [LICENSE](LICENSE)

### 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Flask](https://flask.palletsprojects.com/) - Web framework

---

**Made with ❤️ by [Majid Mahmood](https://github.com/majidmahmoodlhr)**

If you like it, please ⭐ star the repo!
