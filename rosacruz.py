# -*- coding: utf-8 -*-
# rosacruz_sigilo_auto_snap2d.py
# Dibuja sigilos sobre rosacruz.png sin JSON, con auto-ajuste 2D por bordes.

from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import os, sys, math

# --- Transliteración / Guematría ---
latin_to_hebrew = {
    "A":"א","B":"ב","C":"כ","K":"כ","D":"ד","E":"ה","F":"פ","G":"ג",
    "H":"ח","I":"י","J":"י","L":"ל","M":"מ","N":"נ","O":"ו","P":"פ",
    "Q":"ק","R":"ר","S":"ס","T":"ט","U":"ו","V":"ו","W":"ו","X":"קס",
    "Y":"י","Z":"ז"
}
gematria_values = {
    "א":1,"ב":2,"ג":3,"ד":4,"ה":5,"ו":6,"ז":7,"ח":8,"ט":9,"י":10,"כ":20,"ך":500,"ל":30,
    "מ":40,"ם":600,"נ":50,"ן":700,"ס":60,"ע":70,"פ":80,"ף":800,"צ":90,"ץ":900,"ק":100,"ר":200,"ש":300,"ת":400
}

MADRES  = ["א","מ","ש"]
DOBLES  = ["ב","ג","ד","כ","פ","ר","ת"]
SIMPLES = ["ה","ו","ז","ח","ט","י","ל","נ","ס","ע","צ","ק"]

# --- Geometría base (puede variarse finamente) ---
RADIUS_REL = {"madre":0.29, "doble":0.47, "simple":0.66}
ANGLES_DEG = {
    "א":0, "מ":210, "ש":330,
    "ב":150, "ג":170, "ד":200, "כ":230, "פ":260, "ר":310, "ת":20,
    "ה":30, "ו":55, "ז":80, "ח":105, "ט":130, "י":155,
    "ל":190, "נ":215, "ס":240, "ע":275, "צ":305, "ק":335,
}
GLOBAL_ROT_DEG = 0.0
RING_OFFSET_DEG = {"madre":0.0, "doble":0.0, "simple":0.0}

# Ventanas de búsqueda (más grande en el anillo externo)
SEARCH = {
    "madre":  {"dang": 10, "dr": 0.03},
    "doble":  {"dang": 12, "dr": 0.035},
    "simple": {"dang": 14, "dr": 0.045},
}
DEG_STEP = 1.0   # si necesitás más fino, pon 0.5 (más lento)
PATCH = 9        # lado del parche para medir bordes (impar)

def here(*parts): return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)

def safe_open(path):
    p = os.path.abspath(path)
    if not os.path.exists(p): raise FileNotFoundError(p)
    return Image.open(p).convert("RGBA")

def load_font(ttf, px):
    if ttf and os.path.exists(ttf):
        try: return ImageFont.truetype(ttf, int(px))
        except: pass
    return ImageFont.load_default()

def transliterar(s):
    s = s.upper()
    return "".join(latin_to_hebrew.get(ch, "") for ch in s)

def clasif(l):
    if l in MADRES: return "madre"
    if l in DOBLES: return "doble"
    return "simple"

def bbox_not_white(img_rgb):
    white = Image.new("RGB", img_rgb.size, (255,255,255))
    diff  = ImageChops.difference(img_rgb, white).convert("L")
    mask  = diff.point(lambda p: 255 if p > 8 else 0)
    return mask.getbbox()

def center_scale(img):
    rgb = img.convert("RGB")
    bb = bbox_not_white(rgb)
    if not bb:
        W,H = img.size
        return (W/2, H/2, min(W,H))
    L,T,R,B = bb
    cx, cy = (L+R)/2, (T+B)/2
    side_min = min(R-L, B-T)
    return (cx, cy, side_min)

def polar_to_xy(cx, cy, r, ang_from_top_deg):
    rad = math.radians((ang_from_top_deg + GLOBAL_ROT_DEG) - 90.0)
    return (cx + r*math.cos(rad), cy + r*math.sin(rad))

def ring_radius(side_min, k):
    return RADIUS_REL[k] * side_min

def edge_score(edge_img, x, y, patch=PATCH):
    # suma de bordes en un parche cuadrado (con límites)
    W,H = edge_img.size
    half = patch//2
    s = 0
    ix, iy = int(round(x)), int(round(y))
    for j in range(iy-half, iy+half+1):
        if j < 0 or j >= H: continue
        for i in range(ix-half, ix+half+1):
            if i < 0 or i >= W: continue
            s += edge_img.getpixel((i,j))
    return s

