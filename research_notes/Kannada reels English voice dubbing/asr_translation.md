# Kannada ASR and Kannada→English Translation for a Reels Dubbing Pipeline (state as of Oct 2026)

Scope: short Instagram reels, a middle-aged woman speaking casual Kannada with English code-mixing and possibly background music. The goal is natural Indian-English output for dubbing. Execution box: 4 CPU, 15 GB RAM, no GPU.

Research date: 2026-10-08. Vendor model names change often. Every model ID below was read from the vendor's own docs page in October 2026 unless flagged otherwise.

---

## 1. Kannada ASR options: accuracy, timestamps, code-mixing, where they run

### Takeaway
The only recent independent Kannada head-to-head I found is JoshTalks' "Voice of India" benchmark (Aug 2026, unscripted telephonic speech). On Kannada it ranks **Sarvam Saaras v3 first (8.8% OI-WER)**, then Amazon Transcribe (11.1), ElevenLabs Scribe v2 and Gemini 3 Pro (both 14.0), and AI4Bharat IndicConformer (16.3). Meta OmniASR-LLM-7B (35.0) and Deepgram Nova-3 (51.1) fall far behind.

For a dubbing pipeline the trade-off is between accuracy and timing data:
- Sarvam gives only **segment/phrase-level** timestamps (no word-level), but it can also translate speech straight to English and has a `codemix` mode.
- ElevenLabs Scribe v2 and Google's new `gemini-3.5-transcribe` give **word-level** timestamps.

None of the strong options is practical to run on the CPU-only box except possibly the small Whisper fine-tunes and IndicConformer ONNX, and neither has been verified for CPU speed. API-first is the realistic path.

### Cited Findings

