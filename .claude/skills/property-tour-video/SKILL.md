---
name: property-tour-video
description: Edit a property / house-tour short video (Reels, TikTok, 1080x1920) from phone clips + a voiceover using the saved HyperFrames template in templates/property-tour. Use when the user uploads house footage, a listing description, or a voiceover and asks to edit a property video, "guna template", or "macam video Lombong Besi".
---

# Property tour video (HyperFrames template)

Template: `templates/property-tour/` (read its README.md first). Finished reference project: `rumah-tour/`.

Always (user's standing instruction): put the agent's phone number **0198395315** on every video:
set `"phone": "0198395315"` in config.json (shows top-right for the whole film and under the CTA).

Voiceover: when the user has no recording, use ElevenLabs (API key is saved on the cloud environment for
api.elevenlabs.io) with the voice "English Gina" (English) or "Gina slow voice" (Malay); model `eleven_v3`,
stability 0.5, similarity 0.85. Check the take with Whisper (names, CTA word); if a quoted word was skipped,
rephrase ("comment the word X") and regenerate. Then `align_script.py`-style alignment of the known script
onto Whisper timings for exact captions (see taman-pahlawan-v2/align_script.py).
TikTok reach (user's rule): never show the price as big on-screen text and never speak the price in the
voiceover; say "affordable" and end with a "Comment / DM for info" CTA instead (VO: "comment or DM me for more info").
Also avoid hard-sell words TikTok demotes ("selling", "for sale", "buy now", "promo", "price") in on-screen text and VO;
e.g. write "Phase 2" not "Phase 2 now selling".
Cover headline (user's rule): the big yellow words are the landmark people instantly recognise (big mall, town,
LRT station, highway — e.g. "NEAR AEON BUKIT TINGGI", "NEAR KSL MALL KLANG"), never price and never the little-known
taman name; the taman/project name goes in the small italic line. Use "NEXT TO" only when truly adjacent, else "NEAR".
Pronunciation fixes for ElevenLabs (spell in vo_say only, keep correct spelling in vo_display/captions):
"free-hold," for freehold (else heard as "three-hole"), "Araka" for Araca, "AEON Mall ..." (not bare "AEON").
Never claim distances/landmarks you have not verified; label estimates and ask the user to confirm.

ASK FIRST (user's standing instruction): before changing or re-rendering any video, describe the planned
change (what text/voice/scene changes, with the exact new wording) and wait for the user's OK. Snapshots/previews
for discussion are fine; do not render or push a changed video until the user approves.

Workflow:
1. Inspect uploads: `ffprobe` each clip (duration, rotation, HDR transfer), make contact sheets
   (`ffmpeg -vf "fps=3,scale=270:-1,tile=6x3"`) and look at them to name each shot (land, hall, bedroom, bathroom…).
2. `templates/property-tour/new_project.sh <folder> <voiceover>`.
3. `tools/prep_clips.sh <folder> <clips…>` (SDR conversion is mandatory for phone HDR footage). Use `SLOW=2` on
   60fps clips that are too short; extract stills for graphic-heavy scenes. Drop clips that repeat another shot.
4. Transcribe the voiceover with `tools/transcribe.py` (Malay: model `medium`, lang `ms`). Never guess what the
   voiceover says. If huggingface.co is blocked, ask for the script or the network change. Fix misheard
   names via `fix_words`.
5. Edit `config.json`: `text` from the listing copy, `scenes` cut on spoken words, `graphics` cues on the word that
   names the thing. Strongest claim first (hook).
6. `python3 build.py` → `npx hyperframes check` → `npx hyperframes snapshot --at …` and read the frames.
7. Preview first (`npx hyperframes preview --background`, report port 3002). Render only when the user says so:
   `npx hyperframes render -q delivery --sdr -o renders/<name>.mp4`.
