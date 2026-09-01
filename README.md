# 🎬 YouTube Cutter

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dependencies](https://img.shields.io/badge/yt--dlp-ffmpeg-green.svg)](https://github.com/yt-dlp/yt-dlp)

**YouTube Cutter** is a lightweight, high-performance command-line utility designed to download and extract precise time segments from YouTube videos without requiring full-file downloads or heavy manual video editing suites. Built on top of robust media automation tools, it handles high-resolution streams, performs fast frame-accurate cuts, and saves media directly in your requested format.

---

## 📑 Table of Contents

1. [Architecture & System Design](#-architecture--system-design)
2. [Features & Capabilities](#-features--capabilities)
3. [Prerequisites & Dependencies](#-prerequisites--dependencies)
4. [Project Structure & Codebase Overview](#-project-structure--codebase-overview)
5. [Installation & Environment Setup](#-installation--environment-setup)
6. [Complete Usage Guide & CLI Reference](#-complete-usage-guide--cli-reference)
7. [Implementation Details (Source Code Modules)](#-implementation-details-source-code-modules)
8. [Configuration & Customization](#-configuration--customization)
9. [Troubleshooting & Common Issues](#-troubleshooting--common-issues)
10. [Contributing Guidelines](#-contributing-guidelines)
11. [License](#-license)

---

## 🏛️ Architecture & System Design

The application follows a modular pipeline architecture separating stream parsing, time validation, and physical media cutting:
