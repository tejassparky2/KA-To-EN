"""The per-reel script: a list of timed lines that humans can review and edit between stages.

transcript.json  ->  {"segments": [{"id", "start", "end", "kn"}], ...}
script.json      ->  same, plus "en" (the English line to speak) and review flags.

Edit "kn" or "en" by hand and re-run the next stage; nothing else needs to change.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Segment:
    id: int
    start: float
    end: float
    kn: str
    en: str = ""
    en_literal: str = ""  # optional machine cross-check (e.g. Sarvam speech->English), never spoken
    uncertain: bool = False  # translator flagged a doubt (ASR error, idiom, name) -> human should check
    note: str = ""

    @property
    def dur(self) -> float:
        return self.end - self.start


@dataclass
class Script:
    segments: list[Segment]
    total: float  # reel duration in seconds
    meta: dict = field(default_factory=dict)

    def save(self, path: Path) -> Path:
        data = {"total": self.total, "meta": self.meta, "segments": [asdict(s) for s in self.segments]}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> "Script":
        data = json.loads(path.read_text(encoding="utf-8"))
        segs = [Segment(**s) for s in data["segments"]]
        return cls(segments=segs, total=data["total"], meta=data.get("meta", {}))


def slot_end(segs: list[Segment], i: int, total: float, guard: float = 0.05) -> float:
    """Latest time line i may run to: the next line's start (or the reel's end).

    Using the pause after a line before speeding anything up is what pyVideoTrans does, and it
    sounds far more natural than stretching.
    """
    nxt = segs[i + 1].start if i + 1 < len(segs) else total
    return max(segs[i].end, nxt - guard)


def merge_short(segs: list[Segment], min_dur: float = 0.8, max_gap: float = 0.35, max_len: float = 12.0) -> list[Segment]:
    """Fold very short ASR phrases into a neighbour so each line is a speakable unit."""
    out: list[Segment] = []
    for s in segs:
        if out and (s.dur < min_dur or out[-1].dur < min_dur) and s.start - out[-1].end <= max_gap \
                and s.end - out[-1].start <= max_len:
            prev = out[-1]
            out[-1] = Segment(id=prev.id, start=prev.start, end=s.end, kn=f"{prev.kn} {s.kn}".strip(),
                              en_literal=f"{prev.en_literal} {s.en_literal}".strip())
        else:
            out.append(Segment(**asdict(s)))
    for i, s in enumerate(out):
        s.id = i
    return out
