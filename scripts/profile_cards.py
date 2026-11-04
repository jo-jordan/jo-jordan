#!/usr/bin/env python3
"""Draw the profile README cards (stats, languages, streak, activity, pinned repos).

Runs in GitHub Actions; uses only the standard library.

    GITHUB_TOKEN=... python3 scripts/profile_cards.py jo-jordan dist

Set PROFILE_TOKEN (a personal access token) to include private repositories.
"""
import datetime as dt
import html
import json
import os
import sys
import urllib.request
from collections import defaultdict

PINS = ["Holdem", "go-holdem", "super-holdem-server", "websocket_server"]
# Shown instead of the repo description when the repo has none.
PIN_BLURBS = {"Holdem": "Texas Hold'em built with the Godot Engine."}
EXCLUDE_LANGS = {"HTML", "CSS", "SCSS"}
EXCLUDE_REPOS = {"github-readme-stats"}

# Tokyo night palette
BG, BORDER = "#1a1b26", "#292e42"
FG, MUTED, FAINT = "#c0caf5", "#a9b1d6", "#565f89"
BLUE, VIOLET, CYAN, GREEN, PINK, AMBER = "#7aa2f7", "#bb9af7", "#7dcfff", "#9ece6a", "#f7768e", "#e0af68"
SANS = "'Segoe UI', Ubuntu, -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# ---------------------------------------------------------------- data

API = "https://api.github.com/graphql"

REPOS_Q = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    name login createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) { totalCount }
    repositories(ownerAffiliations: [OWNER], isFork: false, first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name description stargazerCount forkCount
        primaryLanguage { name color }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
  }
}"""

YEAR_Q = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def gql(token, query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]


def fetch(login, token):
    repos, cursor = [], None
    while True:
        u = gql(token, REPOS_Q, {"login": login, "cursor": cursor})["user"]
        repos += u["repositories"]["nodes"]
        page = u["repositories"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]

    now = dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    days, commits = {}, 0
    for year in range(start.year, now.year + 1):
        frm = max(start, dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc))
        to = min(now, dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        c = gql(token, YEAR_Q, {"login": login, "from": frm.isoformat(), "to": to.isoformat()})
        c = c["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"]
        for w in c["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]

    return {
        "name": u["name"] or u["login"],
        "created": start.date().isoformat(),
        "today": now.date().isoformat(),
        "followers": u["followers"]["totalCount"],
        "prs": u["pullRequests"]["totalCount"],
        "issues": u["issues"]["totalCount"],
        "contributed_to": u["repositoriesContributedTo"]["totalCount"],
        "commits": commits,
        "repos": repos,
        "days": days,
    }

# ---------------------------------------------------------------- helpers


def esc(s):
    return html.escape(str(s), quote=True)


def kfmt(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def nice_date(iso, year=False):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%b %-d, %Y") if year else d.strftime("%b %-d")


def wrap(text, width, lines):
    words, out, cur = (text or "").split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= width:
            cur = f"{cur} {w}".strip()
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][: width - 1].rstrip() + "…"
    return out


def svg(w, h, body, label):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
<style>
  text {{ font-family: {SANS}; }}
  .t {{ font-size: 15px; font-weight: 600; fill: {FG}; }}
  .eb {{ font: 600 11px {MONO}; fill: {AMBER}; letter-spacing: .08em; }}
  .l {{ font-size: 13px; fill: {MUTED}; }}
  .v {{ font-size: 13px; font-weight: 600; fill: {FG}; font-variant-numeric: tabular-nums; }}
  .s {{ font-size: 12px; fill: {FAINT}; }}
  .m {{ font: 600 10.5px {MONO}; fill: {FAINT}; letter-spacing: .1em; }}
  .in {{ animation: in .6s ease-out backwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: none; }} }}
  .draw {{ animation: draw 2s ease-out .3s backwards; }}
  @keyframes draw {{ from {{ stroke-dasharray: 2400; stroke-dashoffset: 2400; }} to {{ stroke-dasharray: 2400; stroke-dashoffset: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .in, .draw {{ animation: none; }} }}
</style>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
{body}
</svg>
"""


def delay(i, step=0.08):
    return f'style="animation-delay:{i * step:.2f}s"'

# ---------------------------------------------------------------- cards


def stats_card(d):
    stars = sum(r["stargazerCount"] for r in d["repos"])
    years = int(d["today"][:4]) - int(d["created"][:4])
    rows = [
        ("Stars earned", stars, AMBER),
        ("Commits", d["commits"], BLUE),
        ("Pull requests", d["prs"], VIOLET),
        ("Issues", d["issues"], CYAN),
        ("Repositories", len(d["repos"]), GREEN),
    ]
    body = [f'<text class="eb" x="24" y="34">GITHUB STATS</text>',
            f'<text class="t" x="24" y="54">{esc(d["name"])}</text>']
    for i, (label, val, col) in enumerate(rows):
        y = 84 + i * 21
        body.append(
            f'<g class="in" {delay(i + 1)}><circle cx="28" cy="{y - 4}" r="3.5" fill="{col}"/>'
            f'<text class="l" x="40" y="{y}">{label}</text>'
            f'<text class="v" x="262" y="{y}" text-anchor="end">{kfmt(val)}</text></g>')
    body.append(f'<line x1="292" y1="40" x2="292" y2="160" stroke="{BORDER}"/>')
    body.append(
        f'<g class="in" {delay(6)}><text x="344" y="108" text-anchor="middle" '
        f'style="font-size:44px;font-weight:700;fill:{AMBER}">{years}</text>'
        f'<text class="m" x="344" y="132" text-anchor="middle">YEARS ON</text>'
        f'<text class="m" x="344" y="146" text-anchor="middle">GITHUB</text></g>')
    return svg(400, 180, "\n".join(body), f"{d['name']} GitHub stats")


