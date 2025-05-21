
import subprocess
import os
from pathlib import Path

def get_ffmpeg_path():
    """
    Get the path to the FFmpeg executable.
    Defaults to 'ffmpeg' assuming it's on PATH.
    """
    config_path = Path("config/ffmpeg_path.txt")
    if config_path.exists():
        with config_path.open("r") as f:
            return f.read().strip()
    return "ffmpeg"

def extract_audio(input_video, output_audio):
    """
    Extracts audio from a video file and saves it as WAV.
    """
    ffmpeg = get_ffmpeg_path()
    command = [ffmpeg, "-y", "-i", input_video, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", output_audio]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed to extract audio: {result.stderr}")
    return output_audio

def burn_subtitles(input_video, subtitle_file, output_video):
    """
    Embeds subtitles into a video file.
    """
    ffmpeg = get_ffmpeg_path()
    command = [ffmpeg, "-y", "-i", input_video, "-vf", f"subtitles={subtitle_file}", output_video]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed to burn subtitles: {result.stderr}")
    return output_video

def trim_video(input_video, start_time, duration, output_video):
    """
    Trims a video from a given start time and duration.
    Format of time: '00:00:30' (HH:MM:SS)
    """
    ffmpeg = get_ffmpeg_path()
    command = [
        ffmpeg, "-y", "-ss", start_time, "-i", input_video,
        "-t", duration, "-c", "copy", output_video
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed to trim video: {result.stderr}")
    return output_video