**Independent / third-party benchmark (most relevant to real-world casual speech)**
- JoshTalks "Voice of India" benchmark, Kannada OI-WER (%): Saaras v3 **8.8**; Amazon Transcribe **11.1**; ElevenLabs Scribe v2 **14.0**; Gemini 3 Pro **14.0**; IndicConformer **16.3**; Gemini 3 Flash **18.5**; Gemma E4B **31.0**; OpenAI Realtime Whisper **32.9**; OmniASR LLM 7B **35.0**; Deepgram Nova 3 **51.1**; GPT-4o Mini Transcribe **89.6**. Microsoft was not scored. — [JoshTalks benchmark report](https://elevenlabsreport.ai.joshtalks.com/)
- Methodology:
  - The Kannada slice is 24.9 h, 12.6K utterances, 320 speakers, 36 districts.
  - The whole dataset is "536.1 hours of unscripted telephonic conversation" across 15 languages and is closed-source.
  - OI-WER = orthographically-informed WER, which accepts valid spelling variants.
  - Segments are ≤30 s, cut at non-speech.
  - Report is dated Aug 2026 (draft/V2). — [JoshTalks benchmark report](https://elevenlabsreport.ai.joshtalks.com/)
  - Caveats: the audio is telephonic (8 kHz-like) conversation, not reels with music. The report's URL host is "elevenlabsreport", which suggests some ElevenLabs involvement, yet ElevenLabs does not win on Kannada. Deepgram released new Nova-3 *monolingual* Kannada models on 21 Jul 2026 ([Deepgram changelog](https://developers.deepgram.com/changelog/2026/7/21)), and it is unclear whether the benchmark used them.

**Sarvam (API-only)**
- Current STT models on `/speech-to-text`:
  - `saaras:v4` is the default and "recommended". `saaras:v3` is still available.
  - The current STT reference page does not mention the older "Saarika" family. A third-party page still describes "Saarika = transcription, Saaras = speech→English", which looks outdated ([Bolna](https://www.bolna.ai/docs/sarvam-transcriber)). — [Sarvam STT API reference](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe); [Sarvam Saaras model page](https://docs.sarvam.ai/api-reference-docs/models/saaras)
- Saaras v2.5 is marked "Deprecated Soon". — [Saaras model page](https://docs.sarvam.ai/api-reference-docs/models/saaras)
- Modes (`mode` parameter):
  - `transcribe` (default, normalizes numbers)
  - `translate` (Indic speech → English text, always English output)
  - `verbatim`
  - `translit` (romanized)
  - `codemix` (English words in Latin script, Indic words in native script)
  - The STT reference page says `mode` applies to saaras:v3, while the model page describes the modes for the family. Test whether v4 honors `mode`. — [Saaras model page](https://docs.sarvam.ai/api-reference-docs/models/saaras); [STT reference](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe)
- Kannada code is `kn-IN`. `language_code="unknown"` auto-detects. 23 languages are covered (22 Indic + English). — [STT reference](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe); [Saaras model page](https://docs.sarvam.ai/api-reference-docs/models/saaras)
- Timestamps:
  - `with_timestamps=true` returns **chunk-level (sentence/phrase) timestamps only. Word-level is not supported.**
  - The response fields are `words`, `start_time_seconds`, `end_time_seconds`.
  - Word-level timestamps are promised only for an upcoming Realtime endpoint ("Coming Soon"). — [STT reference](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe); [Sarvam ASR blog](https://www.sarvam.ai/blogs/asr)
- `keyterms`: up to 50 terms of ≤64 chars each, saaras:v4 only. — [STT reference](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe)
- Limits:
  - REST is meant for "quick responses under 30 seconds" and gives no hard max. Longer audio should use the Batch API.
  - Batch accepts files up to **2 hours**, 20 files per job, and diarization (`with_diarization=True`, up to 20 speakers). It is chunk-level only, with no word timestamps.
  - Python SDK: `from sarvamai import SarvamAI`, then `client.speech_to_text_job.create_job(model="saaras:v4", mode=..., language_code=..., with_diarization=...)`. — [Sarvam Batch STT docs](https://docs.sarvam.ai/api-reference-docs/speech-to-text/apis/batch); [STT reference](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe)
- Pricing (INR, billed per second):
  - STT ₹30/h; STT + diarization ₹45/h
  - STT + translate ₹30/h; translate + diarization ₹45/h
  - New users get ₹100 free credit. — [Sarvam pricing](https://docs.sarvam.ai/api-reference-docs/pricing)
- Sarvam's self-reported results:
  - Saaras v3 ≈19% WER on IndicVoices overall and 19.31% on the top-10-language subset, vs ~22% for Saaras v2.5 (Feb 11, 2026 post). No per-language Kannada figure is published.
  - Sarvam claims v3 beats GPT-4o Transcribe, Gemini 3 Pro, Deepgram Nova-3 and Scribe v2 but gives no competitor numbers. — [Sarvam ASR blog](https://www.sarvam.ai/blogs/asr)
  - Sarvam publishes no benchmark for saaras:v4. — [Saaras model page](https://docs.sarvam.ai/api-reference-docs/models/saaras)
- The only published Saaras speech→English quality figure: Saaras v2.5 COMET 89.3% across 11 languages on Vistaar + IndicVoices (88.41% for the 9 non-Hindi/English languages). It is old (v2.5) and has no Kannada breakout. — [Saaras model page](https://docs.sarvam.ai/api-reference-docs/models/saaras)

**ElevenLabs Scribe (API-only)**
- The current docs list Scribe v2, Scribe v2 Realtime and Scribe v2 Medical. Kannada is code `kan`, rated "Excellent (≤5% WER)". — [ElevenLabs STT docs](https://elevenlabs.io/docs/overview/capabilities/speech-to-text)
- Features:
  - **word-level timestamps** (start/end per word)
  - diarization up to 32 speakers
  - audio-event tagging (laughter, applause, etc.)
  - max 3 GB / 10 h per file — [ElevenLabs STT docs](https://elevenlabs.io/docs/overview/capabilities/speech-to-text)
- Price: Scribe v2 **$0.22/h** base (keyterm prompting +$0.05/h); Scribe v2 Realtime $0.39/h. — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
  - The Kannada marketing page still says $0.40/h. — [ElevenLabs Kannada page](https://elevenlabs.io/speech-to-text/kannada)
- ElevenLabs' own Kannada FLEURS table (Scribe **v1**, undated): Scribe v1 4.0%, Gemini Flash 2 5.3%, Whisper Large v3 37.5%, Deepgram Nova 2 100%. The same page's intro says 3.1% FLEURS / 5.5% Common Voice, which is internally inconsistent. These are vendor numbers. — [ElevenLabs Kannada page](https://elevenlabs.io/speech-to-text/kannada)
- On real conversational speech, the independent JoshTalks benchmark has Scribe v2 at 14.0% OI-WER for Kannada. — [JoshTalks](https://elevenlabsreport.ai.joshtalks.com/)

**Google: Gemini 3.5 Transcribe and Gemini LLMs (API-only)**
- New dedicated STT model `gemini-3.5-transcribe` (file) and `gemini-3.5-transcribe-live` (streaming). It is listed in the stable Gemini 3 section of the models page (page updated 2026-10-06). — [Gemini models](https://ai.google.dev/gemini-api/docs/models); [gemini-3.5-transcribe page](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-transcribe)
- Features of `gemini-3.5-transcribe`:
  - **Kannada listed as `kn-IN`**; 85+ languages with auto-detect
  - "handles multi-language code-switching"
  - **word-level timestamps** on the file endpoint only. Google says they "degrade transcription accuracy" and are incompatible with custom vocabulary.
  - Limits: 1 h per request, or 30 min with timestamps/diarization
  - diarization up to 8 speakers (3+ experimental)
  - custom vocabulary up to 1,000 terms — [gemini-3.5-transcribe page](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-transcribe)
- Pricing for `gemini-3.5-transcribe`:
  - $2.00 per 1M audio input tokens (≈$0.003/min) plus $12.00 per 1M output text tokens (≈$0.002/min), so ≈$0.005/min (~$0.30/h)
  - Free tier listed. — [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)
  - Note: the pricing page's per-minute estimate assumes 25 audio tokens/s, while the general audio guide says 32 tokens/s. — [Gemini audio guide](https://ai.google.dev/gemini-api/docs/audio)
- General Gemini LLMs (e.g. `gemini-3.8-flash`, the model in the audio guide examples) accept audio:
  - Prompts can reference MM:SS ranges; max 9.5 h audio per prompt; 20 MB inline request limit, Files API above that. — [Gemini audio guide](https://ai.google.dev/gemini-api/docs/audio)
  - `gemini-3.8-flash` pricing: $0.75 in / $3.75 out per 1M tokens through Dec 31 2026, then $1.50 / $7.50 from Jan 1 2027. — [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)
  - The audio guide makes no claim about timestamp reliability for generic LLM transcription. — [Gemini audio guide](https://ai.google.dev/gemini-api/docs/audio)
- No Kannada WER is published for gemini-3.5-transcribe. Third-party coverage exists ([eesel.ai](https://eesel.ai/blog/gemini-3-5-transcribe)) but I did not find Kannada numbers.

**Google Cloud Speech-to-Text v2 (API-only)**
- Models supporting `kn-IN`: `chirp_3` (region `eu`), `chirp_2` (asia-southeast1, europe-west4; has word-level confidence and model adaptation), `chirp`, `long`, `short`. No diarization is listed for Kannada.
- The support page has no timestamp column, so word time offsets for Kannada on chirp_3 are unverified. I read only the first ~100K chars of the page; the global region section was truncated. — [Google Cloud STT supported languages](https://docs.cloud.google.com/speech-to-text/v2/docs/speech-to-text-supported-languages)

**Deepgram (API-only)**
- Kannada (`kn`) was added to Nova-3 on 29 Jan 2026 ([changelog](https://developers.deepgram.com/changelog/2026/1/29)). New Nova-3 monolingual Kannada models (batch + streaming) followed on 21 Jul 2026 ([changelog](https://developers.deepgram.com/changelog/2026/7/21)). Usage: `model="nova-3"`, `language="kn"`.
- The only independent Kannada number is 51.1% OI-WER on JoshTalks, possibly measured before the July model. — [JoshTalks](https://elevenlabsreport.ai.joshtalks.com/)

**AssemblyAI (API-only)**
- The docs list Kannada for Universal-3 Pro ([AssemblyAI supported languages](https://www.assemblyai.com/docs/concepts/supported-languages)), but AssemblyAI's Kannada landing page shows "Coming soon" in a comparison row ([AssemblyAI Kannada page](https://www.assemblyai.com/languages/kannada)). The two conflict, and timestamp support for Kannada is unverified.
- Streaming multilingual does not include Kannada. — [AssemblyAI streaming languages](https://support.assemblyai.com/articles/1008413517-language-support-for-real-time-transcription)

**Amazon Transcribe**
- Scored 11.1% Kannada OI-WER on JoshTalks, second best. — [JoshTalks](https://elevenlabsreport.ai.joshtalks.com/)
- I did not verify Amazon's Kannada language code, timestamps or pricing from AWS docs. A Gnani vendor blog lists "$0.0001 per second", which is unverified. — [Gnani blog](https://www.gnani.ai/resources/blogs/best-kannada-asr-tools-for-indian-languages-in-2026)

**Open models (self-host)**
- **AI4Bharat IndicConformer** (`ai4bharat/indic-conformer-600m-multilingual`):
  - 600M-parameter hybrid CTC+RNNT Conformer; all 22 scheduled languages incl. `kn`
  - **MIT licence**, but the HF repo is **gated** (you must accept terms)
  - Called as `model(wav, "kn", "ctc"|"rnnt")` via `AutoModel.from_pretrained(..., trust_remote_code=True)` on 16 kHz mono
  - The card mentions ONNX but installs the GPU onnxruntime build. CPU speed and timestamps are not documented.
  - The only WER on the card is Hindi 13.2 on Vaani.
  - The card recommends the newer "Indic-Transcribe". — [HF model card](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
  - Kannada OI-WER on JoshTalks: 16.3. — [JoshTalks](https://elevenlabsreport.ai.joshtalks.com/)
- **Indic-Transcribe-core** (`bodhan-ai/indic-transcribe-core`):
  - 25 languages (22 scheduled + Indian English + Bhojpuri + Bhili); built on NVIDIA canary-1b-v2; "ready for commercial use"
  - Claims to transcribe code-mixed speech as spoken
  - Self-reported RTF 911 on one H100. — [HF card](https://huggingface.co/bodhan-ai/indic-transcribe-core)
  - Business Today (18 Aug 2026) ties it to AI4Bharat/IIT Madras (Mitesh Khapra) and Bodhan AI, and says "26 languages", which conflicts with the card. — [Business Today](https://www.businesstoday.in/technology/artificial-intelligence/story/from-hindi-to-regional-accents-this-new-ai-model-is-built-to-understand-26-indian-languages-549708-2026-08-18)
  - No Kannada WER was found.
- **AI4Bharat IndicWhisper (Vistaar)**, Kannada WER: Kathbath 19.3, Kathbath-Hard 22.2, FLEURS 18.6, IndicTTS 13.2. MIT licence; checkpoint is `kannada_models.zip`. This is 2023-era work. — [Vistaar GitHub](https://github.com/AI4Bharat/vistaar)
- **vasista22/whisper-kannada-medium**:
  - Fine-tuned from whisper-medium on IISc-MILE, ULCA, Shrutilipi and FLEURS train+dev
  - Self-reported **FLEURS test WER 7.65**; Apache-2.0
  - The card recommends whisper-jax or a Transformers pipeline with `chunk_length_s=30`, `language="kn"`. Timestamps are not discussed. — [HF card](https://huggingface.co/vasista22/whisper-kannada-medium)
  - Caveat: FLEURS train+dev was in the training data, and the test sentences are read speech. This is an older model (2023).
- **Whisper large-v3 (vanilla)**: 37.5% Kannada FLEURS WER per ElevenLabs' (vendor) table. — [ElevenLabs Kannada page](https://elevenlabs.io/speech-to-text/kannada)
  - Deepgram's 2023 testing found large-v3 hallucinated more than v2 on real-world audio (median WER 53.4 vs 12.7, English-focused). — [Deepgram blog](https://deepgram.com/learn/whisper-v3-results)
  - Repetition loops on large-v3 are reported in [whisper.cpp discussion #1490](https://github.com/ggml-org/whisper.cpp/discussions/1490).
- **Meta Omnilingual ASR**:
  - Apache-2.0. CTC 300M/1B/3B/7B, LLM 300M–7B, "LLM Unlimited" variants, and zero-shot 7B.
  - CTC and LLM models accept only **<40 s** audio (except Unlimited).
  - VRAM at batch=1 for 30 s: CTC-300M ~2 GiB … LLM-7B ~17 GiB.
  - CTC is much faster (RTF 0.001–0.006 relative) than LLM (~0.09). No timestamps are documented. — [omnilingual-asr GitHub](https://github.com/facebookresearch/omnilingual-asr)
  - Meta reports CER <10 for 78% of ~1,600 languages ([Meta blog](https://ai.meta.com/blog/omnilingual-asr-advancing-automatic-speech-recognition/)), but Kannada was only 35.0% OI-WER (LLM 7B) on JoshTalks ([JoshTalks](https://elevenlabsreport.ai.joshtalks.com/)).

**Vendor-marketing figures (low trust)**
- Gnani.ai (28 Jul 2026) claims its own Kannada WER is "<9%" and gives Google ~12–15%, Azure ~13–16%, Amazon ~14–17%, with no named dataset or methodology. Its own FAQ says the figures "need independent verification". — [Gnani blog](https://www.gnani.ai/resources/blogs/best-kannada-asr-tools-for-indian-languages-in-2026)

### Inferences
- **Recommended primary ASR: Sarvam `saaras:v4`**, with `saaras:v3` as the JoshTalks-benchmarked fallback. Use `mode="transcribe"` or `mode="codemix"` with `language_code="kn-IN"` and `with_timestamps=true`.
  - It is cheapest per hour of the top tier (₹30/h, about $0.35/h), best on independent Kannada data, and explicitly code-mix aware.
  - Its timestamps are phrase-level only, and phrase-level segments are actually the natural unit for dubbing.
  - A 30–90 s reel is above the "<30 s" REST guidance. Either chunk on VAD silences into ≤30 s pieces (which also gives clean segment boundaries) or use the Batch API.
- **Word-level timing:** where it is needed (precise lip/pause alignment, subtitle burn-in), run ElevenLabs Scribe v2 ($0.22/h, word timestamps, audio-event tags that help with music) or `gemini-3.5-transcribe` (word timestamps, ~$0.30/h). Use them as a second pass, or align Sarvam's text to their word timings.
- **Cost is negligible:** a 60-second reel costs well under ₹1 on any of these APIs.
- **Background music:** none of the sources benchmarks ASR under music. Running source separation (e.g. Demucs) before ASR is a common mitigation but is not verified here. Scribe's audio-event tagging is the only documented music/noise-aware feature.
- **CPU box:** treat all serious ASR as API calls. Possible on CPU but unverified and likely slow-but-workable for short reels: the gated IndicConformer via ONNX, or vasista22 Whisper-medium via a CPU runtime. Omnilingual 7B and Indic-Transcribe need a GPU/Colab.
- **Whisper large-v3 vanilla:** do not use it for Kannada (≈37.5% FLEURS WER per vendor data, plus hallucination/repetition reports).
- **Translate mode:** Sarvam `mode="translate"` gives a one-shot Kannada speech→English baseline, but its output is likely literal. It is better used as a cross-check against a transcribe → LLM-translate path.

### Gaps
- There is no published per-language Kannada WER for saaras:v4, gemini-3.5-transcribe, Google chirp_3 or Indic-Transcribe-core. IndicVoices/Kathbath/FLEURS Kannada numbers for most commercial systems were not found.
- Whisper paper Kannada FLEURS WER: not retrieved; the 37.5% comes from ElevenLabs only.
- Omnilingual ASR Kannada CER: the per-language CSV in the repo was not retrieved.
- Practitioner reports (Reddit r/kannada, r/LocalLLaMA) on Kannada ASR: **I found no relevant Reddit threads**, and no Kannada-specific GitHub issues on Whisper.
- No source benchmarks Kannada ASR on social-media audio with background music.
- Whether Sarvam's v4 honors every `mode` value: the docs are ambiguous.
- AssemblyAI Kannada availability conflicts across sources. Amazon Transcribe Kannada details were not checked in AWS docs.
- CPU inference speed for IndicConformer and the Whisper fine-tunes was not documented.

---

## 2. Kannada→English translation options and benchmarks

### Takeaway
On standard benchmarks, kn→en is a "solved-ish", high-resource direction. IndicTrans2, Google Translate, Azure and NLLB-54B all land within ~3 chrF++ of each other: IN22-Gen ≈62–65, FLORES ≈59–62, IN22-Conv (conversational) ≈46–48. GPT-3.5 was ~5–12 points worse, but that is a 2023 result.

For dubbing, benchmark adequacy matters less than register and length control, which call for an instruction-following LLM. No published kn→en benchmark covers current Claude, GPT or Gemini models.

### Cited Findings
**IndicTrans2 (AI4Bharat, open, MIT)**
- HF models: `ai4bharat/indictrans2-indic-en-1B` and the distilled `ai4bharat/indictrans2-indic-en-dist-200M`. Language tags are `kan_Knda` → `eng_Latn`. CTranslate2 inference is documented.
- Code and checkpoints are MIT. — [IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2)
- kn→en chrF++ from the IndicTrans2 paper (TMLR 12/2023) — [IndicTrans2 paper PDF](https://arxiv.org/pdf/2305.16307):

  | Test set | IT2 | Google | Azure | NLLB-54B | NLLB-1.2B | IT1 | Paper table |
  |---|---|---|---|---|---|---|---|
  | IN22-Gen | 64.2 | 64.5 | 61.7 | 65.1 | 62.4 | 58.8 | Table 12 |
  | FLORES-200 devtest | 61.5 | 62.1 | 58.6 | 61.0 | – | – | Table 13 |
  | **IN22-Conv** (conversational) | 47.5 | 48.0 | 48.1 | 46.2 | – | – | Table 14 |

  - GPT-3.5-turbo (zero-shot), Table 26: IN22-Gen kn→en **51.7** vs IT2 64.2; IN22-Conv kn→en **42.1** vs IT2 47.5.
  - Distilled 200M vs 1B (Tables 22, 52, 53): IN22-Gen 64.3 vs 64.2; FLORES 60.0 vs 61.5; IN22-Conv **48.3** vs 47.5. The distilled model is essentially as good, which matters for CPU.
- Benchmark sizes: IN22-Gen has 1,024 sentences and IN22-Conv 1,503. — [IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2)

**Sarvam translation (API-only)**
- Endpoint `POST https://api.sarvam.ai/translate` (header `api-subscription-key`). — [Sarvam translate API](https://docs.sarvam.ai/api-reference-docs/text/translate-text)
  - `mayura:v1`: 11 languages incl. `kn-IN` and `en-IN`; max 1,000 chars.
    - `mode` ∈ {`formal`, `modern-colloquial`, `classic-colloquial`, `code-mixed`}
    - `speaker_gender` ∈ {Male, Female}
    - `output_script`
    - source `auto`
  - `sarvam-translate:v1`: 22 scheduled languages; formal mode only; 2,000 chars.
- Price: ₹20 per 10K characters for both. — [Sarvam pricing](https://docs.sarvam.ai/api-reference-docs/pricing)
- Sarvam-Translate is a Gemma3-4B-IT fine-tune. — [Gemmaverse/Sarvam](https://deepmind.google/models/gemma/gemmaverse/sarvam-ai/); [Sarvam blog](https://www.sarvam.ai/blogs/sarvam-translate)
- A Kannada-speaking reviewer (June 2025) found Sarvam Translate output literal and unnatural, including a clear mistranslation of a story title. This is qualitative and an older version. — [Thejesh GN blog](https://thejeshgn.com/2025/06/10/first-impressions-of-sarvam-indic-translate-model/)
- Sarvam also sells an LLM (`sarvam-105b`, ₹29.28 in / ₹73.2 out per 1M tokens). — [Sarvam pricing](https://docs.sarvam.ai/api-reference-docs/pricing)

**Other**
- Krutrim-Translate (Krutrim Community License, gated) reports Kannada chrF++ on IN22. The two retrievals of its card disagreed:
  - Fetched card: kn→en IN22-Gen 58.4, IN22-Conv 47.3.
  - Search snippet: different pairings.
  - Treat as unreliable. — [Krutrim-Translate HF](https://huggingface.co/krutrim-ai-labs/Krutrim-Translate)
- A 2023 LLM study (en→Indic only, chrF): Kannada GPT-3.5 17.8 vs IndicTrans2 25.1 vs Google 24.3. — [arXiv 2311.09216](https://arxiv.org/pdf/2311.09216)

### Inferences
- **Recommended translator: a frontier LLM (Claude / GPT / Gemini) fed the Kannada transcript.** Benchmarks show traditional MT already reaches parity on adequacy. Dubbing, though, needs things only an instruction-following model provides:
  - colloquial Indian-English register
  - keeping English code-mixed words as spoken
  - speaker persona (middle-aged woman, warm/casual)
  - per-segment length budgets
- **Prompt approach:** pass the whole reel transcript as context and translate segment by segment, returning JSON keyed by segment ID. The prompt should:
  - specify Indian English (allow "na", "only", "itself", "no?" sparingly; keep "aunty", food names and kinship terms when natural)
  - say "conversational, not textbook"
  - keep English words the speaker already used
  - preserve fillers and exclamations where they carry personality
- **Baselines for QA/back-off:**
  - IndicTrans2 dist-200M runs on CPU via CTranslate2 (inference, not benchmarked here) and is free and offline.
  - Sarvam `mayura:v1` with `mode="modern-colloquial"` and `speaker_gender="Female"` is a cheap API baseline. Whether `mode` affects English *output* register is undocumented.
- **No current-LLM figures:** there is no current benchmark for Claude/GPT/Gemini on kn→en. Exact current Claude/GPT model IDs were not verified in this research (the Gemini IDs were). The pipeline author should check current model IDs from the vendor docs.

### Gaps
- No IN22/FLORES kn→en scores for current LLMs (Claude, GPT-5-era, Gemini 3.x) or for Sarvam-Translate/Mayura.
- No benchmark of Sarvam Saaras `translate` mode on Kannada specifically.
- No source evaluates the "naturalness of Indian-English register" for translation output. This is only a prompting heuristic, unsourced.
- **I found no practitioner (Reddit/blog) reports** comparing LLMs for Kannada→English colloquial translation.

---

## 3. Length-controlled / isochronous translation for dubbing

### Takeaway
The literature agrees that LLM translations run longer than the source speech. The working recipe is:
1. Compute a per-segment budget from source duration, in syllables or phonemes.
2. Put the budget in the prompt.
3. Check the output and iterate (shorten or lengthen) until it fits.

A prompt instruction alone is unreliable.

### Cited Findings
- **Duration-based Translation** (EMNLP 2025 demo, "End-to-End Multilingual Automatic Dubbing via Duration-based Translation with LLMs"):
  - Predicts the optimal phoneme count from source speech duration and iteratively shortens/lengthens the translation.
  - Reports up to 24% relative improvement in speech overlap vs unconstrained translation, with competitive COMET (en/es/ko).
  - No language-specific tuning. — [ACL Anthology 2025.emnlp-demos.37](https://aclanthology.org/2025.emnlp-demos.37)
- **HOMURA** (arXiv preprint 2026):
  - Notes that LLM translations are "significantly longer than their source utterances".
  - Uses a syllable budget as a cross-lingually comparable unit, plus RL with a dynamic syllable-ratio reward. Reports precise length control vs strong LLM baselines.
  - Implies off-the-shelf LLMs struggle to obey length limits from instructions alone. Preprint, so results are provisional. — [arXiv 2601.10187](https://arxiv.org/pdf/2601.10187v1)
- Commercial reference point: ElevenLabs Dubbing API costs $0.33/min (watermark) or $0.50/min (v1), and $2.20/min (Dubbing v2). — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)

### Inferences
- Practical loop for this pipeline:
  1. Get segment durations from the ASR timestamps (Sarvam chunk-level is sufficient).
  2. Target English syllables ≈ duration × the speaker's English rate (a typical TTS rate of ~4–5 syllables/s is an assumption, not sourced; calibrate on the chosen TTS voice).
  3. Ask the LLM for a translation within ±10% of that budget, plus a shorter alternative.
  4. Count syllables programmatically, synthesize, and measure TTS duration.
  5. If it overshoots by more than ~10–15%, re-prompt "shorten to N syllables keeping meaning and tone", or apply mild time-stretch.
- Kannada is agglutinative, so a Kannada segment often packs more meaning per word than English. Expect English drafts to run long, which is consistent with the HOMURA observation.

### Gaps
- Neither paper evaluates Kannada→English.
- Exact prompt templates from the EMNLP paper were not retrieved.
- No sourced figure for Indian-English speaking rate (syllables/s) for budgeting.

---

## 4. Practical API cheat-sheet (verified Oct 2026)

### Takeaway
All recommended components are cheap (well under $0.01 per reel) and callable via simple REST/SDK. Verified model IDs: `saaras:v4`, `saaras:v3`, `mayura:v1`, `sarvam-translate:v1`, `gemini-3.5-transcribe`, `gemini-3.8-flash`, Scribe v2, `nova-3`.

### Cited Findings

| Service | Model ID / call | Kannada code | Timestamps | Code-mix | Price | Runs where | Source |
|---|---|---|---|---|---|---|---|
| Sarvam STT | `saaras:v4` (default), `saaras:v3`; `/speech-to-text`, `mode`, `with_timestamps` | `kn-IN` | Segment/phrase only | `codemix` mode | ₹30/h (₹45 w/ diarization) | API | [ref](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe), [pricing](https://docs.sarvam.ai/api-reference-docs/pricing) |
| Sarvam STT→EN | same, `mode="translate"` | `kn-IN` | Segment | yes | ₹30/h | API | [Saaras](https://docs.sarvam.ai/api-reference-docs/models/saaras) |
| ElevenLabs | Scribe v2 | `kan` | Word-level | not documented | $0.22/h | API | [docs](https://elevenlabs.io/docs/overview/capabilities/speech-to-text), [pricing](https://elevenlabs.io/pricing/api) |
| Google Gemini | `gemini-3.5-transcribe` | `kn-IN` | Word-level (file endpoint; lowers accuracy) | yes | ~$0.005/min; free tier | API | [model](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-transcribe), [pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| Google Cloud STT v2 | `chirp_3` (eu), `chirp_2` | `kn-IN` | unverified | unverified | not checked | API | [langs](https://docs.cloud.google.com/speech-to-text/v2/docs/speech-to-text-supported-languages) |
| Deepgram | `nova-3` | `kn` | not checked | not checked | not checked | API | [changelog](https://developers.deepgram.com/changelog/2026/7/21) |
| IndicConformer | `ai4bharat/indic-conformer-600m-multilingual` (gated, MIT) | `kn` | not documented | not documented | free | GPU suggested; CPU unverified | [HF](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual) |
| Whisper-kn FT | `vasista22/whisper-kannada-medium` (Apache-2.0) | `kn` | not documented on card | – | free | CPU possible but slow (unverified) | [HF](https://huggingface.co/vasista22/whisper-kannada-medium) |
| Omnilingual ASR | omniASR CTC/LLM 300M–7B (Apache-2.0) | `{lang}_{script}` format; `kan_Knda` unverified | not documented | – | free | GPU (2–17 GiB VRAM) | [GitHub](https://github.com/facebookresearch/omnilingual-asr) |
| Sarvam Translate | `mayura:v1` (modes, 1K chars), `sarvam-translate:v1` (2K chars) | `kn-IN`→`en-IN` | – | `code-mixed` mode | ₹20/10K chars | API | [API](https://docs.sarvam.ai/api-reference-docs/text/translate-text) |
| IndicTrans2 | `ai4bharat/indictrans2-indic-en-dist-200M` / `-1B` (MIT) | `kan_Knda`→`eng_Latn` | – | – | free | CPU via CTranslate2 (feasible for 200M; not benchmarked) | [GitHub](https://github.com/AI4Bharat/IndicTrans2) |
| Gemini LLM | `gemini-3.8-flash` | – | – | – | $0.75/$3.75 per 1M tok (until 2026-12-31) | API | [pricing](https://ai.google.dev/gemini-api/docs/pricing) |

### Inferences
Suggested pipeline:
1. Extract audio with ffmpeg (16 kHz mono). Optionally separate vocals from music.
2. Split on VAD into ≤30 s segments.
3. Run Sarvam `saaras:v4` with `mode="codemix"` (or `transcribe`), `language_code="kn-IN"`, `with_timestamps=true`.
4. In parallel, run `mode="translate"` as a literal-English reference.
5. Optionally run Scribe v2 for word timings and audio-event tags.
6. Have an LLM produce Indian-English dubbing lines per segment with syllable budgets.
7. Synthesize with TTS, measure durations, and loop.

Everything runs fine on the 4-CPU box because all heavy compute is API-side.

### Gaps
- Sarvam REST hard maximum duration is not stated.
- The Sarvam pricing page does not separate saaras v3/v4 or REST/batch prices.
- Deepgram, Google Cloud STT and AssemblyAI Kannada pricing and timestamp details were not verified.
- Claude/OpenAI current model IDs and prices were not verified in this pass.
