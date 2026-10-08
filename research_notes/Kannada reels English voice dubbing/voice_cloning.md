# Cross-lingual voice cloning: Kannada-speaking woman -> English in her own voice with an Indian-English accent (for Instagram reel dubbing)

Research date: 2026-10-08. Model and product facts change quickly; dates are flagged where known. Things I could not verify are listed under Gaps and must not be stated as fact.

**Core framing for the report writer.** In the research literature and in vendor docs, "accent leakage" (the reference speaker's native accent carrying into the target language) is treated as a defect. **For this task it is the desired behaviour.** A Kannada-accented, Indian-English output is exactly what "natural Indian accent" means here. Models and settings that *suppress* leakage, such as Eleven v4, MiniMax Speech 2.6 "Fluent LoRA" and Chatterbox `cfg_weight=0`, tend to push the output toward a generic native-English (likely US-sounding) accent. Models that *retain* reference accent, such as ElevenLabs Multilingual v2, Cartesia clones, F5-TTS-family and Chatterbox at default CFG, are better aligned with the goal.

---

## 1. Commercial services: timbre, accent carry-over, Kannada support, reference audio, consent

### Takeaway
ElevenLabs is the most documented option, but **model choice is critical**. Multilingual v2 is documented to keep the speaker's accent across languages, which is what we want. The new Eleven v4 *deliberately* drops the reference accent when the output language differs, which works against an Indian accent. Its Professional Voice Clone can only be made by the voice owner herself. Sarvam (an Indian vendor) now documents a cross-lingual Voice Cloning API with `en-IN` output and a 10-15 s reference, which makes it the most natural "Indian-English by design" commercial candidate, but I found no independent quality reports. PlayHT is dead.

### Cited Findings
**ElevenLabs: models and accent behaviour**
- **Eleven v4** (`eleven_v4`, plus `eleven_v4_turbo`):
  - When the output language differs from the reference voice's language, v4 "generates fluent, natural-sounding speech in the target language" instead of carrying over the reference accent. ElevenLabs gives the example of a Korean-speaker clone producing natural English rather than Korean-accented English, and calls this a deliberate change, possibly a future toggle with no timeline. When the languages match, the original accent is preserved. — [ElevenLabs Eleven v4 docs](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4)
  - Lists ~90 languages including Kannada, Hindi and English. Supports IVC (sample generally 1-2 minutes) and PVC, with PVC rollout described as "within the next few days" at the time of writing. — [Eleven v4 docs](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4)
  - No Style or Speed sliders (only Stability and Similarity), no SSML. Audio tags (whisper, laugh) are supported but imperfect, and tags "can be tried to guide an accent" with variable results. — [Eleven v4 docs](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4)
- **Language support and limits per model**, from the models page:
  - Kannada is listed only for Eleven v4, v4 Turbo, v3 and v3 Conversational. It is NOT listed for Multilingual v2, Flash v2.5, Turbo v2.5 or Multilingual STS v2.
  - Hindi and English are listed for all of them.
  - Character limits: v4 10,000; v3 5,000; Multilingual v2 10,000; Flash v2.5 40,000.
  - Only Multilingual v2's description says it "keeps the speaker's unique characteristics and accent across languages."
  - Source: [ElevenLabs models overview](https://elevenlabs.io/docs/overview/models)
- **Older help-centre guidance:** "The language is determined by the text, the accent and pronunciation is determined by the voice itself." "Any voice can speak any of the supported languages." It recommends cloning in the target language with the right accent for best results. — [ElevenLabs help: same cloned voice across languages](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/can-i-use-the-same-cloned-designed-voice-across-languages)
- **Changing a clone's accent:** you cannot change a clone's accent or tone after it is created; you must change the samples. PVC is suggested if IVC doesn't capture the voice or accent well. — [ElevenLabs voice-cloning page, via search summary](https://elevenlabs.io/voice-cloning)
- **Cloning from an unsupported language:** you can clone a voice from audio in a language the model does not support, and the clone may capture tone. This is relevant because the clone would be built from Kannada reel audio. — [ElevenLabs voice-cloning](https://elevenlabs.io/voice-cloning)
- **Dubbing Studio:** advertises dubbing into "90+ languages and accents," with output in a clone of the original speaker. — [ElevenLabs Dubbing](https://elevenlabs.io/dubbing-studio). I did not verify whether Kannada is supported as a *source* language for automatic dubbing (see Gaps).

**ElevenLabs Voice Changer (speech-to-speech)**
- It preserves "whispers, laughs, cries, accents, and subtle emotional cues" of the input performance.
- Recommended model is `eleven_multilingual_sts_v2`, covering 29 languages. Any cloned voice in the library can be the target.
- Limit is 5 min per segment. Billed at 1,000 characters per minute of audio. Has a background-noise removal option.
- Source: [ElevenLabs Voice Changer docs](https://elevenlabs.io/docs/capabilities/voice-changer)

**ElevenLabs consent rules**
- PVC: "You can only create a Professional Voice Clone of your own voice. Even with their consent, you cannot clone someone else's voice." The sanctioned route is for the voice owner to create and verify the PVC on her own account and share it via a private link. — [ElevenLabs help: PVC of someone else's voice](https://help.elevenlabs.io/hc/en-us/articles/36842751624209)
- The PVC voice CAPTCHA has the user read a prompt within a time limit, and it is matched to the training samples. — [search summary citing ElevenLabs product text via proofnews](https://proofnews.org/ai-tools-make-it-easy-to-clone-someones-voice-without-consent)
- A Proof News investigation found the cheaper Instant clone tier easy to use without consent checks; it tested the $5 starter tier, not PVC. — [Proof News](https://proofnews.org/ai-tools-make-it-easy-to-clone-someones-voice-without-consent)

**Sarvam (Bulbul v2/v3 + Voice Cloning API)**
- **Bulbul v3 TTS:**
  - 37 preset voices (v2 had 7), 11 language codes including `kn-IN` and `en-IN`, with code-mixed text supported.
  - Pace 0.5-2.0 (v2: 0.3-3.0). Temperature control. Pronunciation dictionary (v3).
  - 2,500 characters per request for v3, 1,500 for v2.
  - No cloning parameter on the standard TTS endpoint.
  - Source: [Sarvam TTS API reference](https://docs.sarvam.ai/api-reference-docs/text-to-speech/convert)
- **Voice Cloning API:**
  - Endpoints `POST /voices/create` (saved voice) and `POST /voices/clone` (one-shot), plus streaming and WebSocket.
  - Recommended reference is 10-15 s of clean audio; the inline ref is capped at 15 s / 10 MB.
  - "The reference clip's language doesn't have to match the output language."
  - Built-in QC transcribes and scores short generations and retries failures.
  - Requires the right to use the voice ("Only clone a voice you have the right to use").
  - Billed per character; rate not on the page.
  - The page does not say whether the clone keeps the original accent across languages.
  - Source: [Sarvam Voice Cloning docs](https://docs.sarvam.ai/api/api-guides-tutorials/voice-cloning/overview)
- **Conflicts and inconsistencies:**
  - An invideo blog (updated Aug 2026) says Bulbul v3 has no self-serve cloning, which conflicts with Sarvam's own docs. — [invideo](https://invideo.io/blog/sarvam-bulbul-indian-tts/)
  - Sarvam's marketing page cites a 30-60 s sample, versus 10-15 s in the API docs. — [Sarvam TTS page](https://www.sarvam.ai/text-to-speech)
  - Sarvam's Content Studio reportedly dubs videos into 11 Indian languages. — [AlphaSignal](https://alphasignal.ai/news/sarvam-opens-content-studio-to-dub-videos-into-11-indian-languages)

**Cartesia (Sonic-3)**
- Cloning "preserves your unique speaking style, accent, and emotion." There is no documented accent-switch control. — [Cartesia product page via search](https://www.cartesia.ai/product/python-text-to-speech-api-tts)
- Cartesia markets India and Hinglish voices. — [Cartesia India](https://www.cartesia.ai/india)
- PVC voices need a dated model ID such as `sonic-3-2026-01-12`. — [Cartesia release notes via releasebot](https://releasebot.io/updates/cartesia)
- Practitioner report: a cloned voice mispronounced Hindi until the language was set explicitly to `hi`. Support advised using sonic-3 or multilingual, not sonic-english. — [Vapi support thread](https://support.vapi.ai/t/33169486/cartesia-voice-language-setting-not-working)

**MiniMax Speech (Hailuo)**
- Speech 2.6 "Fluent LoRA": "even with non-native recordings that may have an accent or be disfluent... replicate the voice's timbre while generating fluent, natural speech" across 40+ languages. This likely *removes* Indian accent, which is the opposite of our goal. — [MiniMax Speech 2.6 announcement](https://www.minimax.io/news/minimax-speech-26)
- Speech 2.5 reportedly kept source accents. One guide lists 2.6 as legacy and 2.8 as current flagship (Aug 2026). — [invideo MiniMax guide](https://invideo.io/blog/minimax-ai-voice-models/)
- Reported cloning audio requirements conflict: 10 s per [Together AI](https://www.together.ai/blog/minimax-speech-2-6) vs ~10 min per [growwstacks review](https://growwstacks.com/blog/minimax-speech-2-6-review).

**Smallest.ai (Lightning v3.1)**
- Docs list Kannada and English among accepted codes, but only 12 of 20 languages have trained voices (the others fall back to English/Hindi voices).
- Indian English voices exist, e.g. meher and aviraj.
- Instant cloning from a few seconds (AWS listing: 5-15 s), plus a professional tier.
- Sources: [Smallest.ai Lightning docs](https://docs.smallest.ai/models/documentation/text-to-speech-lightning/overview), [voices/languages](https://docs.smallest.ai/models/documentation/text-to-speech-lightning/voices-languages.md), [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-rrjz2t3xvpzv4)

**Azure Personal Voice / Custom Neural Voice**
- Personal voice (preview) generates speech in 90+ languages from a one-minute sample. Regions: West Europe, East US, South East Asia. — [Microsoft Learn: personal voice](https://learn.microsoft.com/azure/ai-services/speech-service/personal-voice-overview)
- CNV has a cross-lingual feature. I could not confirm whether `en-IN` is a cross-lingual target. — [Azure language support](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/ai-services/speech-service/language-support.md)

**PlayHT**
- Meta acqui-hired the team (July 2025). The API stopped July 26, 2025, and the service fully shut down Dec 31, 2025 with clones deleted. **Not an option.** — [texttolab](https://texttolab.com/blog/play-ht-shutdown-alternatives), [theplanettools](https://theplanettools.ai/tools/playht). These are secondary and competitor-adjacent sources; dates vary slightly.

### Inferences
- **Best-fit ElevenLabs path:** clone from her Kannada speech and generate English text with **Multilingual v2**. The docs say it retains accent across languages, and the help centre says the accent comes from the voice. Expect Kannada-flavoured English. Avoid v4 for this goal (it is documented to neutralise accent cross-lingually). v3 behaviour is undocumented on this point, so A/B test v2 vs v3.
- ElevenLabs PVC requires *the mother herself* to register and pass the voice CAPTCHA (reading English or Kannada prompts live). IVC is the practical route if the user creates it, but consent must still be real.
- **Sarvam** is the most "Indian-native" API: an `en-IN` output code and cross-lingual cloning from 10-15 s. Accent retention is unverified but plausible, since its training is Indian-centric. It is worth an A/B test alongside ElevenLabs Multilingual v2.
- **Timing:** none of the commercial TTS APIs found offers exact per-segment duration targeting. The available controls are pace (Sarvam 0.5-2.0) and speed on older ElevenLabs models. Dub-timing will need post-hoc time-stretching or iteration on the translation length.

### Gaps
- ElevenLabs:
  - No official statement on whether **Eleven v3** carries the reference accent cross-lingually.
  - Could not open the "How do I select the language and accent" help article (HTTP 403).
  - Exact IVC sample guidance for Multilingual v2 not verified beyond v4's "1-2 minutes".
  - Whether ElevenLabs Dubbing accepts **Kannada as source** language is unverified.
  - Current ElevenLabs pricing not retrieved.
- Sarvam: which Bulbul version powers its cloning is not stated, and pricing is not retrieved.
- Not researched for lack of budget: Resemble AI commercial cloning, and Google Cloud Chirp 3 instant custom voice (availability, en-IN, consent workflow).
- No independent listening tests comparing these APIs on Indian-English accent fidelity were found.

---

## 2. Open-source TTS models: cross-lingual cloning (Kannada reference -> English), licence, duration control

### Takeaway
No open model officially lists Kannada *and* English together with zero-shot cloning, except via workarounds:
- **IndicF5** covers Kannada but not English.
- **Indic Parler-TTS** does Indian English but has no reference-audio cloning.
- **Chatterbox Multilingual** (MIT) includes Hindi and English, but not Kannada.

Flow-matching and AR cloners (F5-TTS, Chatterbox, CosyVoice, Qwen3-TTS, IndexTTS) can take a reference in any language and are *documented to leak reference accent*, which here is useful. IndexTTS2's advertised precise duration control is **not enabled** in released code; IndexTTS-2.5 offers a 0.5-2.0x `duration_factor`. Licence traps: XTTS-v2 (CPML, non-commercial), F5-TTS weights (CC-BY-NC), Fish/OpenAudio S1-mini (CC-BY-NC-SA).

### Cited Findings
**AI4Bharat models**
- **IndicF5:**
  - Trained on 1,417 h across 11 Indian languages including Kannada.
  - Requires a reference clip plus its transcript.
  - Does not list English.
  - Terms: "only clone voices for which you have explicit permission."
  - Source: [AI4Bharat IndicF5 GitHub](https://github.com/AI4Bharat/IndicF5)
- **Indic Parler-TTS:**
  - "Officially supports Indian English accents through its English voices." Kannada is officially supported.
  - 21 named English speakers (recommended: Thoma, Mary) and Kannada speakers (Suresh, Anu, Chetan, Vidya).
  - Voice is chosen by name or text description; **no reference-audio cloning**.
  - Apache-2.0, 0.9B params.
  - Source: [HF model card](https://huggingface.co/ai4bharat/indic-parler-tts)
- AI4Bharat also hosts a **Seed-VC demo**, suggesting interest in the TTS->VC pipeline for Indic voices. — [seed-vc-conversion.ai4bharat.org](https://seed-vc-conversion.ai4bharat.org/)
- **Community example:** a Kannada IndicF5 fine-tune for bedtime stories uses a parent's recorded voice as reference, with 800 clips (~6 h). — [sush0401/IndicF5-Kannada-Bedtime-v2](https://huggingface.co/sush0401/IndicF5-Kannada-Bedtime-v2)

**F5-TTS**
- Licence: code is MIT, but pretrained weights are **CC-BY-NC** because they were trained on Emilia. — [F5-TTS README mirror](https://huggingface.co/spaces/mrfakename/E2-F5-TTS/blame/60bebe5fe89ca4ecf9bb1d5ea6fdb49a827a3130/README_REPO.md)
- Cross-lingual F5-TTS papers (2025-2026) address the need for prompt transcripts in unseen prompt languages via forced alignment, and report cloning from out-of-distribution prompt languages into English. — [arXiv 2509.14579](https://arxiv.org/html/2509.14579v1), [arXiv 2609.15184](https://arxiv.org/pdf/2609.15184)
- **Accent Analogy Guidance** (Cho & Lee, arXiv 24 Sep 2026, submitted to ICASSP 2027):
  - "the accent of the reference leaks into the target speech" in cross-lingual zero-shot TTS.
  - CFG reweighting trades speaker similarity against accent nativeness along a single curve.
  - Tested OmniVoice, MaskGCT, CosyVoice 2 and F5-TTS.
  - Source: [arXiv 2609.29123](https://arxiv.org/abs/2609.29123)

**Chatterbox (Resemble AI)**
- Variants: English 500M, Multilingual V3 (23 languages incl. Hindi and English; no Kannada), single-language Hindi pack, Turbo.
- MIT licence. All output has an imperceptible **PerTh watermark**. Includes a voice-conversion script.
- Accent leakage: "Ensure that the reference clip matches the specified language tag. Otherwise, language transfer outputs may inherit the accent of the reference clip's language. To mitigate this, set cfg_weight to 0."
- Source: [HF ResembleAI/chatterbox](https://huggingface.co/ResembleAI/chatterbox)
- Guidance: lower `cfg_weight` (~0.3) for fast speakers; raise exaggeration (≥0.7) for expressive output. — [Chatterbox multilingual docs mirror](https://github.com/travisvn/chatterbox-multilingual)

**IndexTTS2 / IndexTTS-2.5 (bilibili)**
- **IndexTTS2** (released 2025-09-08) is billed as "The first autoregressive TTS model with precise synthesis duration control", but "This functionality is not yet enabled in this release." It offers emotion control by reference audio, an 8-dim vector, or text. — [index-tts GitHub](https://github.com/index-tts/index-tts)
- **IndexTTS-2.5** (2026-08-10):
  - Chinese/English/Japanese/Spanish/Arabic, with "cross-lingual voice transfer and emotion control disentangled from timbre."
  - `duration_factor` 0.5-2.0. English CMU-phoneme pronunciation control.
  - NVIDIA GPU, ~6 GB VRAM.
  - bilibili Model Use License; commercial use requires contacting bilibili.
  - Sources: [HF IndexTeam/IndexTTS-2.5](https://huggingface.co/IndexTeam/IndexTTS-2.5), [GitHub](https://github.com/index-tts/index-tts)
  - RTF on an RTX 4090 is 0.21 (vs 0.33 for IndexTTS2 fp16). — [GitHub](https://github.com/index-tts/index-tts)

**CosyVoice 3 (Fun-CosyVoice3-0.5B-2512)**
- 9 languages (zh, en, ja, ko, de, es, fr, it, ru) plus 18+ Chinese dialects. Supports "cross-lingual zero-shot voice cloning." — [CosyVoice GitHub](https://github.com/qwenaudio/cosyvoice)
- The licence was claimed as Apache-2.0 only by a third party; I did not verify it. "3.5" is API-only. — [soniqo guide](https://soniqo.audio/es/guides/cosyvoice)

**Qwen3-TTS (Jan 2026)**
- Apache-2.0. 10 languages (zh, en, ja, ko, de, fr, ru, pt, es, it). 3-s cloning, cross-lingual cloning. 1.7B and 0.6B Base, VoiceDesign and CustomVoice variants.
- Source: [arXiv 2601.15621](https://arxiv.org/html/2601.15621), [Gigazine](https://gigazine.net/gsc_news/en/20260123-qwen3-tts-family-opensource)

**XTTS-v2 (Coqui)**
- Weights are under the Coqui Public Model License (non-commercial: no direct or indirect payment from the model or its outputs). Coqui shut down in Dec 2023 / Jan 2024, so **no commercial licence can be bought**.
- The idiap fork (`coqui-tts` on PyPI) maintains the code (MPL-2.0) but doesn't change the weight licence.
- Monetised Instagram reels would likely fall outside CPML.
- Source: [promptquorum XTTS review](https://www.promptquorum.com/power-local-llm/xtts-v2-review), [CPML text mirror](https://huggingface.co/Borcherding/XTTS-v2_CarliG/blob/418d3f6406d97c9c4d1ff2767be43db54e380643/LICENSE.txt). These are secondary sources.

**Fish Audio S1 / OpenAudio S1-mini**
- 13 languages, no Hindi or Kannada. Open S1-mini weights are CC-BY-NC-SA-4.0; full S1 is proprietary/hosted.
- Sources: [Fish Audio S1 blog](https://fish.audio/blog/introducing-s1/), [HF mirror](https://huggingface.co/cocktailpeanut/oa)

**OpenVoice V2**
- MIT ("Free for commercial use"). Native languages en, es, fr, zh, ja, ko. Claims zero-shot cross-lingual cloning where neither reference nor output language need be in training data, plus "granular control over... emotion and accent."
- Source: [OpenVoice GitHub](https://github.com/myshell-ai/OpenVoice)

**Leaderboards**
- The official TTS Arena V2 (HF) uses Elo from blind pairwise votes, but I could not retrieve current standings. — [TTS Arena V2 about](https://tts-agi-tts-arena-v2.hf.space/about)
- A third-party "TTS Arena" on tts.ai ranks Kokoro > CosyVoice 2 > Chatterbox, on very few votes, and Kokoro is "not a voice-cloning model". — [tts.ai arena](https://tts.ai/tools/tts-arena). This is not reliable.

### Inferences
- **Candidate open pipelines for Kannada reference -> Indian-accented English:**
  - (a) **Chatterbox Multilingual V3** with `language_id="en"`, her Kannada clip as reference and **default `cfg_weight` (0.5), not 0**. The documented leakage should give Indian-flavoured English. MIT licence plus watermark.
  - (b) **F5-TTS** base with a Kannada reference plus its transcript. It is strongly accent-leaky per AAG. NC licence; fine for personal use, not for monetised reels.
  - (c) **Qwen3-TTS Base** (Apache-2.0).
  - (d) **CosyVoice 3**.
  - (e) **IndexTTS-2.5**, the only one with a documented duration factor. Its licence is restrictive for commercial use.
- Kannada isn't in any of these models' training lists, so leakage may be *partial or odd*: Kannada phonetics on English words, or dropped words. Test with 5-10 representative lines.
- For dubbing timing, the realistic open option is generate -> measure -> regenerate with `duration_factor` or speed, or time-stretch (e.g. ffmpeg atempo/rubberband) within ±10-15%. IndexTTS2's token-precise mode isn't usable.

### Gaps
- Not verified: VibeVoice (Microsoft), Higgs Audio, Spark-TTS, MaskGCT (only cited in the AAG paper), Zonos, Orpheus, Dia, GPT-SoVITS details. Their language lists, licences and cross-lingual quality were not retrieved. Kokoro is known to lack cloning (tts.ai statement) but its licence and voices weren't verified.
- No published evaluation specifically of Kannada (or any Dravidian) reference -> English output for any model.
- CosyVoice 3 licence not verified from the official LICENSE.
- The F5-TTS claim that fine-tunes inherit NC (GitHub discussion #997) is unverified.

---

## 3. Voice-conversion (speech-to-speech) approach: English source speech -> her timbre

### Takeaway
VC keeps the *source performance's* prosody, emotion, timing and accent, and swaps timbre. It is therefore the most controllable route for dubbing timing and for an authentic Indian accent, *if the source speech is Indian-accented English*. Possible sources:
- An Indian-English human speaker, ideally a female voice-actor or family member reading the English script to the reel's timing.
- An Indian-English TTS voice (Sarvam `en-IN`, Indic Parler-TTS, ElevenLabs Indian voices).

Then convert to her voice with Seed-VC (zero-shot from 1-30 s), RVC (train on ~10-30 min of her clean speech), ElevenLabs Voice Changer, or Chatterbox VC. Seed-VC V2 also has an optional accent-conversion mode, which should be **disabled** here to keep the source accent.

### Cited Findings
**Seed-VC**
- Zero-shot from a 1-30 s reference.
- Models: V1 tiny (25M, real-time), V1 small-wavenet (98M, offline), singing (200M), and **V2** (hubert-bsqvae) with `--convert-style` for "accent & emotion conversion"; setting it false gives timbre-only conversion.
- Fine-tuning needs a minimum of one utterance and 100 steps (~2 min on a T4).
- GPL-3.0. GPU "strongly recommended" for real-time; no CPU figures. The repo is now archived/read-only.
- Source: [Seed-VC GitHub](https://github.com/Plachtaa/seed-vc)
- Authors' own eval vs OpenVoice: speaker similarity 0.8676 vs 0.7547, WER 11.99% vs 15.46% (ground truth WER 8.02%). Self-reported. — [Seed-VC EVAL.md mirror](https://gitcode.com/GitHub_Trending/se/seed-vc/blob/main/EVAL.md), [arXiv 2411.09943](https://arxiv.org/html/2411.09943v1)

**RVC (Retrieval-based Voice Conversion, Applio)**
- Applio docs: a minimum of ~10 min of clean single-speaker audio, with 20-30 min "noticeably better", silences removed. — [Applio training docs](https://mintlify.wiki/IAHispano/Applio/features/training)
- Guides suggest 10-30 min (up to 60 min), 200-500 epochs, with a risk of over-training artifacts. — [voicechanger.live guide (2026-05-28)](https://voicechanger.live/hub/how-to-train-rvc-model)
- Another readme suggests far fewer epochs (e.g. 30 epochs for 10 min). The sources conflict. — [audio-webui RVC readme](https://huggingface.co/spaces/mrtroydev/audio-webui/blob/refs%2Fpr%2F2/readme/rvc/training.md)
- A Fraunhofer ICPR 2024 study compared RVC, kNN-VC, FreeVC and QuickVC on German, including target-audio length 10-2400 s, but its numbers were not retrieved. — [Fraunhofer](https://publica.fraunhofer.de/handle/publica/479709)

**Other VC options**
- ElevenLabs Voice Changer preserves the input's accent and emotional cues, and outputs in any cloned voice. — [ElevenLabs Voice Changer](https://elevenlabs.io/docs/capabilities/voice-changer)
- Chatterbox ships a voice-conversion script (MIT). — [HF ResembleAI/chatterbox](https://huggingface.co/ResembleAI/chatterbox)
- OpenVoice V2 tone-colour converter (MIT); Seed-VC trains using OpenVoice's converter as a timbre shifter. — [OpenVoice GitHub](https://github.com/myshell-ai/OpenVoice), [arXiv 2411.09943](https://arxiv.org/html/2411.09943v1)
- A related cross-attention VC (SEF-VC) captures timbre "to a great extent" from 3 s references, with similarity rising up to 10 s. — [arXiv 2312.08676](https://arxiv.org/pdf/2312.08676)

### Inferences
- **Prosody and accent:** VC outputs inherit the source's rhythm and intonation. So a human Indian-English reading timed to the original reel gives the most natural emotion, accent and lip-sync timing, and her timbre comes from VC. This is likely more natural than pure TTS for short emotive reels, but it requires a source speaker.
- **Instagram reel source audio:** her reels likely contain background music and noise, so vocal isolation (e.g. Demucs/UVR) before building the reference or RVC dataset is important. Sarvam's docs note no server-side clean-up for references ([Sarvam migration guide](https://docs.sarvam.ai/api/migrations/from-elevenlabs/voice-cloning.md)).
- **Data:** ~10-30 min of clean Kannada speech from her existing videos would be enough for RVC. RVC is largely language-agnostic for timbre (inference; not directly sourced).
- **TTS -> VC chain:** Indian-English TTS (Sarvam Bulbul v3 `en-IN` female voice, or Indic Parler-TTS "Mary") -> Seed-VC or RVC to her timbre. This gives a guaranteed Indian accent plus her timbre, but prosody is only as good as the TTS. Pace control on Sarvam (0.5-2.0) helps timing.

### Gaps
- No head-to-head benchmark of Seed-VC vs RVC vs OpenVoice vs ElevenLabs STS on Indian-English or Indic speech was found.
- No CPU-only speed numbers were found for Seed-VC or RVC inference. RVC is known in the community to run on CPU slowly, but I did not verify this with a source.
- The Fraunhofer data-length results were not retrieved.

---

## 4. Techniques to keep an authentic Indian accent

### Takeaway
Three levers are documented:
1. Model choice. Accent-retaining models (ElevenLabs Multilingual v2, Cartesia clones, Chatterbox at default CFG, F5-TTS) versus accent-neutralising ones (Eleven v4, MiniMax 2.6 Fluent LoRA, Chatterbox cfg 0, AAG-style guidance).
2. Reference clip language and accent. Ideally *Indian-English* speech by her; otherwise her Kannada speech.
3. A TTS(en-IN) -> VC pipeline, which guarantees accent independently of the cloner.

### Cited Findings
- ElevenLabs: accent and pronunciation come from the voice; the language comes from the text. Clone from audio in the target language with the right accent for best results. — [ElevenLabs help](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/can-i-use-the-same-cloned-designed-voice-across-languages)
- ElevenLabs Multilingual v2 is described as keeping "accent across languages." — [ElevenLabs models](https://elevenlabs.io/docs/overview/models)
- Eleven v4 does not carry accent cross-lingually but does keep it when languages match. So **if she can record even 1-2 min of English (in her natural Indian accent)**, a v4 clone from that English sample should preserve her Indian-English accent. — [Eleven v4 docs](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4)
- Eleven v4 audio tags "can be tried to guide an accent", results vary. — [Eleven v4 docs](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4)
- Chatterbox: a mismatched reference language makes output "inherit the accent of the reference clip's language"; `cfg_weight=0` removes it. Keep CFG > 0 to retain Indian flavour. — [HF Chatterbox](https://huggingface.co/ResembleAI/chatterbox)
- Indic Parler-TTS supports Indian English directly, and accent can also be specified in the text description. — [HF Indic Parler-TTS](https://huggingface.co/ai4bharat/indic-parler-tts)
- Sarvam Bulbul `en-IN` is "English (Indian accent)". — [Sarvam API](https://www.sarvam.ai/apis/text-to-speech), [Sarvam TTS reference](https://docs.sarvam.ai/api-reference-docs/text-to-speech/convert)
- Research: CFG reweighting moves along a speaker-similarity vs accent-nativeness trade-off. Lower guidance toward the reference means more of the reference accent and more similarity. — [arXiv 2609.29123](https://arxiv.org/abs/2609.29123)
- Research: CrossAccent-TTS (June 2026 preprint) proposes cross-lingual accent-*intensity*-controllable TTS by disentangling speaker and accent. Title only; not evaluated here. — [arXiv 2606.25403](https://arxiv.org/pdf/2606.25403)
- MiniMax Speech 2.6's Fluent LoRA explicitly smooths accented non-native recordings into "fluent" speech, so it is a risk for this goal. — [MiniMax](https://www.minimax.io/news/minimax-speech-26)

### Inferences
- **Recommended A/B matrix:** reference = {her Kannada clip, her English clip if obtainable} × model = {ElevenLabs Multilingual v2, Eleven v3, Eleven v4 with English reference, Sarvam clone `en-IN`, Chatterbox ML V3 cfg 0.5} × VC route = {Sarvam en-IN female TTS -> Seed-VC/RVC}.
- A Kannada reference into an English-only/European-trained model may give a "foreign" accent that is not quite Indian-English. Indian-English training data (Sarvam, Indic Parler) is more likely to yield a *natural* Indian accent than raw leakage from Kannada.
- Write the English script in Indian-English idiom and spell names phonetically. Use Sarvam's pronunciation dictionary (v3) or IndexTTS-2.5 CMU phoneme overrides for tricky words.

### Gaps
- No source measured Indian-English accent authenticity for any clone. Human listening tests by native Indian listeners are needed.
- Whether the Sarvam clone keeps Kannada-origin accent when outputting `en-IN` is undocumented.

---

## 5. Practitioner experiences (Reddit, GitHub issues, blogs)

### Takeaway
Practitioner evidence for this exact scenario is thin. Searches did not surface specific Reddit threads (r/LocalLLaMA, r/ElevenLabs, r/india) on Kannada/Indic -> English cloning. Available reports are a Cartesia language-setting thread and vendor and model-card warnings about accent leakage.

### Cited Findings
- Cartesia: a cloned voice mispronounced Hindi until the language was set explicitly. Auto or English language settings caused mispronunciation. — [Vapi support thread](https://support.vapi.ai/t/33169486/cartesia-voice-language-setting-not-working)
- ElevenLabs IVC "may struggle with uncommon accents or unique voices"; ElevenLabs suggests PVC. — [ElevenLabs PVC docs](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/professional-voice-cloning)
- An F5-TTS adaptation to Romanian reported a residual English accent (the base-model accent persists after language adaptation). — [search summary of preprint, preprints.org](https://www.preprints.org/manuscript/202608.2014). This is unverified in detail.
- The F5-TTS GitHub issue #224 reports that the README examples take 3-5 s on an RTX 4090. — [F5-TTS issue #224](https://github.com/SWivid/F5-TTS/issues/224)

### Inferences
- Expect to iterate. Community consensus-style advice (not sourced to a specific thread) is that clean, noise-free reference audio matters more than model choice.

### Gaps
- Specific Reddit threads on Indian-accent English cloning were not found in search results. These remain unverified and should not be quoted.
- No GitHub issues about Kannada-reference cross-lingual cloning were found.

---

## 6. Hardware feasibility (our box: 4 CPU, 15 GB RAM, no GPU)

### Takeaway
Almost every open model documents only GPU usage. IndexTTS-2.5 needs an NVIDIA GPU (~6 GB VRAM), and Chatterbox and Seed-VC examples use CUDA. CPU-only RTFs were not found. The practical options are API-only (ElevenLabs, Sarvam) or Colab/rented GPU for open models. CPU may be tolerable for short reels (<60 s) with smaller models, but this is unbenchmarked.

### Cited Findings
- IndexTTS-2.5 needs an NVIDIA GPU with ~6 GB VRAM. — [HF IndexTTS-2.5](https://huggingface.co/IndexTeam/IndexTTS-2.5)
- Chatterbox examples use `device="cuda"` with no CPU guidance. Speed claims ("6x faster than real-time", 75 ms) are GPU-only. — [HF Chatterbox](https://huggingface.co/ResembleAI/chatterbox), [Resemble Chatterbox Turbo](https://resemble.ai/chatterbox-turbo)
- Chatterbox Turbo is 350M params, the smaller and more plausible CPU candidate. — [search summary citing Resemble](https://www.resemble.ai/learn/models/chatterbox-turbo)
- F5-TTS RTF figures:
  - 0.1467 PyTorch on an L20 GPU; 0.030 for 7-step Fast F5 on an RTX 3090.
  - Community ONNX and MLX ports exist; CPU numbers not found.
  - Sources: [F5 Triton README](https://huggingface.co/spaces/yl4579/DMOSpeech2-demo/blob/a28c293d75c2856ef830553d65c6568eb5a99d30/f5_tts/runtime/triton_trtllm/README.md), [arXiv 2505.19931](https://arxiv.org/abs/2505.19931v2)
- Seed-VC: a GPU is "strongly recommended" for real-time, with no CPU numbers. — [Seed-VC GitHub](https://github.com/Plachtaa/seed-vc)
- A different flow-matching model (FreyaTTS) reaches RTF 0.165 on a laptop CPU. This shows CPU flow-matching TTS is possible, but it is not evidence for these specific models. — [arXiv 2607.09530](https://arxiv.org/pdf/2607.09530)

### Inferences
- **Execution box:** treat the commercial APIs as the primary path, plus ffmpeg post-processing (time-stretch, mixing) on the CPU box. Run open models (Chatterbox, F5, Seed-VC, RVC training) on Colab or a rented GPU.
- RVC *training* on CPU is impractical (inference, not sourced). RVC/Seed-VC *inference* on CPU for a 30-60 s reel may be minutes rather than seconds. Benchmark before committing.

### Gaps
- No measured CPU RTF for Chatterbox, F5-TTS, Seed-VC, RVC, Qwen3-TTS or CosyVoice.

---

## 7. Ethics, consent and platform policy (subject is the user's mother)

### Takeaway
Every vendor and model card found requires that you have the right or consent to clone the voice. ElevenLabs goes further: a PVC must be created *by the voice owner* and pass a live voice CAPTCHA, even with consent. Chatterbox output is watermarked. Voice-clone scams are well documented in India, so disclosure on reels is advisable.

### Cited Findings
- ElevenLabs: you cannot create a PVC of someone else's voice even with consent. The owner creates and verifies it and can share it privately. — [ElevenLabs help](https://help.elevenlabs.io/hc/en-us/articles/36842751624209)
- ElevenLabs prohibited-use policy bars replicating another's voice without consent or legal right, and bars evading verification. — [aiproductivity.ai summary](https://aiproductivity.ai/guides/elevenlabs-voice-cloning-ethics/). This is secondary; check the primary policy.
- Sarvam: "Only clone a voice you have the right to use"; consent requirements are on its Commercial Licensing page. — [Sarvam Voice Cloning docs](https://docs.sarvam.ai/api/api-guides-tutorials/voice-cloning/overview)
- AI4Bharat IndicF5: "only clone voices for which you have explicit permission." — [IndicF5 GitHub](https://github.com/AI4Bharat/IndicF5)
- IndexTTS-2.5: speaker consent is the user's responsibility. — [HF IndexTTS-2.5](https://huggingface.co/IndexTeam/IndexTTS-2.5)
- Chatterbox embeds an imperceptible PerTh watermark that survives MP3 compression and editing. — [HF Chatterbox](https://huggingface.co/ResembleAI/chatterbox)
- Indian context: Tamil Nadu police warned that scammers take voice samples from social-media videos, and Lucknow reported an AI voice fraud case. — [DT Next via PressReader](https://www.pressreader.com/india/dt-next/20240428/281621015402986), [Gulf News](https://gulfnews.com/world/asia/india/india-lucknow-reports-first-ai-generated-voice-fraud-case-1.1702870783452) (2023-2024, older)

### Inferences
- **Practical consent path:**
  - Get the mother's explicit (ideally recorded or written) consent.
  - For ElevenLabs PVC, she must create the account or verification herself. IVC by the son with her consent is permitted in spirit, but keep the consent record.
  - Label reels as AI-dubbed. Instagram/Meta AI-label policies were not researched here.
- Because her existing public reels already expose her voice, the dubbed output increases impersonation risk. Watermarking (Chatterbox) and disclosure mitigate this.

### Gaps
- Instagram/Meta's 2026 policy on AI-generated or altered audio labelling was not researched.
- India-specific legal rules (e.g. IT Rules amendments on synthetic media) were not researched.
