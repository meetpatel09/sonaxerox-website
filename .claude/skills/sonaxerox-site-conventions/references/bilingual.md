# Gujarati / English pattern

**Static pages (dashboard, simple pages)** — put both texts on the element and swap them:
```html
<span class="name" data-gu="પ્રિન્ટ ઓર્ડર પેજ" data-en="Print order page">પ્રિન્ટ ઓર્ડર પેજ</span>
<script>
  var KEY='sx_lang', btn=document.getElementById('langBtn');
  function setLang(l){ document.body.dataset.lang=l; document.documentElement.lang=l;
    document.querySelectorAll('[data-gu]').forEach(function(el){ el.textContent=el.dataset[l]; });
    btn.textContent = l==='gu' ? 'English' : 'ગુજરાતી'; try{localStorage.setItem(KEY,l)}catch(e){} }
  btn.onclick=function(){ setLang(document.body.dataset.lang==='gu'?'en':'gu'); };
  var s=null; try{s=localStorage.getItem(KEY)}catch(e){}; if(s==='en') setLang('en');
</script>
```
**Dynamic pages (/print/)** — one dictionary `DICT = {key:{gu:'…', en:'…'}}`, `t(key, {n:3})` with `{n}` placeholders, static nodes marked `data-i18n` / `data-i18n-html` / `data-i18n-ph`, and every *dynamic message stored as a descriptor* `{key, params}` (not as finished text) so it re-translates live when the language is toggled. Server error strings are mapped to keys.

## Glossary (use these words; they were chosen with the owner)
| English | Gujarati |
|---|---|
| page(s) | પેજ |
| copies | કોપી |
| colour | કલર (step title: રંગ) |
| black & white | બ્લેક & વ્હાઇટ |
| single side / double side | એક બાજુ / બંને બાજુ |
| total price | કુલ કિંમત |
| pay at pickup | લેતી વખતે ચૂકવો |
| order received | ઓર્ડર મળી ગયો |
| token | ટોકન |
| new order | નવો ઓર્ડર |
| send to shop printer | દુકાનના પ્રિન્ટર પર મોકલો |
| upload PDF | PDF અપલોડ કરો |
| clean document / Auto photo / As is | સાફ દસ્તાવેજ / ઓટો ફોટો / જેમ છે તેમ |
Addressing the father/co-owner: "પપ્પા" + "તમે". Ask a Gujarati speaker to read any new customer-facing text once.
