# Open-source dubbing pipelines and timing/duration alignment (Kannada talking-head reels to English, cloned voice)

Research date: 2026-10-08. Repo facts (last commit date, licence file, README and config contents) come from shallow `git clone` of each repo's default branch on 2026-10-08. The GitHub REST API was not reachable from this session, so star counts and open-issue counts were not collected. Execution constraint: 4 CPU, 15 GB RAM, no GPU.

## 1. Open-source dubbing toolkits: components, Kannada support, cloning, maintenance, licence, hardware

### Takeaway
Every major toolkit uses the same chain: download, then vocal/background separation (Demucs/UVR), then ASR (faster-whisper/WhisperX), then LLM or MT translation, then TTS or voice cloning, then per-segment speed fitting, then remix. Lip-sync is optional (Wav2Lip). For Kannada as a source language, the strongest maintained options are **pyVideoTrans** (GPL-3.0, Kannada in its language table, active as of 2026-10-07) and **SoniTranslate** (Apache-2.0, Kannada listed, with a Kannada wav2vec2 alignment model mapped, active as of 2026-08-28). VideoLingo's default local ASR does not list Kannada. Most cloning backends (XTTS, F5-TTS, CosyVoice, IndexTTS) only need to speak English here, which suits the KN→EN direction. Their weights often carry non-commercial or custom licences, and all are slow on CPU.

### Cited Findings

