import os
import uuid
import subprocess
import threading
import time
import yt_dlp
from flask import Flask, render_template, request, jsonify, send_file, after_this_request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- CONFIG ---
MAX_CUT_DURATION = 600  # 10 minutes - protects your server from abuse
FFMPEG_TIMEOUT = 300    # 5 minutes timeout
MAX_FILE_AGE = 3600      # 1 hour - auto cleanup

# --- AUTO CLEANUP OLD FILES ---
def cleanup_old_files():
    while True:
        time.sleep(1800) # check every 30 min
        now = time.time()
        try:
            for f in os.listdir(OUTPUT_FOLDER):
                path = os.path.join(OUTPUT_FOLDER, f)
                if os.path.isfile(path) and now - os.path.getmtime(path) > MAX_FILE_AGE:
                    os.remove(path)
        except Exception:
            pass

threading.Thread(target=cleanup_old_files, daemon=True).start()

# =========================================================
# HOME
# =========================================================
@app.route("/")
def home():
    return render_template("index.html")

# =========================================================
# HELPERS
# =========================================================
def format_duration(seconds):
    if not seconds:
        return "00:00:00"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def time_to_seconds(value):
    value = value.strip()
    parts = value.split(":")
    
    if len(parts) == 2:  # MM:SS support
        h = 0
        m, s = parts
    elif len(parts) == 3: # HH:MM:SS
        h, m, s = parts
    else:
        raise ValueError("Time must be HH:MM:SS or MM:SS")

    h, m, s = int(h), int(m), int(s)
    if m > 59 or s > 59 or h < 0 or m < 0 or s < 0:
        raise ValueError("Invalid time format")
    return h * 3600 + m * 60 + s

# =========================================================
# FETCH YOUTUBE INFORMATION + AVAILABLE FORMATS
# =========================================================
@app.route("/fetch", methods=["POST"])
def fetch_video():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received."}), 400

    url = data.get("url", "").strip()
    if not url:
        return jsonify({"success": False, "message": "Please enter a YouTube URL."}), 400

    try:
        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
            "extractor_args": {"youtube": {"player_client": ["android"]}} # more stable
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        title = info.get("title") or "Unknown Title"
        channel = info.get("channel") or info.get("uploader") or "Unknown Channel"
        duration = info.get("duration") or 0
        thumbnail = info.get("thumbnail") or ""

        available_formats = []
        seen = set()

        for fmt in info.get("formats", []):
            vcodec = fmt.get("vcodec")
            acodec = fmt.get("acodec")
            height = fmt.get("height")
            width = fmt.get("width")
            ext = (fmt.get("ext") or "").lower()
            format_id = fmt.get("format_id")

            if vcodec in (None, "none"): continue
            if not height or height < 144: continue
            
            format_note = (fmt.get("format_note") or "").lower()
            if "10bit" in format_note or "10-bit" in format_note:
                continue

            has_audio = acodec not in (None, "none")
            key = (int(height), ext, has_audio)
            if key in seen: continue
            seen.add(key)

            available_formats.append({
                "format_id": format_id,
                "height": int(height),
                "width": int(width) if width else None,
                "ext": ext,
                "has_audio": has_audio,
                "label": f"{height}p • {ext.upper()} {'+ Audio' if has_audio else '(No Audio)'}"
            })

        available_formats.sort(key=lambda x: (x["height"], 0 if x["ext"] == "mp4" else 1, 0 if x["has_audio"] else 1))

        return jsonify({
            "success": True,
            "title": title,
            "channel": channel,
            "duration": duration,
            "duration_text": format_duration(duration),
            "thumbnail": thumbnail,
            "formats": available_formats
        })

    except Exception as error:
        print("\nFETCH ERROR:", error)
        return jsonify({"success": False, "message": str(error)}), 500

