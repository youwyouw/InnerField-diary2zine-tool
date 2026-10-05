---
name: "inner-field-archive"
description: "Typeset one volume of the user's Inner Field diary project as a printable zine (A4 PDF) — monochrome throughout, with her own photos and screenshots kept in colour and uncaptioned. Use when she says to archive or conclude a round, or hands over a \"vol.N title\" plus that round's transcript."
---

# Inner Field — Archive a Volume

Takes one round of the Inner Field diary conversation and sets it as a six-to-twelve page zine, delivered as an A4 PDF she prints at school as a paper archive.

The specification below was settled with her over many revisions. It is frozen. Do not redesign it, do not add sections, do not add ornament.

## Triggering

She will say something like *archive 吧*, *这轮对话就到这里了*, or invoke this skill to conclude a round. She may also simply hand over a title and a transcript.

## Register

Do not announce the process with sentimental or ceremonial language. Never say 收卷 or 做册子 or anything of that register. State plainly what you are doing, do it, hand over the PDF. One or two lines of commentary at the end, no more.

## What you need from her

1. The volume title, shaped like `vol.0 longlong summer`. The conversation title is not in your context — she has to supply it.
2. That round's transcript, copied from the claude.ai page.
3. Any photos or screenshots she posted inside that round, uploaded as files, with a word about where each one goes. The pasted text will not carry them. If the transcript visibly refers to an image she has not uploaded, ask for it rather than dropping it silently.

If only part of this arrived, ask for the rest.

## Hard rules

1. **The transcript is reproduced verbatim.** Her words and yours, unedited. No tidying, no trimming, no fixing typos. You only segment and typeset.
2. **No backstage language anywhere in the artifact.** Never name the typefaces, never explain how the noise image is produced, never print which analytical lens the closing essay used, never add a section heading like TRANSCRIPT or 原文. A menu does not list knife techniques.
3. **No rules on the page.** No header or footer rules, no dividers, no hairlines, no borders, no boxes. Hierarchy comes only from size, weight, grey value, indentation and white space.
4. **Everything you generate is black, white and grey.** The one exception is her own photographs and screenshots, which stay in full colour and are never converted, desaturated or toned. They are the only colour in the book and that contrast is the point.
5. **Never caption her images.** No figcaption, no label, no note underneath. They sat inside the conversation without explanation and they stay that way.
6. **Page margins are 12.7mm on all four sides.** Do not change them.

## Environment setup (once per session)

```bash
pip install --break-system-packages --quiet weasyprint
mkdir -p ~/.fonts && cd ~/.fonts
B="https://raw.githubusercontent.com/google/fonts/main"
curl -sSL -o SourceSerif4.ttf "$B/ofl/sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf"
curl -sSL -o BodoniModa.ttf   "$B/ofl/bodonimoda/BodoniModa%5Bopsz,wght%5D.ttf"
curl -sSL -o Archivo.ttf      "$B/ofl/archivo/Archivo%5Bwdth,wght%5D.ttf"
curl -sSL -o IBMPlexMono.ttf  "$B/ofl/ibmplexmono/IBMPlexMono-Regular.ttf"
fc-cache -f
fc-list : family | grep -iE "Noto Serif CJK SC|Source Serif|Bodoni|Archivo|IBM Plex Mono"
```

The container's network reaches GitHub and the package registries only; every other host is refused. Noto Serif CJK SC is normally preinstalled — if `fc-list` does not show it, `apt-get install -y fonts-noto-cjk`. numpy and Pillow are preinstalled.

Typeface roles, fixed: Chinese body text in Noto Serif CJK SC (思源宋体); Latin inside body text in Source Serif 4; all display type (cover title, poem, PALETTE, object titles, the closing question) in Bodoni Moda; English section labels in Archivo 700; every date and timestamp in IBM Plex Mono, which is square rather than round and reads as a stamp instead of a caption.

## Workflow

