#!/usr/bin/env bash
# Convert phone footage (HEVC / HDR-HLG, rotated) to 1080x1920 SDR H.264 the renderer handles well.
# Usage: tools/prep_clips.sh <project-dir> <clip>...          -> assets/clips/<name>.mp4 (silent b-roll)
#        KEEP_AUDIO=1 tools/prep_clips.sh <project-dir> <clip> -> keeps the clip's sound (talking head)
#        SLOW=2 tools/prep_clips.sh <project-dir> <clip>       -> 2x slow motion, saved as <name>_slow.mp4 (best from 60fps)
set -euo pipefail
P="$1"; shift; mkdir -p "$P/assets/clips"
for f in "$@"; do
  n=$(basename "${f%.*}"); n=${n#*-}  # drop upload hash prefix "abcd1234-"
  trc=$(ffprobe -v error -select_streams v -show_entries stream=color_transfer -of csv=p=0 "$f")
  tone="scale=1080:1920"
  case "$trc" in arib-std-b67) tone="$tone,zscale=t=bt709:m=bt709:p=bt709:tin=arib-std-b67:min=bt2020nc:pin=bt2020:npl=200";;
                 smpte2084)    tone="$tone,zscale=t=bt709:m=bt709:p=bt709:tin=smpte2084:min=bt2020nc:pin=bt2020:npl=200";; esac
  vf="fps=30,$tone,format=yuv420p"; out="$P/assets/clips/$n.mp4"
  if [ -n "${SLOW:-}" ]; then vf="setpts=${SLOW}*PTS,$vf"; out="$P/assets/clips/${n}_slow.mp4"; fi
  aud="-an"; [ -n "${KEEP_AUDIO:-}" ] && aud="-c:a aac -b:a 160k"
  ffmpeg -hide_banner -loglevel error -y -i "$f" -vf "$vf" -c:v libx264 -preset fast -crf 19 $aud \
    -color_trc bt709 -color_primaries bt709 -colorspace bt709 -movflags +faststart "$out"
  printf '%s  %ss\n' "$out" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")"
done
