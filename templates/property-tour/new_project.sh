#!/usr/bin/env bash
# Start a new property-tour video from this template.
# Usage: templates/property-tour/new_project.sh <new-folder> [voiceover-file]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$1"; VO="${2:-}"
[ -e "$DEST" ] && { echo "$DEST already exists"; exit 1; }
cp -r "$HERE/skeleton" "$DEST"
cp "$DEST/config.example.json" "$DEST/config.json"
name=$(basename "$DEST")
sed -i "s/\"name\": \"[^\"]*\"/\"name\": \"$name\"/" "$DEST/package.json"
printf '{\n  "id": "%s",\n  "name": "%s",\n  "createdAt": "%s"\n}\n' "$name" "$name" "$(date -u +%FT%TZ)" > "$DEST/meta.json"
mkdir -p "$DEST/assets/clips" "$DEST/assets/stills" "$DEST/assets/vo" "$DEST/renders"
"$HERE/tools/make_sfx.sh" "$DEST" 90 >/dev/null
if [ -n "$VO" ]; then
  ffmpeg -hide_banner -loglevel error -y -i "$VO" -ac 2 -ar 48000 -c:a aac -b:a 160k "$DEST/assets/vo/voiceover.m4a"
fi
echo "Created $DEST — next: prep clips, transcribe, edit config.json, python3 build.py (see templates/property-tour/README.md)"