# =========================================================
# CUT VIDEO
# =========================================================
@app.route("/cut", methods=["POST"])
def cut_video():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received."}), 400

    url = data.get("url", "").strip()
    start_time = data.get("start_time", "").strip()
    end_time = data.get("end_time", "").strip()
    format_id = data.get("format_id", "").strip()

    if not url: return jsonify({"success": False, "message": "YouTube URL is missing."}), 400
    if not start_time or not end_time: return jsonify({"success": False, "message": "Start and end time are required."}), 400
    if not format_id: return jsonify({"success": False, "message": "Please select a video format."}), 400

    try:
        start_seconds = time_to_seconds(start_time)
        end_seconds = time_to_seconds(end_time)
        cut_duration = end_seconds - start_seconds
        if cut_duration <= 0:
            raise ValueError("End time must be greater than start time.")
        if cut_duration > MAX_CUT_DURATION:
            raise ValueError(f"Cut duration too long. Max allowed is {MAX_CUT_DURATION//60} minutes for server safety.")
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 400

    job_id = str(uuid.uuid4())
    output_file = os.path.join(OUTPUT_FOLDER, job_id + ".mp4")

    try:
        ytdlp_options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "format": f"{format_id}+bestaudio/{format_id}",
            "extractor_args": {"youtube": {"player_client": ["android"]}}
        }

        with yt_dlp.YoutubeDL(ytdlp_options) as ydl:
            info = ydl.extract_info(url, download=False)

        # Validate against video duration
        video_duration = info.get("duration")
        if video_duration and end_seconds > video_duration:
            raise ValueError(f"End time exceeds video duration ({format_duration(video_duration)})")

        requested_formats = info.get("requested_formats")
        command = None

        # VIDEO + AUDIO (separate streams)
        if requested_formats:
            video_stream = None
            audio_stream = None
            for item in requested_formats:
                if item.get("vcodec") != "none": video_stream = item.get("url")
                if item.get("acodec") != "none": audio_stream = item.get("url")

            if not video_stream:
                raise Exception("Selected video stream could not be found.")

            if audio_stream:
                command = [
                    "ffmpeg", "-y",
                    "-ss", start_time, "-i", video_stream,
                    "-ss", start_time, "-i", audio_stream,
                    "-t", str(cut_duration),
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart",
                    output_file
                ]
            else:
                command = [
                    "ffmpeg", "-y",
                    "-ss", start_time, "-i", video_stream,
                    "-t", str(cut_duration),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-an", "-movflags", "+faststart",
                    output_file
                ]
        # SINGLE STREAM (already muxed)
        else:
            stream_url = info.get("url")
            if not stream_url:
                raise Exception("Video stream URL could not be found.")
            command = [
                "ffmpeg", "-y",
                "-ss", start_time, "-i", stream_url,
                "-t", str(cut_duration),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
                output_file
            ]

        print(f"\n[CUT] {format_id} | {start_time} -> {end_time} | {cut_duration}s")

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=FFMPEG_TIMEOUT
        )

        if result.returncode != 0:
            print("\nFFMPEG ERROR:", result.stderr)
            raise Exception("FFmpeg failed to create the video. Try a lower quality format.")

        if not os.path.exists(output_file):
            raise Exception("Output video was not created.")

        @after_this_request
        def remove_file(response):
            try:
                # Small delay to ensure file is sent
                def delayed_remove():
                    time.sleep(2)
                    if os.path.exists(output_file):
                        os.remove(output_file)
                threading.Thread(target=delayed_remove, daemon=True).start()
            except Exception:
                pass
            return response

        return send_file(output_file, as_attachment=True, download_name="cut-video.mp4", mimetype="video/mp4")

    except subprocess.TimeoutExpired:
        if os.path.exists(output_file):
            try: os.remove(output_file)
            except: pass
        return jsonify({"success": False, "message": "Cut timed out. Try a shorter clip or lower quality."}), 500

    except Exception as error:
        print("\nCUT ERROR:", error)
        if os.path.exists(output_file):
            try: os.remove(output_file)
            except: pass
        return jsonify({"success": False, "message": str(error)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