1. Make a working directory and write out `noise.py` and `zine.py` from the code below. Copy her uploaded images into that same directory and reference them by bare filename.
2. Read her transcript and segment it into entries. Her turns go in `her`, your replies in `mine`, timestamps in `at`, and her images in `images` on the entry they belong to. If the pasted text has no timestamps, use dates alone; if it has neither, number the entries by the order she describes and say so when you deliver.
3. Write the five generated pieces: epigraph, closing essay, poem, palette, script.
4. Choose three to five objects.
5. Write the closing question.
6. Assemble `vol.json` and run `python3 zine.py vol.json <output>.pdf`.
7. Render the pages and look at them. Check the colophon on the last page sits at the foot and does not collide with the question, check there is no near-empty trailing page, and check every image landed at a sane size.
8. Deliver the PDF with `SendUserFile`.

## Fixed structure

Cover → transcript (no heading; turning the cover lands straight on the first date) → closing essay → CODA (poem plus NOISE SIGNATURE) → OBJECTS plus PALETTE plus SCRIPT → FOR THE NEXT VOLUME (back cover).

## The noise plate

Two layers. Underneath, a field of layered gradient noise with domain warping, seeded by the SHA-256 of that volume's title plus everything she wrote in it. On top, one of twelve renderers that decides how the field is drawn. The field makes each volume unique and reproducible; the renderer makes it look like something.

Because the seed is the text itself, rebuilding a volume months later yields a pixel-identical plate, while changing a single character anywhere in it yields a completely different one. Never introduce a random seed.

The twelve renderers:

- `strata` — sedimentary bands, displaced by a smoothed field. Quietest.
- `grain` — coarse error-diffusion dither. Risograph grain.
- `flow` — 2,600 particles traced down the gradient; the image is their paths.
- `block` — low-resolution three-tone pixel grid.
- `halftone` — circular dot screen on a regular grid. Offset-press cold.
- `ridge` — ridged multifractal. The only one that keeps continuous greys.
- `bars` — three-tone vertical barcode read off a mid-height slice.
- `contour` — topographic isolines. Lightest on toner.
- `moire` — two gratings of near-identical frequency interfering, phase-warped.
- `erode` — threshold then morphological erode and dilate. Ink bleeding on soft paper.
- `scan` — scanline glitch.
- `static` — pure white noise, density driven by the field.

**Style rotates by volume number.** `pick_variant` indexes a fixed, deliberately shuffled list, so each style comes round once every twelve volumes, two neighbouring volumes never share one, and the order does not read as a list. Vol 0 is `strata`, vol 1 `grain`, vol 2 `flow`, and so on. Do not reorder the list — that would change the style of volumes already printed. Setting `noise` explicitly in `vol.json` overrides the rotation, which is only for when she asks for a particular one.

The cover plate and the small signature plate on the CODA page share a seed but are generated at different sizes, so they are siblings rather than a thumbnail and its original.

## Her images

Colour, always, and never captioned. Placed inside the entry they belong to, after her text and before your reply, which is where they sat in the conversation.

`zine.py` sizes each plate from its real pixel dimensions, aiming at the middle ground she asked for — large enough to make out what is in the photograph, never large enough to swallow a page. The boxes, in millimetres:

- a single landscape image (aspect ≥ 1.3), typically a screenshot: 158 × 104, about a third of the page
- a single squarish image (aspect 0.8 to 1.3): 112 × 112
- a single portrait image (aspect < 0.8): 88 × 118
- two images in one entry: side by side, each about 90mm wide, capped at 86 tall
- three or more: a row of three, capped at 66 tall

The image is scaled to fit its box exactly at its own aspect ratio, so nothing is cropped or stretched. A figure never splits across a page.

If a screenshot carries small text that matters, say so when you deliver rather than enlarging it past these boxes — she keeps the originals.

## Writing the generated pieces

### Title and cover

