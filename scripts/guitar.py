#!/usr/bin/env python3
"""Draw assets/guitar.svg, the animated T-style guitar on the profile README.

    python3 scripts/guitar.py assets/guitar.svg
"""
import math, random, sys
random.seed(11)
W, H = 1200, 520
# --- geometry (x grows toward the headstock) ---
SADDLE, NUT = 205.0, 880.0
SCALE = NUT - SADDLE                       # 648 mm scale drawn as 675 px
fret = lambda n: NUT - SCALE * (1 - 2 ** (-n / 12))
FB_END = fret(21) - 8                      # fretboard end, just past fret 21
def neck_y(x, top=True):                   # neck taper: 52px at body -> 40px at nut
    t = (x - FB_END) / (NUT - FB_END)
    half = 26 - 6 * t
    return 250 - half if top else 250 + half
str_bridge = [226 + i * 9.6 for i in range(6)]
str_nut = [236 + i * 5.6 for i in range(6)]
posts = [(938 + i * 21, 213) for i in range(6)]

BODY = ("M492 226 C520 222 538 196 532 166 C526 124 494 98 450 96 C410 94 380 106 344 110 "
        "C300 115 250 96 196 92 C146 88 116 122 114 172 C110 214 110 288 114 330 "
        "C118 382 150 414 200 408 C262 402 300 386 342 390 C392 394 438 404 466 384 "
        "C490 366 486 300 492 274 Z")
GUARD = ("M488 232 C504 224 512 200 506 176 C500 150 482 138 458 138 C434 138 418 150 410 174 "
         "L402 250 C398 298 402 332 414 350 C430 372 454 372 466 356 C480 338 478 300 488 268 Z")
HEAD = ("M880 231 C895 229 905 214 918 205 C926 199 936 197 952 197 L1046 197 "
        "C1068 197 1076 216 1069 232 C1060 251 1032 253 1002 255 C962 258 930 263 905 268 L880 269 Z")

