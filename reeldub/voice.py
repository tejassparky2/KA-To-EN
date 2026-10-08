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


# ---------------------------------------------------------------- open-source engines (run locally, CPU ok)

class ChatterboxEngine:
    """Resemble AI Chatterbox (MIT), zero-shot clone from one short clip of her. Output carries a Perth watermark.

    Its model card says a reference in another language makes the output "inherit the accent of the reference
    clip's language" and that cfg_weight=0 removes that. Here we WANT her accent, so cfg stays around 0.5-0.6.
    multilingual=False uses the English-only model; True uses the 23-language model with language_id="en".
    """

    def __init__(self, ref: Path, multilingual: bool = False, exaggeration: float = 0.6, cfg_weight: float = 0.6,
                 temperature: float = 0.8):
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if multilingual:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            # Pass a plain string: chatterbox 0.1.7 checks `device in ["cpu", "mps"]` to load CUDA-saved weights on CPU.
            self.model = ChatterboxMultilingualTTS.from_pretrained(device=device)
        else:
            from chatterbox.tts import ChatterboxTTS
            self.model = ChatterboxTTS.from_pretrained(device=device)
        self.ref, self.multilingual = str(ref), multilingual
        self.kw = dict(exaggeration=exaggeration, cfg_weight=cfg_weight, temperature=temperature)

    def synth(self, text: str, out: Path, prev: str = "", nxt: str = "") -> Path:
        import soundfile as sf
        extra = {"language_id": "en"} if self.multilingual else {}
        wav = self.model.generate(text, audio_prompt_path=self.ref, **extra, **self.kw)
        tmp = out.with_suffix(".24k.wav")
        sf.write(str(tmp), wav.squeeze(0).cpu().numpy(), self.model.sr)
        media.ffmpeg("-i", str(tmp), "-ar", str(media.SR), "-ac", "1", "-c:a", "pcm_s16le", str(out))
        tmp.unlink()
        return out


class KokoroVCEngine:
    """Kokoro-82M (Apache-2.0) speaks the English, Chatterbox VC swaps in her timbre.

    Kokoro has no cloning and no Indian-English voice, so expect Kokoro's (US/UK) accent in her timbre.
    """

    def __init__(self, ref: Path, kokoro_voice: str = "bf_emma", speed: float = 1.0):
        import torch
        from chatterbox.vc import ChatterboxVC
        from kokoro import KPipeline
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = KPipeline(lang_code=kokoro_voice[0], device=device)
        self.vc = ChatterboxVC.from_pretrained(device)
        self.voice, self.speed, self.ref = kokoro_voice, speed, str(ref)

    def synth(self, text: str, out: Path, prev: str = "", nxt: str = "") -> Path:
        import numpy as np
        import soundfile as sf
        audio = np.concatenate([r.audio.numpy() for r in self.pipe(text, voice=self.voice, speed=self.speed)])
        stock = out.with_suffix(".kokoro.wav")
        sf.write(str(stock), audio, 24000)
        wav = self.vc.generate(str(stock), target_voice_path=self.ref)
        tmp = out.with_suffix(".vc.wav")
        sf.write(str(tmp), wav.squeeze(0).cpu().numpy(), self.vc.sr)
        media.ffmpeg("-i", str(tmp), "-ar", str(media.SR), "-ac", "1", "-c:a", "pcm_s16le", str(out))
        stock.unlink()
        tmp.unlink()
        return out


class CheckedEngine:
    """Re-record a line when an English ASR mishears it (up to `tries`), keeping the best take.

    Same idea as Sarvam's built-in QC: zero-shot cloners occasionally slur, skip or repeat words.
    """

    def __init__(self, engine, tries: int = 3, max_wer: float = 0.25, asr_model: str = "openai/whisper-small.en"):
        import torch
        from transformers import pipeline
        self.engine, self.tries, self.max_wer = engine, tries, max_wer
        self.asr = pipeline("automatic-speech-recognition", model=asr_model,
                            device="cuda:0" if torch.cuda.is_available() else "cpu")
        self.log: list[dict] = []

    def synth(self, text: str, out: Path, prev: str = "", nxt: str = "") -> Path:
        best = None
        for k in range(self.tries):
            take = out.with_name(f"{out.stem}.take{k}.wav")
            self.engine.synth(text, take, prev, nxt)
            heard = self.asr(str(take))["text"]
            score = wer(text, heard)
            if best is None or score < best[0]:
                best = (score, take, heard)
            if score <= self.max_wer:
                break
        score, take, heard = best
        take.replace(out)
        for leftover in out.parent.glob(f"{out.stem}.take*.wav"):
            leftover.unlink()
        self.log.append({"text": text, "heard": heard.strip(), "wer": round(score, 3), "takes": k + 1})
        return out


def wer(ref: str, hyp: str) -> float:
    """Word error rate on lowercased words, punctuation ignored."""
    import re
    r, h = re.findall(r"[a-z0-9']+", ref.lower()), re.findall(r"[a-z0-9']+", hyp.lower())
    if not r:
        return 0.0 if not h else 1.0
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev, d[j] = d[j], cur
    return d[len(h)] / len(r)
