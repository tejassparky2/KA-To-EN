# Make Mom's Kannada Reels Speak Indian English

The best approach in October 2026 runs on two tracks. **First, try Meta's own free "Translate voices with Meta AI" inside Instagram.** Kannada was added on 16 Jan 2026, the feature mimics the creator's voice, and lip-sync is an optional toggle. It is also the only option that needs zero engineering. Its limits are real, though: Meta never explicitly states that Kannada→English works, it handles one speaker only, and you cannot edit the translated text. **Second, for a result you control, build an API-first pipeline orchestrated from our CPU-only box.** The steps are:

1. Separate the music on the CPU.
2. Transcribe with Sarvam's `saaras` ASR. Its v3 model scored 8.8% WER on the only independent Kannada benchmark, best in the field.
3. Have a bilingual family member check the transcript.
4. Translate with a frontier LLM. Give each line a syllable budget and ask for an Indian-English register.
5. Voice the English with a clone that is *allowed to keep her accent*: ElevenLabs Multilingual v2 or Sarvam's cross-lingual clone with `en-IN` output. Avoid Eleven v4, which deliberately strips a cross-language reference accent.
6. Fit durations to the original slots, remix under the original music, and finish with hosted lip-sync: LatentSync at about $0.30 per reel, or Sync lipsync-2-pro at about $4–5 for difficult shots.

ASR, translation and separation together cost cents per minute-long reel. Lip-sync dominates the bill, and voice-cloning prices still need checking. The biggest open question is that no source has measured whether any clone produces *natural Indian English* from a Kannada reference. So a blind listening test, not vendor claims, should pick the voice engine. The strongest single lever is having her record 1–2 minutes of English in her natural accent. Nothing should be cloned without her explicit, recorded consent. ElevenLabs' Professional Voice Clone in particular can only be created by her, on her own account.

## Meta's free in-app translator is the first test, not the final answer

