"""
Genera los SVG animados del perfil (estilo terminal hacker).

    python scripts/generar_svgs.py

Edita las constantes de abajo (frases, textos del terminal, proyecto...)
y vuelve a ejecutarlo. Los SVG salen en assets/.
Las stats (neofetch.svg) las genera el GitHub Action con .github/scripts/neofetch.py
"""
import os
import random
from xml.sax.saxutils import escape

USER = "migueelo14"
ROL = "estudiante de desarrollo"

# Frases que se teclean y se borran solas debajo del banner
FRASES = [
    f"Hola, soy {USER}",
    "Estudiante de desarrollo de software",
    "Automatizo procesos con IA",
    "Java · Python · y lo que haga falta",
    "Me flipa crear juegos y side-projects",
    "Buscando prácticas / FCT. ¡Hablemos!",
]

# Sesión de terminal del "sobre mí": (comando, [líneas de salida])
TERMINAL = [
    ("whoami", [
        ("txt", f"{USER} · {ROL} · fan de automatizarlo todo"),
    ]),
    ("cat sobre_mi.txt", [
        ("ok", "Apasionado por la automatización y el desarrollo con herramientas IA"),
        ("ok", "Creo soluciones que ahorran tiempo y potencian la eficiencia"),
        ("ok", "Me flipa hacer juegos y side-projects: Java, Python, Unity"),
        ("warn", "Buscando prácticas / FCT  ->  abierto a oportunidades"),
    ]),
    ("ls ~/stack", [
        ("ls", "java/  python/  ia/  c#/  unity/  linux/  git/"),
    ]),
]

PROYECTO = {
    "nombre": "flappy-rosso",
    "desc": ["Juego tipo Flappy hecho en Unity.", "Proyecto de PMDM en 2º DAM."],
    "tags": ["C#", "Unity", "Game dev"],
}

# --- paleta ---------------------------------------------------------------
BG = "#0d1117"
PANEL = "#010409"
BAR = "#161b22"
BORDER = "#1f3b2a"
GREEN = "#00ff41"
GREEN2 = "#39d353"
MID = "#006d32"
DIM = "#0e4429"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
WARN = "#e3b341"
FONT = "'Fira Code','JetBrains Mono','Cascadia Code',Consolas,'DejaVu Sans Mono','Courier New',monospace"
CW = 0.6  # ancho de carácter monoespaciado (em)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)


def e(s):
    return escape(s, {'"': "&quot;"})


def svg(w, h, body, style="", title=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{e(title)}">
<title>{e(title)}</title>
<style>
text{{font-family:{FONT}}}
{style}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
{body}
</svg>
"""


def wave_path(y0, amp, period, total, bottom):
    d = f"M0 {y0} Q{period/4:.1f} {y0-amp} {period/2:.1f} {y0}"
    x = period / 2
    while x < total:
        x += period / 2
        d += f" T{x:.1f} {y0}"
    return d + f" L{total} {bottom} L0 {bottom} Z"


def window_chrome(w, title, rx=14):
    return f"""<rect x="0.5" y="0.5" width="{w-1}" height="{{H}}" rx="{rx}" fill="{BG}" stroke="{BORDER}"/>
<path d="M{rx} 0.5 H{w-rx} A{rx-0.5} {rx-0.5} 0 0 1 {w-0.5} {rx} V34 H0.5 V{rx} A{rx-0.5} {rx-0.5} 0 0 1 {rx} 0.5Z" fill="{BAR}"/>
<line x1="0.5" y1="34" x2="{w-0.5}" y2="34" stroke="{BORDER}"/>
<circle cx="22" cy="17" r="6" fill="#ff5f56"/><circle cx="42" cy="17" r="6" fill="#ffbd2e"/><circle cx="62" cy="17" r="6" fill="#27c93f"/>
<text x="{w/2}" y="22" text-anchor="middle" font-size="13" fill="{MUTED}">{e(title)}</text>"""


def typed(x, y, s, size, fill, begin, cps=0.06, anchor_start=True, weight="400", cid="c"):
    """Texto que aparece letra a letra (clip con SMIL discreto). Devuelve (svg, fin)."""
    cw = size * CW
    w = len(s) * cw
    n = len(s)
    vals = ";".join(f"{k*cw:.1f}" for k in range(n + 1))
    dur = max(n * cps, 0.1)
    out = f"""<clipPath id="{cid}"><rect x="{x}" y="{y-size}" width="0" height="{size*1.4}">
<animate attributeName="width" values="{vals}" dur="{dur:.2f}s" begin="{begin:.2f}s" fill="freeze" calcMode="discrete"/></rect></clipPath>
<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{cid})">{e(s)}</text>"""
    return out, begin + dur


