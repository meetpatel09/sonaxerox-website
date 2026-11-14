#!/usr/bin/env python3
"""Makes the A4 counter poster for /print/ : a QR code + the steps in Gujarati.

    pip install segno                      # only needed to run this script (pure Python, not a test dependency)
    .venv/bin/python tools/make_print_poster.py

Writes assets-src/print-poster/poster.html (editable) and poster.pdf (print this on A4).
The rates and limits on the poster are typed into the text below — if the price changes on the page, change them here too.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "assets-src" / "print-poster"
URL = "https://sonaxerox.in/print/"

try:
    import segno
except ImportError:
    sys.exit("Missing 'segno' — run:  .venv/bin/pip install segno   (then run this script again)")

qr = segno.make(URL, error="h")          # H = still scans if the print gets scratched or dirty
qr_svg = qr.svg_inline(border=0, omitsize=True, dark="#161513", scale=1)

HTML = """<!DOCTYPE html>
<html lang="gu"><head><meta charset="UTF-8"><title>Sona Xerox — QR પ્રિન્ટ પોસ્ટર</title>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Work+Sans:wght@400;600&family=Hind+Vadodara:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  @page{size:A4; margin:0;}
  *{box-sizing:border-box;}
  html,body{margin:0; padding:0;}
  body{width:210mm; height:297mm; font-family:'Hind Vadodara','Kohinoor Gujarati','Gujarati MT',sans-serif; color:#161513; background:#fff; position:relative; overflow:hidden;}
  .bar{display:flex; height:7mm;} .bar i{flex:1;} .bar i:nth-child(1){background:#00AEEF;} .bar i:nth-child(2){background:#EC008C;} .bar i:nth-child(3){background:#F5C400;} .bar i:nth-child(4){background:#161513;}
  .wrap{padding:8mm 14mm 0;}
  .brand{display:flex; align-items:center; gap:4mm;}
  .dots{display:grid; grid-template-columns:repeat(2,5mm); grid-template-rows:repeat(2,5mm); gap:1mm;}
  .dots span{border-radius:50%;} .dots span:nth-child(1){background:#00AEEF;} .dots span:nth-child(2){background:#EC008C;} .dots span:nth-child(3){background:#F5C400;} .dots span:nth-child(4){background:#161513;}
  .brand b{font-family:'Archivo Black',sans-serif; font-size:22pt; font-weight:400; letter-spacing:.3pt;}
  .brand small{display:block; font-size:11pt; color:#726F68; margin-top:.5mm;}
  h1{font-size:33pt; line-height:1.2; margin:5mm 0 1.5mm; font-weight:700;}
  .lead{font-size:15pt; color:#4a4843; margin:0 0 5mm; line-height:1.4;}
  .qrrow{display:flex; align-items:center; gap:8mm; margin-bottom:7mm;}
  .qrbox{flex:0 0 86mm; width:86mm; height:86mm; border:2.2mm solid #EC008C; border-radius:6mm; padding:5mm; background:#fff;}
  .qrbox svg{display:block; width:100%; height:100%;}
  .scan{flex:1;}
  .scan .big{font-size:23pt; font-weight:700; line-height:1.3; margin:0 0 3mm;}
  .scan .big em{font-style:normal; color:#EC008C;}
  .scan .url{display:inline-block; font-family:'Work Sans',sans-serif; font-weight:600; font-size:15pt; background:#F5F5F3; border:.4mm solid #DEDCD5; border-radius:3mm; padding:2mm 4mm;}
  .scan .en{font-family:'Work Sans',sans-serif; font-size:10.5pt; color:#726F68; margin:3mm 0 0;}
  ol{list-style:none; margin:0; padding:0; counter-reset:n;}
  ol li{counter-increment:n; display:flex; gap:4mm; align-items:flex-start; font-size:17pt; line-height:1.4; margin-bottom:4mm;}
  ol li::before{content:counter(n); flex:0 0 10.5mm; height:10.5mm; border-radius:50%; background:#161513; color:#fff; font-family:'Work Sans',sans-serif; font-weight:600; font-size:15pt; display:flex; align-items:center; justify-content:center; margin-top:.8mm;}
  ol li:nth-child(5)::before{background:#EC008C;}
  ol li small{display:block; font-size:12.5pt; color:#726F68; line-height:1.35;}
  ol li b{font-weight:700;}
  .prices{display:flex; gap:4mm; margin:4mm 0 0;}
  .prices div{flex:1; border:.5mm solid #DEDCD5; border-radius:4mm; padding:3mm 4mm; background:#F5F5F3; font-size:13.5pt; line-height:1.35;}
  .prices div b{display:block; font-family:'Hind Vadodara',sans-serif; font-size:21pt;}
  .prices .c b{color:#EC008C;} .prices .y{background:#FFF8DC; border-color:#F5C400;}
  .foot{position:absolute; left:0; right:0; bottom:0; background:#161513; color:#fff; padding:4mm 14mm 5mm; display:flex; justify-content:space-between; align-items:center; font-size:13pt;}
  .foot b{font-family:'Work Sans',sans-serif; font-size:15pt;}
</style></head><body>
<div class="bar"><i></i><i></i><i></i><i></i></div>
<div class="wrap">
  <div class="brand"><div class="dots"><span></span><span></span><span></span><span></span></div><div><b>Sona Xerox</b><small>સોના ઝેરોક્ષ · વાલોડ</small></div></div>
  <h1>મોબાઇલથી પ્રિન્ટ ઓર્ડર કરો</h1>
  <p class="lead">લાઇનમાં રાહ જોયા વગર — તમારા ફોનથી ફાઇલ મોકલો, અમે પ્રિન્ટ તૈયાર રાખીશું.</p>

  <div class="qrrow">
    <div class="qrbox">__QR__</div>
    <div class="scan">
      <p class="big">ફોનનો <em>કેમેરા</em> ખોલો અને આ QR કોડ સ્કેન કરો</p>
      <span class="url">sonaxerox.in/print</span>
      <p class="en">Scan with your phone camera to order prints</p>
    </div>
  </div>

  <ol>
    <li><span>QR કોડ સ્કેન કરો અને ખુલેલા પેજ પર <b>PDF અથવા ફોટો</b> પસંદ કરો.
      <small>PDF WhatsApp માં આવી હોય? પહેલા WhatsApp માં તે PDF એક વાર ખોલો, પછી અહીં “Recent” માં ઉપર દેખાશે.</small></span></li>
    <li><span><b>પેજ, રંગ</b> (બ્લેક &amp; વ્હાઇટ કે કલર), <b>એક કે બંને બાજુ</b> અને <b>કોપી</b> પસંદ કરો.</span></li>
    <li><span>તમારો <b>10 અંકનો મોબાઇલ નંબર</b> લખો. કુલ કિંમત આપોઆપ દેખાશે.</span></li>
    <li><span><b>“દુકાનના પ્રિન્ટર પર મોકલો”</b> દબાવો. તમને <b>ટોકન નંબર</b> મળશે.</span></li>
    <li><span>કાઉન્ટર પર <b>ટોકન નંબર બતાવો</b>, પૈસા ચૂકવો અને પ્રિન્ટ લઈ જાઓ.</span></li>
  </ol>

  <div class="prices">
    <div>બ્લેક &amp; વ્હાઇટ<b>₹2 / પેજ</b></div>
    <div class="c">કલર<b>₹10 / પેજ</b></div>
    <div class="y">પૈસા<b>દુકાને ચૂકવવા</b></div>
  </div>
</div>
<div class="foot"><span>એક ઓર્ડરમાં વધુમાં વધુ 30 પેજ · 15 MB. મોટા કામ માટે દુકાને પૂછો.</span><span>WhatsApp / ફોન: <b>77788 05780</b></span></div>
</body></html>
"""

OUT.mkdir(parents=True, exist_ok=True)
html = HTML.replace("__QR__", qr_svg)
(OUT / "poster.html").write_text(html, encoding="utf-8")
qr.save(str(OUT / "qr-print-page.svg"), border=2, scale=10, dark="#161513")
qr.save(str(OUT / "qr-print-page.png"), border=2, scale=20, dark="#161513")

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto((OUT / "poster.html").as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(500)
    over = pg.evaluate("document.querySelector('ol').getBoundingClientRect().bottom + document.querySelector('.prices').getBoundingClientRect().height + 20 > document.querySelector('.foot').getBoundingClientRect().top")
    pg.pdf(path=str(OUT / "poster.pdf"), width="210mm", height="297mm", print_background=True, prefer_css_page_size=True)
    b.close()
print("QR points to:", URL)
print("written:", *(str(f.relative_to(REPO)) for f in sorted(OUT.iterdir())), sep="\n  ")
if over:
    print("WARNING: the text is touching the footer — shorten a line or reduce font sizes.")
