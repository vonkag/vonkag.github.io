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

## Source footage notes

**In-headset VR training recordings** (Drive: `GeneXR/Portfolio Content/Energy Wheel/EBS Recordings`)

| Source | Maps to | Usable |
|---|---|---|
| `EBS001` | Module 1 | Thin. One fixed elevated vantage for five minutes, little variation |
| `EBS002_1` | Module 2, Part A | Best of the set. Ladders, precast panels, exterior, interior gantry |
| `EBS002_2` | Module 2, Part B | ❌ **Nothing usable. Do not cut from this.** Every frame is buried under assessment UI, and it reuses Module 1's environment |
| `EBS003` | Modules 3 and 4 | Strongest. Three distinct environments: roadside utility, trench, precast yard |

Keep cuts named by module (`m1-`, `m2-`, `m3-`) so the training structure survives.

⚠ **Most frames in all four have UI panels over them.** The panels are the product, not
Von's art, so clean frames are the constraint on what can be cut.

⚠ **Never name the product or the client** on anything public. These are VR safety
training modules, nothing more specific.

### Rejected cuts, do not redo

| Cut | Why |
|---|---|
| `m2-ladder-panel` (2A @ 0:13) | Too static. Replaced with `m2-ladder-climb` (2A @ 1:03), which has the worker actually climbing |
| `m3-trench` | ❌ Scene renders against **white, with no HDRI environment**. Reads as unfinished |
| `m3-pump-boom` | ❌ Same. White background, missing HDRI |

⏰ **If the trench and pump-boom scenes are worth re-recording with the HDRI in place,
that has to happen before system access ends on 25 September 2026.** After that the
source is gone and those scenes cannot be recovered.

**Judging cuts from contact sheets has a known blind spot:** frames sampled every 8 to 20
seconds show composition but not motion. Expect a couple of picks per batch to be duller
in motion than they looked as stills. `m2-ladder-panel` was exactly that.