# --- 1. banner -------------------------------------------------------------
def banner():
    W, H = 900, 290
    rnd = random.Random(14)
    chars = "01010110<>/{}[]$#*+=-ABCDEF0123456789"
    rain = []
    for x in range(14, W, 22):
        n = rnd.randint(9, 17)
        s = [rnd.choice(chars) for _ in range(n)]
        dur = rnd.uniform(5, 12)
        delay = -rnd.uniform(0, dur)
        op = rnd.uniform(0.25, 0.7)
        sp = "".join(f'<tspan x="{x}" dy="18">{e(c)}</tspan>' for c in s[:-1])
        sp += f'<tspan x="{x}" dy="18" fill="#d6ffe0">{e(s[-1])}</tspan>'
        rain.append(
            f'<g class="rain" style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s">'
            f'<text font-size="14" fill="{GREEN}" opacity="{op:.2f}">{sp}</text></g>')

    waves = ""
    for i, (y0, amp, per, spd, fill, op) in enumerate([
        (250, 10, 450, 14, DIM, 0.9),
        (258, 8, 300, 9, MID, 0.55),
        (266, 6, 225, 6, GREEN2, 0.25),
    ]):
        waves += (f'<path class="wave" style="animation-duration:{spd}s" '
                  f'd="{wave_path(y0, amp, per, 1800, H)}" fill="{fill}" opacity="{op}"/>')

    line = f"> ssh {USER}@github.com"
    size = 15
    lw = len(line) * size * CW
    prompt, t_end = typed(W / 2 - lw / 2, 92, line, size, MUTED, 0.4, cps=0.055, cid="pr")
    cursor = (f'<rect x="{W/2 + lw/2 + 4:.1f}" y="80" width="9" height="16" fill="{GREEN}">'
              f'<animate attributeName="opacity" values="1;0" dur="1s" repeatCount="indefinite" calcMode="discrete"/></rect>')

    name = USER
    style = f"""
.rain{{animation-name:fall;animation-timing-function:linear;animation-iteration-count:infinite}}
@keyframes fall{{from{{transform:translateY(-330px)}}to{{transform:translateY({H}px)}}}}
.wave{{animation-name:slide;animation-timing-function:linear;animation-iteration-count:infinite}}
@keyframes slide{{from{{transform:translateX(0)}}to{{transform:translateX(-900px)}}}}
.name{{animation:boot .9s {t_end+0.15:.2f}s both steps(1)}}
@keyframes boot{{0%{{opacity:0}}20%{{opacity:.8}}30%{{opacity:.1}}45%{{opacity:1}}60%{{opacity:.3}}75%,100%{{opacity:1}}}}
.sub{{animation:fade .8s {t_end+0.9:.2f}s both}}
@keyframes fade{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.g1{{animation:g1 5s {t_end+1.5:.2f}s infinite steps(1) both}}
.g2{{animation:g2 5s {t_end+1.5:.2f}s infinite steps(1) both}}
@keyframes g1{{0%,86%,100%{{opacity:0;transform:none}}87%{{opacity:.85;transform:translate(-5px,1px)}}89%{{opacity:.85;transform:translate(4px,-2px)}}91%{{opacity:.6;transform:translate(-2px,0)}}93%{{opacity:0}}}}
@keyframes g2{{0%,86%,100%{{opacity:0;transform:none}}87%{{opacity:.85;transform:translate(5px,-1px)}}89%{{opacity:.85;transform:translate(-3px,2px)}}91%{{opacity:.6;transform:translate(2px,1px)}}93%{{opacity:0}}}}
.scan{{animation:scan 6s linear infinite}}
@keyframes scan{{from{{transform:translateY(-60px)}}to{{transform:translateY({H}px)}}}}
"""
    body = f"""<defs>
<clipPath id="win"><rect x="0" y="0" width="{W}" height="{H}" rx="14"/></clipPath>
<radialGradient id="fadeC" cx="50%" cy="52%" r="60%"><stop offset="0" stop-color="#000"/><stop offset=".45" stop-color="#555"/><stop offset="1" stop-color="#fff"/></radialGradient>
<mask id="rainMask"><rect width="{W}" height="{H}" fill="url(#fadeC)"/></mask>
<pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".035"/></pattern>
<linearGradient id="scanG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".5" stop-color="{GREEN}" stop-opacity=".07"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
{window_chrome(W, USER + "@github: ~").replace("{H}", str(H - 1))}
<g clip-path="url(#win)">
  <g mask="url(#rainMask)" transform="translate(0,34)">{"".join(rain)}</g>
  <rect y="34" width="{W}" height="{H-34}" fill="url(#scanlines)"/>
  <rect class="scan" width="{W}" height="60" fill="url(#scanG)"/>
  {waves}
</g>
{prompt}
{cursor}
<g class="name" font-size="70" font-weight="700" text-anchor="middle">
  <text class="g1" x="{W/2}" y="172" fill="#00e5ff">{e(name)}</text>
  <text class="g2" x="{W/2}" y="172" fill="#ff2bd6">{e(name)}</text>
  <text x="{W/2}" y="172" fill="{GREEN}" filter="url(#glow)">{e(name)}</text>
</g>
<text class="sub" x="{W/2}" y="214" text-anchor="middle" font-size="16" fill="{TEXT}">{e(ROL)} <tspan fill="{GREEN}">//</tspan> automatización con IA <tspan fill="{GREEN}">//</tspan> java · python</text>
"""
    return svg(W, H, body, style, f"{USER} — {ROL}")