def snap2d(edge_img, cx, cy, side_min, letra):
    k   = clasif(letra)
    r0  = ring_radius(side_min, k)
    ang = ANGLES_DEG[letra] + RING_OFFSET_DEG[k]

    best = (None, None, -1)  # x,y,score
    dang = SEARCH[k]["dang"]
    dr   = SEARCH[k]["dr"] * side_min

    angs = [ang + d for d in frange(-dang, dang, DEG_STEP)]
    rs   = [r0 + d for d in frange(-dr, dr, max(1.0, dr/6))]  # paso radial ≈ dr/6 px (mín 1px)

    for rr in rs:
        for aa in angs:
            x,y = polar_to_xy(cx, cy, rr, aa)
            sc  = edge_score(edge_img, x, y, PATCH)
            if sc > best[2]:
                best = (x, y, sc)
    return (best[0], best[1])

def frange(a,b,step):
    v = a
    while v <= b:
        yield v
        v += step

def crear_sigilo(nombre, base="rosacruz.png", fuente_ttf=None, debug=False):
    hebreo = transliterar(nombre)
    valor  = sum(gematria_values.get(l,0) for l in hebreo)

    img = safe_open(here(base))
    W,H = img.size
    cx, cy, side_min = center_scale(img)

    # Mapa de bordes (suavizado para estabilidad)
    edges = img.convert("L").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.0))

    overlay = Image.new("RGBA", img.size, (255,255,255,0))
    draw    = ImageDraw.Draw(overlay)

    grosor    = max(2, int(side_min*0.006))
    radio_pto = max(2, int(side_min*0.012))
    font      = load_font(fuente_ttf, int(side_min*0.035))

    coords = []
    letras = []
    for l in hebreo:
        if l in ANGLES_DEG:
            x,y = snap2d(edges, cx, cy, side_min, l)
            coords.append((x,y))
            letras.append(l)

    if len(coords) >= 2:
        draw.line(coords, fill=(0,0,0,230), width=grosor)

    for (x,y), l in zip(coords, letras):
        draw.ellipse((x-radio_pto, y-radio_pto, x+radio_pto, y+radio_pto), fill=(200,30,30,230))
        draw.text((x+radio_pto+2, y-radio_pto-2), l, fill=(0,0,0,255), font=font)

    if debug:
        # marcas de centro/anillos para ver ajuste
        for rrel in (RADIUS_REL["madre"], RADIUS_REL["doble"], RADIUS_REL["simple"]):
            rpx = rrel*side_min
            # 12 marcas cardinales
            for a in range(0, 360, 30):
                x,y = polar_to_xy(cx, cy, rpx, a)
                draw.ellipse((x-2,y-2,x+2,y+2), fill=(30,120,220,220))

    out = Image.alpha_composite(img, overlay)

    # Guardado con contador
    cnt_file = here("contador.txt")
    try:
        cnt = int(open(cnt_file,"r",encoding="utf-8").read().strip())
    except Exception:
        cnt = 0
    cnt += 1
    open(cnt_file,"w",encoding="utf-8").write(str(cnt))

    out_path = here(f"sigilo_{cnt:02d}.png")
    out.convert("RGB").save(out_path, quality=95)
    return hebreo, valor, out_path

# --------- Programa interactivo ----------
if __name__ == "__main__":
    base = None
    for n in ("rosacruz.png","Rosacruz.png","ROSAcruz.png"):
        p = here(n)
        if os.path.exists(p):
            base = os.path.basename(p); break
    if not base:
        print("❌ No encontré rosacruz.png al lado del script."); sys.exit(1)

    fuente_ttf = None  # opcional, p.ej.: here("DejaVuSans.ttf")

    palabra = input("👉 Escribe la palabra que quieres sigilizar: ").strip()
    if not palabra:
        print("No ingresaste ninguna palabra."); sys.exit(1)

    hebreo, valor, archivo = crear_sigilo(palabra, base=base, fuente_ttf=fuente_ttf, debug=False)
    print(f"\nPalabra en hebreo: {hebreo}")
    print(f"Valor numérico: {valor}")
    print(f"✅ Sigilo guardado en: {archivo}")




