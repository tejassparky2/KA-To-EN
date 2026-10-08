"""Re-time her mouth to the English voice with a hosted lip-sync model (needs FAL_KEY).

- fal-ai/latentsync (LatentSync, ByteDance): ~$0.20 per clip up to 40 s, then $0.005/s. Default.
- fal-ai/sync-lipsync/v2/pro (Sync lipsync-2-pro): ~$5/min, better teeth; for hard shots.
Drive it with the clean English voice (no music), then put the final mix back on afterwards.
With per_shot=True the reel is split at hard cuts and only shots that contain dubbed speech are sent,
since sync drift across cuts is a known failure and silent shots should keep her real mouth.
"""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path

import numpy as np

from . import media

ENDPOINTS = {
    "latentsync": ("fal-ai/latentsync", {}),
    "sync-pro": ("fal-ai/sync-lipsync/v2/pro", {"sync_mode": "cut_off"}),
}


def _fal_lipsync(video: Path, audio: Path, out: Path, model: str) -> Path:
    import fal_client
    if not os.environ.get("FAL_KEY"):
        raise SystemExit("FAL_KEY is not set (https://fal.ai/dashboard/keys)")
    endpoint, extra = ENDPOINTS[model]
    args = {"video_url": fal_client.upload_file(video), "audio_url": fal_client.upload_file(audio), **extra}
    result = fal_client.subscribe(endpoint, arguments=args, with_logs=False)
    urllib.request.urlretrieve(result["video"]["url"], out)
    return out


def _has_speech(audio: Path, start: float, end: float, floor: float = 0.01) -> bool:
    data = media.read_audio(audio)[int(start * media.SR): int(end * media.SR)]
    return data.size > 0 and float(np.sqrt(np.mean(data ** 2))) > floor


def lipsync(video: Path, voice: Path, workdir: Path, out: Path, model: str = "latentsync", per_shot: bool = True) -> Path:
    total = media.duration(video)
    cuts = [c for c in media.detect_scene_cuts(video) if 0.5 < c < total - 0.5] if per_shot else []
    bounds = [0.0, *cuts, total]
    if len(bounds) == 2:
        return _fal_lipsync(video, voice, out, model)

    shot_dir = workdir / "shots"
    shot_dir.mkdir(exist_ok=True)
    parts = []
    for k, (s, e) in enumerate(zip(bounds, bounds[1:])):
        clip = shot_dir / f"shot_{k:02d}.mp4"
        # Re-encode for frame-accurate cuts; audio is replaced later anyway.
        media.ffmpeg("-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", str(video), "-an", "-c:v", "libx264",
                     "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", str(clip))
        if _has_speech(voice, s, e):
            aud = media.cut(voice, shot_dir / f"shot_{k:02d}.wav", s, e)
            synced = shot_dir / f"shot_{k:02d}.synced.mp4"
            _fal_lipsync(clip, aud, synced, model)
            parts.append(synced)
        else:
            parts.append(clip)

    w, h, fps = _video_props(video)
    norm = [f"[{i}:v]scale={w}:{h},fps={fps},setsar=1,format=yuv420p[v{i}]" for i in range(len(parts))]
    graph = ";".join(norm) + ";" + "".join(f"[v{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[out]"
    inputs = sum((["-i", str(p)] for p in parts), [])
    media.ffmpeg(*inputs, "-filter_complex", graph, "-map", "[out]", "-c:v", "libx264", "-crf", "16",
                 "-preset", "medium", str(out))
    return out


def _video_props(video: Path) -> tuple[int, int, str]:
    import json
    import subprocess
    info = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
         "-of", "json", str(video)], capture_output=True, text=True, check=True).stdout)["streams"][0]
    return info["width"], info["height"], info["r_frame_rate"]
