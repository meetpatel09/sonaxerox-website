# Scan geometry (math used in /scan)

Let the original photo be `w × h`, centre `c0`. Total turn θ = 90°·q + fine (clockwise). `R(θ)` rotates about the centre.
* `toRot(p) = c1 + R(θ)(p − c0)`, `fromRot` is the inverse; the rotated canvas is the bounding box `bw = |w cosθ| + |h sinθ|`, `bh = |w sinθ| + |h cosθ|`.
* **Vertical** (φ = slider °, f = 1.3·max(bw, bh)), about the centre of the rotated canvas, with (x, y) relative to it:
  `K(x, y) = ( f·x / (f + y·sinφ),  f·y·cosφ / (f + y·sinφ) )` — φ > 0 magnifies the top (top wider).
  Inverse: `y = v·f / (f·cosφ − v·sinφ)`, `x = u·(f + y·sinφ) / f`.
* View bounding box = bbox of `K(toRot(photo corners))`. Stable coordinates `S = K(toRot(p))` do not move when only φ changes — used to keep a user-placed frame fixed on screen: `corners0' = fromS_new(toS_old(corners0))`.
* Painting (φ ≠ 0): for each view pixel → S → `Ki` → `fromRot` → bilinear sample of the original; outside the photo stays transparent (white for the real scan).
* Scan: `warpPerspective(src, corners(shifted by quarter turns), outW, outH, whiteOutside=true)`, with `outW = max(top, bottom)`, `outH = max(left, right)` measured on the original-coordinate quad, capped at 2400 px.
* Starting frame when φ ≠ 0: largest upright rectangle centred in the view quad (binary search on scale, corners tested with a convex-polygon test) × 0.92.

Test photos: `tests/make_fixtures.py::keystone(±24°)` builds a checkerboard as `photo(p) = flat(K_t0(p))` so slider = t0 returns the flat board exactly.
