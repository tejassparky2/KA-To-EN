# Visual lip-sync / video dubbing models and vocal–background separation for re-dubbing 9:16 Instagram reels (research as of Oct 2026)

Context: 15–90 s vertical reels, real Indian woman talking to camera, sometimes moving or with cuts. Goal: lips match new English audio while the person still looks like herself. Execution box: 4 CPU, 15 GB RAM, no GPU.

## Q1. Open-source lip-sync models: quality, resolution, VRAM, speed, licences, motion/occlusion/cuts, face restoration

### Takeaway
LatentSync 1.6 (ByteDance, Apache-2.0, 512x512 face crop, about 18 GB VRAM) is the strongest local default in 2026 for mouth-only dubbing of short social clips. MuseTalk 1.5 (MIT, 256x256, real-time on a V100, runs on 4 GB) is the fast fallback. Wav2Lip variants are non-commercial and dated. InfiniteTalk and LTX LipDub regenerate more of the frame and need heavy NVIDIA GPUs. None of these models is practical on the 4-CPU, no-GPU box. Every model in this list needs a GPU, a hosted API, or a rented cloud GPU such as Colab or Replicate.

### Cited Findings
**LatentSync (ByteDance)**
- Release history:
  - v1.5 came out on 2025-03-14. It added a temporal layer for consistency, improved results on Chinese-language video, and cut stage-2 training VRAM to 20 GB.
  - v1.6 came out on 2025-06-11 and was trained on 512x512 video to reduce blur.
  - No newer version is listed in the README. — [GitHub bytedance/LatentSync](https://github.com/bytedance/LatentSync)
- Inference VRAM is 8 GB for v1.5 and 18 GB for v1.6. The licence is Apache-2.0. — [GitHub bytedance/LatentSync](https://github.com/bytedance/LatentSync)
- Recommended inference settings:
  - Steps: 20–50. More steps give better quality but run slower.
  - Guidance scale: 1.0–3.0. Higher values improve lip-sync accuracy but "may cause distortion or jitter". — [GitHub bytedance/LatentSync](https://github.com/bytedance/LatentSync)
- v1.6 changed only the training data (512x512), to fix the blurry teeth and lips users reported in v1.5. The architecture and training strategy are unchanged, and the same code runs both versions. You switch by changing the `resolution` value in the U-Net config. — [HF ByteDance/LatentSync-1.6](https://huggingface.co/ByteDance/LatentSync-1.6)
- LatentSync generates a 512 px face region and composites it back into the frame. On high-resolution footage the mouth is upscaled, and "the seam between generated and original pixels can show".
  - Sync.so says quality drops on side profiles, occlusions, low light and multiple speakers in frame, and that the model "needs clean, frontal footage".
  - Sync.so also notes the repo has had no release since June 2025 and that, as of July 2026, 228 issues were open.
  - Sync.so sells competing models, so treat this source as a vendor view. — [sync.so blog, What is LatentSync (Jul 2026)](https://sync.so/blog/what-is-latentsync)
- ComfyUI support exists through ComfyUI-LatentSyncWrapper. Its `lips_expression` parameter defaults to 1.5, and 2.0–2.5 is suggested for clear speech. — [GitHub ShmuelRonen/ComfyUI-LatentSyncWrapper](https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper)

**MuseTalk 1.5 (Tencent Music / TMElyralab)**
- v1.5 was released on 2025-03-28 and adds perceptual, GAN and sync losses. Training code was released on 2025-04-05. — [GitHub TMElyralab/MuseTalk](https://github.com/TMElyralab/MuseTalk)
- The face region is 256x256.
  - It runs at 30 fps+ on a Tesla V100.
  - The minimum tested GPU is an RTX 3050 Ti laptop with 4 GB in fp16, where an 8 s video took about 5 min.
  - The code is MIT-licensed, and the weights are usable for any purpose, including commercial. — [GitHub TMElyralab/MuseTalk](https://github.com/TMElyralab/MuseTalk)
- Limitations the README lists itself:
  - 256x256 resolution, with a suggestion to add GFPGAN-style super-resolution afterwards.
  - Identity details such as mustache, lip shape and lip colour are not well preserved.
  - Jitter, caused by single-frame generation.
  - The `bbox_shift` parameter controls how far the mouth opens. — [GitHub TMElyralab/MuseTalk](https://github.com/TMElyralab/MuseTalk)
- The MuseTalk paper says LatentSync and SyncLabs produce clearer facial and dental detail but need longer computation. It claims MuseTalk has a better quality/speed balance. — [arXiv 2410.10122](https://arxiv.org/html/2410.10122v3) (summary via search)
- Practitioner-style reports:
  - The generated mouth can look darker and less saturated than the real footage, giving a visible colour jump. — [Volcengine article](https://www.volcengine.com/article/135136) (secondary)
  - Softness becomes visible in tight close-ups. — [AIREITER MuseTalk review](https://aireiter.com/blog/musetalk-lipsync-review-cost-vs-paid-apis) (secondary)

**Wav2Lip / Easy-Wav2Lip**
- Wav2Lip is personal, research and non-commercial use only. The README says "any form of commercial use is strictly prohibited" (trained on LRS2).
  - Tips: lower input resolution (720p) can work better, and `--pads 0 20 0 0` and `--nosmooth` fix chin and double-mouth artefacts.
  - The README now points to Sync Labs' commercial models as "much higher quality". — [GitHub Rudrabha/Wav2Lip](https://github.com/Rudrabha/Wav2Lip)
- Easy-Wav2Lip has three modes: Fast (plain Wav2Lip), Improved (feathered mouth mask) and Enhanced (plus GFPGAN on the face).
  - On a Colab T4, a 9 s 720p clip took 56 s, against 6 min 53 s for the original Wav2Lip.
  - Every frame must contain a face or it fails.
  - Recommended input is under 720p, under 30 s and about 30 fps.
  - The repo was archived on 2025-01-28. — [GitHub anothermartz/Easy-Wav2Lip](https://github.com/anothermartz/Easy-Wav2Lip)

**VideoReTalking**
- Licence is Apache-2.0. It uses an identity-aware face-enhancement step, and the README notes "DNet cannot handle extreme poses". It requires CUDA 11.1 and PyTorch 1.9, which is dated. — [GitHub OpenTalker/video-retalking](https://github.com/OpenTalker/video-retalking)
- A community tutorial (unofficial) gives an 8 GB VRAM minimum and says CPU runs 10–15x slower. — [dev.to](https://dev.to/dibi8/videoretalking-72k-stars-3e2l)
- A 2026 comparison treats it as a mature multi-stage pipeline, "likely less attractive for modern social clips". — [Instavar, 22 May 2026](https://instavar.com/research/ai-video/open-source-lip-sync-models)

**Diff2Lip, Hallo/Hallo3, LivePortrait, EchoMimic, Sonic**
- Diff2Lip (WACV 2024) is a diffusion inpainting lip-sync model. The LatentSync paper says its pixel-space design is limited to low resolution, which causes blur. — [CVF Diff2Lip](https://openaccess.thecvf.com/content/WACV2024/html/Mukhopadhyay_Diff2Lip_Audio_Conditioned_Diffusion_Models_for_Lip-Synchronization_WACV_2024_paper.html); [LatentSync arXiv](https://arxiv.org/pdf/2412.09262)
- Hallo3 is built on CogVideoX. It is computationally heavy and not real-time, and Hallo3, EchoMimic and Sonic "face challenges in maintaining identity". — [OmniSync arXiv 2505.21448](https://arxiv.org/pdf/2505.21448) and related papers (via search summary)
- Instavar classes Hallo/Hallo2 and EchoMimic as portrait-animation tools, "adjacent rather than equivalent to existing-video dubbing". — [Instavar](https://instavar.com/research/ai-video/open-source-lip-sync-models)
- LivePortrait has a video-to-video portrait-editing mode, but it is mainly an animation tool. I found no verified VRAM figure. — [secourses devlog](https://secourses.itch.io/liveportrait-ai-transform-static-photos-into-talking-videos-now-supporting-video/devlog/769382/liveportrait-ai-transform-static-photos-into-talking-videos-now-supporting-video-to-video-conversion) (third party)

**InfiniteTalk / MultiTalk (MeiGen, Wan2.1-based)**
- InfiniteTalk was released on 2025-08-19 under Apache-2.0. Its video-to-video dubbing mode generates new head, body and expression motion along with lip sync, at 480p or 720p, on a Wan2.1-I2V-14B base.
  - Camera motion is only approximated. SDEdit improves the camera match but adds colour shift.
  - Colour shift grows beyond about 1 min.
  - The FusionX LoRA reduces identity preservation.
  - FP8, no-persistent-params and 4- or 8-step LoRAs exist to cut memory and time. No VRAM figures are given.
  - ComfyUI support is available through Kijai's WanVideoWrapper.
  - It claims better lip sync than MultiTalk. — [GitHub MeiGen-AI/InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk)
- In the InfiniteTalk paper's own HDTF table, LatentSync scores better on pixel-fidelity metrics: FID 16.09 vs 26.11, FVD 48.45 vs 131.65, CSIM 0.916 vs 0.775. The authors attribute this to mouth-only methods leaving the rest of the frame untouched. — [arXiv 2508.14033](https://arxiv.org/html/2508.14033) (via search summary)
- Users report slow inference, memory pressure at 720p, and degradation outside the face. — [Instavar](https://instavar.com/research/ai-video/open-source-lip-sync-models)

**Newer 2025–2026 entries**
- KeySync (Imperial College / Wrocław) is Apache-2.0. It is built for leakage-free dubbing with an occlusion mask (`fix_occlusion` with a click position, optional SAM2).
  - Inputs are 25 fps video and 16 kHz audio.
  - The online demo is capped at 6 s. No VRAM figure is given. — [GitHub antonibigata/keysync](https://github.com/antonibigata/keysync); [arXiv 2505.00497](https://arxiv.org/html/2505.00497v1)
  - Instavar's local tests did not rank it above LatentSync 1.6. — [Instavar](https://instavar.com/research/ai-video/open-source-lip-sync-models)
- LTX LipDub is an IC-LoRA for LTX-2.3 (22B), in beta (v0.9). It regenerates the mouth region from source video plus new dialogue in two passes (low resolution, then upscaled).
  - Validated languages are EN, FR, ES, DE and RU.
  - Runs via ComfyUI or Python. — [LTX docs, LipDub beta](https://docs.ltx.video/open-source-model/usage-guides/lip-dub-beta)
  - Released under a gated community licence; Instavar keeps it on its watchlist, not as a production default. — [Instavar](https://instavar.com/research/ai-video/open-source-lip-sync-models)
- OmniSync is a mask-free Diffusion Transformer lip-sync model from NeurIPS 2025 (spotlight; v1 May 2025, v2 Sep 2025). It claims robustness to pose, occlusion and stylised faces. The abstract page does not confirm a code or weights release. — [arXiv 2505.21448](https://arxiv.org/abs/2505.21448)

**Failure modes reported across models (2026 survey)**
- Blur outside the mouth.
- Visible mouth boxes or black mouths, jitter, and unnatural teeth.
- Identity drift.
- Sync drift on longer clips or clips with cuts.
- Expression leakage into the cheeks and jaw.
- Occlusion by hands, mics or subtitles.
- CUDA and mmcv setup friction. — [Instavar, 22 May 2026](https://instavar.com/research/ai-video/open-source-lip-sync-models)
- Instavar's suggested test fixtures include a "vertical compressed social clip" and "accented or non-English speech". — same source

**Face restoration (GFPGAN / CodeFormer)**
- CodeFormer is under the NTU S-Lab License 1.0. It supports video input (`--face_upsample`, fidelity weight `w` from 0 to 1, where higher means more faithful to the input). The README says nothing about temporal flicker. — [GitHub sczhou/CodeFormer](https://github.com/sczhou/CodeFormer)
- The MuseTalk README itself recommends GFPGAN as super-resolution after its 256 px output. — [GitHub TMElyralab/MuseTalk](https://github.com/TMElyralab/MuseTalk)

### Inferences
- **LatentSync 1.6 on a T4 is doubtful.** It needs 18 GB and a T4 has 16 GB nominal (about 15 GB usable), so it likely will not fit without code changes. Use an L4 (22.5 GB on Colab), an A100, or a hosted endpoint. LatentSync 1.5 (8 GB) and MuseTalk do fit a T4.
- **Our footage is the easy case.** A frontal, single-speaker, talking-to-camera 9:16 reel is the best case for mouth-inpainting models: the face is large, and these models preserve the rest of the frame. That favours LatentSync or MuseTalk over full-frame regenerators such as InfiniteTalk, which may change her body and background and add colour shift.
- **Split at cuts first.** Hard cuts and sync drift on longer clips are a known failure mode. Splitting the reel at scene cuts (for example with PySceneDetect), lip-syncing each shot, and re-concatenating is the safer pipeline. This is inferred and not verified for a specific model.
- **Restoration can backfire.** Running GFPGAN or CodeFormer frame by frame can add flicker and change identity, the "not the same person" risk. Use it sparingly, with a low blend or a high CodeFormer `w`, and only on the mouth/face crop. This is inferred; no source measured it.
- **Licence check.** Wav2Lip is non-commercial and CodeFormer is under the S-Lab licence. For monetised reels, prefer the Apache-2.0 or MIT options (LatentSync, MuseTalk, VideoReTalking, KeySync, InfiniteTalk).

### Gaps
- No measured runtimes for LatentSync 1.6 per second of video on a T4, L4 or A100 were found. Replicate's figure (about 96 s per prediction on an L40S) depends on input.
- No VRAM figures were found for InfiniteTalk, KeySync, LivePortrait, Diff2Lip or Hallo3.
- It is unconfirmed whether OmniSync weights are publicly released.
- No source specifically evaluated these models on Indian or South Asian faces, or on English audio driving lips of a non-native speaker.

## Q2. Commercial lip-sync APIs and services: pricing and quality

### Takeaway
Sync Labs (sync.so) is the purpose-built API for re-lip-syncing existing footage. lipsync-2 costs about $0.04–0.05/s, lipsync-2-pro about $0.067–0.083/s (512x512 face, better teeth), and sync-3 about $0.107–0.133/s (4K, automatic occlusion handling). A 60 s reel therefore costs roughly $2.40–$8 depending on the model. Hosted LatentSync is far cheaper (fal: $0.20 flat up to 40 s; Replicate: about $0.093 per run). ElevenLabs Dubbing does not lip-sync by itself.

### Cited Findings
**Sync Labs (sync.so)**

Plans (each plan adds a usage fee):

| Plan | Monthly | Usage rate | Max video length | Extras |
|---|---|---|---|---|
| Hobbyist | $5 | $0.05/s | 1 min | |
| Creator | $19 | $0.05/s | 5 min | No watermark, Active Speaker Detection |
| Growth | $49 | $0.0475/s | 10 min | |
| Scale | $249 | $0.04/s | 30 min | Batch API |

Source: [sync.so/pricing](https://sync.so/pricing)

Models (per second of output at 25 fps):

| Model | Price | Notes |
|---|---|---|
| lipsync-1.9 (legacy) | $0.02–0.025/s | |
| lipsync-2 | $0.04–0.05/s | 512x512 face |
| lipsync-2-pro | $0.067–0.083/s | 512x512 face with "enhanced teeth and beard detail" |
| sync-3 | $0.107–0.133/s | 4K native, automatic occlusion handling, close-ups, profiles |
| react-1 | $0.133–0.167/s | Expressive emotions; requires a paid subscription |

- lipsync-2 and lipsync-2-pro process long videos in 30–40 s chunks and need natural speaking motion in the input. — [sync.so/docs/models](https://sync.so/docs/models)
- Sync also offers a dubbing flow in which ElevenLabs generates the translated voice and Sync lip-syncs it. — [sync.so blog: AI dubbing](https://sync.so/blog/introducing-ai-dubbing-in-sync)

**Sync models via fal.ai**
- Sync lipsync v2 is $3/min.
- lipsync-2-pro is $5/min ("preserves natural teeth and unique facial features"). — [fal.ai sync-lipsync v2 pro](https://fal.ai/models/fal-ai/sync-lipsync/v2/pro); [fal.ai sync-lipsync v2](https://fal.ai/models/fal-ai/sync-lipsync/v2)
- Runware lists lipsync-2-pro at $0.0733/s. — [Runware](https://runware.ai/models/lipsync-2-pro)

**Hosted LatentSync**
- fal.ai: $0.20 flat for clips up to 40 s, then $0.005 per output second. — [fal.ai LatentSync](https://fal.ai/models/fal-ai/latentsync)
- Replicate (bytedance/latentsync): about $0.093 per run, "varies depending on your inputs", typically about 96 s on an Nvidia L40S. The page does not say whether it runs v1.5 or v1.6. — [Replicate](https://replicate.com/bytedance/latentsync)
- WaveSpeed: from $0.15 per run. — [WaveSpeed](https://wavespeed.ai/vi/models/bytedance/latentsync) (via search)

**Kling LipSync via fal**
- $0.014 per input-video second, rounded up to 5 s increments.
- Input video must be only 2–10 s, at 720–1920 px; audio can be up to 60 s.
- Processing takes about 12 min. — [fal.ai Kling lipsync](https://fal.ai/models/fal-ai/kling-video/lipsync/audio-to-video)

**HeyGen**
- Official plans: Free (1 min video, limited lip-sync trial), Creator $29/mo (600 credits, 30 min, 175+ languages), Pro $49+, Business $149 (+$20/seat). Credits per minute are not listed on the official page. — [heygen.com/pricing](https://www.heygen.com/pricing)
- Secondary sources say lip-sync translation costs 5 credits/min, "precision" 10 credits/min, and audio-only dubbing 2 credits/min. — [Creatify blog 2026](https://creatify.ai/blog/heygen-pricing-(2026)-plans-and-what-you-ll-actually-pay); [eesel.ai](https://eesel.ai/blog/heygen-pricing)

**ElevenLabs**
- The help-centre article "Do you offer lip sync" says, per the search snippet, that ElevenLabs does not lip-sync in Dubbing. Lip sync is available in Image & Video, Flows and Studio via third-party models. The page returned 403 to direct fetch, so this comes from the search snippet. — [ElevenLabs help](https://help.elevenlabs.io/hc/en-us/articles/23793433149073-Do-you-offer-lip-sync)
- A MindStudio blog claims Dubbing V2 includes lip sync. This is unverified and contradicts the official help page. — [MindStudio](https://www.mindstudio.ai/blog/elevenlabs-dubbing-v2-preserve-voice-emotion)

**Rask.ai**
- Third-party sources conflict: Creator $60/mo for 25 min ($3/extra min) vs $39/mo. Lip sync reportedly consumes 1x or 3x minutes (standard vs enhanced). I could not reach the official page. — [Perso.ai review](https://perso.ai/blog/rask-ai-dubbing-review-2026-features-pricing-how-it-compares); [Dupple](https://dupple.com/learn/best-ai-lip-sync-tools) (both are competitors or aggregators)

**Captions**
- Captions' AI dubber "adjusts lip movements and expressions". — [captions.ai](https://www.captions.ai/tools/ai-dubber)
- Its 2023 Lipdub app supported 28 languages, 1 min max, single speaker, with an AI-generated label (2023 info, may be outdated). — [Axios 2023](https://www.axios.com/2023/10/10/ai-videos-transation-languages-lipdub); [VentureBeat](https://venturebeat.com/ai/video-startup-captions-launches-new-ai-dubbing-app-lipdub-with-gen-z-slang)

**Hedra**
- Character-3 is image-to-video (a portrait plus audio produces an avatar), not existing-footage re-sync. Hedra says lip sync "is a capability of the selected model". — [Hedra Character-3](https://www.hedra.com/video-models/hedra-character-3); [Hedra AI lip sync](https://www.hedra.com/uses/ai-lip-sync)

**Tavus**
- Pricing conflicts across sources: €59/mo for 10 lip-sync minutes (OMR, Jul 2025) vs $39/mo (Tavus blog) vs $99/mo (2026 guide). Unverified. — [OMR](https://omr.com/en/reviews/product/tavus/pricing); [Tavus blog](https://tavus.io/post/lip-sync-video-apis)

### Inferences
- **Cost per 60 s reel at list prices:**
  - fal LatentSync: about $0.30 ($0.20 plus 20 s x $0.005).
  - Replicate LatentSync: about $0.10–0.30.
  - Sync lipsync-2: $2.40–3.00.
  - lipsync-2-pro: $4.00–5.00.
  - sync-3: $6.40–8.00.
  - HeyGen lip-sync translation: about 5 credits (secondary source).
- **Kling** caps input video at 10 s, so it does not fit 15–90 s reels without chunking.
- **Hedra** is image-driven, so it would not preserve her real body motion.
- **Recommended path for the no-GPU box:** API-first.
  - Prototype with fal or Replicate LatentSync (cheapest), using our own separated English TTS track.
  - Escalate to Sync lipsync-2-pro or sync-3 for reels with occlusion, profile turns or teeth problems.
- **ElevenLabs** can supply the English voice but needs a separate lip-sync step.

### Gaps
- HeyGen's official per-minute credit cost for lip-sync translation, and its API price, could not be verified.
- Rask.ai's official pricing and lip-sync multiplier could not be confirmed.
- No independent, side-by-side quality benchmark of Sync vs HeyGen vs Rask vs LatentSync on real talking-head footage was found. Most comparisons are vendor-authored.
- I could not confirm which LatentSync version fal and Replicate host.

## Q3. Vocal / background separation for Instagram reels: best models and CPU feasibility

### Takeaway
Use the `audio-separator` Python package (MIT, CPU install available) with a BS-RoFormer vocals model, such as `model_bs_roformer_ep_317_sdr_12.9755.ckpt`, or a MelBand-RoFormer vocals model. These are the current state of the art on MVSEP (about 11.7–12.3 dB vocals SDR on the Multisong set). They clearly beat Demucs v4 (9.0 dB MUSDB overall). Demucs htdemucs runs at about 1.5x track duration on CPU, so a 90 s reel is feasible on the 4-CPU box. RoFormers are heavier, but for 15–90 s clips should still be feasible on CPU; this was not benchmarked. If reels contain sound effects as well as music, a speech/music/SFX "cinematic" model (MVSep DnR v3) is an alternative.

### Cited Findings
**Demucs v4 (htdemucs / htdemucs_ft)**
- Hybrid Transformer Demucs reaches 9.0 dB SDR on the MUSDB HQ test set (fine-tuned), and `htdemucs_ft` "will take 4 times more time but might be a bit better". — [GitHub adefossez/demucs](https://github.com/adefossez/demucs)
- CPU processing time is about 1.5x the track duration. `--shifts` should be used only on GPU.
- `--two-stems=vocals` is not faster.
- Segment length is at most 7.8 s for HT models.
- The licence is MIT. The author is "not actively working on Demucs anymore". — [GitHub adefossez/demucs](https://github.com/adefossez/demucs)
- Other CPU data points vary: a 4-min song took about 90 s on a Ryzen 9 5950X, and about 2 min 15 s for 7 min on an M4 Max CPU. — [stemsplit.io](https://stemsplit.io/blog/spleeter-vs-demucs); [Medium MLX port](https://medium.com/@andradeolivier/i-ported-demucs-to-apple-silicon-it-separates-a-7-minute-song-in-12-seconds-6c4e5cffb5c3) (secondary)

**audio-separator (python-audio-separator)**
- Supports MDX (onnx), VR, Demucs and MDXC/RoFormer models, largely from UVR.
- The licence is MIT.
- CPU install: `pip install "audio-separator[cpu]"`.
- Example: `audio-separator input.wav --model_filename model_bs_roformer_ep_317_sdr_12.9755.ckpt`. — [GitHub nomadkaraoke/python-audio-separator](https://github.com/nomadkaraoke/python-audio-separator)
- Top vocal models in its list, by SDR:
  - `model_bs_roformer_ep_317_sdr_12.9755.ckpt` (vocals 12.9)
  - `model_bs_roformer_ep_368_sdr_12.9628.ckpt` (12.9)
  - `vocals_mel_band_roformer.ckpt` (12.6)
  - `melband_roformer_big_beta4.ckpt` (12.5)
  - `mel_band_roformer_kim_ft_unwa.ckpt` (12.4)
- Preset `vocal_balanced` is described as "Best overall vocal quality".
- The default model differs between the CLI help (BS-RoFormer 317) and the Python API (`model_mel_band_roformer_ep_3005_sdr_11.4360.ckpt`). — same source
- No CPU timing benchmarks are given in the README. — same source

**MVSEP Multisong leaderboard (vocals SDR)**
- The top real models in Oct 2026:
  - BS Roformer 124 bands (MVSep, 2026-07-10): 12.33
  - BS PolarFormer 124 bands: 12.02
  - BS Roformer (MVSep, 2025-07): about 11.89
  - sami-bytedance v1.1: 11.82
  - unwa's BS-Roformer Leap Xe (open UVR-compatible ckpt): about 11.76–11.79
- The first page did not show htdemucs. — [MVSEP leaderboard](https://mvsep.com/quality_checker/multisong_leaderboard?algo_name_filter=&sort=vocals&ensemble=0)

**MVSep DnR v3 (speech / music / SFX)**
- A cinematic 3-stem model (SCNet, MelBand-RoFormer, or an ensemble of the two).
- Speech SDR: about 12.27 (Mel-RoFormer), 12.59 (SCNet Large), 12.81 (ensemble), vs Bandit v2 at 12.29. These are vendor-reported numbers. — [MVSEP algorithms](https://mvsep.com/fr/algorithms?page=2) (via search summary); dataset paper [DnR v3](https://chatpaper.com/paper/38915)
- Older MDX23-based open code for cinematic demixing is also available. — [GitHub ZFTurbo/mvsep-cdx23-cinematic-sound-demixing](https://github.com/zfturbo/mvsep-cdx23-cinematic-sound-demixing)
- A fan-edit forum user reports that UVR "is pretty good at extracting dialogue and music, but sfx get lost". — [fanedit.org](https://fanedit.org/forums/goto/post?id=460738)

**CPU feasibility evidence**
- I found no direct CPU benchmark for BS-RoFormer.
- A StemSep note says a 4-stem fine-tuned Demucs run took 75 s on GPU vs 12–20 min on CPU (full songs). — search summary ([awesome.ecosyste.ms stemsep](https://awesome.ecosyste.ms/projects/github.com%2Fjuxstin1%2Fstemsep))

### Inferences
- **Quality ranking for speech vs Instagram background music:**
  1. BS-RoFormer or MelBand-RoFormer vocal models (via audio-separator, or the UVR5 GUI).
  2. `htdemucs_ft`.
  3. `htdemucs`.
  4. MDX-Net (older).
- **Output stems we need:**
  - The instrumental or "no vocals" stem, kept as the bed under the new English voice.
  - Optionally the vocal stem, for ASR or translation, and to time-align English TTS to the original speech.
- **CPU runtime estimate for a 60 s reel on 4 CPUs:** about 90 s with htdemucs (1.5x real-time, per the README). RoFormer models will be slower, plausibly several minutes. This is unverified, so time a 30 s clip first. Batch overnight processing is clearly feasible either way.
- **Practical audio caveats:**
  - Instagram audio is AAC-compressed, so expect some bleed of music into the vocal stem and vice versa.
  - For the lip-sync model, feed the clean English TTS (not the remixed track), then mix the TTS with the instrumental afterwards.
- **If the reel uses trending licensed music,** consider replacing the bed entirely rather than reusing a separated stem with artefacts. This is a product decision, not researched.

### Gaps
- No verified CPU timings for BS-RoFormer or MelBand-RoFormer via audio-separator.
- I could not see where htdemucs and htdemucs_ft rank on the MVSEP Multisong board; only page 1 of 58 was retrieved.
- There is no dedicated benchmark of speech (as opposed to singing) separation from music in short, compressed social-media clips.

## Q4. Practitioner reports (Reddit, GitHub issues, blogs, comparisons)

### Takeaway
I could not retrieve Reddit threads directly; searches returned no Reddit pages. The best practitioner-level evidence is a May 2026 production comparison (Instavar), vendor and engineering blogs, and project READMEs. They broadly agree:
- LatentSync 1.6 is the local default for short social dubbing.
- MuseTalk is the fast fallback, with softness or colour issues.
- InfiniteTalk is heavy.
- Wav2Lip is a baseline only.
- Sync's commercial models are the quality ceiling.

### Cited Findings
- Instavar (22 May 2026) chose LatentSync 1.6 as the "local model to beat" for short social-video dubbing. Its rules:
  - Promote a challenger only if it wins on mouth fidelity, temporal sync, identity and preprocessing burden.
  - Do not pick from demo clips; test the real failure modes (off-axis face, plosives, accented speech, vertical compressed clip, occlusion). — [Instavar](https://instavar.com/research/ai-video/open-source-lip-sync-models)
- Users of InfiniteTalk report slow inference, 720p memory pressure and degradation outside the face. Every integration found assumes an NVIDIA box. — [Instavar](https://instavar.com/research/ai-video/open-source-lip-sync-models) (summary via search)
- Comparison blogs:
  - A sync.so roundup positions MuseTalk as the "safe default" and VideoReTalking as preserving head motion and lighting. — [sync.so open-source roundup](https://sync.so/blog/the-best-free-open-source-lipsync-tools-2)
  - Another roundup describes LatentSync as trading raw sync accuracy for visual fidelity. — [lipsync.com](https://lipsync.com/blog/open-source-lip-sync)
  - All are vendors.
- MuseTalk real-time pipeline on an RTX 4090: the mouth looks darker and less saturated than the surrounding face, and colour matching only partly helped. — [Volcengine](https://www.volcengine.com/article/135136)
- Easy-Wav2Lip practitioner notes:
  - About 80 ms of audio gets cut, so pad the audio.
  - Every frame needs a face.
  - Keep input under 720p and 30 s. — [Easy-Wav2Lip](https://github.com/anothermartz/Easy-Wav2Lip)
- ComfyUI LatentSync troubleshooting: artefacts or low-quality lips can come from missing auxiliary checkpoint files, and a "tuple index out of range" error is fixed by updating the nodes. — [ThinkDiffusion](https://learn.thinkdiffusion.com/seamless-lip-sync-create-stunning-videos-with-latentsync/)
- Open-source full dubbing pipelines exist (pyVideoTrans, VideoLingo, Linly-Dubbing, ViDubb, which uses Wav2Lip). — [videodubbing.com 2026](https://videodubbing.com/blog/post/best-open-source-video-dubbing-tools-2026/)

### Inferences
- **Evidence quality.** Practitioner consensus aligns with the model docs, but most "comparisons" are vendor blogs (sync.so, lipsync.com, Pixazo, Perso) with commercial bias. Instavar is the most methodical 2026 source.
- **Run our own A/B test.** Before committing, take 3–5 representative reels (static frontal, moving or walking, with cuts, hand near mouth). Run fal LatentSync vs Sync lipsync-2-pro vs sync-3, then judge by eye on a phone screen at 9:16.
- **GPU hardware tiers:**
  - Colab T4: fits LatentSync 1.5, MuseTalk and Easy-Wav2Lip.
  - L4 (22.5 GB): needed for LatentSync 1.6.
  - A100: realistic floor for InfiniteTalk 720p.
  - Recent third-party measurements put Colab at about 1.2 compute units/hr for a T4, 1.7 for an L4 and 5.4 for an A100-40GB (March 2026). Colab Pro is reportedly about $9.99 for 100 units. These figures are unofficial, and sources conflict. — [mccormickml.com](https://mccormickml.com/2024/04/23/colab-gpus-features-and-pricing/); [gpuperhour](https://gpuperhour.com/blog/google-colab-alternatives)

### Gaps
- Direct r/StableDiffusion, r/comfyui, r/LocalLLaMA and r/VideoEditing threads could not be retrieved; search tools returned none. Community sentiment is therefore secondhand.
- No GitHub-issue-level evidence on LatentSync or MuseTalk failures with head motion, cuts or side profiles was retrieved.
- No practitioner report specifically on dubbing Indian-language (Kannada) talking-head reels into English was found.
