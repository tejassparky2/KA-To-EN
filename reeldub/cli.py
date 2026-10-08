"""Command line: one subcommand per stage, with human review between transcription, translation and voicing.

    python -m reeldub prepare reels/recipe.mp4          # separate music, transcribe Kannada
    python -m reeldub translate work/recipe              # -> script.json + script_review.md  (REVIEW IT)
    python -m reeldub make-ref work/recipe --seconds 15  # clean 15 s clip of her voice (listen to it)
    python -m reeldub create-voice --backend sarvam --ref voices/ref.wav --name amma
    python -m reeldub synth work/recipe --tts sarvam     # English lines in her voice, fitted to timing
    python -m reeldub mix work/recipe                    # over the original music -> dubbed.mp4
    python -m reeldub lipsync work/recipe                # mouth matched to English -> final.mp4
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from . import media
from .segments import Script

WORK = Path("work")


def _workdir(arg: str) -> Path:
    p = Path(arg)
    if p.is_dir():
        return p
    p = WORK / Path(arg).stem
    if not p.is_dir():
        raise SystemExit(f"no work dir for {arg}; run `prepare` first")
    return p


# ---------------------------------------------------------------- stages

def cmd_fetch(a):
    out = Path(a.out)
    out.mkdir(exist_ok=True)
    cmd = [sys.executable, "-m", "yt_dlp", "-o", str(out / "%(id)s.%(ext)s"), "-f", "bv*+ba/b", "--merge-output-format", "mp4"]
    if a.cookies:
        cmd += ["--cookies", a.cookies]
    subprocess.run(cmd + a.urls, check=True)


def cmd_prepare(a):
    from . import asr
    video = Path(a.video)
    wd = WORK / video.stem
    wd.mkdir(parents=True, exist_ok=True)
    src = wd / "source.mp4"
    if not src.exists():
        shutil.copy(video, src)
    if not media.has_audio(src):
        raise SystemExit("video has no audio track")
    audio = media.extract_audio(src, wd / "audio.wav")
    total = media.duration(audio)

    if a.no_separate:
        shutil.copy(audio, wd / "vocals.wav")
        media.write_audio(wd / "bed.wav", 0 * media.read_audio(audio))
    else:
        from .separate import separate
        print("separating voice from music (CPU, may take a few minutes)...")
        separate(audio, wd, model=a.sep_model)

    print(f"transcribing Kannada with {a.asr}...")
    if a.asr == "sarvam":
        segs = asr.transcribe_sarvam(wd / "vocals.wav", wd, model=a.model, mode=a.mode, literal=not a.no_literal)
    elif a.asr == "whisper":
        segs = asr.transcribe_whisper(wd / "vocals.wav", wd)
    else:
        segs = asr.transcribe_elevenlabs(wd / "vocals.wav", wd)
    script = Script(segments=segs, total=total, meta={"asr": a.asr, "asr_model": a.model, "source": str(video)})
    script.save(wd / "transcript.json")
    for s in segs:
        print(f"  [{s.start:6.2f}-{s.end:6.2f}] {s.kn}")
    print(f"\n{len(segs)} lines -> {wd/'transcript.json'}\n"
          "Have a Kannada speaker check/fix the 'kn' text there, then run `translate`.")


def write_review(script: Script, path: Path, budgets: list[int]) -> None:
    from .translate import count_syllables
    lines = ["# Translation review", "",
             "Check every line: is the English what she meant, and does it sound like her? "
             "Edit `en` in script.json (not this file), then run `synth`.", "",
             "| # | time | Kannada | machine literal | English (spoken) | syll/budget | check |",
             "|---|---|---|---|---|---|---|"]
    for s, b in zip(script.segments, budgets):
        flag = f"⚠ {s.note}" if s.uncertain else ""
        n = count_syllables(s.en)
        if n > b * 1.15:
            flag += " long"
        cells = [str(s.id), f"{s.start:.1f}-{s.end:.1f}", s.kn, s.en_literal, s.en, f"{n}/{b}", flag.strip()]
        lines.append("| " + " | ".join(c.replace("|", "/") for c in cells) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_translate(a):
    from . import translate as tr
    wd = _workdir(a.work)
    script = Script.load(wd / "transcript.json")
    if a.backend == "claude":
        persona = Path(a.persona).read_text(encoding="utf-8") if a.persona else ""
        glossary = Path(a.glossary).read_text(encoding="utf-8") if a.glossary else ""
        tr.translate_claude(script, persona=persona, glossary=glossary, model=a.model or tr.DEFAULT_MODEL)
    else:
        tr.translate_sarvam(script)
    script.save(wd / "script.json")
    write_review(script, wd / "script_review.md", tr.budgets(script))
    flagged = sum(s.uncertain for s in script.segments)
    for s in script.segments:
        print(f"  [{s.start:6.2f}] {'⚠ ' if s.uncertain else ''}{s.en}")
    print(f"\n-> {wd/'script.json'} ({flagged} line(s) flagged for checking)\n"
          f"Read {wd/'script_review.md'}, fix anything in script.json, then run `synth`.")


def cmd_make_ref(a):
    from .voice import make_reference
    out = make_reference([_workdir(w) for w in a.work], Path(a.out), a.seconds)
    print(f"reference clip: {out} ({media.duration(out):.1f} s). Listen: it must be only her voice, no music.")


def cmd_create_voice(a):
    from . import voice
    refs = [Path(r) for r in a.ref]
    if a.backend == "sarvam":
        vid = voice.create_voice_sarvam(refs[0], a.name, a.ref_language)
    else:
        vid = voice.create_voice_elevenlabs(refs, a.name)
    voice.save_voice(a.backend, vid)
    print(f"{a.backend} voice id: {vid} (saved to {voice.VOICES_FILE})")


def _tts(a):
    from . import voice
    vid = a.voice_id or voice.load_voice(a.tts)
    if not vid:
        raise SystemExit(f"no {a.tts} voice id; run `create-voice --backend {a.tts}` or pass --voice-id")
    if a.tts == "sarvam":
        return voice.SarvamTTS(vid), f"sarvam:{vid}"
    model = a.model or "eleven_multilingual_v2"
    return voice.ElevenTTS(vid, model=model), f"elevenlabs:{vid}:{model}"


def _synth_all(script, engine, tag, tts_dir):
    from .timeline import trim_silence
    clips, naturals = [], []
    segs = script.segments
    for i, s in enumerate(segs):
        if not s.en.strip():
            clips.append(None)
            naturals.append(0.0)
            continue
        h = hashlib.sha1(f"{tag}|{s.en}".encode()).hexdigest()[:10]
        clip = tts_dir / f"seg_{s.id:03d}_{h}.wav"
        if not clip.exists():  # cache: re-running after edits only regenerates changed lines
            raw = tts_dir / f"seg_{s.id:03d}_{h}.raw.wav"
            prev = segs[i - 1].en if i > 0 else ""
            nxt = segs[i + 1].en if i + 1 < len(segs) else ""
            engine.synth(s.en, raw, prev=prev, nxt=nxt)
            trim_silence(raw, clip)
            raw.unlink()
        clips.append(clip)
        naturals.append(media.duration(clip))
    return clips, naturals


def cmd_synth(a):
    from . import timeline
    from .translate import count_syllables, shorten_lines
    wd = _workdir(a.work)
    script = Script.load(wd / "script.json")
    engine, tag = _tts(a)
    tts_dir = wd / "tts"
    tts_dir.mkdir(exist_ok=True)

    clips, naturals = _synth_all(script, engine, tag, tts_dir)
    fits = timeline.plan_fit(script, naturals)
    bad = {f.id: f for f in fits if f.status in ("over_accept", "too_long")}
    if bad and a.auto_shorten:
        by_id = {s.id: s for s in script.segments}
        targets = {i: max(2, int(count_syllables(by_id[i].en) * f.slot * timeline.ACCEPT_TEMPO / f.natural))
                   for i, f in bad.items()}
        print(f"shortening {len(targets)} line(s) that don't fit: {sorted(targets)}")
        shorten_lines(script, targets)
        script.save(wd / "script.json")
        clips, naturals = _synth_all(script, engine, tag, tts_dir)
        fits = timeline.plan_fit(script, naturals)

    timeline.assemble(script, clips, fits, wd / "voice_en.wav")
    (wd / "fit_report.json").write_text(json.dumps([asdict(f) for f in fits], indent=2))
    for f, s in zip(fits, script.segments):
        mark = {"ok": " ", "stretched": "~", "over_accept": "!", "too_long": "X"}[f.status]
        print(f" {mark} #{f.id:<3} {f.natural:5.2f}s in {f.slot:5.2f}s  x{f.tempo:.2f}  {s.en}")
    worst = [f for f in fits if f.status in ("over_accept", "too_long")]
    print(f"\n-> {wd/'voice_en.wav'}")
    if worst:
        print(f"{len(worst)} line(s) are rushed (!) or cut (X). Shorten their `en` in script.json "
              "(or use --auto-shorten) and re-run synth; unchanged lines are cached.")


def cmd_perform(a):
    """Voice conversion route: a recorded English performance, timed to the reel, converted to her voice."""
    from . import voice
    wd = _workdir(a.work)
    vid = a.voice_id or voice.load_voice("elevenlabs")
    if not vid:
        raise SystemExit("needs an ElevenLabs voice id (create-voice --backend elevenlabs)")
    converted = voice.convert_performance(Path(a.guide), wd / "performance_converted.wav", vid)
    total = media.duration(wd / "audio.wav")
    media.ffmpeg("-i", str(converted), "-af", f"apad,atrim=0:{total:.3f}", "-ac", "1", "-ar", str(media.SR),
                 "-c:a", "pcm_s16le", str(wd / "voice_en.wav"))
    print(f"-> {wd/'voice_en.wav'} (now run `mix`)")


def cmd_mix(a):
    from .timeline import mix
    wd = _workdir(a.work)
    mix(wd / "voice_en.wav", wd / "bed.wav", wd / "vocals.wav", wd / "mix.wav", room=a.room, duck=not a.no_duck)
    media.mux(wd / "source.mp4", wd / "mix.wav", wd / "dubbed.mp4")
    print(f"-> {wd/'dubbed.mp4'} (English voice + original music, original video). Next: `lipsync`.")


def cmd_lipsync(a):
    from .lipsync import lipsync
    wd = _workdir(a.work)
    synced = lipsync(wd / "source.mp4", wd / "voice_en.wav", wd, wd / "lipsync_video.mp4",
                     model=a.model, per_shot=not a.whole)
    media.mux(synced, wd / "mix.wav", wd / "final.mp4")
    print(f"-> {wd/'final.mp4'}  Please label the reel as AI-dubbed when posting.")


def cmd_abtest(a):
    """Blind listening test: the same English lines in her voice from several engines, under random letters."""
    import random
    from . import voice
    from .timeline import trim_silence
    wd = _workdir(a.work)
    script = Script.load(wd / "script.json")
    lines = [s.en for s in script.segments if s.en.strip()][: a.lines]
    out_dir = wd / "abtest"
    out_dir.mkdir(exist_ok=True)
    letters = random.sample("ABCDEFGHJKLMNPQRSTUVWXYZ", len(a.engine))
    key = {}
    for letter, spec in zip(letters, a.engine):
        backend, _, rest = spec.partition(":")
        model, _, vid = rest.partition(":")
        vid = vid or voice.load_voice(backend)
        if not vid:
            raise SystemExit(f"no voice id for {spec}")
        engine = voice.SarvamTTS(vid) if backend == "sarvam" else voice.ElevenTTS(vid, model=model or "eleven_multilingual_v2")
        parts = []
        for k, text in enumerate(lines):
            raw = out_dir / f"_{letter}_{k}.raw.wav"
            engine.synth(text, raw)
            parts.append(trim_silence(raw, out_dir / f"_{letter}_{k}.wav"))
            raw.unlink()
        inputs = sum((["-i", str(p)] for p in parts), [])
        pads = "".join(f"[{i}:a]apad=pad_dur=0.6[p{i}];" for i in range(len(parts)))
        media.ffmpeg(*inputs, "-filter_complex", pads + "".join(f"[p{i}]" for i in range(len(parts)))
                     + f"concat=n={len(parts)}:v=0:a=1", str(out_dir / f"{letter}.wav"))
        for p in parts:
            p.unlink()
        key[letter] = spec
    (out_dir / "KEY_do_not_open_until_rated.json").write_text(json.dumps(key, indent=2))
    sheet = ["Rate each clip 1-5:", "  her  = sounds like her", "  indian = sounds like an Indian person speaking English",
             "  foreign = sounds American/British (1 = not at all)", "  natural = sounds like a real person", "",
             "clip | her | indian | foreign | natural"] + [f"{x} | | | |" for x in sorted(letters)]
    (out_dir / "rating_sheet.txt").write_text("\n".join(sheet) + "\n")
    print(f"-> {out_dir}: clips {', '.join(sorted(letters))}, rating_sheet.txt, and a sealed key.")


# ---------------------------------------------------------------- parser

def main(argv=None):
    p = argparse.ArgumentParser(prog="reeldub", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("fetch", help="download reels with yt-dlp (originals from her phone are better)")
    s.add_argument("urls", nargs="+")
    s.add_argument("--cookies", help="cookies.txt from a logged-in browser, if Instagram blocks anonymous access")
    s.add_argument("--out", default="reels")
    s.set_defaults(fn=cmd_fetch)

    s = sub.add_parser("prepare", help="separate music + transcribe Kannada -> transcript.json")
    s.add_argument("video")
    s.add_argument("--asr", choices=["sarvam", "whisper", "elevenlabs"], default="sarvam",
                   help="whisper = open-source vasista22/whisper-kannada-medium, runs offline")
    s.add_argument("--model", default="saaras:v4", help="Sarvam model (saaras:v4 default, saaras:v3 benchmarked)")
    s.add_argument("--mode", default="codemix", choices=["codemix", "transcribe", "verbatim"])
    s.add_argument("--no-literal", action="store_true", help="skip Sarvam's direct speech->English cross-check")
    s.add_argument("--no-separate", action="store_true", help="skip music separation (reel has no music)")
    s.add_argument("--sep-model", help="audio-separator model file (default: MDX-Net on CPU, BS-RoFormer on GPU)")
    s.set_defaults(fn=cmd_prepare)

    s = sub.add_parser("translate", help="Kannada -> her Indian English -> script.json")
    s.add_argument("work")
    s.add_argument("--backend", choices=["claude", "sarvam"], default="claude")
    s.add_argument("--model", help="Claude model id (default: $REELDUB_CLAUDE_MODEL or claude-opus-5-5)")
    s.add_argument("--persona", help="text file describing her (age, region, how she talks, catchphrases)")
    s.add_argument("--glossary", help="text file of names/dishes/terms and how to spell them")
    s.set_defaults(fn=cmd_translate)

    s = sub.add_parser("make-ref", help="cut a clean reference clip of her voice")
    s.add_argument("work", nargs="+")
    s.add_argument("--seconds", type=float, default=15.0, help="15 for Sarvam, 60-120 for ElevenLabs")
    s.add_argument("--out", default="voices/ref.wav")
    s.set_defaults(fn=cmd_make_ref)

    s = sub.add_parser("create-voice", help="create her cloned voice (with her consent)")
    s.add_argument("--backend", choices=["sarvam", "elevenlabs"], required=True)
    s.add_argument("--ref", nargs="+", required=True)
    s.add_argument("--name", default="amma")
    s.add_argument("--ref-language", default="kn-IN", help="language of the reference clip (kn-IN or en-IN)")
    s.set_defaults(fn=cmd_create_voice)

    s = sub.add_parser("synth", help="speak script.json in her voice, fitted to timing -> voice_en.wav")
    s.add_argument("work")
    s.add_argument("--tts", choices=["sarvam", "elevenlabs"], default="sarvam")
    s.add_argument("--voice-id")
    s.add_argument("--model", help="ElevenLabs model (default eleven_multilingual_v2; avoid eleven_v4 with a Kannada clone)")
    s.add_argument("--auto-shorten", action="store_true", help="ask Claude to shorten lines that don't fit, once")
    s.set_defaults(fn=cmd_synth)

    s = sub.add_parser("perform", help="voice-conversion route: recorded English performance -> her voice")
    s.add_argument("work")
    s.add_argument("--guide", required=True, help="WAV of someone reading the English in sync with the reel")
    s.add_argument("--voice-id")
    s.set_defaults(fn=cmd_perform)

    s = sub.add_parser("mix", help="English voice over the original music -> dubbed.mp4")
    s.add_argument("work")
    s.add_argument("--room", type=float, default=0.0, help="0-1, add a little room sound to a dry clone")
    s.add_argument("--no-duck", action="store_true")
    s.set_defaults(fn=cmd_mix)

    s = sub.add_parser("lipsync", help="match her mouth to the English -> final.mp4 (needs FAL_KEY)")
    s.add_argument("work")
    s.add_argument("--model", choices=["latentsync", "sync-pro"], default="latentsync")
    s.add_argument("--whole", action="store_true", help="send the whole reel instead of shot by shot")
    s.set_defaults(fn=cmd_lipsync)

    s = sub.add_parser("abtest", help="blind listening test of several voice engines on the same lines")
    s.add_argument("work")
    s.add_argument("--engine", action="append", required=True,
                   help="sarvam | elevenlabs:<model>[:<voice_id>], repeat for each condition")
    s.add_argument("--lines", type=int, default=8)
    s.set_defaults(fn=cmd_abtest)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
