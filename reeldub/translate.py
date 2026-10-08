"""Kannada lines -> English lines she would naturally say, sized to fit each line's time slot.

Why an LLM rather than plain MT: dubbing needs (a) a warm Indian-English register, (b) her own English
words kept as she said them, (c) a length that fits the slot. Benchmarks score none of these.
Length is budgeted in syllables (English ~0.225 s/syllable, VideoLingo's estimate) and enforced by a
check-and-shorten loop, because LLM translations run long (HOMURA, arXiv 2601.10187).
Budgets are soft: viewers preferred meaning over forced length (arXiv 2110.03847).
"""

from __future__ import annotations

import json
import os
import re

from .segments import Script, slot_end

SEC_PER_SYLLABLE = 0.225
DEFAULT_MODEL = os.environ.get("REELDUB_CLAUDE_MODEL", "claude-opus-5-5")

SYSTEM = """You translate the spoken Kannada of one real woman's Instagram reels into the English she herself would say \
if she were speaking English on camera. Her English voice will be generated from these lines and lip-synced to her face, \
so every line must sound like *her* talking, not like a translator or a subtitle.

How she should sound:
- Natural, warm, spoken Indian English, the way an educated Kannadiga woman of her age actually talks to her viewers. \
Short spoken sentences. Contractions are fine.
- NOT American or British slang ("gonna", "y'all", "awesome", "mate", "folks"). NOT stiff textbook English. \
NOT a caricature: don't sprinkle "only", "itself", "na", "yaar", "kindly" unless that is genuinely how the line would be said.
- Keep every word she already said in English exactly as she said it (the transcript shows these in Latin script).
- Keep Kannada words that Indian English speakers keep: dish and ingredient names (saaru, palya, huli, ragi mudde, \
chitranna...), kinship terms and terms of address (amma, akka, ajji...), festivals, places, people's names. \
Write them in simple Roman spelling. Never translate a name.
- Map Kannada discourse fillers (nodi, alva, aytha, swalpa, ondu...) to a light natural equivalent ("see", "right?", \
"okay?", "a little") or drop them; don't over-use them.

Faithfulness (this is serious, never invent):
- Translate what she said. Do not add facts, jokes, quantities, or claims that are not in the Kannada.
- If a line looks like a speech-recognition error, is ambiguous, or you are unsure of a word, give your best reading \
AND set "uncertain": true with a short "note" saying what to check. A human reviews flagged lines.
- An optional machine "literal" English is provided for some lines; use it only as a hint, it can be wrong.

Timing:
- Keep exactly one English line per input line (same ids) so it stays lip-synced to that moment.
- Each line has a syllable budget = how much English fits the time she spoke. Aim for the budget; going up to ~10% over is \
okay, going far over is not. If you must cut, drop fillers and repetition first, never meaning.
- If a line is far under budget, that's fine; do not pad with invented words.

Reply with JSON only: {"lines": [{"id": <int>, "en": "<english>", "uncertain": <bool>, "note": "<string>"}]}"""


def count_syllables(text: str) -> int:
    """Rough English syllable count (vowel groups, with common silent-e fixes). Good enough for budgets."""
    total = 0
    for word in re.findall(r"[A-Za-z']+|\d+", text.lower()):
        if word.isdigit():
            total += 2 * len(word)  # numbers are long when spoken
            continue
        groups = re.findall(r"[aeiouy]+", word)
        n = len(groups)
        if word.endswith("e") and n > 1 and not word.endswith(("le", "ee", "ye")):
            n -= 1
        if word.endswith("ed") and n > 1 and not word.endswith(("ted", "ded")):
            n -= 1
        total += max(1, n)
    return total


def syllable_budget(seconds: float) -> int:
    return max(2, int(seconds / SEC_PER_SYLLABLE))


def budgets(script: Script) -> list[int]:
    segs = script.segments
    return [syllable_budget(slot_end(segs, i, script.total) - s.start) for i, s in enumerate(segs)]


