"""Kannada speech -> timed Kannada text.

Primary: Sarvam saaras (best Kannada WER on the only independent 2026 benchmark: Saaras v3 8.8%).
  REST is meant for clips < 30 s, so the voice stem is cut at pauses into <= 25 s chunks.
  Timestamps are phrase-level, which is the unit we dub anyway.
Alternative: ElevenLabs Scribe v2 (word-level timestamps), grouped into phrases on pauses.

Always run ASR on the separated vocals, not the music mix.
"""

from __future__ import annotations

import os
from pathlib import Path

from . import media
from .segments import Segment, merge_short


def plan_chunks(silences: list[tuple[float, float]], total: float,
                max_len: float = 25.0, min_len: float = 3.0) -> list[tuple[float, float]]:
    """Cut [0, total] into chunks <= max_len, cutting in the middle of pauses where possible."""
    cuts = sorted((s + e) / 2 for s, e in silences if 0 < (s + e) / 2 < total)
    chunks, pos = [], 0.0
    while total - pos > max_len:
        inside = [c for c in cuts if pos + min_len <= c <= pos + max_len]
        nxt = inside[-1] if inside else pos + max_len
        chunks.append((pos, nxt))
        pos = nxt
    chunks.append((pos, total))
    return chunks


def _sarvam_client():
    from sarvamai import SarvamAI
    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        raise SystemExit("SARVAM_API_KEY is not set (get one at https://dashboard.sarvam.ai/key-management)")
    return SarvamAI(api_subscription_key=key)


def _sarvam_phrases(client, wav: Path, offset: float, chunk_end: float, model: str, mode: str):
    with open(wav, "rb") as f:
        r = client.speech_to_text.transcribe(file=f, model=model, mode=mode, language_code="kn-IN", with_timestamps=True)
    ts = r.timestamps
    if ts and ts.words:
        return [(offset + s, offset + e, t.strip())
                for t, s, e in zip(ts.words, ts.start_time_seconds, ts.end_time_seconds) if t.strip()]
    return [(offset, chunk_end, r.transcript.strip())] if r.transcript.strip() else []


def transcribe_sarvam(vocals: Path, workdir: Path, model: str = "saaras:v4", mode: str = "codemix",
                      literal: bool = True) -> list[Segment]:
    """mode='codemix' keeps her English words in Latin script; 'transcribe' writes everything in Kannada script.

    With literal=True, also asks Sarvam for a direct speech->English translation (mode='translate')
    and stores it as `en_literal`: a cross-check for the human reviewer and a hint for the LLM translator.
    """
    client = _sarvam_client()
    mono = media.to_mono(vocals, workdir / "vocals_16k.wav")
    total = media.duration(mono)
    chunks = plan_chunks(media.detect_silences(mono), total)
    chunk_dir = workdir / "asr_chunks"
    chunk_dir.mkdir(exist_ok=True)

    phrases, literal_phrases = [], []
    for i, (s, e) in enumerate(chunks):
        wav = media.cut(mono, chunk_dir / f"chunk_{i:03d}.wav", s, e)
        phrases += _sarvam_phrases(client, wav, s, e, model, mode)
        if literal:
            literal_phrases += _sarvam_phrases(client, wav, s, e, model, "translate")

    segs = [Segment(id=i, start=round(s, 3), end=round(e, 3), kn=t) for i, (s, e, t) in enumerate(phrases)]
    for s, e, t in literal_phrases:  # attach each English phrase to the Kannada line it overlaps most
        best = max(segs, key=lambda g: min(e, g.end) - max(s, g.start), default=None)
        if best is not None and min(e, best.end) - max(s, best.start) > 0:
            best.en_literal = f"{best.en_literal} {t}".strip()
    return merge_short(segs)


def group_words(words: list[tuple[float, float, str]], max_gap: float = 0.45, max_len: float = 8.0) -> list[Segment]:
    """Group word timings into phrases at pauses (> max_gap) or when a phrase gets long."""
    segs: list[Segment] = []
    cur: list[tuple[float, float, str]] = []
    for w in words:
        if cur and (w[0] - cur[-1][1] > max_gap or w[1] - cur[0][0] > max_len):
            segs.append(Segment(id=len(segs), start=cur[0][0], end=cur[-1][1], kn=" ".join(x[2] for x in cur)))
            cur = []
        cur.append(w)
    if cur:
        segs.append(Segment(id=len(segs), start=cur[0][0], end=cur[-1][1], kn=" ".join(x[2] for x in cur)))
    return segs


def transcribe_elevenlabs(vocals: Path, workdir: Path, model: str = "scribe_v2") -> list[Segment]:
    from elevenlabs.client import ElevenLabs
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    mono = media.to_mono(vocals, workdir / "vocals_16k.wav")
    with open(mono, "rb") as f:
        r = ElevenLabs(api_key=key).speech_to_text.convert(
            model_id=model, file=f, language_code="kan", timestamps_granularity="word", tag_audio_events=False)
    words = [(w.start, w.end, w.text.strip()) for w in r.words if w.type == "word" and w.text.strip()]
    return merge_short(group_words(words))