o = []
add = o.append
add(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated neon T-style electric guitar being strummed">
<defs>
  <linearGradient id="stage" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0b14"/><stop offset="1" stop-color="#11101d"/></linearGradient>
  <radialGradient id="spot" cx=".42" cy=".5" r=".55"><stop offset="0" stop-color="#ff9e3d" stop-opacity=".16"/><stop offset="1" stop-color="#ff9e3d" stop-opacity="0"/></radialGradient>
  <linearGradient id="blonde" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6c770"/><stop offset=".55" stop-color="#e0a043"/><stop offset="1" stop-color="#a8651f"/></linearGradient>
  <radialGradient id="burst" cx=".45" cy=".5" r=".6"><stop offset=".6" stop-color="#5a2a08" stop-opacity="0"/><stop offset="1" stop-color="#3a1604" stop-opacity=".55"/></radialGradient>
  <linearGradient id="maple" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3d9a0"/><stop offset=".5" stop-color="#e8c57f"/><stop offset="1" stop-color="#cfa45c"/></linearGradient>
  <linearGradient id="chrome" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f6fb"/><stop offset=".45" stop-color="#9aa3b5"/><stop offset=".55" stop-color="#e6e9f2"/><stop offset="1" stop-color="#6b7385"/></linearGradient>
  <linearGradient id="gloss" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="guard" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#25232b"/><stop offset="1" stop-color="#0c0b10"/></linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7df9ff" stop-opacity="0"/><stop offset=".5" stop-color="#7df9ff" stop-opacity=".45"/><stop offset="1" stop-color="#7df9ff" stop-opacity="0"/></linearGradient>
  <linearGradient id="eq" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ff2e88"/><stop offset=".6" stop-color="#ff9e3d"/><stop offset="1" stop-color="#7df9ff"/></linearGradient>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>
  <filter id="shadow" x="-10%" y="-10%" width="130%" height="140%"><feDropShadow dx="0" dy="14" stdDeviation="12" flood-color="#000" flood-opacity=".6"/></filter>
  <clipPath id="guitar"><path d="{BODY}"/><path d="{HEAD}"/><path d="M{FB_END:.1f} {neck_y(FB_END):.1f} L{NUT} {neck_y(NUT):.1f} L{NUT} {neck_y(NUT, False):.1f} L{FB_END:.1f} {neck_y(FB_END, False):.1f} Z"/></clipPath>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#7df9ff" stroke-opacity=".06"/></pattern>
</defs>
<style>
  .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .hud {{ font-size: 12px; fill: #7df9ff; fill-opacity: .7; letter-spacing: .14em; }}
  .hud2 {{ font-size: 11px; fill: #c9c3e6; fill-opacity: .55; letter-spacing: .12em; }}
  .dim {{ stroke: #7df9ff; stroke-opacity: .35; stroke-width: 1; fill: none; }}
  .vib {{ animation: strum 4s cubic-bezier(.2,.7,.3,1) infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes strum {{
    0%, 100% {{ opacity: .15; transform: scaleY(1) translateY(0); }}
    1.5% {{ opacity: 1; transform: translateY(-2.6px); }}
    3% {{ transform: translateY(2.4px); }}
    4.5% {{ transform: translateY(-2px); }}
    6% {{ transform: translateY(1.7px); }}
    7.5% {{ transform: translateY(-1.3px); }}
    9% {{ transform: translateY(1px); }}
    11% {{ transform: translateY(-.7px); }}
    13% {{ transform: translateY(.5px); }}
    16% {{ transform: translateY(-.3px); }}
    30% {{ opacity: .35; transform: translateY(0); }}
  }}
  .ring {{ animation: ring 4s ease-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes ring {{ 0% {{ opacity: 0; transform: scale(.3); }} 3% {{ opacity: .8; }} 45%, 100% {{ opacity: 0; transform: scale(1.9); }} }}
  .sweep {{ animation: sweep 6s linear infinite; }}
  @keyframes sweep {{ 0% {{ transform: translateX(-260px); }} 60%, 100% {{ transform: translateX(1200px); }} }}
  .bar {{ transform-box: fill-box; transform-origin: bottom; animation: eq 1.2s ease-in-out infinite alternate; }}
  @keyframes eq {{ from {{ transform: scaleY(.15); }} to {{ transform: scaleY(1); }} }}
  .led {{ animation: led 4s ease-out infinite; }}
  @keyframes led {{ 0%, 100% {{ opacity: .35; }} 2% {{ opacity: 1; }} 25% {{ opacity: .5; }} }}
  .blink {{ animation: blink 1.6s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .float {{ animation: float 6s ease-in-out infinite; }}
  @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-5px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .vib, .ring, .sweep, .bar, .led, .blink, .float {{ animation: none; }} }}
</style>
<rect width="{W}" height="{H}" rx="18" fill="url(#stage)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#spot)"/>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="#7df9ff" stroke-opacity=".18"/>
''')
# HUD corners
for x, y, dx, dy in [(24, 24, 1, 1), (W-24, 24, -1, 1), (24, H-24, 1, -1), (W-24, H-24, -1, -1)]:
    add(f'<path class="dim" style="stroke-opacity:.6" d="M{x} {y + 18*dy} V{y} H{x + 18*dx}"/>')
add('<text class="mono hud" x="52" y="46">JO-JORDAN <tspan fill="#ff2e88">//</tspan> T-STYLE ELECTRIC</text>')
add('<text class="mono hud2" x="52" y="64">ASH BODY · MAPLE NECK · 2× SINGLE COIL</text>')
add(f'<g class="mono" text-anchor="end"><circle class="blink" cx="{W-160}" cy="42" r="4" fill="#ff2e88"/>'
    f'<text class="hud" x="{W-52}" y="46" style="fill:#ff2e88;fill-opacity:.9">● LIVE · 120 BPM</text>'
    f'<text class="hud2" x="{W-52}" y="64">TOKYO · DRINKING OR CODING</text></g>')

add('<g class="float">')
# sound rings from the bridge pickup
for k in range(3):
    add(f'<circle class="ring" style="animation-delay:{k*0.25:.2f}s" cx="262" cy="250" r="120" fill="none" stroke="#ff9e3d" stroke-width="1.5"/>')

add('<g filter="url(#shadow)">')
# body
add(f'<path d="{BODY}" fill="url(#blonde)"/>')
add(f'<path d="{BODY}" fill="url(#burst)"/>')
add(f'<path d="{BODY}" fill="none" stroke="#ffe2a8" stroke-opacity=".7" stroke-width="1.2"/>')
# wood grain
for i in range(9):
    y = 110 + i * 34 + random.uniform(-6, 6)
    add(f'<path d="M110 {y:.0f} C220 {y-14:.0f} 330 {y+16:.0f} 540 {y-4:.0f}" fill="none" stroke="#8a4f17" stroke-opacity=".12" stroke-width="{random.uniform(1,3):.1f}" clip-path="url(#guitar)"/>')
add(f'<path d="{GUARD}" fill="url(#guard)" stroke="#f2ede4" stroke-opacity=".8" stroke-width="2.2"/>')
add(f'<path d="{GUARD}" fill="url(#gloss)"/>')
for sx, sy in [(458, 146), (414, 186), (408, 290), (440, 362), (498, 196)]:
    add(f'<circle cx="{sx}" cy="{sy}" r="2.6" fill="url(#chrome)"/>')
# control plate + knobs + switch
add('<g transform="rotate(-9 380 362)"><rect x="300" y="346" width="150" height="32" rx="16" fill="url(#chrome)"/>'
    '<circle cx="338" cy="362" r="11" fill="url(#chrome)" stroke="#5c6474"/><circle cx="378" cy="362" r="11" fill="url(#chrome)" stroke="#5c6474"/>'
    '<rect x="408" y="358" width="30" height="8" rx="4" fill="#1a1a1f"/><circle class="led" cx="432" cy="362" r="5" fill="#ff2e88"/></g>')
for cx in (338, 378):
    pass
# bridge plate (ashtray), saddles, bridge pickup
add('<path d="M176 196 H296 V304 H176 Z" fill="url(#chrome)" stroke="#59606f" opacity=".92"/>')
add('<path d="M181 201 H291 V299 H181 Z" fill="none" stroke="#ffffff" stroke-opacity=".4"/>')
for sx, sy in [(184, 204), (184, 296), (288, 204), (288, 296)]:
    add(f'<circle cx="{sx}" cy="{sy}" r="2.4" fill="#59606f"/>')
for j in range(3):
    y = 221 + j * 19.2
    add(f'<rect x="196" y="{y:.1f}" width="22" height="16" rx="7" fill="url(#chrome)" stroke="#59606f"/>')
add('<g transform="rotate(-6 262 250)"><rect x="248" y="196" width="28" height="108" rx="6" fill="#121116" stroke="#3a3842"/>')
for i in range(6):
    add(f'<circle class="led" style="animation-delay:{i*0.06:.2f}s" cx="262" cy="{213 + i*14.8:.1f}" r="4.2" fill="#ff9e3d"/>')
add('</g>')
# neck pickup (chrome cover)
add('<rect x="368" y="203" width="26" height="94" rx="11" fill="url(#chrome)" stroke="#59606f"/>')
add('<rect x="372" y="207" width="18" height="86" rx="8" fill="none" stroke="#ffffff" stroke-opacity=".5"/>')
# neck + fretboard
nt, nb = neck_y(FB_END), neck_y(FB_END, False)
add(f'<path d="M{FB_END:.1f} {nt:.1f} L{NUT} {neck_y(NUT):.1f} L{NUT} {neck_y(NUT, False):.1f} L{FB_END:.1f} {nb:.1f} Z" fill="url(#maple)" stroke="#b78a43" stroke-opacity=".6"/>')
for n in range(1, 22):
    x = fret(n)
    add(f'<line x1="{x:.1f}" y1="{neck_y(x)+1:.1f}" x2="{x:.1f}" y2="{neck_y(x, False)-1:.1f}" stroke="#d9dde6" stroke-width="2"/>')
for n in (3, 5, 7, 9, 15, 17, 19, 21):
    x = (fret(n) + fret(n - 1)) / 2
    add(f'<circle cx="{x:.1f}" cy="250" r="3.4" fill="#1b1a20"/>')
x12 = (fret(12) + fret(11)) / 2
add(f'<circle cx="{x12:.1f}" cy="241" r="3.4" fill="#1b1a20"/><circle cx="{x12:.1f}" cy="259" r="3.4" fill="#1b1a20"/>')
add(f'<rect x="{NUT-4}" y="{neck_y(NUT):.1f}" width="5" height="{neck_y(NUT, False)-neck_y(NUT):.1f}" fill="#f7f1e3"/>')
# headstock + tuners
for i, (px, py) in enumerate(posts):
    add(f'<rect x="{px-6}" y="178" width="12" height="22" rx="3" fill="url(#chrome)" stroke="#59606f"/>'
        f'<ellipse cx="{px}" cy="176" rx="9" ry="6" fill="url(#chrome)" stroke="#59606f"/>')
add(f'<path d="{HEAD}" fill="url(#maple)" stroke="#b78a43" stroke-opacity=".7"/>')
add('<path d="M1060 228 C1050 244 1030 247 1000 249" fill="none" stroke="#fff6dc" stroke-opacity=".5"/>')
for px, py in posts:
    add(f'<circle cx="{px}" cy="{py}" r="6.5" fill="url(#chrome)" stroke="#59606f"/><circle cx="{px}" cy="{py}" r="2.2" fill="#3d4250"/>')
add('<rect x="966" y="232" width="18" height="5" rx="2.5" fill="url(#chrome)"/>')   # string tree
add('</g>')  # shadow group

# scan sweep clipped to the guitar
add('<g clip-path="url(#guitar)"><rect class="sweep" x="0" y="80" width="180" height="340" fill="url(#sweep)"/></g>')
# neon edge
for d in (BODY, HEAD):
    add(f'<path d="{d}" fill="none" stroke="#7df9ff" stroke-width="1.6" stroke-opacity=".9" filter="url(#glow)"/>')

# strings: bridge -> nut -> post
gauges = [2.0, 1.7, 1.45, 1.2, 0.95, 0.8]
for i in range(6):
    yb, yn = str_bridge[i], str_nut[i]
    px, py = posts[i]
    col = "#d8c7a0" if i < 3 else "#e9edf5"
    add(f'<path d="M{SADDLE} {yb:.1f} L{NUT} {yn:.1f} L{px} {py}" fill="none" stroke="{col}" stroke-width="{gauges[i]}"/>')
for i in range(6):
    yb, yn = str_bridge[i], str_nut[i]
    add(f'<g class="vib" style="animation-delay:{i*0.07:.2f}s"><line x1="{SADDLE+70}" y1="{yb + (yn-yb)*70/SCALE:.1f}" x2="{NUT-10}" y2="{yn - (yn-yb)*10/SCALE:.1f}" stroke="#7df9ff" stroke-width="{gauges[i]+2.5:.1f}" filter="url(#soft)"/>'
        f'<line x1="{SADDLE+70}" y1="{yb + (yn-yb)*70/SCALE:.1f}" x2="{NUT-10}" y2="{yn - (yn-yb)*10/SCALE:.1f}" stroke="#eaffff" stroke-width="{gauges[i]*.6:.2f}"/></g>')
add('</g>')  # float

# dimension lines (blueprint)
add(f'<g class="mono"><path class="dim" d="M{SADDLE} 426 V440 M{SADDLE} 433 H{NUT} M{NUT} 426 V440"/>'
    f'<rect x="{(SADDLE+NUT)/2-74:.0f}" y="425" width="148" height="16" fill="#0d0d18"/>'
    f'<text class="hud2" x="{(SADDLE+NUT)/2:.0f}" y="437" text-anchor="middle" style="fill:#7df9ff;fill-opacity:.75">SCALE 648 MM · 21 FRETS</text></g>')

# equalizer
n = 72
for k in range(n):
    x = 60 + k * (W - 120) / n
    h = 8 + 26 * abs(math.sin(k * 0.37)) * random.uniform(.5, 1)
    add(f'<rect class="bar" x="{x:.1f}" y="{496 - h:.1f}" width="{(W-120)/n - 4:.1f}" height="{h:.1f}" rx="1.5" fill="url(#eq)" fill-opacity=".8" '
        f'style="animation-duration:{random.uniform(.5, 1.3):.2f}s;animation-delay:-{random.uniform(0, 1.2):.2f}s"/>')
add('</svg>')
open(sys.argv[1], 'w').write("\n".join(o) + "\n")