# --- 2. frases tecleándose -------------------------------------------------
def typing():
    W, H = 900, 60
    size = 22
    cw = size * CW
    ct, hold, dt, gap = 0.07, 1.8, 0.03, 0.35
    # línea temporal
    events = []  # (frase_idx, t_inicio)
    t = 0.3
    spans = []
    for i, f in enumerate(FRASES):
        n = len(f)
        spans.append((t, n))
        t += n * ct + hold + n * dt + gap
    T = t
    texts, cursor_kt, cursor_v = [], [0.0], [None]
    for i, f in enumerate(FRASES):
        n = len(f)
        w = n * cw
        x0 = W / 2 - w / 2
        t0, _ = spans[i]
        kt, vals = [0.0], [0.0]
        for k in range(1, n + 1):
            kt.append(t0 + k * ct); vals.append(k * cw)
        t1 = t0 + n * ct + hold
        for k in range(n - 1, -1, -1):
            kt.append(t1 + (n - k) * dt); vals.append(k * cw)
        # cursor sigue al borde del clip
        for a, v in zip(kt[1:], vals[1:]):
            cursor_kt.append(a); cursor_v.append(x0 + v + 2)
        if i == 0:
            cursor_v[0] = x0 + 2
        kts = ";".join(f"{a/T:.5f}" for a in kt)
        vs = ";".join(f"{v:.1f}" for v in vals)
        texts.append(f"""<clipPath id="t{i}"><rect x="{x0:.1f}" y="10" width="0" height="40">
<animate attributeName="width" values="{vs}" keyTimes="{kts}" dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete"/></rect></clipPath>
<text x="{x0:.1f}" y="38" font-size="{size}" fill="{GREEN}" textLength="{w:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#t{i})">{e(f)}</text>""")
    ckt = ";".join(f"{a/T:.5f}" for a in cursor_kt)
    cv = ";".join(f"{v:.1f}" for v in cursor_v)
    cursor = f"""<rect x="{cursor_v[0]:.1f}" y="18" width="12" height="25" fill="{GREEN}" class="blink">
<animate attributeName="x" values="{cv}" keyTimes="{ckt}" dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete"/></rect>"""
    style = ".blink{animation:bl 1s steps(1) infinite}@keyframes bl{50%{opacity:0}}"
    return svg(W, H, "".join(texts) + cursor, style, " · ".join(FRASES))


