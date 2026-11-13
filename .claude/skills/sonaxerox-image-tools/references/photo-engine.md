# Photo engine parameters (/print)

| Step | Parameters | Why |
|---|---|---|
| working size | 1400 px long side (preview) / 3508 px (PDF) | speed vs A4 @ 300 dpi |
| lighting estimate | 160 px copy; max-filter r = 4; two box blurs r = 3; per channel | sees through text, follows shadows, removes yellow cast |
| shadow floor | 55% of the 90th-percentile paper level | a big dark block (ID photo) is never brightened > ~1.8× |
| paper white | levels `lo` = 1.5th percentile (≤ 110), `hi` = 228 | residual 5–10% shading becomes pure white |
| ink | gamma 1.2 (colour) / 1.7 (B&W) | darker, bolder text for printing |
| Auto photo | stretch 0.5–99.5 percentile (`lo ≤ 60`, `hi ≥ 120`), gamma → mean 0.46 clamped 0.55–1.5, saturation × 1.12 | lifts under-exposed photos (mean 54 → 97 in tests) |
| sharpen | unsharp mask, box radius `round(long/1400)`, amount `slider/50` (+0.6 doc modes, +0.3 photo) | restores crispness after scaling |
| auto style | `looksLikeDoc`: ≥ 40% pale low-colour pixels, 0.8–40% ink, ≤ 45% mid-tones | pre-selects Clean document for paper photos |
| PDF fallbacks | quality/dpi: .92/300 → .82/220 → .72/170 → .62/130 | stay under 15 MB |

Quality bars from tests: paper brightness 124–255 → 255 (std 0); stamp stays red; dark block stays < 60; B&W output has R = G = B.