**SoniTranslate (R3gm/SoniTranslate)**
- Last commit 2026-08-28. Code is Apache-2.0, but the README warns that "the models or weights may have commercial restrictions, as seen with pyannote diarization". — [GitHub repo](https://github.com/R3gm/SoniTranslate)
- Components credited in the README: WhisperX, faster-whisper, edge-tts, Piper TTS, Coqui XTTS (voice cloning from a short clip), OpenVoice/OpenVoiceV2 and FreeVC (voice imitation), BARK, and OpenAI API for transcription/translation/TTS. Pyannote is used for diarization (needs an HF licence acceptance). — [README](https://github.com/R3gm/SoniTranslate)
- Kannada (`kn`) appears in the README language table. The code maps `"Kannada (kn)": "kn"` and assigns the WhisperX-style alignment model `Harveenchadha/vakyansh-wav2vec2-kannada-knm-560` for `kn`. — [soni_translate/language_configuration.py](https://github.com/R3gm/SoniTranslate/blob/HEAD/soni_translate/language_configuration.py)
- CPU mode exists (`app_rvc.py --cpu_mode`). The README install path otherwise targets CUDA 11.8 and PyTorch 2.5.1. — [README](https://github.com/R3gm/SoniTranslate)
- Timing: GUI slider "max acceleration" defaults to 1.9 (range 1.0–2.5), and the API default is `max_accelerate_audio=2.1`. There are checkboxes for `acceleration_rate_regulation` and `avoid_overlap` (both default False). Speed-up is done with ffmpeg `atempo`. — [app_rvc.py](https://github.com/R3gm/SoniTranslate/blob/HEAD/app_rvc.py); [soni_translate/text_to_speech.py](https://github.com/R3gm/SoniTranslate/blob/HEAD/soni_translate/text_to_speech.py)
- Mix options include "Mixing audio with sidechain compression" (ducking the original under the dub). — [app_rvc.py](https://github.com/R3gm/SoniTranslate/blob/HEAD/app_rvc.py)
- Many HuggingFace Space mirrors of SoniTranslate exist (e.g. Saiteja/SoniTranslate, JonnyTran/SoniTranslate), all unofficial copies. — [HF Space example](https://huggingface.co/spaces/JonnyTran/SoniTranslate/blob/main/soni_translate/languages_gui.py)

**pyVideoTrans (jianchang512/pyvideotrans)**
- Last commit 2026-10-07 (very active). Licence GPL-3.0. — [GitHub repo](https://github.com/jianchang512/pyvideotrans)
- ASR options: faster-whisper (local, recommended), WhisperX/Parakeet (timestamp alignment and diarization), OpenAI Whisper, Qwen, and Azure/Google cloud. LLM translation options: DeepSeek, ChatGPT, Claude, Gemini, Ollama (local) and others. TTS options: Edge-TTS (free), F5-TTS, OmniVoice, Qwen3-TTS (voice cloning), GPT-SoVITS, Index-TTS, ChatTTS, CosyVoice. It also includes a vocal-separation utility. — [README](https://github.com/jianchang512/pyvideotrans)
- Kannada is present in its language dictionary (`'kn': [... 'Kannada' ...]`, ISO-639-3 `kan`). — [videotrans/configure/_languages_dict.py](https://github.com/jianchang512/pyvideotrans/blob/HEAD/videotrans/configure/_languages_dict.py)
- Runs on CPU by default. CUDA 12.8 and cuDNN 9.11 are needed only for NVIDIA acceleration. A CLI exists (`uv run cli.py --task ...`). — [README](https://github.com/jianchang512/pyvideotrans)
- Third-party guide: pyVideoTrans' built-in F5-TTS cloning wants a clean 3–10 s WAV of the target voice, with the exact spoken text after a `#` in the filename. — [localaimaster.com guide](https://localaimaster.com/blog/local-ai-video-dubbing) (secondary source; not verified against the repo docs)

**VideoLingo (Huanshere/VideoLingo)**
- Last commit 2026-10-01. Licence Apache-2.0. — [GitHub repo](https://github.com/Huanshere/VideoLingo)
- Default ASR is now local **Qwen3-ASR + Qwen3-ForcedAligner** (WhisperX is credited). ElevenLabs or MAI-Transcribe-2 are cloud alternatives. Translation uses any OpenAI-compatible LLM returning structured JSON. TTS options: OpenAI, Fish Audio, SiliconFlow Fish/CosyVoice2, GPT-SoVITS, Edge TTS, F5-TTS, and a custom adapter. Demucs vocal separation is used. — [README](https://github.com/Huanshere/VideoLingo); [config.yaml](https://github.com/Huanshere/VideoLingo/blob/HEAD/config.yaml)
- The local Qwen3-ASR language list includes Hindi but no Kannada entry was found. — [core/asr_backend/qwen_asr_local.py](https://github.com/Huanshere/VideoLingo/blob/HEAD/core/asr_backend/qwen_asr_local.py)
- README caveats: "Speed adjustment does not guarantee natural delivery or perfect synchronization", and the dubbing workflow does not assign separate voices per speaker. — [README](https://github.com/Huanshere/VideoLingo)
- The default config burns subtitles into the video (`burn_subtitles: true`). — [config.yaml](https://github.com/Huanshere/VideoLingo/blob/HEAD/config.yaml)
- A third-party comparison says VideoLingo has no built-in voice cloning (GPT-SoVITS is a separate install). — [localaimaster.com](https://localaimaster.com/blog/local-ai-video-dubbing). This is partly contradicted by the README, which lists F5-TTS and CosyVoice2 clone backends: [README](https://github.com/Huanshere/VideoLingo)

**KrillinAI (krillinai/KrillinAI, now branded OpenCreator)**
- Last commit 2026-10-05. Licence Apache-2.0. The project has pivoted into a broad creator suite (thumbnails, image and video generation, articles). "Video Translation" and "Smart Dubbing" remain features. — [GitHub repo](https://github.com/krillinai/KrillinAI)
- ASR runs through cloud or local Whisper (faster-whisper, WhisperKit, whisper.cpp), with LLM-based segmentation and alignment. TTS options are mostly cloud: OpenAI TTS, MiniMax, Edge TTS, Aliyun, Volcengine. The video downloader lists Instagram among supported sites. — [README](https://github.com/krillinai/KrillinAI)

**Linly-Dubbing (Kedreamix/Linly-Dubbing)**
- Last commit 2025-03-05, so it is stale (no commits in about 19 months). Licence Apache-2.0. — [GitHub repo](https://github.com/Kedreamix/Linly-Dubbing)
- Components: Demucs and UVR5 (UVR5 is still a TODO), WhisperX and FunASR, GPT/Qwen LLM translation, and TTS via Edge TTS, XTTS, CosyVoice, GPT-SoVITS. Lip-sync is still unchecked on the roadmap. Requires CUDA 11.8 or 12.1 with PyTorch 2.3.1. — [README](https://github.com/Kedreamix/Linly-Dubbing)

**ViDubb (medahmedkrichen/ViDubb)**
- Last commit 2025-07-23 (low activity). Licence Apache-2.0. — [GitHub repo](https://github.com/medahmedkrichen/ViDubb)
- Components: faster-whisper, pyannote 3.1 diarization, NLTK sentence tokenization, MarianMT or optional Groq `llama3-70b` translation, and `audio_separator` for background. TTS is Coqui **XTTS-v2**, with a SpeechBrain wav2vec2 IEMOCAP emotion classifier whose label is passed to TTS. Lip-sync uses Wav2Lip (GAN). The README claims CPU and GPU compatibility. The README itself says llama3-70b is "not as effective" for non-Latin languages. — [inference.py](https://github.com/medahmedkrichen/ViDubb/blob/HEAD/inference.py); [README](https://github.com/medahmedkrichen/ViDubb)

**open-dubbing (Softcatala/open-dubbing)**
- Last commit 2025-07-08. Licence Apache-2.0. The README describes it as "pure experimental". — [GitHub repo](https://github.com/Softcatala/open-dubbing)
- Components: Demucs, pyannote, faster-whisper or HF transformers (with optional VAD), NLLB-200 (1.3B/3.3B) or Apertium translation, and TTS via Coqui, MMS, Edge, OpenAI or a custom API/CLI. Voices are assigned by detected gender (no voice cloning is advertised). There are `--device cpu` and `--cpu_threads` flags. — [README](https://github.com/Softcatala/open-dubbing); [DOCUMENTATION.md](https://github.com/Softcatala/open-dubbing/blob/main/DOCUMENTATION.md)
- Kannada is listed among supported source languages. — [PyPI open-dubbing](https://pypi.org/project/open-dubbing/0.1.2)
- Useful post-edit design: writes `utterance_metadata_XXX.json` with per-utterance `start`, `end`, `translated_text`, `assigned_voice` and `speed` (example shows `"speed": 1.3`), then `--update` re-renders only the changes. — [README](https://github.com/Softcatala/open-dubbing)

**Voice-Pro (abus-aikorea/voice-pro)**
- The correct repo is `abus-aikorea/voice-pro` (not "abus-aikr"). Last commit 2026-07-13. LICENSE file is GPL-3.0, but the README front-matter says `license: LGPL` (inconsistent). — [GitHub repo](https://github.com/abus-aikorea/voice-pro)
- Components: yt-dlp, Demucs, Whisper/faster-whisper/whisper-timestamped/WhisperX, Deep-Translator, Edge-TTS and kokoro, and F5-TTS/E2-TTS/CosyVoice (incl. Fun-CosyVoice3) cloning. It lists a Hindi F5 model (SPRINGLab/F5-Hindi-24KHz). — [README](https://github.com/abus-aikorea/voice-pro)
- The README says development is paused ("Voice-Pro development and updates are not possible for the time being"). It works "well on Windows with NVIDIA GPU", while Mac/Linux are "not verified". A CPU choice exists via `GPU_CHOICE=C`. — [README](https://github.com/abus-aikorea/voice-pro)

**Newer single-author pipelines (2026)**
- `kadirb4rut/video-dubbing-translator` chains vocal-remover, Whisper, WhisperX word alignment, punctuation segmentation, Google Translate, VoxCPM2 cloning at 48 kHz, an explicit "duration fitting" stage, background remix, and optional LatentSync. The author validated it on an 8 GB M1 CPU and says CPU synthesis is slow and "CUDA has not been validated". — [dev.to write-up](https://dev.to/kadirb4rut/i-built-a-local-first-ai-video-dubbing-pipeline-with-whisperx-voxcpm2-1bek); [repo](https://github.com/kadirb4rut/video-dubbing-translator)
- `Root1V/ai-video-dubbing-pipeline` (EN→ES) uses faster-whisper, pyannote, a local LLM via Ollama/llama.cpp, and IndexTTS-2.5 with native duration control. It says "CPU-only works but is much slower", and each TTS worker needs "roughly 4-6GB for IndexTTS-2.5". — [repo README](https://github.com/Root1V/ai-video-dubbing-pipeline)
- The GitHub topic `video-dubbing` lists about 82 repos. — [GitHub topic](https://github.com/topics/video-dubbing) (count as reported by the search summary; not re-verified)

**Key building blocks**
- WhisperX: last commit 2026-09-26, BSD-2-Clause. Its built-in default alignment models cover `te`, `hi` and `ml` but have **no `kn` entry**, so Kannada needs a custom wav2vec2 model (e.g. the vakyansh one SoniTranslate uses). — [whisperx/alignment.py](https://github.com/m-bain/whisperX/blob/HEAD/whisperx/alignment.py)
- ctc-forced-aligner: last commit 2026-09-07, BSD-2-Clause. Default model `MahmoudAshraf/mms-300m-1130-forced-aligner`. It romanizes with `uroman` (`--romanize`, ISO-639-3 `--language`), and the `--split_size` option takes sentence, word or char. Supports `--device cpu`. — [README](https://github.com/MahmoudAshraf97/ctc-forced-aligner)
- F5-TTS: code MIT, but "pre-trained models are licensed under the CC-BY-NC license" (Emilia data). The CLI has `--speed` and `--fix_duration` ("Fix the total duration (ref and gen audios) in seconds"). — [README](https://github.com/SWivid/F5-TTS); [infer_cli.py](https://github.com/SWivid/F5-TTS/blob/HEAD/src/f5_tts/infer/infer_cli.py)
- IndexTTS: the LICENSE is the custom "bilibili Model Use License Agreement". IndexTTS-2.5 was released 2026-08-10 (ZH/EN/JA/ES/AR) with `duration_factor` 0.5–2.0. — [README](https://github.com/index-tts/index-tts)

### Inferences
- For KN→EN, Kannada support matters only at the **ASR and alignment** stage. TTS only needs good English plus cross-lingual cloning from a Kannada reference clip. So English-capable cloners (F5-TTS, IndexTTS-2/2.5, CosyVoice, XTTS-v2, VoxCPM2) are all candidates, but their cross-lingual timbre carry-over from a Kannada reference is untested here.
- Given no GPU, a lean custom script is likely more practical than installing a full GUI toolkit (VideoLingo, Voice-Pro and Linly assume CUDA). The custom script would borrow VideoLingo's speed/merge logic and pyVideoTrans' gap-extension logic. pyVideoTrans (CPU default, Kannada listed) is the best "off-the-shelf" fallback, but note its GPL-3.0 licence.
- Linly-Dubbing, ViDubb and open-dubbing are effectively unmaintained or experimental in 2026, so use them as code references rather than dependencies.

### Gaps
- Star counts and open-issue counts were not collected (the GitHub API was blocked in this session).
- Whether Linly-Dubbing lists Kannada could not be confirmed: the code grep returned no hits.
- No benchmark found of CPU-only end-to-end runtime for a 30–90 s reel in any of these toolkits.
- XTTS-v2 weights licence (Coqui Public Model License, non-commercial) was not re-verified from a primary page in this session.

## 2. Timing / duration alignment techniques

### Takeaway
Isochrony is controlled at three points: (a) translation verbosity, (b) pause/segment placement (prosodic alignment), and (c) TTS duration. Post-hoc time-stretching is the last resort. Research and toolkits converge on keeping speed-ups modest. VideoLingo's defaults are 1.2x "accept" and 1.4x hard max. Amazon's alignment model penalises any speaking rate above 1.0 and treats ≥2.0 as unintelligible, and it found non-uniform, phoneme-aware stretching preferred over uniform stretching. Practical wins come from using the silence between segments (extend each slot to the next segment's start), merging short lines, LLM-shortening lines that are still too long, and TTS-native duration control (IndexTTS `duration_factor`, F5-TTS `fix_duration`/`speed`).

### Cited Findings

**Research on isochrony and automatic dubbing (mostly Amazon, 2020–2022; older but still the reference work)**
- Federico et al., "From Speech-to-Speech Translation to Automatic Dubbing" (2020). It adds (1) MT that outputs a preferred length, (2) prosodic alignment of the translation to original speech segments, (3) neural TTS with fine-tuned utterance duration, and (4) audio rendering that adds background noise and reverberation extracted from the original. Evaluated on EN→IT TED talks. — [arXiv 2001.06785](https://arxiv.org/abs/2001.06785)
- Effendi et al. (Amazon), "Duration modeling of neural TTS for automatic dubbing": isochrony is controlled via "the verbosity of machine translation, inserting pauses in translations (prosodic alignment), and controlling the duration of TTS utterances". Listening tests fixed speaking rates at {1.1, 1.2, 1.3, 1.4} for fast speech. **Non-isoelastic (phoneme-dependent) stretching was preferred over uniform stretching** for both slow and fast speech, with fast-speech "Wins" gains of +172.8% (en-it) and +82.5% (en-es), all statistically significant. — [Amazon Science PDF](https://cdn.amazon.science/2c/de/191aa8ec423696fcab88f2945f64/duration-modeling-of-neural-tts-for-automatic-dubbing.pdf)
- Virkar et al., "Prosodic Alignment for off-screen automatic dubbing" (Interspeech 2022). Target segments may extend or contract the source interval by fractions of Δ on each side (δ ∈ {0, ±1/4, ±2/4, ±3/4, ±4/4}·Δ), "trad[ing] off strict isochrony for small adjustments to the speaking rate". The speaking-rate score is 1 for r ≤ 1, falls as (2 − r) for 1 < r ≤ 2, and is 0 for r > 2, "since too high speaking rates will result in unintelligible TTS speech". Relaxations improved fluency and smoothness, not segmentation accuracy. For off-screen speech, the whole inter-phrase and inter-sentence gap can be used. — [arXiv 2204.02530](https://arxiv.org/pdf/2204.02530)
- Lakew et al., "Machine Translation Verbosity Control for Automatic Dubbing" (ICASSP 2021). Compared verbosity tokens, fine-tuning and rescoring, and got translations closer to source length. However, **a subjective test found viewers preferred videos dubbed with uncontrolled translations**. — [arXiv 2110.03847](https://arxiv.org/pdf/2110.03847); [Slator summary](https://tech.slator.com/amazon-ai-researchers-explore-length-controlled-mt/)
- Tam et al. (Interspeech 2022), isochrony-aware MT: a single MT model directly emits translations with pause markers, instead of translating then segmenting. — [ISCA PDF](https://www.isca-archive.org/interspeech_2022/tam22_interspeech.pdf)
- Sharma et al. (Amazon), intra-sentential speaking-rate control: phrase-level rate control after full-sentence TTS, using attention-based forced alignment over pause markers. — [Amazon Science PDF](https://cdn.amazon.science/2b/54/3665414b4ef5b3df9be4edeac3af/intra-sentential-speaking-rate-control-in-neural-text-to-speech-for-automatic-dubbing.pdf)
- HOMURA (arXiv 2601.10187, Jan 2026) reports "a systemic cross-lingual verbosity bias" in LLM translation. It introduces the Sand-Glass benchmark with **syllable-level duration budgets** and KL-regularised RL to balance length compliance against meaning. — [arXiv 2601.10187](https://arxiv.org/pdf/2601.10187v1); [papers.cool abstract](https://papers.cool/arxiv/2601.10187) (only the abstract and excerpts were seen; numbers not verified)

**TTS-native duration control**
- IndexTTS2 paper: AR TTS makes duration control hard, "a significant limitation in ... video dubbing". IndexTTS2 has a mode that "explicitly specifies the number of generated tokens to precisely control speech duration" and a free mode. — [arXiv 2506.21619](https://arxiv.org/html/2506.21619v2); [AAAI version](https://ojs.aaai.org/index.php/AAAI/article/view/40820)
- However, the official README says for IndexTTS-2 (2025-09-08) that precise duration control is "not yet enabled in this release". IndexTTS-2.5 (2026-08-10) exposes `duration_factor` (0.5–2.0, >1 slows down, <1 speeds up). IndexTTS-2.5 languages are ZH/EN/JA/ES/AR. — [index-tts README](https://github.com/index-tts/index-tts)
- F5-TTS CLI: `--speed` and `--fix_duration` (total duration of reference plus generated audio, in seconds). — [infer_cli.py](https://github.com/SWivid/F5-TTS/blob/HEAD/src/f5_tts/infer/infer_cli.py)
- Sarvam (Indian-language dubbing vendor, Feb 2026) says post-hoc stretched speech "sounds mechanical" and compressed speech "feels rushed". Its model takes a target duration upfront. Example: a ~2 s English phrase may be ~3 s in Hindi or ~1.5 s in Tamil. — [Sarvam Dub blog](https://www.sarvam.ai/blogs/sarvam-dub) (vendor claim)

**How the toolkits do it (concrete parameters)**
- VideoLingo `config.yaml`: `speed_factor: {min: 1, accept: 1.2, max: 1.4}`; `min_subtitle_duration: 2.5`; `min_trim_duration: 3.5`; `tolerance: 1.5` s ("allowed extension time to the next subtitle"). Its subtitle settings are `max_length: 75` characters and `target_multiplier: 1.2` (translated lines are allowed to be longer). `max_split_length: 20` words: below 18 words "will cut too finely", above 22 is "too long". — [config.yaml](https://github.com/Huanshere/VideoLingo/blob/HEAD/config.yaml)
- VideoLingo logic:
  - It estimates each English line's duration before TTS at 0.225 s per syllable plus pause weights. — [estimate_duration.py](https://github.com/Huanshere/VideoLingo/blob/HEAD/core/tts_backend/estimate_duration.py)
  - If the estimate exceeds the slot, an LLM shortens the line ("cleverly shortening subtitles slightly"), or it falls back to stripping punctuation. — [_8_1_audio_task.py](https://github.com/Huanshere/VideoLingo/blob/HEAD/core/_8_1_audio_task.py); [prompts.py](https://github.com/Huanshere/VideoLingo/blob/HEAD/core/prompts.py)
  - It classifies lines as too fast or too slow against `accept`, and merges a line with up to 2 neighbours when gaps are below `tolerance`. — [_8_2_dub_chunks.py](https://github.com/Huanshere/VideoLingo/blob/HEAD/core/_8_2_dub_chunks.py)
  - It computes a per-chunk speed factor (with a 0.1 s safety margin), applies ffmpeg `atempo`, and lists lines that had to be cut "so they can be shortened by hand". — [_10_gen_audio.py](https://github.com/Huanshere/VideoLingo/blob/HEAD/core/_10_gen_audio.py)
- pyVideoTrans (alignment rewritten 2026-09-23/24): four modes, namely audio speed-up only, video slow-down only, both (each absorbs **half** the overrun), or no change.
  - Defaults are `max_audio_speed_rate: 50` and `max_video_pts_rate: 10` (effectively uncapped).
  - Each subtitle's end is extended to the next subtitle's start, so inter-sentence silence is used before any speed-up.
  - The first segment start is forced to 0.
  - Video is slowed first, then its real duration is measured, then audio is stretched with **pyrubberband** to that exact length. This is needed because ffmpeg PTS slow-down drifts 20–200 ms per segment.
  - The last frame is frozen (`tpad`) if the dub overruns the video.
  — [docs/Synchronize.md](https://github.com/jianchang512/pyvideotrans/blob/HEAD/docs/Synchronize.md); [videotrans/task/_rate.py](https://github.com/jianchang512/pyvideotrans/blob/HEAD/videotrans/task/_rate.py)
- SoniTranslate: max acceleration defaults to 1.9–2.1x via `atempo`, plus optional "acceleration rate regulation" and "avoid overlap". — [app_rvc.py](https://github.com/R3gm/SoniTranslate/blob/HEAD/app_rvc.py)
- ViDubb calls XTTS-v2 with `speed=2` and an emotion label. — [inference.py](https://github.com/medahmedkrichen/ViDubb/blob/HEAD/inference.py)
- Root1V pipeline uses three layers:
  1. IndexTTS-2.5 `duration_factor`, estimated from a chars-per-second heuristic, aimed at "the real gap available until the next one starts".
  2. ffmpeg speed-up "within a range that doesn't distort the voice too much", then uncapped chained `atempo` for the final fit.
  3. A hard trim with ~80 ms fade-out, used only when needed.
  The LLM prompt asks to "favor concise phrasing (similar length to the source)". Consecutive same-speaker segments can be grouped into one TTS call. — [Root1V README](https://github.com/Root1V/ai-video-dubbing-pipeline)

**Time-stretch tools**
- ffmpeg `atempo` accepts tempo 0.5 to 100 in the installed ffmpeg build. Older ffmpeg capped it at 0.5–2.0, which is why scripts chain filters. — Local `ffmpeg -h filter=atempo` output on this box; older limit per [ffmpeg-devel 2018 thread](https://ffmpeg.org/pipermail/ffmpeg-devel/2018-June/230964.html)
- The local ffmpeg build includes the `rubberband` filter. — local `ffmpeg -filters`
- Rubber Band's command-line tool has a crispness setting (0–5, default 4), and version 3's "finer" engine targets higher quality. The developers concede that no time-stretcher is transparent. — [breakfastquay usage](https://breakfastquay.com/rubberband/usage.txt); [Rubber Band "why"](https://breakfastquay.com/rubberband/why.html)
- A 2018 anecdote found rubberband output had "echo artifacts... robotic" (older version, settings unknown). — [ffmpeg-devel](https://ffmpeg.org/pipermail/ffmpeg-devel/2018-June/230958.html)

**Word-level alignment for Kannada**
- WhisperX has no default Kannada align model. — [alignment.py](https://github.com/m-bain/whisperX/blob/HEAD/whisperx/alignment.py)
- SoniTranslate pairs `kn` with `Harveenchadha/vakyansh-wav2vec2-kannada-knm-560`. — [language_configuration.py](https://github.com/R3gm/SoniTranslate/blob/HEAD/soni_translate/language_configuration.py)
- ctc-forced-aligner uses the MMS-1130 aligner with uroman romanization (`--language` ISO-639-3, `--romanize`). Kannada (`kan`) is not explicitly listed in the README. — [README](https://github.com/MahmoudAshraf97/ctc-forced-aligner)
- The CoreML port of the MMS forced aligner is described as CC-BY-NC-4.0. — [HF chordai/mms-fa-aligner-coreml](https://huggingface.co/chordai/mms-fa-aligner-coreml)
- PyTorch's MMS forced-alignment tutorial covers the multilingual uroman route. — [torchaudio tutorial](https://pytorch.org/audio/2.1/tutorials/forced_alignment_for_multilingual_data_tutorial.html)

### Inferences
- A defensible default for talking-head reels is:
  - Set each English segment's budget to the source slot plus the following silence (pyVideoTrans "end = next start", VideoLingo tolerance ≤1.5 s).
  - Estimate English duration at ~0.22 s per syllable before TTS. Ask the LLM translator for a syllable budget per line (HOMURA/Sand-Glass framing).
  - Re-prompt to shorten if the estimate is more than 1.2x over the slot.
  - Use TTS-native rate control first, then a rubberband or atempo stretch capped around 1.2x (VideoLingo `accept`) and never above ~1.4x.
  - Only after that, trim with a fade or extend the last frame.
- Because Kannada is often more syllable-dense than English, English output may frequently be **shorter** than the slot. Slowing or padding (inserting pauses at phrase boundaries, `speed_factor.min: 1` = never slow down audio) may matter as much as speed-up. This is unverified for KN→EN specifically.
- Avoid pyVideoTrans' "video slow-down" mode on talking heads: slowed face and mouth motion is visible. It suits B-roll better.
- Lakew's finding (viewers preferred uncontrolled translations) argues for soft length constraints plus a check that meaning is preserved, not aggressive compression.

### Gaps
- No peer-reviewed number was found for the "≤1.2–1.3x sounds natural" rule. The available evidence is VideoLingo's 1.2/1.4 defaults and Amazon's tests at 1.1–1.4 (relative preference only, no absolute naturalness cut-off).
- The seconds-to-tokens conversion for IndexTTS2's fixed-duration mode was not verified, and the official README says it was not enabled in the IndexTTS-2 release.
- No study found specifically on KN→EN length ratios (syllables or seconds).
- ctc-forced-aligner and MMS quality on Kannada was not tested or confirmed in any source found.
- Montreal Forced Aligner Kannada models were not researched (tool budget).

## 3. Audio mixing: background re-add, loudness, room/reverb matching, EQ

### Takeaway
Standard practice is to separate vocals with Demucs/UVR, then build the background as **mix minus vocals** (not a sum of stems), duck it under the new voice (sidechain), and add the original room's reverb to the dry TTS. Amazon's dubbing pipeline estimated reverberation time (RT) and convolved a synthetic RIR. Normalise to about −14 LUFS integrated with ≤ −1 dBTP for Reels, but that target is a community convention, not a published Meta spec. Note that ffmpeg `loudnorm` defaults to −24 LUFS / −2 dBTP / LRA 7, so the targets must be set explicitly.

### Cited Findings
- Federico et al. add "background noise and reverberation extracted from the original audio" to the TTS output. — [arXiv 2001.06785](https://arxiv.org/abs/2001.06785)
- In that line of work, the RIR was not estimated directly (an ill-posed problem). They blindly estimated reverberation time, generated a synthetic RIR, and convolved it with the dubbed audio. — [arXiv 2001.06785 PDF](https://arxiv.org/pdf/2001.06785) (via search summary; detail not re-read in full)
- Newer research estimates an RIR from reverberant speech and text (Gencho, 2026) and argues explicit RIRs are reusable filters. — [arXiv 2602.09233](https://arxiv.org/pdf/2602.09233)
- Commercial ADR-matching tools learn an IR or EQ profile from reference dialogue and apply it to dry dialogue: Supertone Air, iZotope Dialogue Match, Waves Atlas Reverb. — [Supertone Air](https://www.supertone.ai/en/air); [iZotope Dialogue Match listing](https://www.hhb.co.uk/?p=9059)
- Film practice: a common mistake is using an IR from the wrong kind of space, and EQ matching should be subtle. — [Enhanced Media blog](https://enhanced.media/blog/2020/7/28/how-to-create-realistic-reverb-for-your-films)
- Demucs on CPU:
  - One benchmark took 187.8 s on CPU vs 15.6 s on an RTX 3060 Ti for a 6:24 track. — [LinuxLinks](https://www.linuxlinks.com/machine-learning-linux-demucs-music-source-separation/2/)
  - `htdemucs` takes ~90 s and `htdemucs_ft` ~120 s on CPU for a 4-min song, and htdemucs_ft needs 8 GB+ RAM. — [stemsplit vendor blog](https://stemsplit.io/blog/spleeter-vs-demucs)
  - An ONNX single-file htdemucs runs on CPU without PyTorch. — [HF adowu/htdemucs-onnx](https://huggingface.co/adowu/htdemucs-onnx)
- One dubbing-oriented Demucs checkpoint takes the background as mix-minus-vocals. It reports the background stays within 0.1 dB of the original, vs 8.5 dB down when summing stems (project's own claim). — [HF blaze-voice-ai/dubbing-demucs](https://huggingface.co/blaze-voice-ai/dubbing-demucs)
- VideoLingo notes its raw-audio sample rate also caps the Demucs vocals and the voice-clone reference bandwidth ("16000 caps them near 7 kHz"). Its default is 32 kHz / 128k. — [config.yaml](https://github.com/Huanshere/VideoLingo/blob/HEAD/config.yaml)
- SoniTranslate offers "Mixing audio with sidechain compression". — [app_rvc.py](https://github.com/R3gm/SoniTranslate/blob/HEAD/app_rvc.py)
- Loudness:
  - Commonly cited Reels target is −14 LUFS / −1 dBTP. OpenClip says Instagram/TikTok "don't publish exact specs" and recommends −14 to −16 LUFS. — [OpenClip](https://openclip.app/learn/audio-normalization); [Opus.pro](https://opus.pro/blog/best-loudness-normalizers)
  - The browser-use/video-use project hard-codes −14 LUFS / −1 dBTP / LRA 11 for social. — [instagit summary](https://instagit.com/browser-use/video-use/loudness-normalization-targets-video-use.md) (auto-generated write-up)
  - ffmpeg `loudnorm` defaults: I = −24, TP = −2, LRA = 7. — local `ffmpeg -h filter=loudnorm`

### Inferences
- For a phone-recorded talking-head reel, a CPU-cheap chain:
  1. `demucs --two-stems vocals` (htdemucs, or ONNX).
  2. Background = original minus vocals.
  3. Dry TTS, then a light EQ match to the original vocal stem, then a short convolution reverb or synthetic RIR (ffmpeg `afir`, available locally) sized to the estimated RT.
  4. Mix with the background ducked under the voice (sidechaincompress).
  5. Two-pass `loudnorm` I=−14 TP=−1.
  The room-tone bed should come from the separated background so pauses aren't dead silent.
- Using the original Kannada vocal stem as the clone reference also transfers its room colour into some cloners (F5/IndexTTS reproduce reference acoustics). This may reduce the need for reverb matching but also imports noise. This is untested here.

### Gaps
- No official Meta/Instagram loudness specification was found.
- No open-source, CPU-friendly blind RT60/RIR estimator was identified and verified in this pass.
- No practitioner A/B evidence was found on reverb matching for AI dubs specifically.

## 4. Practitioner workflow for Indian-language content and common pitfalls

### Takeaway
No substantive Reddit threads were surfaced by search (results were dominated by vendor blogs and GitHub). Practitioner-style guidance from repos and dev write-ups is consistent: treat duration fitting as its own stage, fix length in the text before synthesis, keep a human edit pass on translated text and timings (open-dubbing JSON, VideoLingo's pause-after-translate), use a clean, natural-pace reference clip, and expect accent, emotion and identity drift in cross-lingual cloning.

### Cited Findings
- "A translated sentence rarely has the same duration as the source sentence", which is why one developer made duration fitting its own stage instead of hoping the synthesizer matches. — [dev.to kadirb4rut](https://dev.to/kadirb4rut/i-built-a-local-first-ai-video-dubbing-pipeline-with-whisperx-voxcpm2-1bek)
- VideoLingo supports `pause_after_translate` to hand-edit the Translation column before dubbing, and lists lines whose dubbing was cut so they can be shortened by hand. — [config.yaml](https://github.com/Huanshere/VideoLingo/blob/HEAD/config.yaml); [_10_gen_audio.py](https://github.com/Huanshere/VideoLingo/blob/HEAD/core/_10_gen_audio.py)
- open-dubbing's editable `utterance_metadata` JSON (text, voice, speed) plus `--update` re-render is designed for post-editing. — [README](https://github.com/Softcatala/open-dubbing)
- VideoLingo caveat: background noise and language-specific alignment models affect word timestamps, vocal separation may help, and numbers or symbols may lack reliable word timings. Mixed-language speech (code-mixing) is "not guaranteed" to keep accurate text and timing. — [README](https://github.com/Huanshere/VideoLingo)
- Sarvam (vendor, Feb 2026) lists Indian-content pitfalls:
  - time-stretch artefacts
  - identity drift across languages
  - code-mixing of languages and scripts within sentences
  - names, places and brands needing correct pronunciation
  - technical terms
  It measures speaker similarity with ECAPA-TDNN cosine similarity. — [Sarvam Dub blog](https://www.sarvam.ai/blogs/sarvam-dub)
- Vendor guidance (Captions/ElevenLabs-style help pages):
  - The clone reproduces the reference's cadence, so slow, flat reference speech gives slow, flat dubs.
  - Generate per segment, edit the script length before voicing, then fine-align in a timeline.
  - Robotic output often comes from timing mismatch and lost delivery.
  — [captions.ai voice clone help](https://captions.ai/help/guides/advanced/voice-clone); [sync.so blog](https://sync.so/blog/why-does-ai-dubbing-sound-robotic) (vendor content)
- Emotion: ViDubb classifies the source segment's emotion (SpeechBrain IEMOCAP: neutral/angry/happy/sad) and passes it to TTS. — [inference.py](https://github.com/medahmedkrichen/ViDubb/blob/HEAD/inference.py)
- IndexTTS-2/2.5 separate timbre from emotion, so an emotion reference or vector can be given independently of the voice reference. — [index-tts README](https://github.com/index-tts/index-tts)
- Burned-in subtitles: VideoLingo burns subtitles by default (`burn_subtitles: true`). If the source reel already has burned-in Kannada captions, the dubbed video will show them unless they are masked or cropped. No toolkit found removes burned-in text automatically. — [config.yaml](https://github.com/Huanshere/VideoLingo/blob/HEAD/config.yaml)

### Inferences
- Recommended pipeline for this project (synthesised from the above, CPU-only):
  1. Download (owner-authorised).
  2. Demucs two-stem separation.
  3. Kannada ASR, then a human check of the transcript.
  4. Word alignment (custom Kannada wav2vec2 or MMS).
  5. LLM translation with per-line syllable budgets, then a human check.
  6. Duration estimation, with re-shortening and segment merging.
  7. Cloned English TTS from a 5–10 s clean Kannada reference (pick a lively, natural-pace segment).
  8. Rate fitting (TTS-native first, stretch ≤1.2–1.4x).
  9. Reverb/EQ match, then remix with ducking, then loudness −14 LUFS.
  10. Mux, optionally adding English captions (after checking for existing burned-in Kannada captions).
- Cross-lingual cloning from Kannada into English risks accent carry-over (a Kannada-accented English voice), which may be desirable for authenticity. That needs a listening test per voice model.

### Gaps
- No Reddit or YouTube-creator first-hand threads about KN→EN (or any Indian→English) cloned dubbing were found. Search results were vendor-dominated. This remains unverified community knowledge.
- No source found on lip-sync value for short KN→EN talking-head reels on CPU. Wav2Lip and LatentSync are GPU-oriented, and lip-sync is out of scope for CPU in practice. This is an inference only.

## 5. Downloading Instagram reels in 2026 (yt-dlp / instaloader) and rights

### Takeaway
yt-dlp (latest on PyPI: 2026.8.19) still has an Instagram extractor, but in mid-2026 reels intermittently fail with "empty media response". Newer builds attempt browser impersonation, which needs `curl_cffi`. Login cookies (`--cookies-from-browser`/`--cookies`) are the documented fallback. Instaloader (latest 4.15.3) works but is heavily rate-limited for anonymous use, especially from cloud IPs, and its docs say logged-in access seems unaffected. Since the user owns or has permission for the account, the cleanest path is often to export the original file from Instagram or the creator's own device.

### Cited Findings
- yt-dlp latest PyPI release 2026.8.19. instaloader latest 4.15.3. — [PyPI yt-dlp](https://pypi.org/project/yt-dlp/); [PyPI instaloader](https://pypi.org/project/instaloader/) (checked via `pip index versions` on 2026-10-08)
- Reported in Seal issue #2566, opened 2026-06-29:
  - yt-dlp stable 2026.06.09 failed on a reel with "No csrf token set by Instagram API" and "Instagram sent an empty media response. Check if this post is accessible in your browser without being logged-in".
  - Nightly 2026.06.28 failed with "The extractor is attempting impersonation, but no impersonate target is available" (curl_cffi missing).
  - The issue was closed as duplicate without a maintainer explanation.
  — [Seal issue #2566](https://github.com/JunkFood02/Seal/issues/2566)
- A 2026 guide says Instagram "almost always" requires a logged-in session for yt-dlp, so pass browser cookies. — [techearl guide](https://techearl.com/download-instagram-reel) (secondary)
- Instaloader troubleshooting says cloud, VPN and proxy IPs "might be subject to significantly stricter limits for anonymous access", while logged-in access (`--login`) does "not seem to be affected". "Too many queries" is a warning, not an error. — [Instaloader troubleshooting (mirror)](https://git.sudo.is/mirrors/Instaloader/src/branch/master/docs/troubleshooting.rst)
- Third-party claim: anonymous access is throttled to roughly 1–2 requests per 30 s, producing 401 "please wait". — [kitemetric blog](https://kitemetric.com/blogs/troubleshooting-instagram-scraping-with-instaloader) (unverified)
- KrillinAI/OpenCreator's built-in downloader lists Instagram among supported sites for public videos. — [README](https://github.com/krillinai/KrillinAI)
- Consent: vendors stress explicit permission before cloning a voice. Sarvam's cloning is "live recording only, with explicit consent". — [lingopal blog](https://lingopal.ai/blog/ai-voice-cloning-for-documentary-dubbing-preserve-the-narrator-s-voice); [Sarvam Content Studio](https://www.sarvam.ai/products/content-studio)

### Inferences
- On this server (a cloud IP), anonymous Instagram fetches are likely to be throttled or blocked. The most reliable inputs are: the original MP4 provided by the account owner; Instagram's own "Download your information" export; or yt-dlp with the owner's cookies plus `pip install "yt-dlp[default,curl-cffi]"` for impersonation. The extras name is from general knowledge of yt-dlp packaging, so verify it against the yt-dlp README.
- Downloaded reels are already re-encoded (AAC) and may contain music licensed only for in-app use. Re-uploading a dub with the separated background music could trigger copyright matching, so consider replacing the music bed.

### Gaps
- Instagram Terms of Use text on automated collection could not be retrieved (help page rendered empty), so it is not quoted here.
- No official yt-dlp changelog entry confirming the state of the Instagram extractor as of October 2026 was verified.
