"""Audio and video with FFmpeg."""
from pathlib import Path

from .tools import require, run

AUDIO_CODEC = {
    "mp3": ["-c:a", "libmp3lame", "-q:a", "2"],
    "wav": ["-c:a", "pcm_s16le"],
    "m4a": ["-c:a", "aac", "-b:a", "192k"],
    "ogg": ["-c:a", "libvorbis", "-q:a", "5"],
    "flac": ["-c:a", "flac"],
}


def convert(src, out_dir, fmt, opts):
    out = Path(out_dir) / f"{Path(src).stem}.{fmt}"
    height = int(opts.get("resolution") or 0)
    scale = [f"scale=-2:{height}"] if height else []
    args = [require("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", src]
    if fmt == "mp4":
        args += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart"]
    elif fmt == "webm":
        args += ["-c:v", "libvpx-vp9", "-crf", "33", "-b:v", "0", "-deadline", "realtime", "-cpu-used", "8",
                 "-c:a", "libopus"]
    elif fmt == "gif":
        size = f"scale=-2:{height or 360}:flags=lanczos"
        args += ["-an", "-vf", f"fps=12,{size},split[a][b];[a]palettegen[p];[b][p]paletteuse"]
        scale = []
    else:  # audio output, also "extract audio" from a video
        args += ["-vn", *AUDIO_CODEC[fmt]]
    if scale:
        args += ["-vf", ",".join(scale)]
    run(args + [out], opts["_timeout"])
    return [out]