def _client():
    import anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set")
    return anthropic.Anthropic()


def _ask(client, model: str, system: str, user: str) -> dict:
    msg = client.messages.create(model=model, max_tokens=8000, system=system,
                                 messages=[{"role": "user", "content": user}])
    text = "".join(b.text for b in msg.content if b.type == "text")
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise RuntimeError(f"translator did not return JSON:\n{text[:500]}")
    return json.loads(match.group(0))


def _apply(script: Script, lines: list[dict]) -> None:
    by_id = {s.id: s for s in script.segments}
    for ln in lines:
        seg = by_id.get(int(ln["id"]))
        if seg is not None:
            seg.en = ln.get("en", "").strip()
            seg.uncertain = bool(ln.get("uncertain", False))
            seg.note = ln.get("note", "") or ""


def translate_claude(script: Script, persona: str = "", glossary: str = "", model: str = DEFAULT_MODEL,
                     tolerance: float = 1.15, rounds: int = 2) -> Script:
    client = _client()
    b = budgets(script)
    payload = [{"id": s.id, "seconds": round(slot_end(script.segments, i, script.total) - s.start, 2),
                "syllable_budget": b[i], "kannada": s.kn, **({"literal": s.en_literal} if s.en_literal else {})}
               for i, s in enumerate(script.segments)]
    user = ""
    if persona:
        user += f"About her (from her family):\n{persona.strip()}\n\n"
    if glossary:
        user += f"Fixed spellings / terms to keep:\n{glossary.strip()}\n\n"
    user += "The whole reel, in order:\n" + json.dumps(payload, ensure_ascii=False, indent=1)
    _apply(script, _ask(client, model, SYSTEM, user)["lines"])

    # Check-and-shorten loop for lines that clearly won't fit.
    for _ in range(rounds):
        over = [(s, b[i]) for i, s in enumerate(script.segments) if count_syllables(s.en) > b[i] * tolerance]
        if not over:
            break
        req = [{"id": s.id, "kannada": s.kn, "current_english": s.en, "syllables_now": count_syllables(s.en),
                "syllable_budget": bud} for s, bud in over]
        user = ("These lines are too long to fit the time she spoke. Rewrite each to fit its syllable budget, keeping "
                "her meaning, her voice and her own English words; drop fillers/repetition first. Same JSON format.\n"
                + json.dumps(req, ensure_ascii=False, indent=1))
        _apply(script, _ask(client, model, SYSTEM, user)["lines"])
    script.meta["translator"] = {"backend": "claude", "model": model}
    return script


def shorten_lines(script: Script, targets: dict[int, int], model: str = DEFAULT_MODEL) -> Script:
    """Ask for shorter versions of specific lines (id -> syllable target). Used after TTS reveals overruns."""
    client = _client()
    by_id = {s.id: s for s in script.segments}
    req = [{"id": i, "kannada": by_id[i].kn, "current_english": by_id[i].en, "syllables_now": count_syllables(by_id[i].en),
            "syllable_budget": t} for i, t in targets.items()]
    user = ("When spoken, these lines ran past the time she spoke. Rewrite each to fit its syllable budget, keeping her "
            "meaning and voice; drop fillers/repetition first. Same JSON format.\n" + json.dumps(req, ensure_ascii=False, indent=1))
    _apply(script, _ask(client, model, SYSTEM, user)["lines"])
    return script


def translate_sarvam(script: Script) -> Script:
    """Fallback with no LLM key: Sarvam mayura, colloquial mode, female speaker. Expect more literal output."""
    from .asr import _sarvam_client
    client = _sarvam_client()
    for s in script.segments:
        r = client.text.translate(input=s.kn, source_language_code="kn-IN", target_language_code="en-IN",
                                  model="mayura:v1", mode="modern-colloquial", speaker_gender="Female")
        s.en = r.translated_text.strip()
    script.meta["translator"] = {"backend": "sarvam", "model": "mayura:v1"}
    return script