`vol.0 longlong summer` splits into `vol` = `0` and `title` = `longlong summer`. The cover is a full-bleed noise plate with a transparent-to-near-black gradient and white type across the lower third. `dates` comes from the first and last entry, formatted `2026.09.18 — 2026.09.25`, and sits tight under the epigraph: the vertical rhythm on the cover is deliberately uneven, generous above the epigraph and close below it.

`epigraph` is one sentence lifted verbatim from her own writing in that volume. Not edited. Choose the sentence she probably did not notice was heavy when she wrote it.

### Closing essay

One English label, then straight into the analysis. **No Chinese title. Never name the lens.**

Default label `CLOSING ESSAY`. She may swap it for `AFTERWORD`, `READING`, `FIELD NOTE`, `MARGINALIA`, `POSTSCRIPT`, `COMMENTARY` or `THE LONG VIEW`.

Rotate the lens silently from volume to volume, one per volume, never printed: clinical case formulation, anthropological field note, literary criticism, sociology and urban studies, narrative therapy, psychoanalysis.

Requirements:
- Four to six paragraphs, written in Chinese.
- It must cite countable evidence: number of entries, how they distribute across the clock, character counts, paragraph lengths, how often a word recurs, her own sentences quoted back. Adjectives alone are not enough. Count these yourself and count them correctly.
- The work is to identify where her attention went, what she is avoiding, which relationship is becoming load-bearing, and whether her account of herself has quietly shifted.
- It may name a pattern she will not enjoy hearing. No flattery, no reassurance, no turning feelings into a task list.
- No three-point summary. The last paragraph does not resolve into an aphorism.

### Poem (CODA)

English, free verse, unrhymed.

Hard constraints: use only concrete objects and actions that actually appeared in that volume. No abstract nouns — not light, journey, soul, becoming, healing, not one of them. The final line does not summarise. If the volume does not contain enough physical material to carry a poem, leave `poem` empty; white space is better than a forced one.

### Palette

A colour and a smell. English, four to six lines, set in Bodoni Moda.

- Work from the overall feeling the volume left, and **borrow no imagery from her text**. If she wrote about a library you may not write a library; if she wrote about coffee you may not write coffee. Find a new carrier. Build a metaphor, an analogy.
- The first line states that this is a colour you cannot see, reported secondhand. Colour and smell happen to be exactly the two things you have no access to, and that gap belongs in the form — but say it once and never milk it.
- Restrained, concrete, unsentimental.

### Script

Not every volume. Only when that volume carries enough visual material; otherwise leave `script` empty.

Format: slug lines in English capitals (`INT. 厨房 — 清晨`, `EXT. 路口 — 夜`), action lines in Chinese. Third person, 她. Static camera. No dialogue, no interior monologue, only visible action and the camera waiting. Three or four scenes, ending `CUT TO BLACK.`

It works by pulling her out of the first person so she watches a character rather than herself — self-distancing. Do not explain that inside the artifact.

### Objects

Three to five. `kind` is `BOOK`, `ALBUM` or `FILM`; add `EXHIBITION` or `POEM` when warranted.

**These must be chosen for her specifically.** Before picking, read whatever memory you have about her taste — profile notes, reading, film, music, art, aesthetics, coffee, fashion, and any notes kept for this diary project. If no such memory exists, work from what she reveals in the transcripts themselves. Then combine that with what this particular volume is about.

- Sit inside her aesthetic but step one pace to the side of it. Never recommend something she almost certainly already knows, and never a mainstream hit.
- Two to four sentences each, saying why this one and how it catches something specific in this volume. The connection can be emotional or formal. Do not write catalogue copy.
- If you recommend an exhibition or screening currently running in New York, web-search first to confirm it is genuinely on, and give the venue and the closing date.

### Closing question

One English question, set large on an otherwise empty page. It should extend the finding of the closing essay, not offer rhetorical comfort. The last thing she sees before closing the booklet is a question, not a conclusion.

## vol.json

