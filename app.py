import os
os.environ["PATH"] += os.pathsep + os.path.abspath("./bin")
import os
import uuid
import subprocess
import yt_dlp

from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# FORMAT DURATION
# =========================================================

def format_duration(seconds):

    if not seconds:
        return "00:00:00"

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# =========================================================
# FETCH YOUTUBE INFORMATION + AVAILABLE FORMATS
# =========================================================

@app.route("/fetch", methods=["POST"])
def fetch_video():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400

    url = data.get("url", "").strip()

    if not url:
        return jsonify({
            "success": False,
            "message": "Please enter a YouTube URL."
        }), 400

    try:

        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True
        }

        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        title = (
            info.get("title")
            or "Unknown Title"
        )

        channel = (
            info.get("channel")
            or info.get("uploader")
            or "Unknown Channel"
        )

        duration = info.get("duration") or 0

        thumbnail = (
            info.get("thumbnail")
            or ""
        )


        # =================================================
        # FIND ACTUAL YOUTUBE VIDEO FORMATS
        # =================================================

        available_formats = []

        seen = set()

        for fmt in info.get("formats", []):

            video_codec = fmt.get("vcodec")

            audio_codec = fmt.get("acodec")

            height = fmt.get("height")

            width = fmt.get("width")

            ext = (
                fmt.get("ext")
                or ""
            ).lower()

            format_id = fmt.get("format_id")


            # Ignore audio-only formats
            if video_codec in (
                None,
                "none"
            ):
                continue


            # Ignore formats without resolution
            if not height:
                continue


            # Ignore tiny/unknown formats
            if height < 144:
                continue


            # Ignore 10-bit formats
            format_note = (
                fmt.get("format_note")
                or ""
            ).lower()

            if "10bit" in format_note:
                continue

            if "10-bit" in format_note:
                continue


            # Determine audio status
            has_audio = (
                audio_codec not in (
                    None,
                    "none"
                )
            )


            # Prefer MP4 where available
            key = (
                int(height),
                ext,
                has_audio
            )

            if key in seen:
                continue

            seen.add(key)


            available_formats.append({

                "format_id": format_id,

                "height": int(height),

                "width": (
                    int(width)
                    if width
                    else None
                ),

                "ext": ext,

                "has_audio": has_audio,

                "label":
                    f"{height}p • "
                    f"{ext.upper()}"

            })


        # =================================================
        # SORT FORMATS
        # =================================================

        available_formats.sort(
            key=lambda x: (
                x["height"],
                0 if x["ext"] == "mp4" else 1,
                0 if x["has_audio"] else 1
            )
        )


        # =================================================
        # RETURN DATA
        # =================================================

        return jsonify({

            "success": True,

            "title": title,

            "channel": channel,

            "duration": duration,

            "duration_text":
                format_duration(duration),

            "thumbnail": thumbnail,

            "formats":
                available_formats

        })


    except Exception as error:

        print("\nFETCH ERROR:")
        print(error)

        return jsonify({

            "success": False,

            "message": str(error)

        }), 500


# =========================================================
# TIME → SECONDS
# =========================================================

def time_to_seconds(value):

    parts = value.split(":")

    if len(parts) != 3:

        raise ValueError(
            "Time must be in HH:MM:SS format."
        )

    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])

    if minutes > 59 or seconds > 59:

        raise ValueError(
            "Invalid time format."
        )

    return (
        hours * 3600
        + minutes * 60
        + seconds
    )


# =========================================================
# CUT VIDEO
# =========================================================

