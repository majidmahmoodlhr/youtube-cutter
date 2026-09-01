# YouTube Cutter

> Download and cut YouTube videos with frame-accurate precision. No bloat, no full downloads.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Made with yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-red)](https://github.com/yt-dlp/yt-dlp)

**YouTube Cutter** is a lightweight, high-performance CLI tool to download *only the segment you need* from any YouTube video. Specify a start and end time, and get a clean, ready-to-use clip in seconds.

Perfect for creating shorts, tutorials, highlights, memes, or datasets.

---

### ✨ Features

- **Precise Cutting:** Frame-accurate trimming with `HH:MM:SS` support
- **Fast & Efficient:** No need to download the entire video first
- **High Quality:** Supports up to 4K / 1080p downloads
- **Flexible Output:** Save as `mp4`, `mkv`, `mp3`, `wav` and more
- **Simple CLI:** Intuitive commands, no config needed
- **Powered by yt-dlp + FFmpeg:** Reliable, actively maintained backend

### 📦 Installation

**1. Prerequisites**

You must have FFmpeg installed.

- Windows: `winget install ffmpeg` or download from ffmpeg.org
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

**2. Clone & Install**

```bash
git clone https://github.com/majidmahmoodlhr/youtube-cutter.git
cd youtube-cutter
pip install -r requirements.txt
```

Or install directly:

```bash
pip install yt-dlp
pip install .
```

### 🚀 Quick Start

```bash
python cutter.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start 00:01:10 --end 00:01:45
```

This will download the clip from `1:10` to `1:45` and save it as `output.mp4`.

### 💻 Usage

#### Basic Syntax

```bash
python cutter.py --url <YOUTUBE_URL> --start <START_TIME> --end <END_TIME> [options]
```

#### Examples

**1. Cut a 30-second clip:**
```bash
python cutter.py -u https://youtu.be/dQw4w9WgXcQ -s 00:00:10 -e 00:00:40
```

**2. Save as MP3 (audio only):**
```bash
python cutter.py -u https://youtu.be/dQw4w9WgXcQ -s 01:15:00 -e 01:16:30 --format mp3
```

**3. Custom filename and quality:**
```bash
python cutter.py -u https://youtu.be/dQw4w9WgXcQ -s 00:10:00 -e 00:12:00 -o my_clip.mp4 --quality 1080
```

#### CLI Reference

| Argument | Short | Description | Example |
| :--- | :--- | :--- | :--- |
| `--url` | `-u` | YouTube video URL (required) | `-u https://youtu.be/...` |
| `--start` | `-s` | Start time `HH:MM:SS` or `MM:SS` | `-s 00:01:10` |
| `--end` | `-e` | End time `HH:MM:SS` or `MM:SS` | `-e 00:02:00` |
| `--output` | `-o` | Output filename | `-o clip.mp4` |
| `--format` | `-f` | Output format (mp4, mkv, mp3) | `-f mp3` |
| `--quality` | `-q` | Video quality (best, 1080, 720) | `-q 720` |

### 🗂️ Project Structure

```
youtube-cutter/
├── cutter.py          # Main entry point & CLI logic
├── downloader.py      # Handles yt-dlp download
├── trimmer.py         # Handles FFmpeg cutting
├── utils.py           # Time validation & helpers
├── requirements.txt
└── README.md
```

### ⚙️ How It Works

1.  **Parse:** Validates your URL and timestamps.
2.  **Fetch:** Uses `yt-dlp` to get the best available stream metadata.
3.  **Cut:** Uses `FFmpeg` to cut the segment without full re-encoding where possible for speed.

### 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push and open a Pull Request

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the amazing download engine
- [FFmpeg](https://ffmpeg.org/) for media processing

---

**Made with ❤️ by [Majid Mahmood](https://github.com/majidmahmoodlhr)**

> If you like this project, please give it a ⭐ on GitHub!