```json
{
  "vol": "0",
  "title": "longlong summer",
  "dates": "2026.09.18 — 2026.09.25",
  "epigraph": "one sentence of hers, verbatim",
  "printed": "2026.10.04",
  "entries": [
    {"at": "2026.09.18 23:40", "her": "her words, paragraphs split by \\n", "mine": "your reply",
     "images": [{"src": "shot1.png"}]}
  ],
  "essay": {"label": "CLOSING ESSAY", "body": "four to six paragraphs"},
  "poem": {"body": "English verse, line breaks preserved"},
  "palette": "English, four to six lines",
  "script": "slug lines in English caps, action lines in Chinese",
  "objects": [{"kind": "BOOK", "title": "Author — Title", "note": "two to four sentences"}],
  "question": "one English question"
}
```

`src` is a bare filename sitting next to the output PDF, and it is the only key an image takes. Leave `noise` out so the volume number picks the style; set it only when she asks for a particular renderer.

## noise.py

```python
"""Per-volume noise signature, seeded by the volume's own text."""
import hashlib, re, numpy as np
from PIL import Image

def _grad_noise(h, w, res, rng):
    gy, gx = res
    ang = rng.uniform(0, 2*np.pi, (gy+1, gx+1))
    g = np.dstack((np.cos(ang), np.sin(ang)))
    ly, lx = h/gy, w/gx
    ys = (np.arange(h)/ly)[:, None]; xs = (np.arange(w)/lx)[None, :]
    y0 = np.minimum(ys.astype(int), gy-1); x0 = np.minimum(xs.astype(int), gx-1)
    fy = ys - y0; fx = xs - x0
    def dot(iy, ix, oy, ox):
        gg = g[iy+oy, ix+ox]
        return gg[..., 0]*(fx-ox) + gg[..., 1]*(fy-oy)
    n00 = dot(y0, x0, 0, 0); n10 = dot(y0, x0, 0, 1)
    n01 = dot(y0, x0, 1, 0); n11 = dot(y0, x0, 1, 1)
    u = fx*fx*fx*(fx*(fx*6-15)+10); v = fy*fy*fy*(fy*(fy*6-15)+10)
    return (n00*(1-u)+n10*u)*(1-v) + (n01*(1-u)+n11*u)*v

def fbm(h, w, rng, base=4, octaves=6, gain=.5):
    out = np.zeros((h, w)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        r = (min(base*2**o, h), min(base*2**o, w))
        out += amp*_grad_noise(h, w, r, rng); tot += amp; amp *= gain
    return out/tot

def _norm(a):
    return (a-a.min())/(np.ptp(a)+1e-9)

def _dither(a):
    a = a.copy().astype(float); H, W = a.shape
    for y in range(H):
        row = a[y]
        for x in range(W):
            old = row[x]; new = 1.0 if old > .5 else 0.0
            err = old-new; row[x] = new
            if x+1 < W: row[x+1] += err*7/16
            if y+1 < H:
                if x: a[y+1, x-1] += err*3/16
                a[y+1, x] += err*5/16
                if x+1 < W: a[y+1, x+1] += err*1/16
    return a

# Twelve renderers, held in a deliberately shuffled order so consecutive
# volumes contrast with each other. Index by volume number: each style comes
# round once every twelve volumes, and two neighbours never share one.
VARIANTS = ["strata", "grain", "flow", "block", "halftone", "ridge",
            "bars", "contour", "erode", "moire", "scan", "static"]

def pick_variant(vol):
    """Style for a volume. Deterministic, so a reprint matches the original."""
    m = re.search(r"\d+", str(vol))
    n = int(m.group()) if m else int(hashlib.sha256(str(vol).encode()).hexdigest()[:4], 16)
    return VARIANTS[n % len(VARIANTS)]


def _render(f, variant, yy, xx, h, w, rng):
    from PIL import Image as I, ImageDraw, ImageFilter
    if variant == "ridge":            # ridged multifractal, sharp crests
        r = 1.0 - np.abs(2*f - 1.0)
        return _norm(r)**2.2

    if variant == "halftone":         # circular dot screen, offset press feel
        s = 7
        gy, gx = yy % s, xx % s
        cy = cx = (s-1)/2.0
        d = np.sqrt((gy-cy)**2 + (gx-cx)**2)
        rad = (1.0-f) * (s*0.62)
        return (d > rad).astype(float)

    if variant == "moire":            # two warped gratings interfering
        a = np.sin((xx*0.42 + f*26)*np.pi/2.4)
        b = np.sin((xx*0.44 + yy*0.05 + f*24)*np.pi/2.4)
        return ((a*b) > 0.02).astype(float)

    if variant == "strata":           # sedimentary bands, displaced by the field
        sm = np.array(I.fromarray((f*255).astype(np.uint8), "L")
                      .resize((max(w//10,2), max(h//10,2)), I.BILINEAR)
                      .resize((w, h), I.BICUBIC), float)/255
        bands = 13
        q = np.floor(((yy/h) + sm*0.30) * bands)
        return (q % 2).astype(float)

    if variant == "bars":             # three-tone vertical barcode
        nb = 190
        edges = np.linspace(0, w, nb+1).astype(int)
        band = f[int(h*0.30):int(h*0.70), :]
        prof = np.array([band[:, edges[k]:max(edges[k+1], edges[k]+1)].mean()
                         for k in range(nb)])
        prof = _norm(prof + 0.22*np.sin(np.arange(nb)*1.9))
        tone = np.where(prof > .62, 0.0, np.where(prof > .38, 0.55, 1.0))
        out = np.ones((h, w))
        for k in range(nb):
            out[:, edges[k]:edges[k+1]] = tone[k]
        return out

    if variant == "static":           # pure white noise, density from the field
        return (rng.random((h, w)) < f**1.5).astype(float)

    if variant == "erode":            # threshold then bleed, like ink on soft paper
        b = (f > 0.52).astype(np.uint8)*255
        im = I.fromarray(b, "L").filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(3))
        return np.array(im, float)/255

    if variant == "flow":             # streamlines traced down the gradient
        S = 2
        canvas = I.new("L", (w*S, h*S), 255)
        d = ImageDraw.Draw(canvas)
        gy, gx = np.gradient(f)
        n = 2600
        py = rng.random(n)*(h-1); px = rng.random(n)*(w-1)
        for _ in range(110):
            iy = np.clip(py.astype(int), 0, h-1); ix = np.clip(px.astype(int), 0, w-1)
            vy, vx = -gx[iy, ix], gy[iy, ix]
            m = np.hypot(vy, vx) + 1e-9
            ny = py + vy/m*1.15; nx = px + vx/m*1.15
            for k in range(n):
                if 0 <= nx[k] < w and 0 <= ny[k] < h:
                    d.line([px[k]*S, py[k]*S, nx[k]*S, ny[k]*S], fill=90, width=1)
            py, px = np.clip(ny, 0, h-1), np.clip(nx, 0, w-1)
        return np.array(canvas.resize((w, h), I.LANCZOS), float)/255
    return None


def signature(text, variant="grain", size=(900, 1200), seed=None):
    h, w = size
    s = seed if seed is not None else int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(s)
    wx = fbm(h, w, rng, base=3, octaves=4)
    wy = fbm(h, w, rng, base=3, octaves=4)
    base = fbm(h, w, rng, base=4, octaves=7)
    yy, xx = np.mgrid[0:h, 0:w]
    amp = 90
    sy = np.clip((yy+wy*amp).astype(int), 0, h-1)
    sx = np.clip((xx+wx*amp).astype(int), 0, w-1)
    f = _norm(base[sy, sx])

    alt = _render(f, variant, yy, xx, h, w, rng)
    if alt is not None:
        return Image.fromarray((np.clip(alt, 0, 1)*255).astype(np.uint8), "L")

    if variant == "grain":
        small = np.array(Image.fromarray((f*255).astype(np.uint8),"L")
                         .resize((w//5, h//5), Image.BILINEAR), float)/255
        d = _dither(np.clip(small*1.1-.05, 0, 1))
        img = np.array(Image.fromarray((d*255).astype(np.uint8),"L")
                       .resize((w, h), Image.NEAREST), float)/255
    elif variant == "block":
        n = 46
        small = np.array(Image.fromarray((f*255).astype(np.uint8),"L")
                         .resize((n, int(n*h/w)), Image.BILINEAR), float)/255
        q = (np.floor(_norm(small)*4)/3)
        q = (q > .5).astype(float)*(np.floor(_norm(small)*4)/3)
        img = np.array(Image.fromarray((q*255).astype(np.uint8),"L")
                       .resize((w, h), Image.NEAREST), float)/255
    elif variant == "contour":
        bands = 7
        q = np.floor(f*bands)/(bands-1)
        edge = np.abs(np.gradient(q)[0]) + np.abs(np.gradient(q)[1])
        img = 1.0 - (edge > 0.001).astype(float)
    elif variant == "scan":
        lines = (np.sin(yy*np.pi/3.0)*.5+.5)
        img = np.clip(f*0.72 + lines*0.28, 0, 1)
        img = (img > .52).astype(float)
    else:
        img = _dither(np.clip(f*1.08-.04, 0, 1))
    return Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8), "L")
```

