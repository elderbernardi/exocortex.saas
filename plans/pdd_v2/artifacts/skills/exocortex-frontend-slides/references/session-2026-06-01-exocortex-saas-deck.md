# Session 2026-06-01 — Exocórtex.SaaS deck

## Context

Created a premium HTML/PDF/ZIP deck about Exocórtex.SaaS from a free-form brief. The deck explained the product idea, use cases, domain portability, and the relationship between Exocórtex methodology and Hermes Agent as the execution/evolution engine.

## Durable workflow notes

- Treat this class of request as `speaker-led` unless the user asks for reading-first slides.
- For Exocórtex/Hermes product decks, a strong default visual direction is technical-editorial: dark navy/green-black background, bone paper contrast, restrained IFSul green accents, rare red accent.
- Preserve Markdown source even when the HTML is authored directly from the brief.
- Use browser visual QA on at least the cover and one dense slide. Dense matrix slides can look acceptable in DOM overflow checks but still feel generic or crowded.
- DOM overflow check used successfully:

```js
(() => {
  const slides=[...document.querySelectorAll('.slide')];
  return slides.map((s,i)=>({
    i:i+1,
    overflow:s.scrollWidth>s.clientWidth||s.scrollHeight>s.clientHeight,
    sw:s.scrollWidth,
    sh:s.scrollHeight,
    title:(s.querySelector('h1,h2')?.textContent||'').slice(0,80)
  }));
})()
```

## Chrome PDF fallback

If Playwright is unavailable but Chrome/Chromium exists, export PDF with:

```bash
/usr/bin/google-chrome-stable \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --print-to-pdf="$ART/exports/deck.pdf" \
  --print-to-pdf-no-header \
  "file://$ART/exports/deck.html"
```

This is a fallback, not a replacement for the skill's normal Playwright script.

## Viewer controls

Navigation controls inside HTML are useful during review, but can visually pollute screenshots and presentations. Good compromise:

```css
.deck-controls {
  opacity: .14;
  transition: opacity .2s ease;
}
.deck-controls:hover { opacity: .95; }
@media print {
  .deck-controls, .edit-hotzone, .edit-toggle { display: none !important; }
}
```

## Manifest / ZIP sequencing

When the ZIP includes `manifest.json`, rebuild in this order:

1. hash source/html/pdf and write manifest;
2. create ZIP;
3. hash ZIP and add ZIP entry to manifest;
4. optionally rebuild ZIP so it contains the manifest that lists the ZIP entry;
5. understand that the ZIP hash changes if the manifest inside it changes. Do not chase infinite fixed-point hashes. For local delivery, final manifest outside the ZIP is the authoritative receipt.