# --- 3. terminal "sobre mí" ------------------------------------------------
def terminal():
    W = 900
    size = 15
    cw = size * CW
    lh = 27
    x = 26
    y = 70
    t = 0.5
    parts = []
    prompt = f"{USER}@github:~$ "
    pw = len(prompt) * cw
    idx = 0
    colors = {"txt": TEXT, "ok": TEXT, "warn": WARN, "ls": GREEN2}
    marks = {"txt": "", "ok": "[+] ", "warn": "[!] ", "ls": ""}
    for cmd, outs in TERMINAL:
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="700" fill="{GREEN}" textLength="{pw-cw:.1f}" lengthAdjust="spacingAndGlyphs" opacity="0">{e(prompt.rstrip())}'
                     f'<animate attributeName="opacity" to="1" dur=".01s" begin="{t:.2f}s" fill="freeze"/></text>')
        tx, t = typed(x + pw, y, cmd, size, TEXT, t + 0.35, cps=0.065, cid=f"cmd{idx}")
        parts.append(tx)
        idx += 1
        t += 0.35
        y += lh
        for kind, line in outs:
            mark = marks[kind]
            mcol = WARN if kind == "warn" else GREEN
            parts.append(
                f'<text x="{x+18}" y="{y}" font-size="{size}" fill="{colors[kind]}" opacity="0">'
                f'<tspan fill="{mcol}">{e(mark)}</tspan>{e(line)}'
                f'<animate attributeName="opacity" to="1" dur=".25s" begin="{t:.2f}s" fill="freeze"/></text>')
            t += 0.22
            y += lh
        t += 0.4
        y += 8
    # prompt final + cursor
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="700" fill="{GREEN}" textLength="{pw-cw:.1f}" lengthAdjust="spacingAndGlyphs" opacity="0">{e(prompt.rstrip())}'
                 f'<animate attributeName="opacity" to="1" dur=".01s" begin="{t:.2f}s" fill="freeze"/></text>')
    parts.append(f'<rect x="{x+pw:.1f}" y="{y-13}" width="9" height="17" fill="{GREEN}" opacity="0">'
                 f'<animate attributeName="opacity" values="1;0" dur="1s" begin="{t:.2f}s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    H = y + 28
    body = window_chrome(W, "~/sobre_mi — bash").replace("{H}", str(H - 1)) + "\n" + "\n".join(parts)
    return svg(W, H, body, "", f"Sobre mí — {USER}")


# --- 4. tarjeta de proyecto (con un pájaro pixel-art volando) --------------
BIRD = [
    "..XXXX..",
    ".XXXXWB.",
    "XXXXXWW.",
    "YYXXXXOO",
    "XXXXXXO.",
    ".XXXXX..",
]


def proyecto():
    W, H = 900, 210
    p = PROYECTO
    sx0, sy0, sw, sh = 16, 16, 300, H - 32  # escena
    px = 5
    bird = []
    cols = {"X": "#ff3b3b", "W": "#ffffff", "B": "#111111", "O": "#ffb000", "Y": "#c41e1e"}
    for r, row in enumerate(BIRD):
        for c, ch in enumerate(row):
            if ch != ".":
                cls = ' class="wing"' if ch == "Y" else ""
                bird.append(f'<rect{cls} x="{c*px}" y="{r*px}" width="{px}" height="{px}" fill="{cols[ch]}"/>')
    pipes = ""
    for i in range(4):
        px0 = sx0 + 60 + i * 150
        gap_y = [70, 40, 95, 55][i]
        pipes += (f'<rect x="{px0}" y="{sy0}" width="34" height="{gap_y}" fill="{MID}" stroke="{GREEN2}" stroke-width="2"/>'
                  f'<rect x="{px0-4}" y="{sy0+gap_y-12}" width="42" height="12" fill="{MID}" stroke="{GREEN2}" stroke-width="2"/>'
                  f'<rect x="{px0}" y="{sy0+gap_y+70}" width="34" height="{sh-gap_y-70}" fill="{MID}" stroke="{GREEN2}" stroke-width="2"/>'
                  f'<rect x="{px0-4}" y="{sy0+gap_y+70}" width="42" height="12" fill="{MID}" stroke="{GREEN2}" stroke-width="2"/>')
    rnd = random.Random(3)
    stars = "".join(f'<rect x="{sx0+rnd.randint(4,sw-6)}" y="{sy0+rnd.randint(4,sh-30)}" width="2" height="2" fill="{TEXT}" opacity="{rnd.uniform(.2,.7):.2f}"/>' for _ in range(22))
    tx = sx0 + sw + 34
    tags = ""
    ox = tx
    for tg in p["tags"]:
        w = len(tg) * 13 * CW + 22
        tags += (f'<rect x="{ox:.1f}" y="128" width="{w:.1f}" height="26" rx="13" fill="{DIM}" stroke="{MID}"/>'
                 f'<text x="{ox + w/2:.1f}" y="146" text-anchor="middle" font-size="13" fill="{GREEN2}">{e(tg)}</text>')
        ox += w + 10
    desc = "".join(f'<text x="{tx}" y="{94 + i*22}" font-size="15" fill="{TEXT}">{e(d)}</text>' for i, d in enumerate(p["desc"]))
    style = f"""
.pipes{{animation:pipes 6s linear infinite}}
@keyframes pipes{{from{{transform:translateX(0)}}to{{transform:translateX(-600px)}}}}
.bird{{animation:bob 1.2s ease-in-out infinite alternate}}
@keyframes bob{{from{{transform:translate(70px,72px) rotate(-8deg)}}to{{transform:translate(70px,104px) rotate(10deg)}}}}
.wing{{animation:flap .25s steps(1) infinite}}
@keyframes flap{{50%{{transform:translateY(-5px)}}}}
.ground{{animation:ground 1s linear infinite}}
@keyframes ground{{from{{transform:translateX(0)}}to{{transform:translateX(-20px)}}}}
.card{{transition:none}}
"""
    body = f"""<defs><clipPath id="scene"><rect x="{sx0}" y="{sy0}" width="{sw}" height="{sh}" rx="10"/></clipPath>
<pattern id="dash" width="20" height="8" patternUnits="userSpaceOnUse"><rect width="10" height="8" fill="{MID}"/><rect x="10" width="10" height="8" fill="{DIM}"/></pattern></defs>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{BG}" stroke="{BORDER}"/>
<g clip-path="url(#scene)">
  <rect x="{sx0}" y="{sy0}" width="{sw}" height="{sh}" fill="{PANEL}"/>{stars}
  <g class="pipes">{pipes}<g transform="translate(600,0)">{pipes}</g></g>
  <g class="bird">{"".join(bird)}</g>
  <rect class="ground" x="{sx0}" y="{sy0+sh-10}" width="{sw+40}" height="10" fill="url(#dash)"/>
</g>
<rect x="{sx0}" y="{sy0}" width="{sw}" height="{sh}" rx="10" fill="none" stroke="{BORDER}"/>
<text x="{tx}" y="44" font-size="13" fill="{MUTED}">★ proyecto destacado</text>
<text x="{tx}" y="74" font-size="28" font-weight="700" fill="{GREEN}">{e(p["nombre"])}</text>
{desc}
{tags}
<text x="{tx}" y="186" font-size="13" fill="{MUTED}"><tspan fill="{GREEN}">$</tspan> git clone github.com/{USER}/{e(p["nombre"])}</text>
"""
    return svg(W, H, body, style, f"Proyecto destacado: {p['nombre']}")


# --- 5. pie ----------------------------------------------------------------
def footer():
    W, H = 900, 130
    waves = ""
    for y0, amp, per, spd, fill, op in [(34, 9, 450, 16, DIM, 0.75), (28, 7, 300, 10, MID, 0.35), (22, 5, 225, 7, GREEN2, 0.15)]:
        waves += (f'<g transform="translate(0,{H}) scale(1,-1)"><path class="wave" style="animation-duration:{spd}s" '
                  f'd="{wave_path(H - y0, amp, per, 1800, H)}" fill="{fill}" opacity="{op}"/></g>')
    style = """
.wave{animation-name:slide;animation-timing-function:linear;animation-iteration-count:infinite}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-900px)}}
.blink{animation:bl 1s steps(1) infinite}@keyframes bl{50%{opacity:0}}
"""
    body = f"""<defs><clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>
<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{BG}"/>{waves}</g>
<text x="{W/2}" y="{H-54}" text-anchor="middle" font-size="15" fill="{MUTED}"><tspan fill="{GREEN}">{USER}@github:~$</tspan> exit</text>
<text x="{W/2}" y="{H-28}" text-anchor="middle" font-size="14" fill="{TEXT}">conexión cerrada · gracias por pasarte <tspan class="blink" fill="{GREEN}">█</tspan></text>
"""
    return svg(W, H, body, style, "Gracias por pasarte")


if __name__ == "__main__":
    files = {
        "banner.svg": banner(),
        "typing.svg": typing(),
        "terminal.svg": terminal(),
        "proyecto-flappy-rosso.svg": proyecto(),
        "footer.svg": footer(),
    }
    for name, content in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"ok  assets/{name}  ({len(content)//1024} KB)")
