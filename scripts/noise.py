"""Per-volume noise signature. Seeded by the volume's own text, so the same
text always yields the same image. Layered gradient noise + domain warp,
rendered monochrome. Variants: field / contour / dither / scan."""
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

def signature(text, variant="dither", size=(900, 1200), seed=None):
    h, w = size
    s = seed if seed is not None else int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(s)
    # domain warp: displace the sampling field by another noise field
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

    if variant == "grain":          # coarse 1-bit dither, chunky print grain
        small = np.array(Image.fromarray((f*255).astype(np.uint8),"L")
                         .resize((w//5, h//5), Image.BILINEAR), float)/255
        d = _dither(np.clip(small*1.1-.05, 0, 1))
        img = np.array(Image.fromarray((d*255).astype(np.uint8),"L")
                       .resize((w, h), Image.NEAREST), float)/255
    elif variant == "block":        # low-res quantised grid, hard monochrome
        n = 46
        small = np.array(Image.fromarray((f*255).astype(np.uint8),"L")
                         .resize((n, int(n*h/w)), Image.BILINEAR), float)/255
        q = (np.floor(_norm(small)*4)/3)
        q = (q > .5).astype(float)*(np.floor(_norm(small)*4)/3)
        img = np.array(Image.fromarray((q*255).astype(np.uint8),"L")
                       .resize((w, h), Image.NEAREST), float)/255
    elif variant == "contour":
        bands = 7
        q = np.floor(f*bands)/ (bands-1)
        edge = np.abs(np.gradient(q)[0]) + np.abs(np.gradient(q)[1])
        img = 1.0 - (edge > 0.001).astype(float)
    elif variant == "scan":
        lines = (np.sin(yy*np.pi/3.0)*.5+.5)
        img = np.clip(f*0.72 + lines*0.28, 0, 1)
        img = (img > .52).astype(float)
    else:  # dither, fine grain
        img = _dither(np.clip(f*1.08-.04, 0, 1))
    return Image.fromarray((np.clip(img, 0, 1)*255).astype(np.uint8), "L")

if __name__ == "__main__":
    import sys
    t = sys.argv[1] if len(sys.argv) > 1 else "inner field"
    for v in ("contour", "scan", "grain", "block"):
        signature(t, v, (560, 760)).save(f"noise_{v}.png")
        print("wrote", v)
