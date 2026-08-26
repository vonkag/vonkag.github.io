#!/usr/bin/env bash
# Turn a source export into web-ready files for the portfolio.
#
#   ./tools/convert.sh loop    <input> <name> [start] [duration]
#   ./tools/convert.sh feature <input> <name> [start] [duration]
#
#   loop     silent, no audio, for the hover grid. Keep these 5 to 15 seconds.
#   feature  keeps audio, for a click-to-play card. Fine up to a minute or so.
#
# Examples
#   ./tools/convert.sh loop    "J:/.../crane.mp4" crane 4 8
#   ./tools/convert.sh feature "J:/.../TelCo_Env_Custom_2_4Wipe.mp4" telco-rebrand
#
# Outputs into media/: <name>.mp4, <name>.webm, <name>-poster.jpg
set -euo pipefail

# ffmpeg is not on PATH on this machine. Shutter Encoder ships a full build with
# libx264 and libvpx-vp9, which is all we need.
FF="${FF:-/c/Program Files/Shutter Encoder/Library/ffmpeg.exe}"
[ -x "$FF" ] || { echo "ffmpeg not found at: $FF"; exit 1; }

MODE="${1:?mode required: loop | feature}"
SRC="${2:?input file required}"
NAME="${3:?output name required}"
START="${4:-}"
DUR="${5:-}"

OUT="$(cd "$(dirname "$0")/.." && pwd)/media"
mkdir -p "$OUT"

TRIM=()
[ -n "$START" ] && TRIM+=(-ss "$START")
[ -n "$DUR" ]   && TRIM+=(-t "$DUR")

# 1280 wide is plenty for a portfolio tile and roughly quarters the file against 1080p.
# -2 keeps height even, which H.264 requires.
SCALE="scale=1280:-2"

case "$MODE" in
  loop)    FPS=30; AUDIO=(-an);                             CRF264=28; CRFVP9=33 ;;
  feature) FPS=30; AUDIO=(-c:a aac -b:a 128k -ac 2);        CRF264=25; CRFVP9=31 ;;
  *) echo "mode must be loop or feature"; exit 1 ;;
esac

echo "==> $NAME  ($MODE)"

# H.264 fallback. +faststart moves the index to the front so playback can begin
# before the whole file has downloaded.
"$FF" -hide_banner -loglevel error -y "${TRIM[@]}" -i "$SRC" \
  -vf "$SCALE,fps=$FPS" -c:v libx264 -crf "$CRF264" -preset slow -pix_fmt yuv420p \
  "${AUDIO[@]}" -movflags +faststart "$OUT/$NAME.mp4"

# VP9, roughly 30% smaller. Listed FIRST in <source> so browsers prefer it.
VP9AUDIO=(-an)
[ "$MODE" = "feature" ] && VP9AUDIO=(-c:a libopus -b:a 96k)
"$FF" -hide_banner -loglevel error -y "${TRIM[@]}" -i "$SRC" \
  -vf "$SCALE,fps=$FPS" -c:v libvpx-vp9 -crf "$CRFVP9" -b:v 0 -row-mt 1 \
  "${VP9AUDIO[@]}" "$OUT/$NAME.webm" 2>/dev/null

# Poster frame, taken 1s in so it is never a black fade-up.
POSTER_SS="${START:-0}"
"$FF" -hide_banner -loglevel error -y -ss "$(awk "BEGIN{print $POSTER_SS+1}")" -i "$SRC" \
  -vframes 1 -vf "$SCALE" -q:v 3 "$OUT/$NAME-poster.jpg"

ls -lh "$OUT/$NAME.mp4" "$OUT/$NAME.webm" "$OUT/$NAME-poster.jpg" | awk '{print "   ", $5, $9}'

# VP9 usually wins, but not always. On high-motion footage (wipes, fast camera moves)
# x264 can come out smaller. Browsers take the FIRST <source> they can play, so put
# whichever is smaller first, or drop the webm entirely if it lost.
m=$(stat -c%s "$OUT/$NAME.mp4"); w=$(stat -c%s "$OUT/$NAME.webm")
if [ "$w" -gt "$m" ]; then
  echo "   NOTE: webm is larger than mp4 here. List the .mp4 <source> FIRST,"
  echo "         or just delete $NAME.webm and ship the mp4 alone."
fi
