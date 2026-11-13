"""Generate a language-distribution SVG (light + dark) from public, non-fork repos."""
import json, os, sys, urllib.request

USER = os.environ.get("GH_USER", "SercanFurkan")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TOP = 6
COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572A5", "Kotlin": "#A97BFF",
    "C#": "#178600", "PHP": "#4F5D95", "HTML": "#e34c26", "CSS": "#563d7c", "PLpgSQL": "#336790",
    "TeX": "#3D6117", "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051", "COBOL": "#8a6f3a",
}

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "lang-card"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

repos = get(f"https://api.github.com/users/{USER}/repos?type=owner&per_page=100")
totals = {}
for r in repos:
    if r["fork"] or r["private"] or r["name"] == USER:
        continue
    for lang, n in get(r["languages_url"]).items():
        totals[lang] = totals.get(lang, 0) + n

if not totals:
    sys.exit("no language data")
total = sum(totals.values())
rows = sorted(totals.items(), key=lambda kv: -kv[1])[:TOP]

def svg(fg, muted, track):
    w, rh, pad = 495, 28, 20
    h = pad * 2 + 24 + rh * len(rows)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Most used languages">',
           f'<text x="{pad}" y="{pad+14}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="16" font-weight="600" fill="{fg}">Most Used Languages</text>']
    for i, (lang, n) in enumerate(rows):
        y = pad + 24 + i * rh + 6
        pct = n / total * 100
        color = COLORS.get(lang, "#8b949e")
        out.append(f'<text x="{pad}" y="{y+11}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="12" fill="{fg}">{lang}</text>')
        out.append(f'<rect x="150" y="{y+2}" width="270" height="10" rx="5" fill="{track}"/>')
        out.append(f'<rect x="150" y="{y+2}" width="{max(4, 270*pct/100):.1f}" height="10" rx="5" fill="{color}"/>')
        out.append(f'<text x="{w-pad}" y="{y+11}" text-anchor="end" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="12" fill="{muted}">{pct:.1f}%</text>')
    out.append("</svg>")
    return "\n".join(out)

os.makedirs("assets", exist_ok=True)
open("assets/languages-dark.svg", "w").write(svg("#c9d1d9", "#8b949e", "#30363d"))
open("assets/languages-light.svg", "w").write(svg("#24292f", "#57606a", "#d0d7de"))
print({k: round(v / total * 100, 1) for k, v in rows})
