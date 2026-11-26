"""
Genera assets/neofetch.svg: tus stats de GitHub con pinta de `neofetch`.
Lo ejecuta el workflow .github/workflows/perfil.yml (una vez al día).

Local:  GITHUB_TOKEN=$(gh auth token) python .github/scripts/neofetch.py
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "migueelo14")
ROL = "estudiante de desarrollo"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
MIN_MOSTRAR = 20
IGNORAR = {"ShaderLab", "HLSL", "GLSL", "Makefile", "CMake", "Dockerfile", "Batchfile"}

BG, BAR, BORDER = "#0d1117", "#161b22", "#1f3b2a"
GREEN, GREEN2, MID, DIM = "#00ff41", "#39d353", "#006d32", "#0e4429"
TEXT, MUTED = "#c9d1d9", "#8b949e"
SHADES = ["#00ff41", "#26a641", "#006d32", "#7ee787", "#0e4429", "#56d364"]
FONT = "'Fira Code','JetBrains Mono','Cascadia Code',Consolas,'DejaVu Sans Mono','Courier New',monospace"

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "neofetch.svg")


def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GraphQL: {data['errors']}")
    return data["data"]


def datos():
    u = gql("""query($login:String!){user(login:$login){
      createdAt followers{totalCount}
      pullRequests{totalCount}
      repositories(ownerAffiliations:OWNER,isFork:false,first:100%s){
        totalCount nodes{isPrivate stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}
    }}""" % (",privacy:PUBLIC" if os.environ.get("SOLO_PUBLICOS") else ""), login=USER)["user"]

    creado = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    ahora = dt.datetime.now(dt.timezone.utc)
    commits = contribs = 0
    desde = creado
    while desde < ahora:
        hasta = min(desde + dt.timedelta(days=365), ahora)
        c = gql("""query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){
          contributionsCollection(from:$from,to:$to){totalCommitContributions restrictedContributionsCount
            contributionCalendar{totalContributions}}}}""",
                login=USER, **{"from": desde.isoformat(), "to": hasta.isoformat()})["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"]
        contribs += c["contributionCalendar"]["totalContributions"]
        desde = hasta

    # lenguajes: cada repo pesa lo mismo (si no, Unity se come todo por los bytes)
    peso = {}
    repos = u["repositories"]["nodes"]
    for r in repos:
        edges = [x for x in r["languages"]["edges"] if x["node"]["name"] not in IGNORAR]
        total = sum(x["size"] for x in edges)
        for x in edges:
            peso[x["node"]["name"]] = peso.get(x["node"]["name"], 0) + x["size"] / total
    tot = sum(peso.values()) or 1
    langs = sorted(((k, v / tot) for k, v in peso.items()), key=lambda kv: -kv[1])[:5]

    meses = (ahora.year - creado.year) * 12 + ahora.month - creado.month
    if ahora.day < creado.day:
        meses -= 1
    a, m = divmod(max(meses, 0), 12)
    uptime = " ".join(filter(None, [f"{a} año{'s' if a != 1 else ''}" if a else "",
                                    f"{m} mes{'es' if m != 1 else ''}" if m or not a else ""]))
    return {
        "uptime": uptime,
        "repos": u["repositories"]["totalCount"],
        "publicos": sum(not r["isPrivate"] for r in repos),
        "stars": sum(r["stargazerCount"] for r in repos),
        "followers": u["followers"]["totalCount"],
        "prs": u["pullRequests"]["totalCount"],
        "commits": commits,
        "contribs": contribs,
        "langs": langs,
    }


# logo pixel-art "M14"
GLYPHS = {
    "M": ["X...X", "XX.XX", "X.X.X", "X.X.X", "X...X", "X...X", "X...X"],
    "1": ["..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", ".XXX."],
    "4": ["...X.", "..XX.", ".X.X.", "X..X.", "XXXXX", "...X.", "...X."],
}


def logo(x0, y0, px=13):
    rects, shadow = [], []
    gx = x0
    col = 0
    for ch in "M14":
        g = GLYPHS[ch]
        for c in range(5):
            for r in range(7):
                if g[r][c] == "X":
                    x, y = gx + c * px, y0 + r * px
                    d = 0.6 + col * 0.05 + r * 0.02
                    shadow.append(f'<rect x="{x+4}" y="{y+4}" width="{px-1}" height="{px-1}" fill="{DIM}"/>')
                    rects.append(f'<rect class="px" style="animation-delay:{d:.2f}s" x="{x}" y="{y}" width="{px-1}" height="{px-1}" fill="{GREEN}"/>')
            col += 1
        gx += 5 * px + px
        col += 1
    return "".join(shadow) + "".join(rects)


def render(d):
    W = 900
    e = escape
    repos = f"{d['repos']} públicos" if d["publicos"] == d["repos"] else f"{d['repos']} ({d['publicos']} públicos)"
    lines = [("Usuario", USER), ("Rol", ROL), ("Enfoque", "automatización con IA"),
             ("Stack", "Java · Python · C# · Unity"), ("Uptime", d["uptime"]), ("Repos", repos)]
    # los contadores solo aparecen cuando ya lucen (se activan solos al crecer)
    if d["commits"] >= MIN_MOSTRAR:
        lines.append(("Commits", f"{d['commits']} en total"))
    if d["contribs"] >= MIN_MOSTRAR:
        lines.append(("Contribuciones", f"{d['contribs']} en total"))
    if d["prs"]:
        lines.append(("Pull requests", str(d["prs"])))
    if d["stars"]:
        lines.append(("Estrellas", f"★ {d['stars']}"))
    if d["followers"]:
        lines.append(("Seguidores", str(d["followers"])))
    lines.append(("Estado", "buscando prácticas / FCT"))
    x = 330
    y = 82
    lh = 25
    out = []
    t = 1.6
    out.append(f'<text class="in" style="animation-delay:1.3s" x="{x}" y="{y}" font-size="17" font-weight="700" fill="{GREEN}">{e(USER)}<tspan fill="{TEXT}">@</tspan>github</text>')
    out.append(f'<text class="in" style="animation-delay:1.4s" x="{x}" y="{y+16}" font-size="15" fill="{MID}">{"-" * (len(USER) + 7)}</text>')
    y += 44
    for k, v in lines:
        out.append(f'<text class="in" style="animation-delay:{t:.2f}s" x="{x}" y="{y}" font-size="15" fill="{GREEN2}" font-weight="700">{e(k)}<tspan fill="{MUTED}">:</tspan>'
                   f'<tspan x="{x+150}" fill="{TEXT}" font-weight="400">{e(v)}</tspan></text>')
        y += lh
        t += 0.12
    # barra de lenguajes
    y += 8
    out.append(f'<text class="in" style="animation-delay:{t:.2f}s" x="{x}" y="{y}" font-size="15" fill="{GREEN2}" font-weight="700">Lenguajes<tspan fill="{MUTED}">:</tspan>'
               f'<tspan fill="{MUTED}" font-weight="400" font-size="12"> (por proyecto)</tspan></text>')
    y += 14
    bw, bx = 540, x
    out.append(f'<rect x="{bx}" y="{y}" width="{bw}" height="10" rx="5" fill="{BAR}"/>')
    out.append(f'<clipPath id="bar"><rect x="{bx}" y="{y}" width="0" height="10" rx="5">'
               f'<animate attributeName="width" from="0" to="{bw}" dur="1.2s" begin="{t+0.2:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/></rect></clipPath>')
    segs, lx = [], bx
    for i, (name, p) in enumerate(d["langs"]):
        w = bw * p
        segs.append(f'<rect x="{lx:.1f}" y="{y}" width="{w:.1f}" height="10" fill="{SHADES[i % len(SHADES)]}"/>')
        lx += w
    out.append(f'<g clip-path="url(#bar)">{"".join(segs)}</g>')
    y += 32
    lx = bx
    for i, (name, p) in enumerate(d["langs"]):
        label = f"{name} {p*100:.0f}%"
        out.append(f'<g class="in" style="animation-delay:{t+0.4+i*0.1:.2f}s"><rect x="{lx}" y="{y-10}" width="10" height="10" rx="2" fill="{SHADES[i % len(SHADES)]}"/>'
                   f'<text x="{lx+16}" y="{y}" font-size="13" fill="{TEXT}">{e(label)}</text></g>')
        lx += 16 + len(label) * 13 * 0.6 + 22
    t += 0.9
    y += 26
    # bloques de color típicos de neofetch
    for i, c in enumerate(["#010409", DIM, MID, "#26a641", GREEN2, GREEN, "#7ee787", TEXT]):
        out.append(f'<rect class="in" style="animation-delay:{t+i*0.06:.2f}s" x="{x + i*30}" y="{y}" width="26" height="16" fill="{c}"/>')
    y += 16
    H = y + 30
    hoy = dt.datetime.now(dt.timezone.utc).strftime("%d/%m/%Y")
    style = f"""
