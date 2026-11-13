---
name: sonaxerox-print-pipeline
description: The Sona Xerox online print-order system end to end — the /print page, its Google Apps Script backend (Drive + Sheet), the Windows shop-PC listener (listener.py, SumatraPDF), tokens, order statuses, prices, SECRET, printers — plus the payment/UPI/Razorpay/Cashfree decision history. Use for anything about print orders, an order stuck on NEW, "nothing printed", the listener or its config, Apps Script deployment, changing the per-page price, the order payload, abuse/spam orders, or whether to add online payment — even if the user just says "the printing part".
---

# Print pipeline

```
/print/ (browser) → Apps Script web app → Drive folder SonaXerox-Orders (PDF) + Sheet "Sona Xerox Orders" (row, status NEW)
shop PC listener.py ── every 15 s ── pending → file → (SumatraPDF prints) → done | error
```
Repo: page `print/index.html`, backend `backend/orders-backend.gs` + `backend/drive-cleanup.gs`, shop PC `shop-pc/`. Longer reference: `references/api-and-ops.md`.

## What the page sends (POST, `Content-Type: text/plain`, JSON)
`{fileName, fileData (base64 PDF), pages, color: "bw"|"color", side: "single"|"double", copies, phone (10 digits)}` → `{ok:true, token:"S105"}` or `{ok:false, error}`. Errors the page maps to Gujarati: `No file received`, `Invalid phone number`, `Max 30 pages per order`.
Limits: ≤ 30 pages, ≤ 30 copies, PDF ≤ 15 MB (page side). When the customer prints only some pages, the page **builds a new PDF with just those pages** — what is stored is exactly what is printed.

## Status lifecycle
`NEW → PRINTED | ERROR → "(file deleted)"` after 24 h (hourly trigger on the **Head** deployment). **`NEW` is never deleted** (PC may have been off). Token = `S` + (100 + sheet row). Sheet columns: Time, Token, Phone, Colour, Sides, Copies, Pages, File URL, File ID, Status.

## Printing rules (listener)
Printer by colour (`PRINTER_COLOR` vs `PRINTER_BW`, same name allowed); SumatraPDF settings `simplex|duplexlong, color|monochrome, <N>x if copies>1, fit`. Settings live in `listener.config.json` next to `listener.py` (git-ignored) — replacing `listener.py` never wipes them.

## Changing the price
Edit `print/index.html` **in three places**: constants `RATE_BW` / `RATE_COLOR`; the dictionary entries `per2`, `per10`, `priceIdle` (Gujarati *and* English). Run `tests/test_print_pdf.py` — it fails while any text still shows the old rate. Double-sided costs the same per page today; if that changes the price maths and breakdown text both change. The price on screen is an estimate computed in the browser; staff confirm at the counter.

## Security (public repo, public Apps Script URL)
- `SECRET` protects the listener endpoints only; keep the real value only in Apps Script + shop PC config. The template value `CHANGE-ME-sona-valod-2026` is public — confirm the live one differs.
- **`doPost` is open → anyone can send an order and it prints.** Known risk; mitigations in `docs/BACKLOG.md` (approve-before-print, per-phone rate limit, payment first).
- Phones are stored in the Sheet; PDFs are deleted after 24 h.

## Payment — what was decided (Oct 2026)
Pay at pickup for now. **Do not recommend the "YouPI-PG" repo**: forgeable payment confirmation (public/guessable/hard-coded pairing tokens, optional signature), publicly known default secrets, an app that forwards *all* SMS incl. OTPs, whole-mailbox Gmail access, an anonymous renamed Baileys WhatsApp library, and no licence (`"license": "Commercial"`). Options kept: UPI link/QR + staff "Paid" button; or a licensed gateway — Razorpay UPI 2% + 18% GST (≈ 2.36%); Cashfree 1.95% + GST (≈ 2.30%) with a new-merchant 0% platform-fee offer to 31 Mar 2027 (GST on the notional fee still applies ≈ 0.35%). Re-check current pricing before advising. A gateway means: KYC, Terms/Privacy/Refund/Contact pages, server-side confirmation, and **unpaid orders must not print**.

## Troubleshooting
| Symptom | Likely cause / action |
|---|---|
| order stays `NEW` | listener not running (Task Manager → `pythonw.exe`) or PC off; start `start-listener-hidden.vbs`; check `listener.log` |
| `Unauthorized` in log | `SECRET` differs between Apps Script and `listener.config.json` |
| `CONFIG PROBLEMS` | the log lists which setting (URL, default secret, printer name, Sumatra path) |
| order → `ERROR` | wrong printer name / Sumatra path / printer offline; see log |
| site shows old price/text | hard refresh; `tools/verify_live.py` |
| customer says "order failed" | Apps Script quota/outage, or file > 15 MB / > 30 pages |
After editing the Apps Script: **Deploy → Manage deployments → ✏️ → New version** (the URL stays the same).
