---
name: sonaxerox-image-tools
description: Engineering notes for the browser image/PDF tools on sonaxerox.in — the /scan page (corner dots, turn, straighten, the upright Vertical slider, homography scan), the photo clean-up editor on /print (Clean document, Auto photo, A4 PDF), HEIC and blob/CSP-safe photo decoding, and the Aadhaar Scale-text and Burn tools. Use before changing /scan, the photo editor in /print or /aadhaar-card, and whenever a photo won't open, comes out sideways/blurry/crooked, a scan looks skewed, or the user asks for rotate/straighten/perspective/crop/brightness/"make it print friendly" features.
---

# Image tools — invariants and pitfalls

Read the relevant reference before touching the code: `references/scan-geometry.md`, `references/photo-engine.md`, `references/decoding.md`.

## Scan page (`/scan/`) — the model
- Original pixels (`srcCanvas`, ≤ 2800 px) are **never modified**. View = original → *turn/straighten* (similarity) → *vertical* (perspective) → screen.
- The 4 dots live in **original-photo coordinates** (`corners0`). Turning and straightening carry them with the photo. **Vertical is the exception**: an untouched starting frame (`frameDefault`) is re-fitted as an upright rectangle inside the corrected photo; once the user drags a dot, the frame stays fixed on screen while the photo is squeezed beneath it. Reason: four points already determine a perspective, so Vertical can only change the scan by moving the frame relative to the photo.
- The scan = **one homography from the original pixels** (dots → rectangle), white outside the photo. After quarter turns the dot order is rotated (`shift = (4 − q) % 4`) so the page follows what the user sees. Never re-sample through an intermediate rotated image.
- Preview painting: fast canvas path when Vertical = 0; per-pixel bilinear path otherwise (≈ 40 ms at 1100 px). The slider is a normal `<input type=range>` rotated −90° (works on old browsers; the native vertical-slider CSS does not).

## Photo clean-up (`/print/`) — the model
Per photo: decode (EXIF-aware) → working copy ≤ 1400 px for live preview → on *Done*, each photo is re-decoded at ≤ 3508 px **one at a time** (memory), processed, laid out on A4 (Fit = 10 mm border, Fill = cover; landscape if wider than tall) and embedded as JPEG. PDF over 15 MB → rebuilt at four lower quality/resolution steps.
"Clean document" divides out a lighting estimate per channel (max-filter radius 4 + two box blurs on a 160 px copy, floor at 55% of the paper level so big dark areas are never over-brightened), snaps paper to white (`hi = 228`), darkens ink (gamma 1.2; B&W 1.7). Tuned on a shadowed, yellow, sideways certificate: paper brightness 124–255 → exactly 255, text and stamp kept, dark ID-photo block kept.

## Decoding photos (all pages)
Try in order: `<img>` from a blob URL (applies EXIF) → `createImageBitmap(file, {imageOrientation:'from-image'})` → `FileReader` data URL. The first alone fails inside sandboxed previews that block `blob:` images. **HEIC** (iPhone/AirDrop) cannot be decoded by desktop browsers: detect by name/type or the `ftyp` brand bytes and convert with **heic2any 0.0.4** loaded on demand from cdnjs; distinguish "converter could not load" (internet) from "file unreadable". Draw straight into the capped canvas (iOS Safari limits canvas area to ~16.7 MP); fill white first so transparent PNGs aren't black. Never label a bug in our own code as "can't open that image" — decode errors and processing errors are reported separately.

## Aadhaar tools (`/aadhaar-card/`)
*Scale text*: lift the selected box, 4 corner handles, proportional by default (Shift = free), old spot left as is, Enter/Esc, optional sharpen after upscaling. *Burn*: gamma-based darkening weighted so near-white paper is untouched; per-stroke undo; limited to the selection if one exists. Both operate on the card canvas (1011 × 638 px = 85.6 × 54 mm at 300 dpi).

## Before you change any of it
Run `python3 tests/run_all.py --only scan` / `--only print_photos` / `--only aadhaar`. Add a fixture whose right answer is exact. Check phone touch and the 320×520 screen.
