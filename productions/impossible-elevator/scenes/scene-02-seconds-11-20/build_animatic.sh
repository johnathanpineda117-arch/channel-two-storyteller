#!/usr/bin/env bash
# Rebuild the 10.00s Scene 02 animatic from locked keyframes.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
KF="$HERE/keyframes"
WORK="${TMPDIR:-/tmp}/elevator-scene-02-rebuild"
mkdir -p "$WORK"

scale() {
  ffmpeg -y -hide_banner -loglevel error -i "$1" \
    -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" "$2"
}

scale "$KF/00-button-mash.png" "$WORK/00.png"
scale "$KF/02-first-blackout.png" "$WORK/02.png"
scale "$KF/03-avatar-closer.png" "$WORK/03.png"
scale "$KF/05-avatar-meters-away.png" "$WORK/05.png"
scale "$KF/07-sprint-doors-closing.png" "$WORK/07.png"
scale "$KF/08-hand-catches-doors.png" "$WORK/08.png"
scale "$KF/09-floor-13-reveal.png" "$WORK/09.png"
ffmpeg -y -hide_banner -loglevel error -f lavfi -i "color=c=black:s=1080x1920:d=1" -frames:v 1 "$WORK/black.png"

cat > "$WORK/concat.txt" <<'EOF'
file '00.png'
duration 2.00
file '02.png'
duration 0.35
file '03.png'
duration 1.65
file '02.png'
duration 0.35
file '05.png'
duration 1.65
file '07.png'
duration 2.00
file '08.png'
duration 1.00
file '09.png'
duration 0.75
file 'black.png'
duration 0.25
file 'black.png'
EOF

ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i "$WORK/concat.txt" \
  -r 30 -pix_fmt yuv420p -c:v libx264 -preset fast -crf 18 "$WORK/picture.mp4"

# Audio is generated beside this script's last mux; reuse repo audio if present,
# otherwise picture-only.
if [[ -f /tmp/elevator-scene-02/audio.wav ]]; then
  ffmpeg -y -hide_banner -loglevel error \
    -i "$WORK/picture.mp4" -i /tmp/elevator-scene-02/audio.wav \
    -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart \
    "$HERE/scene-02-seconds-11-20.mp4"
else
  ffmpeg -y -hide_banner -loglevel error \
    -i "$WORK/picture.mp4" -an -movflags +faststart \
    "$HERE/scene-02-seconds-11-20.mp4"
fi

echo "wrote $HERE/scene-02-seconds-11-20.mp4"
