"""Thin ffmpeg/ffprobe helpers. Everything here runs on CPU."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 44100  # working sample rate for all intermediate audio


def run(cmd: list[str]) -> str:
    """Run a command, raise with stderr tail on failure, return stderr (ffmpeg logs there)."""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-20:])
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{tail}")
    return proc.stderr


def ffmpeg(*args: str) -> str:
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *args])


def duration(path: str | Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def has_audio(path: str | Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return bool(out.strip())


def extract_audio(video: Path, out_wav: Path, sr: int = SR, mono: bool = False) -> Path:
    ffmpeg("-i", str(video), "-vn", "-ac", "1" if mono else "2", "-ar", str(sr), "-c:a", "pcm_s16le", str(out_wav))
    return out_wav


def to_mono(src: Path, out_wav: Path, sr: int = 16000, normalize: bool = True) -> Path:
    """Mono copy for ASR. Normalising loudness helps both ASR and pause detection on quiet recordings."""
    args = ["-i", str(src), "-ac", "1", "-ar", str(sr)]
    if normalize:
        args += ["-af", "loudnorm=I=-23:TP=-2"]
    ffmpeg(*args, "-c:a", "pcm_s16le", str(out_wav))
    return out_wav


def cut(src: Path, out: Path, start: float, end: float, sr: int | None = None, mono: bool = False) -> Path:
    args = ["-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(src)]
    if mono:
        args += ["-ac", "1"]
    if sr:
        args += ["-ar", str(sr)]
    ffmpeg(*args, "-c:a", "pcm_s16le", str(out))
    return out


def detect_silences(path: Path, noise_db: float | None = None, min_dur: float = 0.3) -> list[tuple[float, float]]:
    """Return (start, end) silence intervals using ffmpeg silencedetect.

    By default the threshold sits 22 dB below the file's integrated loudness, so it works on quiet and loud
    recordings alike.
    """
    if noise_db is None:
        noise_db = loudness_lufs(path) - 22.0
    log = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path),
               "-af", f"silencedetect=noise={noise_db}dB:d={min_dur}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    total = duration(path)
    if len(ends) < len(starts):  # trailing silence runs to end of file
        ends.append(total)
    return [(max(0.0, s), e) for s, e in zip(starts, ends)]


def detect_scene_cuts(video: Path, threshold: float = 0.35) -> list[float]:
    """Timestamps (s) of hard cuts, via ffmpeg's scene-change score."""
    log = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(video),
               "-vf", f"select='gt(scene,{threshold})',showinfo", "-an", "-f", "null", "-"])
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]


def time_stretch(src: Path, out: Path, tempo: float) -> Path:
    """Change speed without changing pitch. tempo > 1 speeds up. Uses rubberband (better on speech than atempo)."""
    if abs(tempo - 1.0) < 1e-3:
        ffmpeg("-i", str(src), "-c:a", "pcm_s16le", str(out))
    else:
        ffmpeg("-i", str(src), "-af", f"rubberband=tempo={tempo:.4f}", "-c:a", "pcm_s16le", str(out))
    return out


def loudness_lufs(path: Path) -> float:
    """Integrated loudness (LUFS) via loudnorm's measurement pass."""
    log = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path),
               "-af", "loudnorm=print_format=json", "-f", "null", "-"])
    blob = log[log.rfind("{"): log.rfind("}") + 1]
    return float(json.loads(blob)["input_i"])


def read_audio(path: Path, sr: int = SR) -> np.ndarray:
    """Read as float32 (frames, channels) at `sr`, resampling via ffmpeg if needed."""
    info = sf.info(str(path))
    if info.samplerate != sr:
        tmp = path.with_suffix(f".{sr}.wav")
        ffmpeg("-i", str(path), "-ar", str(sr), "-c:a", "pcm_s16le", str(tmp))
        path = tmp
    data, _ = sf.read(str(path), dtype="float32", always_2d=True)
    return data


def write_audio(path: Path, data: np.ndarray, sr: int = SR) -> Path:
    sf.write(str(path), np.clip(data, -1.0, 1.0), sr, subtype="PCM_16")
    return path


def subtract(mix: Path, stem: Path, out: Path) -> Path:
    """out = mix - stem (sample-aligned). Gives a music bed that keeps everything that isn't the voice."""
    a, b = read_audio(mix), read_audio(stem)
    if b.shape[1] != a.shape[1]:
        b = np.repeat(b[:, :1], a.shape[1], axis=1)
    n = min(len(a), len(b))
    bed = a.copy()
    bed[:n] -= b[:n]
    return write_audio(out, bed)


def mux(video: Path, audio: Path, out: Path) -> Path:
    """Replace the video's audio track. Video stream is copied untouched."""
    ffmpeg("-i", str(video), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out))
    return out
