# KA-To-EN

Dub Amma's Kannada Instagram reels into **natural Indian English, in her own cloned voice, with her lips
re-synced**, so it looks and sounds like her speaking English.

The research behind every choice here, with sources and a verified/unverified table, is in
[`reports/Kannada reels English voice dubbing.md`](reports/Kannada%20reels%20English%20voice%20dubbing.md)
(raw notes in `research_notes/`).

> **Consent first.** Only clone her voice with her explicit permission. Keep the cloned voice private,
> and label posted reels as AI-dubbed. ElevenLabs' Professional Voice Clone must be created by her on her own account.

## Option 0: try Instagram's own free translator first

Since 16 Jan 2026, Instagram's **"Translate voices with Meta AI"** supports Kannada. It mimics the creator's
voice, has an optional lip-sync toggle, and is free for public accounts.

Limits:
- Meta has not explicitly confirmed **Kannada → English**; check it in her app.
- It works on one-speaker reels only.
- You can only approve or discard the result. You **cannot edit the English**.

If it sounds like her and the English is right, you may not need anything below.

## Option 1: this pipeline (full control over every word)

```
reel.mp4
 ├─ separate   her voice ↔ music        (local CPU, audio-separator)
 ├─ prepare    Kannada speech → text    (Sarvam saaras, best measured Kannada ASR)   → transcript.json  ✋ review
 ├─ translate  Kannada → her English    (Claude, syllable-budgeted, Indian English)   → script.json      ✋ review
 ├─ synth      English in HER voice     (Sarvam en-IN clone or ElevenLabs Multilingual v2), fitted to timing
 ├─ mix        voice over original music, −14 LUFS                                    → dubbed.mp4
 └─ lipsync    mouth re-synced per shot (fal LatentSync, or Sync lipsync-2-pro)       → final.mp4
```

### Setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt          # needs ffmpeg with rubberband (most builds have it)
cp .env.example .env                     # add your keys
set -a; source .env; set +a
```

| Key | Used for | Needed? |
|---|---|---|
| `SARVAM_API_KEY` | Kannada ASR, Indian-English voice clone | yes |
| `ANTHROPIC_API_KEY` | translation | recommended (fallback: `--backend sarvam`, more literal) |
| `ELEVENLABS_API_KEY` | alternative voice, voice conversion | optional |
| `FAL_KEY` | lip-sync | for the final step |

### Run it on one reel

Put the **original MP4s from her phone** in `reels/`. Downloading also works (`python -m reeldub fetch <url> --cookies cookies.txt`),
but Instagram often blocks it and recompresses the audio.

```bash
# 1. Separate music, transcribe Kannada
python -m reeldub prepare reels/rasam.mp4
#    → work/rasam/transcript.json. Have a Kannada speaker fix any wrong words in "kn".

# 2. Translate into her English (fill in examples/persona.example.txt about her; it matters)
python -m reeldub translate work/rasam --persona my_persona.txt --glossary my_glossary.txt
#    → work/rasam/script.json + script_review.md. Read every line; lines marked ⚠ need checking.
#      Edit "en" in script.json. Leave a line's "en" empty to keep that moment silent.

# 3. One-time: make her voice (needs her consent)
python -m reeldub make-ref work/rasam --seconds 15 --out voices/ref15.wav     # LISTEN: only her, no music
python -m reeldub create-voice --backend sarvam --ref voices/ref15.wav --name amma

# 4. Speak the English in her voice, fitted to the original timing
python -m reeldub synth work/rasam --tts sarvam
#    Table shows each line: ' ' fits, '~' sped up ≤1.2x, '!' rushed, 'X' cut. Shorten '!'/'X' lines in
#    script.json (or add --auto-shorten) and re-run; unchanged lines are cached, not re-billed.

# 5. Put it over the original music, then lip-sync
python -m reeldub mix work/rasam                 # → work/rasam/dubbed.mp4  (watch this before paying for lip-sync)
python -m reeldub lipsync work/rasam             # → work/rasam/final.mp4
python -m reeldub lipsync work/rasam --model sync-pro   # for shots where she turns, covers her mouth, etc.
```

## Making it sound like *her*, with an Indian accent

This is the part that matters most, and the part nobody has benchmarked. The research found:

- **Avoid ElevenLabs Eleven v4 with a Kannada clone.** Its docs say it deliberately drops the reference accent
  when the output language differs. She would come out sounding non-Indian.
- **ElevenLabs `eleven_multilingual_v2`** (this tool's ElevenLabs default) is documented to keep the accent across languages.
- **Sarvam's clone** outputs `en-IN` (Indian English). Its docs say "a hint" of the reference accent carries over,
  and that cross-lingual cloning works best with references closer to 15 s than 10 s.
- **Best single trick: get 1–2 minutes of her speaking English** in her normal accent and clone from that
  (for Sarvam also pass `--ref-language en-IN`). With a same-language reference, ElevenLabs says even v4 keeps the accent.
- **Most natural option, voice conversion.** Someone records the English lines in sync with the reel, in a natural
  Indian accent (or Amma herself, if she's willing). ElevenLabs then swaps in her voice, keeping that performance's
  timing, emotion and accent:
  `python -m reeldub perform work/rasam --guide guide_take.wav`

**Choose by listening, not by vendor claims.** Run a blind test on the same lines:

```bash
python -m reeldub abtest work/rasam --engine sarvam \
    --engine elevenlabs:eleven_multilingual_v2 --engine elevenlabs:eleven_v3
```

This writes clips `A.wav`, `B.wav`… with a rating sheet and a sealed key. Ask family members, who know her
voice, plus a couple of Indian listeners who don't. Rate each clip on: sounds like her, sounds Indian,
sounds American/British, and sounds natural. Pick the best on "her" + "Indian".

## What it costs (per ~60 s reel, Oct 2026 prices)

| Step | Cost |
|---|---|
| ASR (Sarvam, ₹30/hour) | < ₹1 |
| Translation (Claude) | a few cents |
| Voice (Sarvam / ElevenLabs) | per character, under your plan (not priced in the research) |
| Lip-sync | ~$0.30 (fal LatentSync) to ~$5 (Sync lipsync-2-pro) |

## What runs where

Everything except the APIs runs on a plain CPU machine. Measured on this repo's 4-core box, for 26 s of audio:

| Separator model | Time |
|---|---|
| MDX-Net Voc_FT | 33 s (default on CPU) |
| Demucs htdemucs_ft | 150 s |
| BS-RoFormer | 669 s (best quality; default when a CUDA GPU is present) |

Choose one with `--sep-model`.

Lip-sync models need a GPU (LatentSync 1.6 needs ~18 GB VRAM), which is why the hosted API is used.

## Status and honest limits

- **Tests.** The local stages (separation, pause detection, timing, mixing, per-shot lip-sync splitting) and all
  stage hand-offs are tested offline: `pytest -q`, 13 tests. Measurements were made on Kannada FLEURS speech mixed
  with synthetic music.
- **APIs.** API calls follow each vendor's current official SDK/docs (checked 8 Oct 2026). They have **not yet been
  run against live keys**, so expect small fixes on the first real run.
- **Unconfirmed vendor details.**
  - `saaras:v4` has no published Kannada benchmark (v3 scored 8.8% WER).
  - Whether v4 honours `mode` is unconfirmed; use `--model saaras:v3` if output looks off.
- **Human review is required.** No source has measured translation quality for current LLMs on colloquial Kannada,
  so a bilingual family member should read every `kn` and `en` line. The translator is told never to invent content
  and to flag doubts (⚠), but a human is the safeguard.
- **Burned-in captions.** Kannada captions burned into the original video are not removed.
