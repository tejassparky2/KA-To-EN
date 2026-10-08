# End-to-end AI video translation / dubbing services: Kannada source to English output, voice clone and lip-sync (as of Oct 2026)

Research date: 2026-10-08. Language lists change often, so each claim notes its source and date where the page gives one. "Unverified" means I could not find a primary source that confirms it. Most official pages were read directly with WebFetch; I note where a claim comes only from a third-party page or a search-result summary.

## Summary table (Kannada → English, cloned voice, lip-sync)

| Service | Kannada as SOURCE? | English target | Voice clone | Lip-sync | Max length | Edit transcript/translation before render | Price for about 1-min reel | API |
|---|---|---|---|---|---|---|---|---|
| Meta AI translations (Instagram/Facebook Reels) | Kannada is supported (rollout began 16 Jan 2026). Kannada→English direction is **implied, not stated** (see Q1) | Yes | Yes ("mimics the sound and tone of a creator's voice") | Optional toggle | Not stated | Preview and approve/discard only. No text editing found | Free | No |
| ElevenLabs Dubbing (v2 automatic + API; v1 Dubbing Studio) | **Yes**: `kn` listed for Dubbing v2 and v1 | Yes (en, en-GB, en-US, en-AU, en-CA) | Yes, "Cloning strength" 0–10 (default 7) | **No lip-sync** (audio-only dub) | 180 min / 1 GB (app auto), 3 GB (API), 45 min (Studio) | Studio (v1, "maintenance mode") yes. v2 has no in-app editor. API transcript editing is Enterprise-only | Auto dub: 2,000 credits/min with watermark, 3,000 without | Yes, all plans |
| HeyGen Video Translate | "Kannada (India)" is on the help-center language list. Source/target role not stated | Yes | Yes | Yes | Free 1 min; Creator/Pro 30 min; Business 60 min | Proofreading/script editing listed on Pro | Free plan: 3 videos/mo, 1 min max, watermark; Creator $29/mo | Yes (HeyGen API; not checked here) |
| Rask AI | **Likely**: Rask's translator page links a "Kannada Video Translator" under "Translate audio into English from 40+ source languages" | Yes | Yes, 32 languages (whether English output counts was not checked) | Yes, "across 135+ languages"; uses 3x minutes (third-party) | "Up to 5 hours" / "up to 1 GB" | Yes, line-by-line edit and per-segment regenerate | 7-day free trial; paid prices not checked | Yes |
| VEED | **Yes**: Kannada is #42 on the dubbing "spoken languages" list (page updated 19 Aug 2026) | Yes (#1 target) | Not stated on the page | Optional lipsync | Not checked | Not checked | Not checked | Not checked |
| BlipCut | **Yes**: Kannada is on the source list (77 inputs), the target list ("Kannada(IN)") and the voice-cloning list | Yes | Yes, Kannada on the cloning list | Advertised; no per-language list | Not checked | Not checked | Not checked | Not checked |
| Kapwing | Kannada confirmed as a **target**. Source list ("155 variants") not itemised, so unverified | Yes | Business/Enterprise only | Optional; Pro/Business | Free: under 8 min | Edits after dub generation (transcript edits re-translate) | Uses transcription + translation + TTS minutes | Not checked |
| Synthesia Dubbing 2.0 (15 Jul 2026) | Unverified (claims "over 130" languages, no list found) | Yes | Not described in the 2.0 post | Yes, upgraded model | Not stated | Enterprise: review/refine transcript and translation, regenerate a segment | Not stated | Not checked |
| Vozo | Unverified ("160+ languages", list not retrieved) | Yes | Yes (VoiceREAL / VoiceNATIVE) | Yes (LipREAL) | "Up to 2h" | Yes, line-by-line edit and regenerate | Not retrieved | API link exists |
| Perso AI (ESTsoft) | Unverified (counts only: "99+ detected", "12, 74, 111" supported) | Yes | Yes | "Lip Dubbing" 2/13/60 min per month on Starter/Creator/Pro | Starter 3 min, Creator 15, Pro 30, Ent 60 | Script editing on Starter and above | Starter $6.99/mo (7 min); Creator $29 (40 min, $0.73/min); Pro $99 (180 min, $0.55/min) | Yes (API key access listed) |
| Captions / Mirage (Lipdub) | **Not listed** (help page modified 20 Apr 2026; includes Hindi, Hinglish, Tamil) | Yes | Yes | Yes (Lipdub) | Not checked | Not checked | Not checked | Not checked |
| Akool | Unverified ("155+" / "140+" languages, no list) | Yes | Not checked | Yes, proprietary Lip Sync model | Not checked | Not checked | Not checked | Yes (AWS Marketplace listing) |
| Smartcat | Unverified for ASR source ("280 languages supported by Smartcat"). Kannada is not among the 36 voice-over locales, but that matters only for Kannada *output* | Yes | Not mentioned in the help article (marketing claims cloning) | Not mentioned | Not checked | Yes, edit target text and timecodes in Subtitle Editor | Not checked | Not checked |
| Speechify Studio dubbing | Unverified. A G2 listing includes Kannada; the source direction is not confirmed | Yes | Claimed | Not checked | Not checked | Not checked | Not checked | Not checked |
| Wavel | Unverified (pages say 30+, 40+ or 100+; partial lists stop at Hindi) | Yes | Yes | Lip-sync product page exists | Not checked | Not checked | Not checked | Not checked |
| Dubverse (India) | Unverified as source. Kannada appears as a language, mainly in the English→Indic direction (2022 data) | Yes | Supreme tier ("DubX" multi-speaker cloning) | Not checked | Not checked | Not checked | Third-party: Pro ~$18/mo, Supreme ~$30/mo (conflicting) | Yes (TTS/dubbing API per reviews) |
| Sarvam Studio / Dubbing API | Sources are "any language" (Studio) | **No English target**: Indian-language outputs only | Yes | Not mentioned ("Audio-Visual Sync" only) | 1 h (Starter/Pro), 4 h (Business) | Creator Studio editor flow | ₹40/min API; ₹72–80/min with editor_flow | Yes |
| YouTube auto-dubbing | **No**: Kannada is not in the to-English source list (includes Malayalam, Tamil, Telugu, Bengali, Punjabi, Hindi, Urdu) | n/a | Expressive speech in 8 languages only | Experimental pilot, select channels | 120 min | "You cannot edit automatic dubs" | Free | No |
| Google Vids | Unverified. No source found that Vids dubs/translates speech | — | — | — | — | — | — | — |
| Gan.ai | Unverified. Myna-mini TTS covers 22 Indic + English (Aug 2024); lip-sync API was only "planned" | — | Claimed by a third party only | Planned (2024) | — | — | — | TTS API |
| Pixa | Unverified. No results found | — | — | — | — | — | — | — |
| VideoDubber (extra find) | Claims Kannada→English page with voice clone and lip-sync (vendor SEO page) | Yes | Claimed | Claimed | — | — | — | — |
| Murf (extra find) | Has a "kannada-to-english-video" translator page (vendor). Lip-sync not shown | Yes | — | — | — | — | — | — |