Meta AI translations for Reels launched in October 2025 for English, Spanish, Hindi and Portuguese. On **16 Jan 2026** Meta said translations were "starting to roll out in more languages, including Bengali, Tamil, Telugu, Marathi, and Kannada" on Instagram and Facebook. Meta states that the feature "mimics the sound and tone of a creator's voice," that creators can "choose to enable the lip syncing feature," and that it is **free for all public Instagram accounts in countries where Meta AI is available** ([Meta Newsroom](https://about.fb.com/news/2025/10/discover-reels-around-world-meta-ai-translation/)). One news outlet reported a 1,000-follower or professional-account requirement for Instagram ([Social Media Today](https://www.socialmediatoday.com/news/meta-adds-more-languages-to-ai-translations-for-reels/810019/)). Meta's own wording is more authoritative. The direction is the catch. The original four languages were explicitly "to and from English," and Meta described the Indic expansion as "the same capability" ([Meta Newsroom, Nov 2025](https://about.fb.com/news/2025/11/instagram-empowers-creators-to-go-global-with-local-voice-translations-and-fonts/)). That implies Kannada→English works, but no Meta page found says so explicitly, so it stays **unverified until someone checks in the app**.

Meta's creator guidance limits the feature further. **"Currently only reels with one speaker can be translated."** Creators can preview the result and then approve or discard it. Meta advises speaking facing the camera with the mouth uncovered and keeping background noise and music low ([Instagram Creators blog](https://creators.instagram.com/blog/meta-ai-translations)). No Meta page describes editing the transcript or translation. A mistranslated Kannada idiom or family name therefore cannot be fixed, only discarded. The feature must also be switched on from *her* account, and the translated version is served to viewers inside Instagram rather than handed back as a file. That makes Meta the right free baseline, and the right control condition in the A/B test below. It does not suit a workflow where someone wants to polish the English.

Among third-party all-in-one services, only a handful have primary-source evidence of **Kannada as a source language with English output**. The comparison below is the shortlist. Each row needs a test clip, because a language appearing on a list says nothing about how well the service handles colloquial, code-mixed Kannada.

| Service | Kannada-source evidence | Voice clone | Lip-sync | Edit English before render | Price signal | Status |
|---|---|---|---|---|---|---|
| Meta AI (Instagram) | Kannada added 16 Jan 2026; KN→EN implied ([Meta](https://about.fb.com/news/2025/10/discover-reels-around-world-meta-ai-translation/)) | Yes | Optional | No (approve/discard only) | Free | Direction unverified |
| ElevenLabs Dubbing v2 | `kn` listed in v2 and v1 tables ([docs](https://elevenlabs.io/docs/capabilities/dubbing)) | Yes; "cloning strength" 0–10 | **None** | Studio v1 only (maintenance mode); API edits Enterprise-only | 3,000 credits/min without watermark | Verified |
| HeyGen | "Kannada (India)" listed; source vs target role not stated ([help](https://help.heygen.com/en/articles/11391941-video-translation-languages-we-support)) | Yes | Yes | Pro ($49/mo) | Free: 3 videos/mo, 1 min, watermark; Creator $29/mo ([pricing](https://www.heygen.com/pricing)) | Partly verified |
| Rask AI | "Kannada Video Translator" under "into English" ([Rask](https://www.rask.ai/tools/video-translator)) | 32 languages | Yes | Line-by-line | 7-day trial; prices conflict | Likely |
| VEED | Kannada #42 on detectable source list, 19 Aug 2026 ([VEED](https://support.veed.io/en/articles/12781545-supported-languages-for-dubbing)) | Not stated | Optional | Not checked | Not checked | Source verified |
| BlipCut | Kannada on source, target and cloning lists ([BlipCut](https://videotranslator.blipcut.com/support/supported-languages.html)) | Yes | Advertised | Not checked | Not checked | Source verified |
| YouTube auto-dub | **Kannada absent** from to-English list ([YouTube Help](https://support.google.com/youtube/answer/15569972?hl=en)) | — | Pilot only | No | Free | Excluded |
| Captions/Mirage | Not listed ([Mirage help](https://help.mirage.app/docs/captions/dubbing)) | — | — | — | — | Excluded |
| Sarvam Dubbing | Any source, but **Indian-language targets only** ([Sarvam docs](https://docs.sarvam.ai/api/api-guides-tutorials/dubbing/overview.md)) | Yes | Not mentioned | Yes | ₹40/min | Excluded (no English) |

ElevenLabs is the best-documented Kannada-source dubber, but two details matter for this project. Its dubs are **audio-only**, so lip-sync is a separate step. Its English targets are en-US, en-GB, en-AU and en-CA, with **no en-IN** ([ElevenLabs docs](https://elevenlabs.io/docs/capabilities/dubbing)). Synthesia's help centre, which uses ElevenLabs cloning, warns that instant clones "cannot always preserve the accent of non-native English speakers" because ElevenLabs "only has English accent data for US, UK, Australian, and Canadian English" ([Synthesia Help](https://help.synthesia.io/en/articles/9770805-why-is-my-accent-not-being-captured-in-my-voice-clone)). This is the clearest documented mechanism behind the "Indian mom suddenly sounds American" failure the user wants to avoid. Sync.so offers a combined flow in which ElevenLabs produces the translated voice and Sync lip-syncs it ([sync.so](https://sync.so/blog/introducing-ai-dubbing-in-sync)), a reasonable mid-effort option. No Kannada-specific quality review of any service turned up on Reddit, G2 or Trustpilot.

## Sarvam ASR and an LLM translator solve the language half for pennies

The one recent independent Kannada head-to-head is JoshTalks' "Voice of India" benchmark (Aug 2026). It uses 24.9 hours of unscripted Kannada telephone speech from 320 speakers. Kannada WER, using the benchmark's orthographically-informed scoring that accepts valid spelling variants, came out as follows: **Sarvam Saaras v3 8.8%**, Amazon Transcribe 11.1%, ElevenLabs Scribe v2 and Gemini 3 Pro 14.0%, AI4Bharat IndicConformer 16.3%, Meta OmniASR-LLM-7B 35.0%, and Deepgram Nova-3 51.1% ([JoshTalks](https://elevenlabsreport.ai.joshtalks.com/)). Two caveats apply. The audio is telephonic conversation, not music-backed reels. And the report's hostname ("elevenlabsreport") hints at ElevenLabs involvement, though ElevenLabs did not win. Vendor figures, such as ElevenLabs' 4.0% Kannada result on the FLEURS benchmark, are far rosier and should be discounted ([ElevenLabs](https://elevenlabs.io/speech-to-text/kannada)). Vanilla Whisper large-v3 scored 37.5% on that same vendor table and should not be used for Kannada.

Sarvam's current default model is **`saaras:v4`**. v3 remains available, and v4 has no published benchmark. Settings for our use are `language_code="kn-IN"`, a `codemix` mode that keeps her English words in Latin script, and a `translate` mode that outputs English directly. The STT reference ties `mode` to v3, so test whether v4 honours it. Timestamps are **phrase-level only, with no word-level timing**, and the REST endpoint targets clips under 30 s. A 60–90 s reel therefore needs either cutting at silences or the Batch API. The price is **₹30 per hour** of audio ([Sarvam STT reference](https://docs.sarvam.ai/api-reference-docs/speech-to-text/transcribe); [Saaras model page](https://docs.sarvam.ai/api-reference-docs/models/saaras); [Sarvam pricing](https://docs.sarvam.ai/api-reference-docs/pricing)). Phrase-level segments are the natural unit for dubbing anyway. Two options cover the cases that need word timing, such as captions or a tight check on where pauses fall. ElevenLabs Scribe v2 gives word timestamps and audio-event tags at **$0.22/h** ([ElevenLabs pricing](https://elevenlabs.io/pricing/api)). Google's `gemini-3.5-transcribe` gives word timestamps for about $0.005/min, but Google warns that timestamps "degrade transcription accuracy" ([Gemini docs](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-transcribe)). For self-hosted alignment, note that WhisperX ships no Kannada alignment model. SoniTranslate maps Kannada to `Harveenchadha/vakyansh-wav2vec2-kannada-knm-560` ([SoniTranslate config](https://github.com/R3gm/SoniTranslate/blob/HEAD/soni_translate/language_configuration.py)).

Translation is less of a bottleneck than it looks. On the IndicTrans2 paper's benchmarks, Kannada→English from IndicTrans2, Google, Azure and NLLB-54B lands within about 2 points of each other on chrF++, a character-overlap score where higher is better. The conversational test set (IN22-Conv) gives roughly **46–48** for all of them. The distilled 200M IndicTrans2 model (**48.3**) matches its 1B parent ([IndicTrans2 paper](https://arxiv.org/pdf/2305.16307)), and it runs on CPU via CTranslate2. Dubbing, however, needs things benchmarks do not score: a warm, conversational Indian-English register; her own English words kept as spoken; and lines that fit a time slot. That argues for a **frontier LLM translator** given the whole reel transcript and asked for per-segment JSON. This is an inference. **No published benchmark covers Kannada→English for current Claude, GPT or Gemini models.** The only LLM data point is GPT-3.5 in 2023, which trailed IndicTrans2 by 5–12 points. Gemini's `gemini-3.8-flash` is a verified, cheap option at $0.75/$3.75 per million input/output tokens until 31 Dec 2026 ([Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)). Claude and GPT model IDs were not verified in this research. Sarvam's `mayura:v1`, in `modern-colloquial` mode with `speaker_gender="Female"`, makes a cheap cross-check at ₹20 per 10K characters ([Sarvam translate API](https://docs.sarvam.ai/api-reference-docs/text/translate-text)). One Kannada-speaking reviewer found Sarvam's older translation model literal and unnatural ([Thejesh GN](https://thejeshgn.com/2025/06/10/first-impressions-of-sarvam-indic-translate-model/)).

Length control needs a loop, not just an instruction. The HOMURA preprint documents a "systemic cross-lingual verbosity bias" in LLM translation and uses **syllable budgets** as the cross-language unit ([arXiv 2601.10187](https://arxiv.org/pdf/2601.10187v1)). An EMNLP 2025 system that predicts a phoneme budget from source duration, then iteratively shortens or lengthens, reports up to **24% better speech overlap** with competitive translation quality ([ACL Anthology](https://aclanthology.org/2025.emnlp-demos.37)). A counterweight: Amazon researchers found that viewers *preferred* dubs made from uncontrolled translations over length-forced ones ([arXiv 2110.03847](https://arxiv.org/pdf/2110.03847)). Budgets should therefore be soft, and meaning should win ties. Kannada is agglutinative, so English drafts may often come out *shorter* than the slot. In that case, pause placement matters as much as speeding up. This KN→EN length behaviour is a hypothesis; no study measured it.

## Accent survives only if the voice model is allowed to "leak" it

The research literature and vendor docs treat "accent leakage" as a defect: a reference speaker's native accent bleeding into the target language. **For this project it is the goal.** Models and settings built to suppress leakage push her toward generic native-sounding, probably American, English. Models that keep the reference accent push toward Kannada-flavoured Indian English.

ElevenLabs shows the split most clearly. **Eleven v4 deliberately drops the reference accent when the output language differs.** Its docs give the example of a Korean speaker's clone producing natural English rather than Korean-accented English. When the reference and output languages *match*, v4 keeps the accent ([Eleven v4 docs](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4)). **Multilingual v2 is the only ElevenLabs model whose description says it "keeps the speaker's unique characteristics and accent across languages"** ([ElevenLabs models](https://elevenlabs.io/docs/overview/models)). ElevenLabs' help centre adds that "the accent and pronunciation is determined by the voice itself" ([ElevenLabs help](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/can-i-use-the-same-cloned-designed-voice-across-languages)). Kannada is not a listed language for Multilingual v2, but that does not matter, because the model only has to *speak English*. ElevenLabs says a clone can be made from audio in an unsupported language and may still capture tone ([ElevenLabs voice cloning](https://elevenlabs.io/voice-cloning)). Eleven v3's cross-language accent behaviour is undocumented.

Combining these facts yields the most important practical lever. **If she can record even 1–2 minutes of English in her normal accent, a v4 clone from that English sample should keep her Indian-English accent**, because reference and output now match. Without that, use Multilingual v2 from Kannada audio. MiniMax Speech 2.6's "Fluent LoRA" explicitly smooths accented, non-native recordings into "fluent, natural speech," which is the wrong direction here ([MiniMax](https://www.minimax.io/news/minimax-speech-26)).

Sarvam is the most "Indian by design" commercial candidate. Its Voice Cloning API (`/voices/create`, `/voices/clone`) takes a **10–15 s reference**, states that "the reference clip's language doesn't have to match the output language," supports `en-IN` ("English, Indian accent") output, and runs a built-in transcribe-and-retry quality check ([Sarvam Voice Cloning](https://docs.sarvam.ai/api/api-guides-tutorials/voice-cloning/overview); [Sarvam TTS reference](https://docs.sarvam.ai/api-reference-docs/text-to-speech/convert)). Its cross-lingual guide (checked 8 Oct 2026) says a speaker with a regional accent "will retain a hint of that accent in the cloned output", calls this "usually desirable", and recommends references closer to 15 s than 10 s for cross-lingual use ([Sarvam: Clone across languages](https://docs.sarvam.ai/api/api-guides-tutorials/voice-cloning/how-to/clone-across-languages)). The generate endpoint also takes `max_audio_duration`, which time-stretches output to fit a slot, which is useful for dubbing ([Sarvam Generate Speech reference](https://docs.sarvam.ai/api-reference/voice-cloning/clone)). How strong the accent hint is for a Kannada reference has not been measured, and its per-character price was not retrieved. An Aug 2026 third-party blog claims Bulbul v3 has no self-serve cloning, contradicting Sarvam's docs ([invideo](https://invideo.io/blog/sarvam-bulbul-indian-tts/)). Cartesia says its clones preserve "speaking style, accent, and emotion" but gives no switch to control it. PlayHT shut down entirely on 31 Dec 2025 ([texttolab](https://texttolab.com/blog/play-ht-shutdown-alternatives)).

The **voice-conversion route** gives the most control over accent and timing. Voice conversion keeps the source performance's rhythm, emotion and accent and swaps only the timbre. A source of Indian-accented English goes in and comes out in her timbre. That source can be a female relative reading the English script to the reel's timing, or a Sarvam `en-IN` TTS voice. ElevenLabs Voice Changer (`eleven_multilingual_sts_v2`) preserves "whispers, laughs, cries, accents" and can target any cloned voice ([ElevenLabs Voice Changer](https://elevenlabs.io/docs/capabilities/voice-changer)). Open-source alternatives:

- **Seed-VC** works zero-shot from a 1–30 s reference. Its V2 `--convert-style` flag performs accent conversion and must stay **off** here. It is GPL-3.0, and the repo is now archived ([Seed-VC](https://github.com/Plachtaa/seed-vc)).
- **RVC** needs about 10–30 minutes of her clean speech to train ([Applio docs](https://mintlify.wiki/IAHispano/Applio/features/training)).

No head-to-head comparison of these on Indian speech exists.

Open-source cloners are viable only on a GPU, and their licences are uneven:

- **Chatterbox Multilingual V3** (MIT, watermarked output) supports Hindi and English but not Kannada. Its model card states that a mismatched reference makes output "inherit the accent of the reference clip's language," and that `cfg_weight=0` removes it. **Leave it at the default to keep her accent** ([Chatterbox](https://huggingface.co/ResembleAI/chatterbox)).
- **F5-TTS** weights are CC-BY-NC.
- **XTTS-v2** is non-commercial, and its licence can no longer be bought.
- **IndexTTS-2.5** is the only open model with usable duration control (`duration_factor` 0.5–2.0), but it carries a bilibili licence and needs about 6 GB of VRAM ([IndexTTS](https://github.com/index-tts/index-tts)).
- **Qwen3-TTS** (Apache-2.0) does cross-lingual cloning ([arXiv 2601.15621](https://arxiv.org/html/2601.15621)).
- **Indic Parler-TTS** officially speaks Indian English but cannot clone from reference audio ([HF](https://huggingface.co/ai4bharat/indic-parler-tts)). That makes it a good *source* voice for the conversion route.

A Sept 2026 paper confirms that cross-lingual guidance strength trades speaker similarity against accent nativeness along a single curve ([arXiv 2609.29123](https://arxiv.org/abs/2609.29123)). That is the theoretical reason to keep guidance close to the reference. One honest caution: raw leakage from Kannada into a European-trained English model may sound "foreign" rather than *Indian-English*. Voices trained on Indian English, such as Sarvam's or Indic Parler's, could sound more natural. Only listening will tell.

## The CPU box can separate, time and mix, but lip-sync needs a GPU or an API

**Music separation runs fine locally.** The MIT-licensed `audio-separator` package installs CPU-only (`pip install "audio-separator[cpu]"`) and wraps BS-RoFormer vocal models such as `model_bs_roformer_ep_317_sdr_12.9755.ckpt`, rated about 12.9 dB on SDR, the standard separation-quality score where higher is better ([python-audio-separator](https://github.com/nomadkaraoke/python-audio-separator)). Demucs v4 scores 9.0 dB and runs at **about 1.5× the track's duration on CPU**, so roughly 90 s for a 60 s reel ([Demucs](https://github.com/adefossez/demucs)). RoFormer CPU timing is unbenchmarked, so time a 30 s clip first. Build the music bed as **original minus vocals** rather than a sum of stems. One dubbing-tuned Demucs project claims this keeps the background within 0.1 dB of the original ([blaze-voice-ai](https://huggingface.co/blaze-voice-ai/dubbing-demucs)). Instagram audio is AAC-compressed, so expect some bleed between stems. If a reel uses trending licensed music, consider replacing the bed instead of re-uploading separated audio.

**Timing has well-tested defaults.**

- **Use the silence first.** pyVideoTrans extends each line's slot to the next line's start before stretching anything ([pyVideoTrans Synchronize.md](https://github.com/jianchang512/pyvideotrans/blob/HEAD/docs/Synchronize.md)).
- **Estimate before synthesis and cap the speed-up.** VideoLingo estimates English at **0.225 s per syllable**, asks an LLM to shorten lines that won't fit, accepts up to **1.2×** speed-up and hard-caps at **1.4×** ([VideoLingo config](https://github.com/Huanshere/VideoLingo/blob/HEAD/config.yaml); [estimate_duration.py](https://github.com/Huanshere/VideoLingo/blob/HEAD/core/tts_backend/estimate_duration.py)).
- **Never approach 2×.** Amazon's dubbing research scores speaking rates of 2× and above as unintelligible ([arXiv 2204.02530](https://arxiv.org/pdf/2204.02530)).
- **Prefer phoneme-aware stretching.** Listeners significantly preferred it to uniform stretching ([Amazon Science](https://cdn.amazon.science/2c/de/191aa8ec423696fcab88f2945f64/duration-modeling-of-neural-tts-for-automatic-dubbing.pdf)).
- **Don't slow the video.** pyVideoTrans can slow video to absorb overruns, but a slowed talking face is visible, so use audio-only fitting here.

The local ffmpeg build includes both `rubberband` and an `atempo` filter accepting 0.5–100. Remember that ffmpeg's `loudnorm` defaults to −24 LUFS, so set the common Reels target of **−14 LUFS / −1 dBTP** explicitly. Meta publishes no official loudness spec ([OpenClip](https://openclip.app/learn/audio-normalization)). Classic dubbing research re-adds the original room's background noise and reverberation to the dry TTS ([arXiv 2001.06785](https://arxiv.org/abs/2001.06785)), so apply a short reverb plus a mild EQ match before mixing with sidechain ducking.

**Lip-sync is the one stage the box cannot do.** Open-source options:

- **LatentSync 1.6** (ByteDance, Apache-2.0) is the 2026 practitioners' "local model to beat" for short social clips ([Instavar, May 2026](https://instavar.com/research/ai-video/open-source-lip-sync-models)). It works on a 512×512 face crop and needs **about 18 GB of VRAM** ([LatentSync](https://github.com/bytedance/LatentSync)). That rules out a free Colab T4 and calls for an L4 or a hosted endpoint.
- **MuseTalk 1.5** (MIT) runs on 4 GB but outputs a 256 px mouth. Reported weaknesses include softness, jitter and a darker mouth patch ([MuseTalk](https://github.com/TMElyralab/MuseTalk)).
- **Wav2Lip** prohibits commercial use.
- **InfiniteTalk** regenerates head and body motion. In its own paper's table it loses to LatentSync on fidelity and identity metrics ([arXiv 2508.14033](https://arxiv.org/html/2508.14033)).

Hosted pricing settles the question for us:

- **fal LatentSync** costs $0.20 flat up to 40 s, then $0.005 per second ([fal](https://fal.ai/models/fal-ai/latentsync)).
- **Replicate** charges about $0.093 per run ([Replicate](https://replicate.com/bytedance/latentsync)).
- **Sync** charges $0.04–0.05/s for lipsync-2, $0.067–0.083/s for lipsync-2-pro (better teeth), and $0.107–0.133/s for sync-3 (4K, automatic occlusion handling) ([sync.so pricing](https://sync.so/pricing); [models](https://sync.so/docs/models)).
- **Kling** accepts only 2–10 s of input video, which rules it out ([fal Kling](https://fal.ai/models/fal-ai/kling-video/lipsync/audio-to-video)).

Our footage is the easy case for these models: one woman, frontal, talking to camera, with a large face in a 9:16 frame. Mouth-only models preserve everything else, which protects the "still looks like her" goal.

Three practical rules follow, all inferred rather than tested on our footage:

1. Cut the reel at scene cuts and lip-sync each shot separately. Sync drift across cuts is a known failure ([Instavar](https://instavar.com/research/ai-video/open-source-lip-sync-models)).
2. Drive the lip-sync model with the **clean English voice track**, then put the final music mix back in afterwards.
3. Use face restorers like GFPGAN or CodeFormer sparingly, if at all, because they can add flicker and drift her identity.

| Stage | On our 4-CPU / 15 GB box? | Evidence |
|---|---|---|
| ffmpeg extract, stretch, mix, loudness | Yes | Verified locally (filters present) |
| Demucs separation | Yes, ~1.5× real time | Verified (README) |
| BS-RoFormer separation | Probably, minutes per reel | Unbenchmarked |
| IndicTrans2 dist-200M (CTranslate2) | Probably | Unbenchmarked |
| IndicConformer / Whisper-kn fine-tunes | Possibly, slow | Unbenchmarked |
| Open TTS/VC (Chatterbox, F5, Seed-VC, RVC inference) | Minutes at best; RVC training impractical | Unbenchmarked; all docs assume CUDA |
| LatentSync 1.6 / MuseTalk | No | GPU-only (18 GB / 4 GB VRAM) |

## Consent and disclosure gate every step

Every vendor and model card reviewed requires the right to clone the voice. ElevenLabs goes furthest. **"You can only create a Professional Voice Clone of your own voice. Even with their consent, you cannot clone someone else's voice."** The sanctioned route is for the voice owner to create and verify the clone herself, then share it privately ([ElevenLabs help](https://help.elevenlabs.io/hc/en-us/articles/36842751624209)). Verification is a live voice CAPTCHA matched to the training samples. Sarvam says "only clone a voice you have the right to use" ([Sarvam](https://docs.sarvam.ai/api/api-guides-tutorials/voice-cloning/overview)), and AI4Bharat's IndicF5 asks for "explicit permission" ([IndicF5](https://github.com/AI4Bharat/IndicF5)). In practice:

- Get her explicit consent and keep a short recorded or written note of it.
- Have her create any ElevenLabs PVC personally on her own account.
- Keep the clone private.
- Label the reels as AI-dubbed. Meta labels its own output "Translated with Meta AI" ([India TV News](https://www.indiatvnews.com/technology/news/instagram-expands-meta-ai-reel-translations-to-bengali-tamil-telugu-kannada-and-marathi-2026-01-17-1026257)).

The risk is concrete. Indian police have warned that scammers harvest voice samples from social-media videos ([DT Next](https://www.pressreader.com/india/dt-next/20240428/281621015402986)). A high-quality English clone of a public creator widens that attack surface, which also argues against leaving clones on shared accounts. Chatterbox embeds an imperceptible watermark that survives MP3 compression ([Chatterbox](https://huggingface.co/ResembleAI/chatterbox)). Two gaps remain unresearched: **Instagram's 2026 AI-labelling rules and India's synthetic-media rules**. Check both before monetised posting.

Two input issues need attention. **Get the original MP4s from her phone rather than scraping.** yt-dlp's Instagram extractor failed intermittently in mid-2026 with "empty media response" errors ([Seal #2566](https://github.com/JunkFood02/Seal/issues/2566)), and anonymous Instaloader access from cloud IPs is heavily throttled ([Instaloader docs](https://git.sudo.is/mirrors/Instaloader/src/branch/master/docs/troubleshooting.rst)). Also check for burned-in Kannada captions. No toolkit removes them automatically ([VideoLingo config](https://github.com/Huanshere/VideoLingo/blob/HEAD/config.yaml)).

## Build it in three tiers

The concrete pipeline is a lean custom script on the CPU box that calls APIs. It borrows its timing logic from VideoLingo and pyVideoTrans and its edit-and-re-render design from open-dubbing's per-utterance JSON (`start`, `end`, `translated_text`, `speed`, then re-render only what changed) ([open-dubbing](https://github.com/Softcatala/open-dubbing)). We prefer a custom script to installing a full GUI toolkit for three reasons. VideoLingo's default local ASR lacks Kannada. Linly-Dubbing and ViDubb are stale. And pyVideoTrans, the best off-the-shelf fallback, is GPL-3.0, though it runs on CPU by default and lists Kannada ([pyVideoTrans](https://github.com/jianchang512/pyvideotrans)).

| # | Stage | Primary choice | Fallback / cross-check | Runs on |
|---|---|---|---|---|
| 1 | Ingest | Original MP4 from her phone; ffmpeg to 32 kHz audio | yt-dlp with her cookies | CPU |
| 2 | Shot split | PySceneDetect at hard cuts | Manual | CPU |
| 3 | Separate | audio-separator BS-RoFormer; bed = mix − vocals | Demucs htdemucs | CPU |
| 4 | ASR | Sarvam `saaras:v4`, `kn-IN`, `codemix`, timestamps, ≤30 s VAD chunks | `saaras:v3`; Scribe v2 for word timings | API |
| 5 | Human check | Bilingual family member fixes transcript JSON | — | Human |
| 6 | Translate | Frontier LLM, whole-reel context, Indian-English register, per-line syllable budget (0.225 s/syllable), JSON | Sarvam `translate` mode / `mayura:v1` as literal reference | API |
| 7 | Human check | Read English aloud; fix idioms, names, tone | — | Human |
| 8 | Voice | Winner of the A/B test (likely ElevenLabs Multilingual v2 IVC, Sarvam `en-IN` clone, or v4 from her English sample) | Voice conversion: Indian-English reading → ElevenLabs Voice Changer | API |
| 9 | Fit | Extend slot to next start; re-prompt if >1.2× over; rubberband ≤1.2×, never >1.4×; pad pauses if short | Trim with 80 ms fade | CPU |
| 10 | Mix | Short reverb + EQ match, sidechain duck bed, loudnorm −14 LUFS / −1 dBTP | — | CPU |
| 11 | Lip-sync | fal LatentSync per shot, driven by the clean voice track | Sync lipsync-2-pro or sync-3 for occlusion/profile shots | API |
| 12 | Mux and label | Replace audio with the final mix; add "AI-dubbed" disclosure | — | CPU |

The three tiers trade effort for control:

| Tier | What it is | Cost per ~60 s reel | Strengths | Weaknesses |
|---|---|---|---|---|
| **1. Quickest free** | Meta AI "Translate voices" on her public account with lip-sync on; pick reels with low music. Optional side-test: HeyGen free (1 min, watermark) | $0 | Zero engineering; native distribution; voice + lip-sync | KN→EN unconfirmed; no text edits; one speaker; no file to keep; accent behaviour unknown |
| **2. Best-quality API pipeline** | The 12-stage pipeline above | ASR <₹1; translation ≈$0.01 (my arithmetic at gemini-3.8-flash rates); lip-sync $0.30 (fal LatentSync) to $4–8 (Sync pro / sync-3); TTS not priced (ElevenLabs/Sarvam rates not retrieved) | Editable at every step; accent-retaining voice by choice; best-measured Kannada ASR | Needs a script and a human review pass; TTS subscription |
| **3. Self-hosted / GPU** | Same orchestration; voice from Chatterbox ML V3 (default CFG) or Qwen3-TTS, or Indic Parler/Sarvam `en-IN` → Seed-VC/RVC; lip-sync with LatentSync 1.6 on an L4, MuseTalk/LatentSync 1.5 on a T4 | GPU rental only; third-party estimates put Colab at ~1.2 (T4) to 1.7 (L4) compute units/hr ([mccormickml](https://mccormickml.com/2024/04/23/colab-gpus-features-and-pricing/)) | No per-reel API fees; full control; RVC can be trained on 10–30 min of her speech | Licence traps (F5 NC, XTTS NC, Seed-VC GPL, IndexTTS bilibili); setup friction; no measured CPU speeds |

A sensible middle path is ElevenLabs Dubbing with high cloning strength, piped into Sync for lip-sync. ElevenLabs' 3,000 credits per minute without a watermark fits the Starter plan's 30K monthly credits at about 10 minutes a month (my arithmetic from [ElevenLabs pricing](https://elevenlabs.io/pricing)). It skips our script entirely but gives up editing on the self-serve plans and offers no en-IN target.

## A blind listening test should pick the voice, not vendor claims

No source has measured Indian-English accent fidelity for any clone, so the voice engine must be chosen empirically. The protocol below is our design, built from the documented model behaviours above. Pick **8 English lines** from two or three real reels, covering a greeting, a recipe or instruction, an emotional line, a line with a Kannada name or food word, and a line with her own code-mixed English. Fix the English text across all conditions. Use the same 10–15 s clean Kannada reference clip, isolated with audio-separator, and the same 1–2 min English sample if she records one.

| ID | Condition | Why it's in the test |
|---|---|---|
| A | ElevenLabs Multilingual v2, IVC from her Kannada audio | Documented to keep accent across languages |
| B | Eleven v3, IVC from Kannada | Behaviour undocumented |
| C | Eleven v4, IVC from her **English** sample | Same-language reference should keep accent |
| D | Eleven v4, IVC from Kannada | **Negative control**: documented to neutralise accent |
| E | Sarvam clone, `en-IN` output, Kannada reference | Indian-trained; docs say a "hint" of the reference accent carries over |
| F | Chatterbox ML V3, `language_id="en"`, default `cfg_weight` (GPU) | Documented leakage, open-source |
| G | Same as F with `cfg_weight=0` | Control for leakage removal |
| H | Sarvam `en-IN` stock female TTS → ElevenLabs Voice Changer (or Seed-VC, style conversion off) | Accent guaranteed by source; tests timbre transfer |
| I | Meta AI in-app output of the same reel | Free baseline |
| Anchors | Her real voice (Kannada, plus English if recorded); stock Sarvam `en-IN` voice | Calibrate "her" and "Indian" |

Run the test in two rounds:

1. **Dry voice only.** Present the clips in random order with condition labels hidden. Use at least five listeners: family members who know her voice plus two or three Indian listeners who don't. Each listener rates every clip from 1 to 5 on four questions: "sounds like her," "sounds like an Indian person speaking English," "sounds American or British" (reverse-scored), and naturalness.
2. **Full reel on a phone.** Take the top two conditions through the full pipeline, including lip-sync, and judge them on a phone at 9:16.

Add two objective checks:

- **Speaker similarity:** cosine similarity of ECAPA-TDNN speaker embeddings against her reference. This is the metric Sarvam uses for identity drift ([Sarvam Dub blog](https://www.sarvam.ai/blogs/sarvam-dub)).
- **Intelligibility:** word error rate from an English ASR transcribing each clip.

The decision rule: pick the highest mean of the "her" and "Indian" ratings. Disqualify any condition that scores 3 or more on "American/British", or that has clearly worse WER than the anchors. If condition D *beats* A on Indian-ness, the documented accent behaviour does not hold for Kannada references. That is worth knowing, and it would shift the weight toward Sarvam and voice conversion.

## What is verified and what is not

| Claim | Status |
|---|---|
| Meta added Kannada to Reels translation (16 Jan 2026); voice mimic; optional lip-sync; free; one speaker | Verified (Meta pages) |
| Meta supports Kannada→English specifically | **Unverified**, implied by "same capability" |
| Saaras v3 best Kannada ASR (8.8%) | Verified, single independent benchmark on telephone audio |
| `saaras:v4` quality; v4 honours `mode` | **Unverified** |
| ElevenLabs Dubbing accepts Kannada source, no lip-sync, no en-IN | Verified (docs; lip-sync from help snippet) |
| Eleven v4 strips cross-language accent; Multilingual v2 keeps it | Verified as vendor documentation; **not independently measured** |
| Sarvam clone keeps her accent in `en-IN` | Vendor docs say a "hint" carries over; **not independently measured** |
| LLMs beat MT for colloquial Kannada→English | **Unverified** inference; no current-LLM benchmark |
| LatentSync 1.6 needs ~18 GB VRAM; hosted prices | Verified (README, vendor pages) |
| CPU speed of RoFormer, IndicTrans2, open TTS/VC | **Unbenchmarked** |
| −14 LUFS for Reels | Community convention, no Meta spec |
| HeyGen/Rask/VEED/BlipCut quality on Kannada | **Unverified**; no user reports found |
| Instagram AI-label rules; Indian synthetic-media law | **Not researched** |

## Conclusion

The difficulty has moved. Kannada ASR and translation, once the obvious hard part, are now cheap and good enough, provided a bilingual human reads both the transcript and the English. The real risks now sit in two places nobody benchmarks: whether the cloned voice keeps her Indian-English accent, and whether the mouth looks like hers. The documented ElevenLabs behaviour shows the trap. The newest model is the wrong one for this goal, because the industry is optimising toward "native-sounding" English that erases exactly the accent this project wants to keep. Defaults will drift her toward American English unless the pipeline deliberately chooses accent-retaining models or an Indian-accented source performance.

The cheapest, highest-leverage move is low-tech: ask her to record a couple of minutes of English, and confirm in the Instagram app whether Meta already offers Kannada→English on her account. The first unlocks a same-language clone that should keep her accent. The second may make the whole pipeline unnecessary for casual posting. The custom pipeline then earns its keep only on reels where the English wording matters enough to edit, and the blind listening test, not vendor marketing, decides whose voice she speaks with.
