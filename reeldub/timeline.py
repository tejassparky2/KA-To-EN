"""Fit each English line into its time slot, lay them on the reel's timeline, and mix with the music bed.

Timing rules (from the dubbing toolkits and Amazon's automatic-dubbing papers, see reports/):
1. Use the pause after a line before touching speed.
2. Speed up with pitch-preserving rubberband; up to 1.2x is accepted, 1.4x is the hard cap.
   (2x and above is unintelligible per Amazon's scoring.)
3. Anything that still doesn't fit is reported so the line can be re-translated shorter.
Video is never slowed: a slowed talking face is visible.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import media
from .segments import Script, slot_end

ACCEPT_TEMPO = 1.2
HARD_TEMPO = 1.4
MIN_TEMPO = 0.88  # slowest we go to make a short English line last as long as her Kannada one


@dataclass
class Fit:
    id: int
    start: float
    natural: float  # seconds the TTS line takes at normal speed
    slot: float  # seconds available
    tempo: float
    status: str  # ok | slowed | stretched | over_accept | too_long

    @property
    def placed(self) -> float:
        return self.natural / self.tempo


def plan_fit(script: Script, naturals: list[float], accept: float = ACCEPT_TEMPO, hard: float = HARD_TEMPO,
             slowest: float = MIN_TEMPO) -> list[Fit]:
    """Tempo per line: speed up a line that overruns its slot, slow down (a little) one that ends before she does,
    so the English starts and stops with her mouth instead of leaving a silent gap."""
    fits = []
    for i, (seg, nat) in enumerate(zip(script.segments, naturals)):
        slot = slot_end(script.segments, i, script.total) - seg.start
        ratio = nat / slot if slot > 0 else float("inf")
        if nat < seg.dur * 0.97 and nat > 0:
            tempo = max(nat / seg.dur, slowest)
            tempo, status = (round(tempo, 4), "slowed") if tempo < 0.99 else (1.0, "ok")
        elif ratio <= 1.0:
            tempo, status = 1.0, "ok"
        elif ratio <= accept:
            tempo, status = ratio, "stretched"
        elif ratio <= hard:
            tempo, status = ratio, "over_accept"
        else:
            tempo, status = hard, "too_long"
        fits.append(Fit(seg.id, seg.start, round(nat, 3), round(slot, 3), round(tempo, 4), status))
    return fits


def trim_silence(src: Path, out: Path, threshold_db: float = -45.0) -> Path:
    """Strip leading/trailing silence that TTS engines add, so durations are honest."""
    trim = f"silenceremove=start_periods=1:start_threshold={threshold_db}dB:start_silence=0.03"
    media.ffmpeg("-i", str(src), "-af", f"{trim},areverse,{trim},areverse", "-ac", "1", "-ar", str(media.SR),
                 "-c:a", "pcm_s16le", str(out))
    return out


def assemble(script: Script, clips: list[Path | None], fits: list[Fit], out: Path, fade: float = 0.08) -> Path:
    """Place (stretched) clips at their start times on a silent track the length of the reel."""
    track = np.zeros(int(script.total * media.SR) + media.SR, dtype=np.float32)
    for i, (clip, fit) in enumerate(zip(clips, fits)):
        if clip is None:  # line left empty on purpose
            continue
        stretched = clip.with_name(clip.stem + ".fit.wav")
        media.time_stretch(clip, stretched, fit.tempo)
        audio = media.read_audio(stretched)[:, 0]
        start = int(fit.start * media.SR)
        limit = int(slot_end(script.segments, i, script.total) * media.SR) + int(0.15 * media.SR)
        audio = audio[: max(0, min(len(audio), limit - start))]
        if fit.status == "too_long" and len(audio) > int(fade * media.SR):
            n = int(fade * media.SR)
            audio[-n:] *= np.linspace(1.0, 0.0, n, dtype=np.float32)
        end = min(len(track), start + len(audio))
        track[start:end] += audio[: end - start]
    track = track[: int(script.total * media.SR)]
    return media.write_audio(out, track[:, None])


def bed_is_voice_leak(bed: Path, script: Script, gap_floor_db: float = -55.0, margin_db: float = 15.0) -> tuple[bool, float, float]:
    """True when the bed is near-silent between her lines but not under them: no real music, only Kannada left over
    from separation. Returns (leak, dB under speech, dB in gaps)."""
    x = media.read_audio(bed).mean(axis=1)
    speech = np.zeros(len(x), bool)
    for s in script.segments:
        speech[int(s.start * media.SR):int(s.end * media.SR)] = True

    def db(a: np.ndarray) -> float:
        return float(20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9)) if len(a) else -120.0

    in_speech, in_gaps = db(x[speech]), db(x[~speech])
    return in_gaps < gap_floor_db and in_speech - in_gaps > margin_db, in_speech, in_gaps


def mix(voice: Path, bed: Path, ref_vocals: Path, out: Path, room: float = 0.0, duck: bool = True,
        lufs: float = -14.0, true_peak: float = -1.0) -> Path:
    """Voice (loudness-matched to her original vocals) over the music bed, normalised for Reels.

    -14 LUFS / -1 dBTP is the common community target for Reels; Meta publishes no official spec.
    `room` (0-1) adds a short early-reflection tail so a dry clone sounds like it was in the same room.
    """
    gain = media.loudness_lufs(ref_vocals) - media.loudness_lufs(voice)
    vchain = f"volume={gain:.2f}dB,aformat=channel_layouts=stereo"
    if room > 0:
        vchain += f",aecho=0.9:0.9:23|41|67:{0.25 * room:.3f}|{0.16 * room:.3f}|{0.09 * room:.3f}"
    graph = f"[0:a]{vchain},asplit=2[v1][v2];[1:a]aformat=channel_layouts=stereo[b];"
    if duck:
        graph += "[b][v1]sidechaincompress=threshold=0.04:ratio=3:attack=15:release=350[bd];"
    else:
        graph += "[b]anull[bd];[v1]anullsink;"
    graph += (f"[bd][v2]amix=inputs=2:normalize=0:duration=longest,"
              f"loudnorm=I={lufs}:TP={true_peak}:LRA=11,aresample={media.SR}[out]")
    media.ffmpeg("-i", str(voice), "-i", str(bed), "-filter_complex", graph, "-map", "[out]",
                 "-c:a", "pcm_s16le", str(out))
    return out
