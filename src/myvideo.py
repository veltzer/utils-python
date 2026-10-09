import json
import os
import subprocess


def info(file_path: str) -> dict[str, str | int | float]:
    size = os.path.getsize(file_path)
    finfo: dict[str, str | int | float] = {
        "duration": "00:00:00.00",
        "durationsecs": 0.0,
        "bitrate": "0",
        "vcodec": "",
        "vformat": "",
        "acodec": "",
        "asamplerate": "0",
        "achannels": "0",
        "size": size,
    }
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
    except subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError:
        return finfo

    if "format" in data:
        fmt = data["format"]
        if "duration" in fmt:
            dur = float(fmt["duration"])
            finfo["durationsecs"] = dur
            hours = int(dur // 3600)
            minutes = int((dur % 3600) // 60)
            seconds = int(dur % 60)
            hundredths = int((dur - int(dur)) * 100)
            finfo["duration"] = (
                f"{hours:02d}:{minutes:02d}:{seconds:02d}.{hundredths:02d}"
            )
        if "bit_rate" in fmt:
            finfo["bitrate"] = str(int(fmt["bit_rate"]) // 1000)

    for stream in data.get("streams", []):
        if stream["codec_type"] == "video" and not finfo["vcodec"]:
            finfo["vcodec"] = stream.get("codec_name", "")
            finfo["vformat"] = stream.get("pix_fmt", "")
        elif stream["codec_type"] == "audio" and not finfo["acodec"]:
            finfo["acodec"] = stream.get("codec_name", "")
            finfo["asamplerate"] = stream.get("sample_rate", "0")
            finfo["achannels"] = stream.get("channels", 0)
    return finfo