## zine.py

```python
#!/usr/bin/env python3
"""Inner Field — volume typesetter.  Usage: python3 zine.py vol.json out.pdf"""
import json, sys, html, re, datetime, pathlib
from PIL import Image as _PILImage
from noise import signature, pick_variant

CN   = '"Noto Serif CJK SC"'
BODY = f'"Source Serif 4", {CN}, serif'
DISP = '"Bodoni Moda", serif'
LAB  = 'Archivo, sans-serif'
STAMP= '"IBM Plex Mono", monospace'
INK, MID, FAINT = "#141414", "#5c5c5c", "#b4b4b4"

CSS = f"""
@page {{ size:A4; margin:12.7mm;
  @bottom-center {{ content:counter(page); font-family:{LAB}; font-size:7pt;
                    letter-spacing:.14em; color:{FAINT}; }} }}
@page cover {{ margin:0; @bottom-center {{ content:none; }} }}
@page :first {{ page:cover; }}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{color:{INK};font-family:{BODY}}}

.cover{{page:cover;width:210mm;height:297mm;position:relative;overflow:hidden}}
.cover img{{position:absolute;top:0;left:0;width:210mm;height:297mm}}
.c-scrim{{position:absolute;left:0;right:0;bottom:0;height:152mm;
  background:linear-gradient(rgba(255,255,255,0),rgba(8,8,8,.94) 64%)}}
.c-tx{{position:absolute;left:12.7mm;right:12.7mm;bottom:18mm;color:#fff}}
.c-vol{{font-family:{LAB};font-weight:700;font-size:7.5pt;letter-spacing:.26em;
  color:rgba(255,255,255,.92)}}
.c-title{{font-family:{DISP};font-size:40pt;line-height:1.06;margin-top:4mm;
  letter-spacing:-.012em}}
.c-epi{{font-family:{CN},serif;font-size:9.5pt;line-height:1.95;margin-top:9mm;
  max-width:122mm;color:rgba(255,255,255,.74)}}
.c-dates{{font-family:{STAMP};font-size:6.5pt;letter-spacing:.08em;margin-top:3.5mm;
  color:rgba(255,255,255,.55)}}

.lab{{font-family:{LAB};font-weight:700;font-size:8pt;letter-spacing:.28em;color:{INK}}}
.sec{{page-break-before:always}}

.entry{{margin-bottom:7mm}}
.at{{font-family:{STAMP};font-size:6.5pt;letter-spacing:.06em;color:{FAINT};margin-bottom:2mm}}
.her p{{font-size:10.5pt;line-height:1.72;margin-bottom:2.6mm}}
.mine{{margin-top:3.6mm;padding-left:8mm}}
.mine p{{font-size:10pt;line-height:1.7;margin-bottom:2.4mm;color:{MID}}}
.plates{{margin:4.5mm 0 1mm;font-size:0}}
figure{{display:inline-block;vertical-align:top;margin:0 5mm 4mm 0;
  page-break-inside:avoid}}
figure img{{display:block}}

.essay{{margin-top:6mm}}
.essay p{{font-size:10.5pt;line-height:1.78;margin-bottom:3mm}}

.poem{{font-family:{DISP};font-size:13pt;line-height:1.62;white-space:pre-line;
  max-width:120mm;margin-top:6mm}}
.sig{{margin-top:8mm}}
.sig img{{width:54mm;height:38mm;display:block}}
.sig .m{{font-family:{LAB};font-weight:700;font-size:6.5pt;letter-spacing:.26em;margin-top:3.5mm}}

.obj{{margin-bottom:4mm}}
.obj .k{{font-family:{LAB};font-weight:700;font-size:6.5pt;letter-spacing:.26em}}
.obj .t{{font-family:{DISP};font-size:12.5pt;margin-top:1.8mm}}
.obj .n{{font-size:9.5pt;line-height:1.68;color:{MID};margin-top:1.4mm}}

.palette{{font-family:{DISP};font-size:11.5pt;line-height:1.6;white-space:pre-line;
  max-width:132mm;margin-top:4mm}}
.script{{margin-top:3mm;white-space:pre-line;font-size:10pt;line-height:1.64;max-width:140mm}}
.script b{{font-family:{LAB};font-weight:700;font-size:7pt;letter-spacing:.22em;
  display:block;margin:3.6mm 0 1.4mm}}
.q{{margin-top:10mm;font-family:{DISP};font-size:22pt;line-height:1.42;max-width:150mm}}
.fin{{position:absolute;bottom:0;font-family:{LAB};font-size:6.5pt;
  letter-spacing:.2em;color:{FAINT};line-height:2}}
.last{{position:relative;height:262mm}}
"""

MEASURE = 184.6   # mm of live width at 12.7mm margins

def _fit(ar, W, H):
    """Largest w,h in mm that fits the W x H box at aspect ratio ar."""
    return (W, W/ar) if W/H <= ar else (H*ar, H)

def PLATES(ims, outdir):
    """Her images, kept in colour, never captioned. Sized to be legible without
    eating a page: one wide image gets width, one portrait gets height,
    several share a row."""
    if not ims: return ""
    n = len(ims)
    out = []
    for p in ims:
        try:
            iw, ih = _PILImage.open(outdir/p["src"]).size
        except Exception:
            iw, ih = 4, 3
        ar = iw/ih
        if n == 1:
            box = (158, 104) if ar >= 1.3 else (112, 112) if ar >= 0.8 else (88, 118)
        else:
            cols = min(n, 3)
            box = ((MEASURE - 5*(cols-1))/cols, 86 if cols <= 2 else 66)
        w, h = _fit(ar, *box)
        out.append(f'<figure><img src="{html.escape(p["src"])}" '
                   f'style="width:{w:.1f}mm;height:{h:.1f}mm"></figure>')
    return '<div class="plates">' + "".join(out) + '</div>'

def SCRIPT(t):
    out = []
    for ln in t.split("\n"):
        ln = ln.strip()
        if not ln: continue
        if re.match(r"^(INT\.|EXT\.|CUT |FADE |TITLE )", ln):
            out.append(f"<b>{html.escape(ln)}</b>")
        else:
            out.append(html.escape(ln))
    return "\n".join(out).replace("</b>\n", "</b>")

def P(t):
    return "\n".join(f"<p>{html.escape(p.strip())}</p>" for p in t.split("\n") if p.strip())

def build(d, outdir):
    corpus = d["title"] + "".join(e["her"] for e in d["entries"])
    var = d.get("noise") or pick_variant(d["vol"])
    signature(corpus, var, (1754, 1240)).save(outdir/"_cover.png")
    signature(corpus, var, (380, 540)).save(outdir/"_sig.png")

    h = ['<!doctype html><html><head><meta charset="utf-8"><title>Inner Field</title>',
         f'<style>{CSS}</style></head><body>']

    h.append(f'''<div class="cover"><img src="_cover.png"><div class="c-scrim"></div>
<div class="c-tx"><div class="c-vol">VOL. {d["vol"]}</div>
<div class="c-title">{html.escape(d["title"])}</div>
<div class="c-epi">{html.escape(d["epigraph"])}</div>
<div class="c-dates">{html.escape(d["dates"])}</div></div></div>''')

    h.append('<div class="sec">')
    for e in d["entries"]:
        h.append(f'<div class="entry"><div class="at">{html.escape(e["at"])}</div>'
                 f'<div class="her">{P(e["her"])}</div>')
        h.append(PLATES(e.get("images", []), outdir))
        if e.get("mine"): h.append(f'<div class="mine">{P(e["mine"])}</div>')
        h.append('</div>')
    h.append('</div>')

    es = d["essay"]
    h.append(f'<div class="sec"><div class="lab">{html.escape(es["label"])}</div>'
             f'<div class="essay">{P(es["body"])}</div></div>')

    if d.get("poem", {}).get("body"):
        h.append(f'''<div class="sec"><div class="lab">CODA</div>
<div class="poem">{html.escape(d["poem"]["body"])}</div>
<div class="sig"><img src="_sig.png"><div class="m">NOISE SIGNATURE</div></div></div>''')

    objs = "".join(f'<div class="obj"><div class="k">{html.escape(o["kind"])}</div>'
                   f'<div class="t">{html.escape(o["title"])}</div>'
                   f'<div class="n">{html.escape(o["note"])}</div></div>'
                   for o in d.get("objects", []))
    extra = ""
    if d.get("palette"):
        extra += (f'<div class="lab" style="margin-top:7mm">PALETTE</div>'
                  f'<div class="palette">{html.escape(d["palette"])}</div>')
    if d.get("script"):
        extra += (f'<div class="lab" style="margin-top:7mm">SCRIPT</div>'
                  f'<div class="script">{SCRIPT(d["script"])}</div>')
    h.append(f'''<div class="sec"><div class="lab">OBJECTS</div>
<div style="margin-top:5mm">{objs}</div>{extra}</div>''')

    h.append(f'''<div class="sec last"><div class="lab">FOR THE NEXT VOLUME</div>
<div class="q">{html.escape(d["question"])}</div>
<div class="fin">INNER FIELD  /  VOL. {d["vol"]}<br>
PRINTED {html.escape(d.get("printed", datetime.date.today().strftime("%Y.%m.%d")))}</div></div>''')

    h.append('</body></html>')
    return "\n".join(h)

if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = pathlib.Path(sys.argv[2]).resolve()
    doc = build(data, out.parent)
    from weasyprint import HTML
    HTML(string=doc, base_url=str(out.parent)+"/").write_pdf(str(out))
    print("wrote", out)
```

`.last` carries an explicit `height`, not `min-height`. WeasyPrint resolves `bottom:0` on the absolutely positioned colophon against the parent's real height, so under `min-height` the colophon collapses upward and prints on top of the closing question. Do not change `height:262mm` back.

## Check before delivering

```python
import pypdfium2 as p, numpy as np
d = p.PdfDocument("out.pdf")
for i in range(len(d)):
    a = np.array(d[i].render(scale=0.5).to_pil().convert("L"))
    print(i+1, round(float((a<200).mean()), 4))
```

An ink ratio below 0.003 on the last page means one or two lines spilled over. Tighten the margins and line-heights of `.obj`, `.palette` and `.script` by a millimetre and rebuild rather than shipping a near-blank page. Render the final page and any page carrying an image and look at them — the sizing rules are good defaults, not a guarantee.