@app.route("/cut", methods=["POST"])
def cut_video():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "No data received."
        }), 400


    url = data.get(
        "url",
        ""
    ).strip()


    start_time = data.get(
        "start_time",
        ""
    ).strip()


    end_time = data.get(
        "end_time",
        ""
    ).strip()


    format_id = data.get(
        "format_id",
        ""
    ).strip()


    if not url:

        return jsonify({
            "success": False,
            "message": "YouTube URL is missing."
        }), 400


    if not start_time or not end_time:

        return jsonify({
            "success": False,
            "message": "Start and end time are required."
        }), 400


    if not format_id:

        return jsonify({
            "success": False,
            "message": "Please select a video format."
        }), 400


    try:

        start_seconds = time_to_seconds(
            start_time
        )

        end_seconds = time_to_seconds(
            end_time
        )

        cut_duration = (
            end_seconds -
            start_seconds
        )

        if cut_duration <= 0:

            raise ValueError(
                "End time must be greater than start time."
            )


    except Exception as error:

        return jsonify({

            "success": False,

            "message": str(error)

        }), 400


    job_id = str(uuid.uuid4())

    output_file = os.path.join(
        OUTPUT_FOLDER,
        job_id + ".mp4"
    )


    try:

        # =================================================
        # ASK YT-DLP FOR THE USER'S SELECTED FORMAT
        # =================================================

        ytdlp_options = {

            "quiet": True,

            "no_warnings": True,

            "noplaylist": True,

            "format":
                f"{format_id}+bestaudio/"
                f"{format_id}"

        }


        with yt_dlp.YoutubeDL(
            ytdlp_options
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )


        requested_formats = info.get(
            "requested_formats"
        )


        command = None


        # =================================================
        # VIDEO + AUDIO
        # =================================================

        if requested_formats:

            video_stream = None
            audio_stream = None


            for item in requested_formats:

                if item.get("vcodec") != "none":

                    video_stream = item.get(
                        "url"
                    )


                if item.get("acodec") != "none":

                    audio_stream = item.get(
                        "url"
                    )


            if not video_stream:

                raise Exception(
                    "Selected video stream could not be found."
                )


            if audio_stream:

                command = [

                    "ffmpeg",

                    "-y",

                    "-ss",
                    start_time,

                    "-i",
                    video_stream,

                    "-ss",
                    start_time,

                    "-i",
                    audio_stream,

                    "-t",
                    str(cut_duration),

                    "-map",
                    "0:v:0",

                    "-map",
                    "1:a:0",

                    "-c:v",
                    "libx264",

                    "-preset",
                    "veryfast",

                    "-crf",
                    "23",

                    "-c:a",
                    "aac",

                    "-b:a",
                    "128k",

                    "-movflags",
                    "+faststart",

                    output_file

                ]


            else:

                command = [

                    "ffmpeg",

                    "-y",

                    "-ss",
                    start_time,

                    "-i",
                    video_stream,

                    "-t",
                    str(cut_duration),

                    "-c:v",
                    "libx264",

                    "-preset",
                    "veryfast",

                    "-crf",
                    "23",

                    "-an",

                    "-movflags",
                    "+faststart",

                    output_file

                ]


        # =================================================
        # SINGLE STREAM
        # =================================================

        else:

            stream_url = info.get(
                "url"
            )


            if not stream_url:

                raise Exception(
                    "Video stream URL could not be found."
                )


            command = [

                "ffmpeg",

                "-y",

                "-ss",
                start_time,

                "-i",
                stream_url,

                "-t",
                str(cut_duration),

                "-c:v",
                "libx264",

                "-preset",
                "veryfast",

                "-crf",
                "23",

                "-c:a",
                "aac",

                "-b:a",
                "128k",

                "-movflags",
                "+faststart",

                output_file

            ]


        print("\n==============================")
        print("STARTING VIDEO CUT")
        print("==============================")
        print("Format:", format_id)
        print("Start:", start_time)
        print("End:", end_time)
        print("Duration:", cut_duration)
        print("==============================\n")


        result = subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True

        )


        if result.returncode != 0:

            print("\nFFMPEG ERROR:")
            print(result.stderr)

            raise Exception(
                "FFmpeg failed to create the video."
            )


        if not os.path.exists(
            output_file
        ):

            raise Exception(
                "Output video was not created."
            )


        return send_file(

            output_file,

            as_attachment=True,

            download_name="cut-video.mp4",

            mimetype="video/mp4"

        )


    except Exception as error:

        print("\nCUT ERROR:")
        print(error)


        if os.path.exists(
            output_file
        ):

            try:

                os.remove(
                    output_file
                )

            except Exception:
                pass


        return jsonify({

            "success": False,

            "message": str(error)

        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
