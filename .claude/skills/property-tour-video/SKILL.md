---
name: property-tour-video
description: Edit a property / house-tour short video (Reels, TikTok, 1080x1920) from phone clips + a voiceover using the saved HyperFrames template in templates/property-tour. Use when the user uploads house footage, a listing description, or a voiceover and asks to edit a property video, "guna template", or "macam video Lombong Besi".
---

# Property tour video (HyperFrames template)

Template: `templates/property-tour/` (read its README.md first). Finished reference project: `rumah-tour/`.

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
