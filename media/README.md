# media/

Web-ready assets only. Generate them with `../tools/convert.sh`, do not drop raw
exports in here.

    ./tools/convert.sh loop    "J:/path/to/source.mp4" mobile-crane 4 8
    ./tools/convert.sh feature "J:/path/to/source.mp4" telco-rebrand

- **loop** strips audio, for the hover grid. Keep to 5 to 15 seconds.
- **feature** keeps audio, for a click-to-play card.
- Trailing numbers are optional start and duration in seconds.

Stills need no conversion. Drop a jpg straight in and reference it with `<img>` in a
tile; the hover script ignores tiles that contain no video, so stills and clips mix
freely in the same grid.

## Naming

Kebab-case, describe the object, never the brand or the client.

- `mobile-crane`, not a manufacturer name
- `road-paver`, not a manufacturer name
- `telco-rebrand`, not the client or product name

Same rule that keeps EbS and client names off the CV. The object is what shows the
skill; the badge on it adds nothing and carries risk.

## Watch out for

- **Never Git LFS.** GitHub Pages serves the pointer file instead of the video and the
  clip silently breaks.
- **100MB hard limit per file.** The conversion settings keep clips far under this.
- **webm does not always win.** On high-motion footage x264 can beat VP9. The script
  warns you; when it does, ship the mp4 alone.
