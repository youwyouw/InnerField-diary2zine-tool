#!/usr/bin/env python3
"""Inner Field — volume typesetter.
Usage: python3 zine.py volume.json out.pdf
"""
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

.objs{{margin-top:8mm}}
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

def P(t):
    return "\n".join(f"<p>{html.escape(p.strip())}</p>" for p in t.split("\n") if p.strip())


def build(d, outdir):
    corpus = d["title"] + "".join(e["her"] for e in d["entries"])
    var = d.get("noise") or pick_variant(d["vol"])
    signature(corpus, var, (1754, 1240)).save(outdir/"_cover.png")
    signature(corpus, var, (380, 540)).save(outdir/"_sig.png")

    h = [f'<!doctype html><html><head><meta charset="utf-8"><title>Inner Field</title>',
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

    h.append(f'''<div class="sec"><div class="lab">CODA</div>
<div class="poem">{html.escape(d["poem"]["body"])}</div>
<div class="sig"><img src="_sig.png"><div class="m">NOISE SIGNATURE</div></div></div>''')

    objs = "".join(f'<div class="obj"><div class="k">{html.escape(o["kind"])}</div>'
                   f'<div class="t">{html.escape(o["title"])}</div>'
                   f'<div class="n">{html.escape(o["note"])}</div></div>' for o in d.get("objects", []))
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
<div class="fin">INNER FIELD &nbsp;/&nbsp; VOL. {d["vol"]}<br>
PRINTED {html.escape(d.get("printed", datetime.date.today().strftime("%Y.%m.%d")))}</div></div>''')

    h.append('</body></html>')
    return "\n".join(h)

if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = pathlib.Path(sys.argv[2]).resolve()
    doc = build(data, out.parent)
    (out.parent/"_preview.html").write_text(doc, encoding="utf-8")
    from weasyprint import HTML
    HTML(string=doc, base_url=str(out.parent)+"/").write_pdf(str(out))
    print("wrote", out)