def langs_card(d):
    sizes, colors = defaultdict(int), {}
    for r in d["repos"]:
        if r["name"] in EXCLUDE_REPOS:
            continue
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            if n in EXCLUDE_LANGS:
                continue
            sizes[n] += e["size"]
            colors[n] = e["node"]["color"] or FAINT
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:8]
    total = sum(v for _, v in top) or 1
    body = ['<text class="eb" x="24" y="34">LANGUAGES</text>',
            '<text class="t" x="24" y="54">Most used</text>',
            '<clipPath id="bar"><rect x="24" y="70" width="352" height="8" rx="4"/></clipPath>',
            '<g clip-path="url(#bar)">']
    x = 24.0
    for name, v in top:
        w = 352 * v / total
        body.append(f'<rect x="{x:.2f}" y="70" width="{w + 0.5:.2f}" height="8" fill="{colors[name]}"/>')
        x += w
    body.append("</g>")
    for i, (name, v) in enumerate(top):
        cx, cy = (24 if i < 4 else 212), 104 + (i % 4) * 20
        body.append(
            f'<g class="in" {delay(i + 1, .06)}><circle cx="{cx + 5}" cy="{cy - 4}" r="4.5" fill="{colors[name]}"/>'
            f'<text class="l" x="{cx + 16}" y="{cy}">{esc(name)}</text>'
            f'<text class="s" x="{cx + 164}" y="{cy}" text-anchor="end">{100 * v / total:.1f}%</text></g>')
    return svg(400, 180, "\n".join(body), "Most used languages")


def streaks(days, today):
    dates = sorted(days)
    total = sum(days.values())
    longest, run, run_start, best = 0, 0, None, (None, None)
    for ds in dates:
        if days[ds] > 0:
            run_start = ds if run == 0 else run_start
            run += 1
            if run > longest:
                longest, best = run, (run_start, ds)
        else:
            run = 0
    # current streak: count back from today (or yesterday if today has nothing yet)
    cur, end = 0, dt.date.fromisoformat(today)
    if days.get(today, 0) == 0:
        end -= dt.timedelta(days=1)
    day = end
    while days.get(day.isoformat(), 0) > 0:
        cur += 1
        day -= dt.timedelta(days=1)
    cur_range = ((day + dt.timedelta(days=1)).isoformat(), end.isoformat()) if cur else (None, None)
    return total, (cur, cur_range), (longest, best)


def streak_card(d):
    total, (cur, cr), (lng, lr) = streaks(d["days"], d["today"])
    def span(r, year=False):
        if not r[0]:
            return "Start one today"
        tail = f", {r[1][:4]}" if year else ""
        return f"{nice_date(r[0])} – {nice_date(r[1])}{tail}"
    W, H, col = 820, 170, 820 / 3
    body = []
    for i in (1, 2):
        body.append(f'<line x1="{col * i:.1f}" y1="34" x2="{col * i:.1f}" y2="136" stroke="{BORDER}"/>')
    # total
    body.append(
        f'<g class="in"><text x="{col / 2:.1f}" y="82" text-anchor="middle" style="font-size:30px;font-weight:700;fill:{FG}">{total:,}</text>'
        f'<text class="m" x="{col / 2:.1f}" y="110" text-anchor="middle">TOTAL CONTRIBUTIONS</text>'
        f'<text class="s" x="{col / 2:.1f}" y="130" text-anchor="middle">{nice_date(d["created"], True)} – Present</text></g>')
    # current, ringed
    cx = col * 1.5
    body.append(
        f'<g class="in" {delay(2)}><circle cx="{cx:.1f}" cy="64" r="34" fill="none" stroke="{AMBER}" stroke-width="3" stroke-opacity=".9"/>'
        f'<text x="{cx:.1f}" y="75" text-anchor="middle" style="font-size:30px;font-weight:700;fill:{AMBER}">{cur}</text>'
        f'<text class="m" x="{cx:.1f}" y="124" text-anchor="middle" style="fill:{AMBER}">CURRENT STREAK</text>'
        f'<text class="s" x="{cx:.1f}" y="143" text-anchor="middle">{span(cr)}</text></g>')
    # longest
    cx = col * 2.5
    body.append(
        f'<g class="in" {delay(4)}><text x="{cx:.1f}" y="82" text-anchor="middle" style="font-size:30px;font-weight:700;fill:{PINK}">{lng}</text>'
        f'<text class="m" x="{cx:.1f}" y="110" text-anchor="middle">LONGEST STREAK</text>'
        f'<text class="s" x="{cx:.1f}" y="130" text-anchor="middle">{span(lr, year=True)}</text></g>')
    return svg(W, H, "\n".join(body), "Contribution streak")


