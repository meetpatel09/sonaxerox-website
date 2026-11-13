# Decoding photos — checklist

1. `loadViaImg`: `new Image()` + `URL.createObjectURL` (EXIF applied by the browser).
2. `loadViaBitmap`: `createImageBitmap(file, {imageOrientation:'from-image'})`, falling back to no options. Works when `blob:` images are blocked.
3. `loadViaDataUrl`: `FileReader.readAsDataURL` → `Image`.
4. HEIC: name/type contains `hei[cf]` **or** bytes 4–7 = `ftyp` and brand ∈ {heic, heix, hevc, hevx, heim, heis, hevm, hevs, mif1, msf1} → `heic2any({blob, toType:'image/jpeg', quality:0.92})` (first element if an array) → decode again through 1–3. Show a "Converting your iPhone photo…" overlay; on failure say *internet* vs *unreadable*.
5. Draw directly into a canvas at the final cap (`imageSmoothingQuality='high'`); `fillRect(white)` first; close `ImageBitmap`s.
Messages (English): "Could not open that image — try a JPG or PNG photo" · "Could not convert this iPhone (HEIC) photo — check your internet connection, or choose a JPG instead" · "Could not read this iPhone (HEIC) photo — please choose a JPG instead".
The print page currently decodes with steps 2 then 1 and does **not** convert HEIC (backlog).
