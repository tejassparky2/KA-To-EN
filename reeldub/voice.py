"""Her voice: reference clips, cloned-voice creation, and English speech in that voice.

Accent is the whole game here. Research summary (see reports/):
- ElevenLabs `eleven_multilingual_v2` is documented to keep a clone's accent across languages -> default.
- ElevenLabs Eleven v4 deliberately drops the reference accent when the output language differs, so do NOT
  use v4 with a Kannada reference (it is fine with a reference of her speaking English).
- Sarvam's cross-lingual clone speaks `en-IN` (Indian English) and its docs say a hint of the reference
  accent carries over.
- Voice conversion (`sts`): someone performs the English in an Indian accent, to the reel's timing,
  and ElevenLabs converts the timbre to hers. Most control over accent, emotion and timing.
Consent: only clone her voice with her explicit permission; ElevenLabs PVC must be created by her.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path

import requests

from . import media
from .segments import Script

SARVAM_BASE = "https://api.sarvam.ai"
VOICES_FILE = Path("voices/voices.json")


# ---------------------------------------------------------------- reference clips

def best_window(script: Script, target: float) -> tuple[float, float]:
    """Contiguous run of lines, at most `target` seconds long, with the most actual speech in it."""
    segs = script.segments
    best, best_speech = (0.0, 0.0), -1.0
    for i in range(len(segs)):
        speech = 0.0
        for j in range(i, len(segs)):
            if segs[j].end - segs[i].start > target:
                break
            speech += segs[j].dur
            if speech > best_speech:
                best, best_speech = (segs[i].start, segs[j].end), speech
    return best


def make_reference(workdirs: list[Path], out: Path, seconds: float) -> Path:
    """Build a clean reference clip from the separated vocals of one or more reels.

    Sarvam wants 10-15 s (closer to 15 for cross-lingual). ElevenLabs instant clones want ~1-2 min.
    Listen to the result: it must be only her, no music, no other voices.
    """
    pieces, remaining = [], seconds
    for wd in workdirs:
        if remaining <= 1.0:
            break
        script = Script.load(wd / "transcript.json")
        s, e = best_window(script, remaining)
        if e - s < 1.0:
            continue
        pieces.append(media.cut(wd / "vocals.wav", out.parent / f"_ref_{wd.name}.wav", s, e, sr=24000, mono=True))
        remaining -= e - s
    if not pieces:
        raise SystemExit("no usable speech found; run `prepare` first")
    out.parent.mkdir(parents=True, exist_ok=True)
    if len(pieces) == 1:
        pieces[0].replace(out)
    else:
        inputs = sum((["-i", str(p)] for p in pieces), [])
        media.ffmpeg(*inputs, "-filter_complex", f"concat=n={len(pieces)}:v=0:a=1", "-c:a", "pcm_s16le", str(out))
        for p in pieces:
            p.unlink()
    return out


# ---------------------------------------------------------------- voice registry

def save_voice(backend: str, voice_id: str) -> None:
    VOICES_FILE.parent.mkdir(exist_ok=True)
    data = json.loads(VOICES_FILE.read_text()) if VOICES_FILE.exists() else {}
    data[backend] = voice_id
    VOICES_FILE.write_text(json.dumps(data, indent=2))


def load_voice(backend: str) -> str | None:
    if VOICES_FILE.exists():
        return json.loads(VOICES_FILE.read_text()).get(backend)
    return None


def _key(name: str) -> str:
    key = os.environ.get(name)
    if not key:
        raise SystemExit(f"{name} is not set")
    return key


def _multipart(fields: dict) -> dict:
    """requests only sends multipart/form-data when given `files`; Sarvam's voice endpoints require it."""
    return {k: (None, str(v)) for k, v in fields.items() if v is not None}


def create_voice_sarvam(ref: Path, name: str, ref_language: str = "kn-IN") -> str:
    with open(ref, "rb") as f:
        files = _multipart({"name": name, "language": ref_language})
        files["file"] = (ref.name, f, "audio/wav")
        r = requests.post(f"{SARVAM_BASE}/voices/create", headers={"api-subscription-key": _key("SARVAM_API_KEY")},
                          files=files, timeout=300)
    r.raise_for_status()
    return r.json()["data"]["voice_id"]


def create_voice_elevenlabs(refs: list[Path], name: str) -> str:
    from elevenlabs.client import ElevenLabs
    handles = [open(p, "rb") for p in refs]
    try:
        r = ElevenLabs(api_key=_key("ELEVENLABS_API_KEY")).voices.ivc.create(
            name=name, files=handles, description="Private clone, created with her consent, for dubbing her own reels.")
    finally:
        for h in handles:
            h.close()
    return r.voice_id


# ---------------------------------------------------------------- text -> her voice

class SarvamTTS:
    """Sarvam cross-lingual clone, Indian-English output."""

    def __init__(self, voice_id: str, qc: bool = True):
        self.voice_id, self.qc, self.key = voice_id, qc, _key("SARVAM_API_KEY")

    def synth(self, text: str, out: Path, prev: str = "", nxt: str = "") -> Path:
        fields = {"voice_id": self.voice_id, "text": text, "language_code": "en-IN", "output_audio_codec": "wav",
                  "speech_sample_rate": media.SR, "enable_qc": str(self.qc).lower()}
        r = requests.post(f"{SARVAM_BASE}/voices/clone", headers={"api-subscription-key": self.key},
                          files=_multipart(fields), timeout=300)
        r.raise_for_status()
        out.write_bytes(base64.b64decode(r.json()["audio"]))
        return out


class ElevenTTS:
    """ElevenLabs clone. Default model keeps the voice's accent across languages."""

    def __init__(self, voice_id: str, model: str = "eleven_multilingual_v2", stability: float = 0.5,
                 similarity: float = 0.9):
        from elevenlabs.client import ElevenLabs
        from elevenlabs.types import VoiceSettings
        if model.startswith("eleven_v4"):
            print("warning: Eleven v4 drops the reference accent across languages; "
                  "use it only with a voice cloned from her speaking English.")
        self.client = ElevenLabs(api_key=_key("ELEVENLABS_API_KEY"))
        self.voice_id, self.model = voice_id, model
        self.settings = VoiceSettings(stability=stability, similarity_boost=similarity, style=0.0, use_speaker_boost=True)

    def synth(self, text: str, out: Path, prev: str = "", nxt: str = "") -> Path:
        audio = self.client.text_to_speech.convert(
            voice_id=self.voice_id, text=text, model_id=self.model, output_format="mp3_44100_128",
            voice_settings=self.settings, previous_text=prev or None, next_text=nxt or None)
        mp3 = out.with_suffix(".mp3")
        mp3.write_bytes(b"".join(audio))
        media.ffmpeg("-i", str(mp3), "-ar", str(media.SR), "-ac", "1", "-c:a", "pcm_s16le", str(out))
        mp3.unlink()
        return out


def convert_performance(guide: Path, out: Path, voice_id: str, model: str = "eleven_multilingual_sts_v2") -> Path:
    """Voice conversion: keep the guide performance's words, timing, emotion and accent; swap in her timbre."""
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=_key("ELEVENLABS_API_KEY"))
    with open(guide, "rb") as f:
        audio = client.speech_to_speech.convert(voice_id=voice_id, audio=f, model_id=model,
                                                output_format="mp3_44100_128", remove_background_noise=True)
        mp3 = out.with_suffix(".mp3")
        mp3.write_bytes(b"".join(audio))
    media.ffmpeg("-i", str(mp3), "-ar", str(media.SR), "-ac", "1", "-c:a", "pcm_s16le", str(out))
    mp3.unlink()
    return out