Table sources are cited per service in the sections below.

## Q1. Meta AI translations for Instagram/Facebook Reels: languages, Kannada, English, eligibility, lip-sync

### Takeaway
Kannada is an official Meta AI Reels translation language. Rollout began on Instagram and Facebook on 16 Jan 2026. The service is free, keeps the creator's voice and has optional lip-sync, which makes it the most direct no-cost option for an Instagram creator. However, no Meta page explicitly says Kannada → English works. The wording ("translate reels **into** Bengali, Tamil, Telugu, Kannada, and Marathi", and "the same capability" as the bidirectional to/from-English launch) implies it but does not state it. Translation is limited to one speaker per reel (Instagram creators blog), and you cannot edit the translated text, only preview and approve or discard.

### Cited Findings
- 9 Oct 2025 original post: "Translations are now supported in English, Spanish, Hindi, and Portuguese." It also says the tool works in "multi-lingual translations between English, Spanish, Portuguese, and Hindi" — [Meta Newsroom, "Discover Reels From Around the World With Meta AI Translation"](https://about.fb.com/news/2025/10/discover-reels-around-world-meta-ai-translation/)
- 16 Jan 2026 update on the same post: translations are "starting to roll out in more languages, including Bengali, Tamil, Telugu, Marathi, and Kannada," on Instagram and Facebook — [Meta Newsroom](https://about.fb.com/news/2025/10/discover-reels-around-world-meta-ai-translation/)
- 4 Jun 2026 update: expanding "to Arabic, Bahasa Indonesian, French, Thai, and Vietnamese on Facebook". 14 Jul 2026 update: expanding "to French, German, Italian, Japanese, and Korean on Instagram" — [Meta Newsroom](https://about.fb.com/news/2025/10/discover-reels-around-world-meta-ai-translation/)
- Eligibility (Meta's wording): "Translating reels with Meta AI is free, and is accessible to Facebook creators with 1,000 followers or more and to all public Instagram accounts in countries where Meta AI is available." — [Meta Newsroom](https://about.fb.com/news/2025/10/discover-reels-around-world-meta-ai-translation/). Social Media Today (Jan 2026) instead reported a Page/professional mode requirement plus 1,000 followers. This conflicts for Instagram, and Meta's own text is more authoritative — [Social Media Today](https://www.socialmediatoday.com/news/meta-adds-more-languages-to-ai-translations-for-reels/810019/)
- Voice: "Meta AI mimics the sound and tone of a creator's voice to translate reels." Lip-sync: creators can "choose to enable the lip syncing feature, which syncs the translated audio" to mouth movements — [Meta Newsroom](https://about.fb.com/news/2025/10/discover-reels-around-world-meta-ai-translation/)
- Nov 2025 (House of Instagram, Mumbai): the October launch covered translation "to and from English, Hindi, Spanish, and Portuguese", and "the same capability will soon be available in Bengali, Tamil, Telugu, Kannada, and Marathi." — [Meta Newsroom, "Instagram Empowers Creators to Go Global with Local Voice Translations and Fonts"](https://about.fb.com/news/2025/11/instagram-empowers-creators-to-go-global-with-local-voice-translations-and-fonts/)
- A separate Oct 2025 Meta post is titled "Translate, Dub, and Lip Sync Your Reels Between Hindi and English", which shows Indic→English was supported for Hindi. I did not open this post; the title comes from search results — [Meta Newsroom](https://about.fb.com/news/2025/10/translate-dub-and-lip-sync-your-reels-between-hindi-and-english-now-on-instagram-and-facebook/)
- Instagram Creators blog (updated 16 Jan, © 2026):
  - Creators can preview and approve translations before they are shared, and get a notification to publish or discard them.
  - "Currently only reels with one speaker can be translated", and multi-speaker support is "coming soon."
  - Tips: face the camera, speak clearly, don't cover your mouth, and minimize background noise or music.
  - Source: [Instagram Creators blog, "Expanding Translations to More Languages"](https://creators.instagram.com/blog/meta-ai-translations)
- Conflict on speaker count: third-party guides say up to two speakers (the Inro blog, summarised by search), while the official Instagram creators blog says one speaker — [Inro](https://www.inro.social/blog/meta-ai-reel-translation); [Instagram Creators blog](https://creators.instagram.com/blog/meta-ai-translations)
- Translated reels are labelled "Translated with Meta AI" (search summary of news coverage) — [India TV News, 17 Jan 2026](https://www.indiatvnews.com/technology/news/instagram-expands-meta-ai-reel-translations-to-bengali-tamil-telugu-kannada-and-marathi-2026-01-17-1026257); [Business Standard, 16 Jan 2026](https://www.business-standard.com/technology/tech-news/instagram-expands-meta-ai-reel-translations-to-more-indian-languages-126011600728_1.html) (returned 403 to direct fetch, so content is from search snippets only)
- No Meta page I read describes editing the transcript or translation text, or a maximum reel length — [Meta Newsroom](https://about.fb.com/news/2025/10/discover-reels-around-world-meta-ai-translation/)

### Inferences
- Because the Oct 2025 languages were explicitly "to and from" and Meta calls the Indic expansion "the same capability", Kannada → English very likely works. Still, the user should confirm in-app: Reel upload → "Translate voices with Meta AI" → check that English is offered as the output for a Kannada reel.
- Meta is the only free option that does voice clone, lip-sync and native distribution together. The translated version is served to viewers on Instagram, and the user does not get a separate English file to edit. For the mother's account, the setting must be enabled on her account. The user's account would only work if he re-posts the reel.
- No text editing means mistranslations of Kannada idioms or names cannot be fixed. The only choice is to discard.

### Gaps
- No official Meta help-center page with an explicit language-pair matrix was found. The help.instagram.com page was not reached.
- No creator reviews of Kannada→English quality on Meta were found.
- Maximum reel length for translation was not found.

## Q2. ElevenLabs Dubbing (Automatic/v2, Dubbing Studio, API): Kannada source, voice clone, watermark, pricing

### Takeaway
ElevenLabs officially lists Kannada (`kn`) for both Dubbing v2 and v1. It is the most clearly documented Kannada source → English dub with per-speaker voice cloning, but it is **audio-only (no lip-sync)**. Dubs are watermarked on the free tier. The transcript/translation editor (Dubbing Studio) is v1-only and in maintenance mode. On v2, editing via the API is Enterprise-only.

### Cited Findings
- Kannada (`kn`) is listed in the Dubbing v2 language table and in the Dubbing v1 table. English dialects listed: en-AU, en-CA, en-GB, en-US — [ElevenLabs docs, Dubbing](https://elevenlabs.io/docs/capabilities/dubbing)
- Limits:
  - Automatic Dubbing: 1 GB and 180 minutes in the app, 3 GB via the API.
  - Dubbing Studio: 1 GB and 45 minutes.
  - Up to 32 speakers per file.
  - Source: [ElevenLabs docs](https://elevenlabs.io/docs/capabilities/dubbing)
- Voice clone: v2 has a "Cloning strength" setting from 0 to 10 (default 7), labelled "Speaker similarity" in the app. Higher values favor similarity to the original speaker, and lower values favor natural delivery in the target language — [ElevenLabs docs](https://elevenlabs.io/docs/capabilities/dubbing)
- Watermark: "Free-tier dubs are watermarked automatically; paid-tier dubs are not." — [ElevenLabs docs](https://elevenlabs.io/docs/capabilities/dubbing)
- Editing:
  - Dubbing Studio is v1-only and "is in maintenance mode and receives critical bug fixes only".
  - v2 has no in-app editor.
  - "Transcript editing and audio regeneration via the API are available on Enterprise plans only."
  - Source: [ElevenLabs docs](https://elevenlabs.io/docs/capabilities/dubbing)
- API: creating and downloading dubs is available on all plans. Concurrency is 3 jobs (self-serve) and 10 (Enterprise) — [ElevenLabs docs](https://elevenlabs.io/docs/capabilities/dubbing)
- Pricing FAQ:
  - "Dubbing 2,000 credits per minute (automatic with watermark), 3,000 (automatic without watermark), 5,000 (Dubbing Studio with watermark) or 10,000 (Dubbing Studio without watermark)."
  - Monthly credits: Free 10k, Starter 30k, Creator 121k, Pro 600k.
  - The docs also say "Dubbing v2 is priced per minute in US dollars on Automatic Dubbing", but no USD figure was retrieved.
  - Sources: [ElevenLabs pricing](https://elevenlabs.io/pricing); [ElevenLabs docs](https://elevenlabs.io/docs/capabilities/dubbing)
- Accent risk: Synthesia's help center (which uses ElevenLabs cloning) says ElevenLabs instant cloning "cannot always preserve the accent of non-native English speakers" because "ElevenLabs only has English accent data for US, UK, Australian, and Canadian English". Its suggested fix is a Professional Voice Clone — [Synthesia Help Center](https://help.synthesia.io/en/articles/9770805-why-is-my-accent-not-being-captured-in-my-voice-clone)

### Inferences
- A 1-minute reel at 3,000 credits/min (no watermark) fits within the Starter plan's 30k credits (about 10 min/month). This is my arithmetic, not a vendor figure.
- To keep an Indian-English accent, the user will probably need a higher "Speaker similarity" setting and/or a professional clone. The en-US/en-GB/en-AU/en-CA dialect list contains no en-IN.
- For lip-sync, the ElevenLabs audio would need a separate lip-sync tool (out of scope here).

### Gaps
- USD plan prices (Starter/Creator/Pro) were not captured from the pricing page in this session.
- No Reddit or user reports specific to Kannada→English ElevenLabs quality were found.

## Q3. Other end-to-end services: Kannada → English support, voice clone, lip-sync, editing, pricing

### Takeaway
Only a few services have **primary-source evidence of Kannada as a source language** with English output:

- ElevenLabs (official docs)
- VEED (help article updated 19 Aug 2026)
- BlipCut (support page; Kannada is also on its voice-clone list)
- Rask (Kannada→English page on its own site, so likely)
- HeyGen (Kannada on its translation list, but source/target role not stated)

Of these, VEED, BlipCut, Rask and HeyGen also offer lip-sync. YouTube auto-dubbing explicitly does **not** support Kannada. Captions/Mirage does not list it. Sarvam supports Kannada but outputs only Indian languages, not English. Synthesia, Vozo, Perso, Akool, Smartcat, Speechify, Wavel, Dubverse, Gan.ai, Pixa and Google Vids remain **unverified** for a Kannada source.

### Cited Findings

**HeyGen**
- The help article "Video translation languages we support" lists "Kannada (India)". The article does not say whether it is a source or target and has no last-updated date — [HeyGen Help](https://help.heygen.com/en/articles/11391941-video-translation-languages-we-support)
- Pricing: Free $0 (3 videos/month, 1 min max per video, 30+ languages, watermark not removed); Creator $29/mo (30 min max, 175+ languages/dialects); Pro $49/mo (30 min, plus "editing and proofreading of translation scripts"); Business $149/mo + $20/seat (60 min). Credits per translation minute are not stated — [HeyGen pricing](https://www.heygen.com/pricing)
- An older third-party listing showed output options "English (American accent)" and "English (your accent)". This is dated and may not reflect the current product — [Digidop](https://digidop.com/tools/heygen-video-translate)

**Rask AI**
- The translator page links a "Kannada Video Translator" under "Translate audio into English from 40+ source languages" and claims "Translate into 135+ languages" — [Rask AI Video Translator](https://www.rask.ai/tools/video-translator)
- Voice cloning in 32 of the 135+ languages. Lip-sync "across 135+ languages", preview before export — [Rask AI](https://www.rask.ai/tools/video-translator)
- Edit text line by line, regenerate a segment, and flagged segments for review. Files "up to 5 hours" / "up to 1 GB". API available. 7-day free trial, no card — [Rask AI](https://www.rask.ai/tools/video-translator)
- Lip-sync consumes 3x the standard minutes (third-party, competitor-run review) — [Perso blog, Rask review 2026](https://perso.ai/blog/rask-ai-dubbing-review-2026-features-pricing-how-it-compares)
- The rask.ai/languages URL returned 404 — not available.

**VEED**
- "Supported languages for Dubbing" (updated 19 Aug 2026): Kannada is #42 on the spoken-language list ("languages that we can detect in the original file"), and English is #1 on the "languages we can dub to" list — [VEED Support](https://support.veed.io/en/articles/12781545-supported-languages-for-dubbing)
- Optional lip-sync is mentioned on VEED dubbing pages (search summary) — [VEED AI Dubbing](https://www.veed.io/tools/voice-dubber/ai-dubbing)
- An old VEED page reportedly said dubbing was unavailable in India. That page is about 4 years old and probably outdated (search summary only) — [VEED Support (subtitle languages)](https://support.veed.io/en/articles/6971225-languages-we-support-for-subtitle-generation-and-translation)

**BlipCut**
- The support page lists Kannada among the 77 source languages, "Kannada(IN)" among the 142 target languages, and Kannada in "Supported Languages for Voice Cloning". Lip-sync has no per-language list. The page is undated (© 2026) — [BlipCut supported languages](https://videotranslator.blipcut.com/support/supported-languages.html)

**Kapwing**
- Kannada is on "Supported Target Languages for Translation". Source videos are claimed in "155 different language variants" but not listed. Voice is cloned only for Business/Enterprise. Lip-sync requires Pro/Business. Free users can dub videos under 8 minutes. Dubs use transcription, translation and TTS minutes — [Kapwing Dubbing FAQs](https://www.kapwing.com/help/dubbing-faqs/)

**Synthesia**
- Dubbing 2.0 (15 Jul 2026) claims "over 130" languages and an upgraded lip-sync. Enterprise adds review/refine of transcript and translation without spending credits per pass, segment regeneration and glossary. No language list, voice clone details or prices are given — [Synthesia blog](https://www.synthesia.io/post/introducing-dubbing-2-0)

**Vozo**
- "160+ languages" (no list retrieved), cloned or AI voices (VoiceREAL/VoiceNATIVE), LipREAL lip-sync, line-by-line edit and regenerate, uploads "Up to 2h", and an API link. Pricing was not retrieved — [Vozo Video Translator](https://vozo.ai/video-translator)

**Perso AI (ESTsoft)**
- Plans: Starter $6.99/mo (420 credits, 7 min), Creator $29 (40 min, $0.73/min), Pro $99 (180 min, $0.55/min). "Lip Dubbing" is 2/13/60 min per month. Max length per video: Starter 3 min, Creator 15, Pro 30, Enterprise 60. Script editing on Starter and above. API key access is listed. No language names are given — [Perso pricing](https://perso.ai/pricing)

**Captions / Mirage**
- The dubbing help page (modified 20 Apr 2026) lists about 30 languages including Hindi, Hinglish and Tamil, **not Kannada**. The Lipdub page is similar. These come from a search summary of the official pages — [Mirage help: Dubbing](https://help.mirage.app/docs/captions/dubbing); [Captions help: Lipdub](https://captions.ai/help/docs/captions/lipdub)

**Akool**
- Claims 155+ languages (app page) or 140+ (older FAQ). No list with Kannada was found. A proprietary Lip Sync model option exists — [Akool video translation](https://akool.com/apps/video-translation); [Akool FAQ](https://help.akool.com/video-translation/faq)

**Smartcat**
- "You can choose from the 280 languages supported by Smartcat". Voice-over is available in 36 locales (Kannada not among them, though this matters only for Kannada output). Editing of target text and timecodes in the Subtitle Editor. Voice cloning is not mentioned in the help article — [Smartcat Help](https://help.smartcat.com/add-multilingual-ai-dubbing-videos/)

**Speechify**
- A G2 listing reportedly includes Kannada among Speechify Studio languages. The dubbing direction (Kannada as source) is unverified — [G2 Speechify Studio](https://www.g2.com/products/speechify-speechify-studio-ai-voice-generator/reviews); [Speechify Kannada dubbing page](https://speechify.com/ai-dubbing/kannada/)

**Wavel**
- Language counts conflict (30+, 40+, 100+). Voice cloning for dubbing is claimed, and there is a lip-sync product page. Kannada is not found on any list — [Wavel dubbing](https://wavel.ai/solutions/dubbing); [Wavel lip-sync](https://wavel.ai/solutions/dubbing/lip-sync-dubbing-ai)

**Dubverse (India)**
- Historically English→30+ languages including Kannada (YourStory, Jul 2022 — old). Third-party pricing: Pro ~$18/mo, Supreme ~$30/mo, with cloning on Supreme (conflicting figures). Kannada as a dubbing source is unverified — [YourStory 2022](https://yourstory.com/2022/07/dubverse-saas-startup-breaking-language-barriers-ai); [Toolradar](https://toolradar.com/tools/dubverse)

**Sarvam AI**
- Studio: "Upload a video in any language" and get dubs "in the Indian language of your choice". English is not a target. Kannada is supported as an Indian output. Voice cloning yes. A free tier exists, with access "limited to select partners" — [Sarvam Studio](https://www.sarvam.ai/products/studio.md)
- Dubbing API:
  - "12 Indian target languages".
  - Max file length: 1 h (Starter/Pro) or 4 h (Business).
  - Price: ₹40/min on Starter by default; with editor_flow, ₹80/min (Starter), ₹75/min (Pro), ₹72/min (Enterprise).
  - Lip-sync is not mentioned.
  - Source: [Sarvam docs](https://docs.sarvam.ai/api/api-guides-tutorials/dubbing/overview.md)

**YouTube auto-dubbing**
- Languages that can be dubbed into English: Arabic, Bengali, Chinese, Chinese (Traditional), Dutch, Farsi, French, German, Hebrew, Hindi, Indonesian, Italian, Japanese, Korean, Malayalam, Polish, Portuguese, Punjabi, Romanian, Russian, Spanish, Swahili, Tamil, Telugu, Thai, Turkish, Ukrainian, Urdu, Vietnamese. **Kannada is not included.** Other details:
  - Lip-sync is an "experimental" pilot for select channels.
  - "You cannot edit automatic dubs."
  - Videos over 120 min are ineligible.
  - The help page is undated.
  - Source: [YouTube Help](https://support.google.com/youtube/answer/15569972?hl=en)
- Feb 2026: auto-dubbing expanded to 27 languages for all creators. Expressive speech covers 8 languages (only Hindi among Indic) — [Storyboard18](https://www.storyboard18.com/digital/youtube-expands-auto-dubbing-to-27-languages-adds-more-natural-and-expressive-voices-88923.htm)

**Gan.ai**
- Myna-mini TTS covers 22 Indic languages plus English (Aug 2024). Lip-sync API was listed only as "planned" — [Storyboard18](https://www.storyboard18.com/amp/advertising/gan-ai-launches-myna-mini-a-tts-model-supporting-22-indic-languages-39415.htm)

**Pixa and Google Vids**
- No sources were found showing a Kannada-source speech dubbing product.

**Additional vendor claims found (unverified, vendor SEO pages)**
- VideoDubber has a Kannada→English video page claiming voice clone and lip-sync — [VideoDubber](https://videodubber.ai/translate-kannada-video-to-english/)
- Murf has a "kannada-to-english-video" translator page — [Murf](https://murf.ai/tools/video-translator/kannada-to-english-video)
- Fliki claims Kannada in both directions (search summary) — [Fliki](https://fliki.ai/features/translator/kannada)

### Inferences
- For a ~1-min vertical reel with the mother's own voice plus lip-sync and the ability to fix the English text, the best-documented candidates are:
  - **Meta (free, in-app)**: no text editing.
  - **HeyGen**: Kannada listed; Pro needed for script editing.
  - **Rask**: line editing, lip-sync, Kannada→English page.
  - **VEED and BlipCut**: Kannada source confirmed; BlipCut also clones in Kannada.
  - **ElevenLabs**: best-documented Kannada source with a strength knob, but no lip-sync.
- A Kannada language listing does not guarantee good ASR or translation quality for colloquial spoken Kannada. A test clip is needed on each service.

### Gaps
- Exact per-minute prices for Rask, VEED, BlipCut, Vozo, Akool, Wavel, Speechify and Kapwing were not retrieved.
- Official language lists for Synthesia, Vozo, Perso, Akool, Wavel, Speechify, Dubverse and Rask (cloning list) were not reachable, so Kannada support for them is unverified.
- Whether lip-sync specifically supports Kannada-source videos (as opposed to the English output) is not documented by any vendor. Lip-sync generally depends on the output audio, so this may not matter.
- Gan.ai current products and Pixa: no information found.

## Q4. Known issues: accent drift to American, mistranslation of Indian languages, lip-sync artifacts on vertical video; quality reports

### Takeaway
Little independent, Kannada-specific quality evidence exists. Documented issues are mostly from adjacent contexts:

- ElevenLabs-based clones may lose a non-native accent because only US/UK/AU/CA English accent data exists. This is the closest documented cause of "Indian accent turns American".
- HeyGen translations are reported as literal into Hindi.
- YouTube auto-dubs are called robotic or emotionless.
- Meta's underlying models note ASR variance by accent.

No vertical-video-specific lip-sync failure reports were found.

### Cited Findings
- "ElevenLabs instant cloning cannot always preserve the accent of non-native English speakers... ElevenLabs only has English accent data for US, UK, Australian, and Canadian English". The fix is a Professional Voice Clone, and importing clones into Synthesia is Enterprise-only — [Synthesia Help Center](https://help.synthesia.io/en/articles/9770805-why-is-my-accent-not-being-captured-in-my-voice-clone)
- A forum user found a clone "superimposes a bit of an American accent". The reply was that more samples improve accuracy. This is old and not dubbing-specific — [Core Electronics forum](https://forum.core-electronics.com.au/t/generate-any-voice-using-artificial-intelligence-elevenlabs-speech-synthesis/16315)
- HeyGen into Hindi was found "literal", and native speakers found parts hard to follow. This is one personal anecdote (search summary) — [Ken Kousen Substack](https://kenkousen.substack.com/p/tales-from-the-jar-side-translations)
- HeyGen lip-sync is "strong for major languages, weaker for uncommon ones". This comes from a competitor-run review, so it carries commercial bias — [Perso blog, HeyGen review 2026](https://perso.ai/blog/heygen-ai-dubbing-review-2026)
- HeyGen 2023 test: the face appeared brighter after translation (a color-shift artifact), and the voice was slightly robotic — [The Decoder](https://the-decoder.com/heygen-offers-ai-powered-video-translation-with-impressive-lip-syncing-capabilities/)
- Creators described YouTube AI dubs as "emotionless" and "robotic", and cited wrong-gender voices (search summary) — [Slator](https://slator.com/creators-ai-dubbing-facebook-instagram/)
- Meta's SeamlessM4T documentation (as relayed by a secondary blog) says ASR performance "may vary based on gender, race, accent or language", and that slang/proper-noun translation may be inconsistent — [Medium, exitfund](https://medium.com/@exitfund/metas-ai-dubbing-threatens-the-originality-of-your-voice-and-words-8d5d500621b1) (secondary source)
- Meta's own guidance to reduce errors: one speaker, face the camera, don't cover the mouth, minimize background music/noise — [Instagram Creators blog](https://creators.instagram.com/blog/meta-ai-translations)
- Dubverse voice quality is reported as "uneven across vernacular languages" (vendor-review aggregator) — [rfp.wiki Dubverse](https://www.rfp.wiki/vendors/dubverse)
- Sarvam claims 0.88 speaker similarity and a blind comparison against ElevenLabs, YouTube Dub and Rask. These are vendor-reported figures for Indic outputs — [Sarvam Studio](https://www.sarvam.ai/products/studio.md)

### Inferences
- Background music (common in Instagram reels) will likely hurt ASR and voice-clone quality on every service. Meta explicitly warns about it.
- "Indian accent preserved in English" is not guaranteed by any vendor. ElevenLabs lists no en-IN dialect for dubbing. Expect some drift toward US/UK English, and test the cloning-strength or similarity settings.
- Without transcript editing (Meta, YouTube), Kannada mistranslations cannot be corrected. Services with line-level editing (Rask, Vozo, HeyGen Pro, Perso, Synthesia Enterprise, ElevenLabs Studio v1) allow review by a bilingual person before render.

### Gaps
- No Reddit, Trustpilot or G2 reviews specifically about Kannada → English dubbing were found for any service.
- No reports were found on lip-sync artifacts specific to 9:16 vertical video.
- No independent benchmark of Kannada ASR/translation accuracy across these products was found.