text{{font-family:{FONT}}}
.px{{opacity:0;animation:pix .25s ease-out forwards}}
@keyframes pix{{from{{opacity:0;transform:translateY(-6px)}}to{{opacity:1;transform:none}}}}
.in{{opacity:0;animation:fin .35s ease-out forwards}}
@keyframes fin{{from{{opacity:0;transform:translateX(-6px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion: reduce){{.px,.in{{animation:none;opacity:1}}}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Stats de GitHub de {e(USER)}">
<title>Stats de GitHub de {e(USER)}</title>
<style>{style}</style>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{BG}" stroke="{BORDER}"/>
<path d="M14 0.5 H{W-14} A13.5 13.5 0 0 1 {W-0.5} 14 V34 H0.5 V14 A13.5 13.5 0 0 1 14 0.5Z" fill="{BAR}"/>
<line x1="0.5" y1="34" x2="{W-0.5}" y2="34" stroke="{BORDER}"/>
<circle cx="22" cy="17" r="6" fill="#ff5f56"/><circle cx="42" cy="17" r="6" fill="#ffbd2e"/><circle cx="62" cy="17" r="6" fill="#27c93f"/>
<text x="{W/2}" y="22" text-anchor="middle" font-size="13" fill="{MUTED}">{e(USER)}@github:~$ neofetch</text>
{logo(42, (H + 34) / 2 - 45)}
{"".join(out)}
<text x="{W-20}" y="{H-14}" text-anchor="end" font-size="11" fill="{MUTED}" opacity=".7">actualizado {hoy}</text>
</svg>
"""


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("Falta GITHUB_TOKEN")
    svg = render(datos())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("ok  assets/neofetch.svg")
