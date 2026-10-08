"""End-to-end run of the CLI stages with the paid APIs replaced by offline fakes.

Checks the glue: work-dir layout, JSON hand-offs, TTS caching, fitting, mixing and muxing.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from reeldub import cli, media
from reeldub.segments import Segment
from reeldub.translate import count_syllables


@pytest.fixture()
def reel(tmp_path):
    """9 s vertical clip: tone 'speech' 0.5-3.5 s and 5-8 s over quiet noise."""
    tone = tmp_path / "tone.wav"
    media.ffmpeg("-f", "lavfi", "-i", "sine=f=300:r=44100:d=9", "-af",
                 "volume='if(between(t,0.5,3.5)+between(t,5,8),1,0)':eval=frame", "-ac", "2", str(tone))
    out = tmp_path / "reel.mp4"
    media.ffmpeg("-f", "lavfi", "-i", "testsrc2=s=360x640:r=25:d=9", "-i", str(tone), "-f", "lavfi",
                 "-i", "anoisesrc=c=pink:a=0.01:r=44100:d=9", "-filter_complex", "[1:a][2:a]amix=inputs=2[a]",
                 "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                 "-shortest", str(out))
    return out


class FakeTTS:
    calls = 0

    def synth(self, text, out, prev="", nxt=""):
        FakeTTS.calls += 1
        dur = 0.2 * count_syllables(text)
        t = np.arange(int(dur * media.SR)) / media.SR
        media.write_audio(out, (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)[:, None])
        return out


def test_offline_pipeline(reel, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def fake_asr(vocals, workdir, **kw):
        return [Segment(0, 0.5, 3.5, "ನಮಸ್ಕಾರ ಎಲ್ಲರಿಗೂ"), Segment(1, 5.0, 8.0, "ಇವತ್ತು ರಾಗಿ ಮುದ್ದೆ ಮಾಡೋಣ")]

    def fake_translate(script, **kw):
        script.segments[0].en = "Namaskara everyone"
        script.segments[1].en = "Today we will make ragi mudde, it is very simple and very tasty, see"
        return script

    monkeypatch.setattr("reeldub.asr.transcribe_sarvam", fake_asr)
    monkeypatch.setattr("reeldub.translate.translate_claude", fake_translate)
    monkeypatch.setattr(cli, "_tts", lambda a: (FakeTTS(), "fake"))

    cli.main(["prepare", str(reel), "--no-separate"])
    wd = Path("work/reel")
    assert (wd / "transcript.json").exists()

    cli.main(["translate", str(wd)])
    script = json.loads((wd / "script.json").read_text())
    assert script["segments"][1]["en"].startswith("Today")
    assert "ragi mudde" in (wd / "script_review.md").read_text()

    cli.main(["synth", str(wd)])
    fits = json.loads((wd / "fit_report.json").read_text())
    assert [f["status"] for f in fits][0] in ("ok", "slowed")  # short line fits (slowed at most to MIN_TEMPO)
    assert fits[1]["tempo"] > 1.0  # the long line had to be sped up
    assert abs(media.duration(wd / "voice_en.wav") - media.duration(wd / "audio.wav")) < 0.05

    calls = FakeTTS.calls
    cli.main(["synth", str(wd)])  # unchanged lines come from cache
    assert FakeTTS.calls == calls

    cli.main(["mix", str(wd)])
    assert media.has_audio(wd / "dubbed.mp4")
    assert abs(media.loudness_lufs(wd / "mix.wav") - (-14.0)) < 1.5


def test_lipsync_per_shot_offline(tmp_path, monkeypatch):
    """Two shots, speech only in the second: only that shot is sent, and the result re-joins cleanly."""
    a, b, video = tmp_path / "a.mp4", tmp_path / "b.mp4", tmp_path / "v.mp4"
    media.ffmpeg("-f", "lavfi", "-i", "testsrc2=s=360x640:r=25:d=3", "-pix_fmt", "yuv420p", str(a))
    media.ffmpeg("-f", "lavfi", "-i", "smptebars=s=360x640:r=25:d=3", "-pix_fmt", "yuv420p", str(b))
    media.ffmpeg("-i", str(a), "-i", str(b), "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]",
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video))
    voice = tmp_path / "voice.wav"
    t = np.arange(6 * media.SR) / media.SR
    media.write_audio(voice, (0.3 * np.sin(2 * np.pi * 220 * t) * (t > 3.5)).astype(np.float32)[:, None])

    sent = []

    def fake_fal(v, au, out, model):
        sent.append(v.name)
        media.ffmpeg("-i", str(v), "-c", "copy", str(out))
        return out

    from reeldub import lipsync
    monkeypatch.setattr(lipsync, "_fal_lipsync", fake_fal)
    out = lipsync.lipsync(video, voice, tmp_path, tmp_path / "synced.mp4")
    assert sent == ["shot_01.mp4"]
    assert abs(media.duration(out) - 6.0) < 0.1


def test_abtest_offline(tmp_path, monkeypatch):
    from reeldub import voice
    from reeldub.segments import Script
    monkeypatch.chdir(tmp_path)
    wd = Path("work/r")
    wd.mkdir(parents=True)
    Script([Segment(0, 0, 1, "k", en="Hello everyone"), Segment(1, 2, 3, "k", en="Let us start")], 4.0).save(wd / "script.json")
    monkeypatch.setattr(voice, "load_voice", lambda b: "vid")
    monkeypatch.setattr(voice, "SarvamTTS", lambda vid: FakeTTS())
    monkeypatch.setattr(voice, "ElevenTTS", lambda vid, model: FakeTTS())
    cli.main(["abtest", str(wd), "--engine", "sarvam", "--engine", "elevenlabs:eleven_multilingual_v2"])
    key = json.loads((wd / "abtest" / "KEY_do_not_open_until_rated.json").read_text())
    assert sorted(key.values()) == ["elevenlabs:eleven_multilingual_v2", "sarvam"]
    for letter in key:
        assert media.duration(wd / "abtest" / f"{letter}.wav") > 1.0