def activity_card(d, n=31):
    end = dt.date.fromisoformat(d["today"])
    pts = [((end - dt.timedelta(days=n - 1 - i)).isoformat()) for i in range(n)]
    vals = [d["days"].get(p, 0) for p in pts]
    top = max(vals + [4])
    step = max(1, -(-top // 4))
    ymax = step * 4
    W, H, L, R, T, B = 820, 250, 56, 28, 64, 40
    pw, ph = W - L - R, H - T - B
    X = lambda i: L + pw * i / (n - 1)
    Y = lambda v: T + ph * (1 - v / ymax)
    body = ['<text class="eb" x="24" y="34">ACTIVITY</text>',
            f'<text class="t" x="24" y="54">Contributions in the last {n} days</text>',
            f'<defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".35"/>'
            f'<stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient></defs>']
    for k in range(5):
        v = step * k
        body.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W - R}" y2="{Y(v):.1f}" stroke="{BORDER}"/>'
                    f'<text class="s" x="{L - 10}" y="{Y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    for i in range(0, n, 5):
        body.append(f'<text class="s" x="{X(i):.1f}" y="{H - 14}" text-anchor="middle">{nice_date(pts[i])}</text>')
    line = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
    body.append(f'<polygon class="in" style="animation-delay:.8s" points="{X(0):.1f},{Y(0):.1f} {line} {X(n - 1):.1f},{Y(0):.1f}" fill="url(#fill)"/>')
    body.append(f'<polyline class="draw" points="{line}" fill="none" stroke="{VIOLET}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>')
    for i, v in enumerate(vals):
        body.append(f'<circle class="in" style="animation-delay:{.3 + i * .05:.2f}s" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="2.6" fill="{PINK}"/>')
    body.append(f'<circle cx="{X(n - 1):.1f}" cy="{Y(vals[-1]):.1f}" r="6" fill="none" stroke="{AMBER}" stroke-width="1.5"/>')
    return svg(W, H, "\n".join(body), "Contribution activity")


BOOK = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.71 "
        "1.71.75.75 0 0 1-1.06 1.06A2.5 2.5 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.71A2.5 2.5 0 0 1 4.5 9h8Z")
FORK = ("M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 "
        "2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 "
        "0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z")


def pin_card(r):
    lang = r["primaryLanguage"] or {"name": "Markdown", "color": FAINT}
    lines = wrap(r["description"] or PIN_BLURBS.get(r["name"], "No description yet."), 54, 2)
    body = [f'<path transform="translate(24 21)" d="{BOOK}" fill="{FAINT}"/>',
            f'<text x="48" y="34" style="font-size:15px;font-weight:600;fill:{BLUE}">{esc(r["name"])}</text>']
    for i, ln in enumerate(lines):
        body.append(f'<text class="l" x="24" y="{62 + i * 18}" style="font-size:12.5px">{esc(ln)}</text>')
    lw = 24 + 16 + len(lang["name"]) * 7.2
    body.append(
        f'<g class="in"><circle cx="29" cy="101" r="5" fill="{lang["color"] or FAINT}"/>'
        f'<text class="s" x="40" y="105">{esc(lang["name"])}</text>'
        f'<text class="s" x="{lw + 14:.0f}" y="105">★ {r["stargazerCount"]}</text>'
        f'<path transform="translate({lw + 54:.0f} 93)" d="{FORK}" fill="{FAINT}"/>'
        f'<text class="s" x="{lw + 74:.0f}" y="105">{r["forkCount"]}</text></g>')
    return svg(400, 124, "\n".join(body), f"{r['name']} repository")


def render_all(d, out):
    os.makedirs(out, exist_ok=True)
    files = {
        "stats.svg": stats_card(d),
        "languages.svg": langs_card(d),
        "streak.svg": streak_card(d),
        "activity.svg": activity_card(d),
    }
    by_name = {r["name"]: r for r in d["repos"]}
    for name in PINS:
        if name in by_name:
            files[f"pin-{name}.svg"] = pin_card(by_name[name])
        else:
            print(f"warning: pinned repo {name!r} not found (private, renamed or a fork?)", file=sys.stderr)
    for fn, content in files.items():
        with open(os.path.join(out, fn), "w", encoding="utf-8") as f:
            f.write(content)
    print("wrote", ", ".join(files))


if __name__ == "__main__":
    login = sys.argv[1] if len(sys.argv) > 1 else "jo-jordan"
    out = sys.argv[2] if len(sys.argv) > 2 else "dist"
    token = os.environ.get("PROFILE_TOKEN") or os.environ["GITHUB_TOKEN"]
    render_all(fetch(login, token), out)
