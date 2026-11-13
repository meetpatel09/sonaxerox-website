# Decisions (and why)

Each entry: what we chose · why · what we gave up. Dates are when it was decided.

**D1 — Static pages on GitHub Pages, no build step** (Jul 2026). Free, nothing to run or patch, anyone can edit a file, any version can be restored from git. *Gave up:* shared code between pages (some image code exists in two pages).

**D2 — Everything is processed in the browser** (Jul 2026). Aadhaar / voter IDs and customers' documents never reach a server of ours; no server cost. *Gave up:* heavy work depends on the customer's phone (photos are capped at 2800 px / 3508 px).

**D3 — Google Apps Script as the only backend** (Jul 2026). Free, Drive + Sheet included, the shop already uses Google. *Gave up:* speed (a second or two per call), quotas, no real queue. The shop PC *polls* it because Apps Script cannot call into the shop.

**D4 — Pages from the repo root; developer folders hidden by `_config.yml`** (Nov 2026). Zero change to URLs and no settings to switch. The alternative (`site/` folder + a deploy workflow) is cleaner but needs a Pages-settings change and risks downtime. *Gave up:* the site still builds with Jekyll (harmless: plain HTML is copied as-is).

**D5 — Payment: pay at pickup for now** (Oct 2026).
* *Rejected:* the open-source "YouPI-PG" UPI gateway a friend suggested. Audit of its code: payment confirmation can be **forged** (pairing token is a public default / guessable / a hard-coded constant, and the signature check is optional); its sample config ships publicly known secrets; its Android app forwards **every SMS** (OTPs included) and allows plain HTTP; Gmail access is the whole mailbox and the login redirect is hard-wired to the developer's domain; the WhatsApp part is an anonymous renamed copy of the unofficial Baileys library (WhatsApp can ban the number); it has **no licence** (`package.json` says "Commercial") although it was offered as "free and open source".
* *Options kept:* (a) UPI link/QR with the amount, staff tap "Paid" — free, manual; (b) a licensed gateway. Numbers checked on **17 Oct 2026** (re-check before deciding): Razorpay standard UPI = 2% + 18% GST on the fee (≈ 2.36%); Cashfree standard 1.95% + GST (≈ 2.30%), and a new-merchant offer of 0% platform fee on the first ₹20 lakh **until 31 Mar 2027**, but GST on the notional fee is still charged (≈ 0.35% effective). UPI itself has zero MDR by rule.
* *Why not now:* the customer is at the shop anyway; a gateway needs KYC, policy pages and a small server for confirmation. Revisit when online-only orders become common.

**D6 — The ₹ sign is bundled in the page** (Oct 2026). On a PC whose fonts have no ₹ (older Windows) it showed as an empty box. A ~1 KB subset of Poppins (SIL OFL) is embedded for U+20B9 only (`tools/templates/rupee-face.css`). A test reproduces the problem with Arial-like fonts.

**D7 — Scan geometry** (Nov 2026). Dots live in original-photo coordinates; the scan is one homography from the original pixels; the Vertical slider keeps a user-placed frame fixed on screen. Reason: a 4-point homography already fixes any perspective, so the slider had to *move the frame relative to the photo* to change the result at all. See `docs/ARCHITECTURE.md` §3.

**D8 — Tests are real-browser tests with faked network and synthetic photos** (Nov 2026). Mocks of the DOM would not have caught: the ₹ box, blocked `blob:` images, the footer covering Send on small phones, the missing scan correction after a 90° turn. Each of those became a test.

**D9 — Private tools are `noindex`, and `robots.txt` does *not* list them** (Nov 2026). A `Disallow` line would advertise the secret paths; `<meta name="robots" content="noindex">` is enough and is enforced by a test. (`scan`, `aadhaar-card` and `voter-card` were missing it before this setup.)

**D10 — Customer pages default to Gujarati** (Oct 2026). Wording: "પેજ" (page), "કોપી" (copy), "કલર" (colour), "બ્લેક & વ્હાઇટ". Have a native speaker read new Gujarati text once.
