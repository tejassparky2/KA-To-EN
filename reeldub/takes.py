"""A person reads the English script into one recording; cut it into lines and place each on her timing.

The reader pauses between lines and may repeat a line after a stumble. We split the recording at pauses,
transcribe each piece with Whisper, then align pieces to script lines in order: each line takes one or more
consecutive pieces, and a piece that matches nothing (a false start, a cough, a worse take) is dropped.
"""

from __future__ import annotations

from pathlib import Path

from . import media
from .segments import Script
from .voice import wer

SKIP_COST = 0.05  # dropping a piece: a needed piece still wins (its words would count as missing), a repeat loses
MISSING_COST = 1.5  # a line nobody read
MAX_GROUP = 4  # pieces one line may span (a mid-line breath can split it)


def speech_pieces(silences: list[tuple[float, float]], total: float, pad: float = 0.08,
                  min_len: float = 0.25) -> list[tuple[float, float]]:
    """Speech spans between the pauses, slightly padded so word edges aren't clipped."""
    pieces, t = [], 0.0
    for s, e in sorted(silences) + [(total, total)]:
        if s - t >= min_len:
            pieces.append((max(0.0, t - pad), min(total, s + pad)))
        t = max(t, e)
    return pieces


def align(lines: list[str], heard: list[str]) -> list[tuple[int, int] | None]:
    """For each line, the [a, b) range of pieces read for it (None if missing), keeping order.

    Minimises total WER over lines plus SKIP_COST per dropped piece. When a line is read twice, the retake that
    matches better is kept and the other dropped, because a doubled transcript scores worse than either take.
    """
    n, m = len(lines), len(heard)
    inf = float("inf")
    f = [[inf] * (n + 1) for _ in range(m + 1)]
    back: list[list[tuple | None]] = [[None] * (n + 1) for _ in range(m + 1)]
    f[0][0] = 0.0
    for i in range(m + 1):
        for j in range(n + 1):
            c = f[i][j]
            if c == inf:
                continue
            if i < m and c + SKIP_COST < f[i + 1][j]:
                f[i + 1][j], back[i + 1][j] = c + SKIP_COST, ("skip", i)
            if j < n:
                if c + MISSING_COST < f[i][j + 1]:
                    f[i][j + 1], back[i][j + 1] = c + MISSING_COST, ("missing", i)
                for b in range(i + 1, min(m, i + MAX_GROUP) + 1):
                    cost = c + wer(lines[j], " ".join(heard[i:b]))
                    if cost < f[b][j + 1]:
                        f[b][j + 1], back[b][j + 1] = cost, ("take", i)
    out: list[tuple[int, int] | None] = [None] * n
    i, j = m, n
    while i or j:
        kind, prev_i = back[i][j]
        if kind == "skip":
            i = prev_i
            continue
        j -= 1
        out[j] = (prev_i, i) if kind == "take" else None
        i = prev_i
    return out


def import_takes(script: Script, recording: Path, out_dir: Path, asr_model: str = "openai/whisper-small.en"):
    """Cut the recording into one clean clip per script line. Returns (clips, report)."""
    import torch
    from transformers import pipeline

    out_dir.mkdir(parents=True, exist_ok=True)
    full = out_dir / "recording.wav"  # mono, rumble and steady hiss (fans) reduced
    media.ffmpeg("-i", str(recording), "-ac", "1", "-ar", str(media.SR), "-af", "highpass=f=70,afftdn=nf=-30",
                 "-c:a", "pcm_s16le", str(full))
    total = media.duration(full)
    pieces = speech_pieces(media.detect_silences(full, min_dur=0.6), total)
    asr = pipeline("automatic-speech-recognition", model=asr_model,
                   device="cuda:0" if torch.cuda.is_available() else "cpu")
    heard = []
    for k, (s, e) in enumerate(pieces):
        clip = media.cut(full, out_dir / f"piece_{k:03d}.wav", s, e, sr=16000, mono=True)
        heard.append(asr(str(clip))["text"].strip())
        clip.unlink()

    spoken = [s for s in script.segments if s.en.strip()]
    groups = align([s.en for s in spoken], heard)
    by_id = {s.id: (g, s) for g, s in zip(groups, spoken)}
    clips, report = [], []
    for seg in script.segments:
        g, _ = by_id.get(seg.id, (None, None))
        if not seg.en.strip() or g is None:
            clips.append(None)
            if seg.en.strip():
                report.append({"id": seg.id, "text": seg.en, "heard": "", "wer": 1.0})
            continue
        a, b = g
        clip = media.cut(full, out_dir / f"line_{seg.id:03d}.wav", pieces[a][0], pieces[b - 1][1])
        clips.append(clip)
        said = " ".join(heard[a:b])
        report.append({"id": seg.id, "text": seg.en, "heard": said, "wer": round(wer(seg.en, said), 3)})
    used = {k for g in groups if g for k in range(*g)}
    dropped = [heard[k] for k in range(len(pieces)) if k not in used]
    return clips, {"lines": report, "dropped_pieces": dropped, "pieces": len(pieces)}
