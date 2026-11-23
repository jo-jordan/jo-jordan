#!/usr/bin/env python3
"""Draw assets/guitar.svg: the animated 2D gold T-style guitar on the profile README.

    python3 scripts/guitar.py assets/guitar.svg

Geometry is in millimetres (x toward the headstock, y up), on a real
648 mm scale with 22 frets, and is scaled and tilted into the canvas.
"""
import math
import random
import sys

random.seed(5)
W, H = 1200, 540
K = 1.1                                    # px per mm
NUT, SCALE, FB_END, SADDLE = 594.0, 648.0, 128.0, -54.0
fret = lambda n: NUT - SCALE * (1 - 2 ** (-n / 12))
half_w = lambda x: 28 + (21.4 - 28) * (x - FB_END) / (NUT - FB_END)

BODY = [(188, 28), (193, 101), (164, 141), (133, 150), (48, 157), (-32, 160), (-120, 156), (-165, 141), (-190, 80),
        (-195, 0), (-190, -82), (-169, -143), (-120, -160), (-32, -163), (48, -161), (133, -154), (176, -138),
        (189, -122), (186, -108), (174, -100), (150, -90), (130, -70), (126, -50), (133, -28)]
GUARD = [(170, 27), (168, 48), (146, 72), (119, 81), (60, 82), (14, 80), (11, 40), (10, -18), (10, -80),
         (11, -116), (48, -121), (110, -125), (146, -123), (170, -118), (177, -112), (170, -105), (148, -96),
         (127, -76), (120, -50), (123, -27)]
HEAD = [(594, -21.4), (630, -23), (690, -25), (740, -22), (772, -8), (784, 12), (780, 34), (762, 44), (700, 46),
        (650, 44), (624, 37), (606, 26), (594, 21.4)]
POSTS = [(625 + 25 * i, 30) for i in range(6)]


def spline(pts, per=8):
    """Centripetal Catmull-Rom through pts (open)."""
    p = [(2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])] + pts + [(2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        t0 = 0.0
        t1 = t0 + math.dist(p0, p1) ** 0.5
        t2 = t1 + math.dist(p1, p2) ** 0.5
        t3 = t2 + math.dist(p2, p3) ** 0.5
        for s in range(per):
            t = t1 + (t2 - t1) * s / per
            mix = lambda a, b, ta, tb: tuple(((tb - t) * u + (t - ta) * v) / (tb - ta) for u, v in zip(a, b))
            a1, a2, a3 = mix(p0, p1, t0, t1), mix(p1, p2, t1, t2), mix(p2, p3, t2, t3)
            out.append(mix(mix(a1, a2, t0, t2), mix(a2, a3, t1, t3), t1, t2))
    out.append(pts[-1])
    return out


def path(pts, close=True):
    return "M" + " L".join(f"{x:.1f} {-y:.1f}" for x, y in pts) + (" Z" if close else "")


body_d = path(spline(BODY) + [(190, -28), (190, 28)])
guard_d = path(spline(GUARD) + [(123, 24), (170, 24)])
head_d = path(spline(HEAD))
fb = [(FB_END, half_w(FB_END)), (NUT, half_w(NUT)), (NUT, -half_w(NUT)), (FB_END, -half_w(FB_END))]
fb_d = path(fb)
neck_d = path([(118, half_w(FB_END) + .9), (NUT, half_w(NUT) + .9), (NUT, -half_w(NUT) - .9), (118, -half_w(FB_END) - .9)])

o = []
add = o.append
add(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated gold T-style electric guitar with a dark brushed pickguard; its strings are strummed every few seconds">
<defs>
  <radialGradient id="stage" cx=".5" cy=".46" r=".75"><stop offset="0" stop-color="#2a1c0b"/><stop offset=".5" stop-color="#15100b"/><stop offset="1" stop-color="#0a090c"/></radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="#ffb11f" stop-opacity=".5"/><stop offset="1" stop-color="#ffb11f" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="12" cy="12" r="1" fill="#ffd27a" fill-opacity=".07"/></pattern>

  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6b31c"/><stop offset=".45" stop-color="#e99a0a"/><stop offset="1" stop-color="#cf7c00"/></linearGradient>
  <radialGradient id="goldHi" cx=".25" cy=".8" r=".55"><stop offset="0" stop-color="#f3d23a" stop-opacity=".75"/><stop offset=".6" stop-color="#f0c020" stop-opacity=".18"/><stop offset="1" stop-color="#f0c020" stop-opacity="0"/></radialGradient>
  <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff6d0" stop-opacity="0"/><stop offset=".5" stop-color="#fff6d0" stop-opacity=".5"/><stop offset="1" stop-color="#fff6d0" stop-opacity="0"/></linearGradient>
  <filter id="flake" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="4" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 .93  0 0 0 0 .62  0 0 0 9 -5.75"/>
  </filter>
  <filter id="flakeDark" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="9" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 .45  0 0 0 0 .2  0 0 0 0 0  0 0 0 8 -4.6"/>
  </filter>

  <linearGradient id="guard" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5a5d64"/><stop offset=".5" stop-color="#3f4248"/><stop offset="1" stop-color="#4c4f56"/></linearGradient>
  <pattern id="brush" width="170" height="7" patternUnits="userSpaceOnUse">
    <rect x="0" y="0.6" width="120" height=".5" fill="#fff" fill-opacity=".10"/><rect x="60" y="2.1" width="110" height=".4" fill="#000" fill-opacity=".22"/>
    <rect x="20" y="3.4" width="90" height=".5" fill="#fff" fill-opacity=".07"/><rect x="0" y="4.8" width="150" height=".4" fill="#000" fill-opacity=".16"/>
    <rect x="90" y="5.9" width="80" height=".5" fill="#fff" fill-opacity=".09"/>
  </pattern>
  <linearGradient id="black" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34363c"/><stop offset=".35" stop-color="#121316"/><stop offset="1" stop-color="#060607"/></linearGradient>
  <radialGradient id="knob" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#5b5e66"/><stop offset=".4" stop-color="#1c1d21"/><stop offset="1" stop-color="#050506"/></radialGradient>
  <linearGradient id="brass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f5dd96"/><stop offset=".5" stop-color="#cfa54a"/><stop offset="1" stop-color="#8b6418"/></linearGradient>
  <linearGradient id="champ" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a39566"/><stop offset=".3" stop-color="#f6efd0"/><stop offset=".6" stop-color="#cdbf8e"/><stop offset="1" stop-color="#8f8050"/></linearGradient>
  <linearGradient id="ebony" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b2420"/><stop offset=".5" stop-color="#171210"/><stop offset="1" stop-color="#0e0b0a"/></linearGradient>
  <linearGradient id="fretm" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8d929c"/><stop offset=".45" stop-color="#f7f8fb"/><stop offset="1" stop-color="#70757f"/></linearGradient>
  <linearGradient id="maple" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9c68a"/><stop offset=".6" stop-color="#d7ad6c"/><stop offset="1" stop-color="#b98a4a"/></linearGradient>
  <linearGradient id="eq" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#c26a00"/><stop offset="1" stop-color="#ffd36b"/></linearGradient>

  <filter id="drop" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="12" stdDeviation="11" flood-color="#000" flood-opacity=".65"/></filter>
  <filter id="small" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="1.2" stdDeviation="1.2" flood-color="#000" flood-opacity=".55"/></filter>
  <filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="blur1" x="-5%" y="-300%" width="110%" height="700%"><feGaussianBlur stdDeviation="1.1"/></filter>
  <clipPath id="bodyClip"><path d="{body_d}"/></clipPath>
  <clipPath id="guardClip"><path d="{guard_d}"/></clipPath>
  <clipPath id="headClip"><path d="{head_d}"/></clipPath>
</defs>
<style>
  .float {{ animation: float 7s ease-in-out infinite; }}
  @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}
  .halo {{ animation: halo 3.6s ease-out infinite; }}
  @keyframes halo {{ 0%, 100% {{ opacity: .45; }} 3% {{ opacity: 1; }} 40% {{ opacity: .5; }} }}
  .sheen {{ animation: sheen 7s ease-in-out infinite; }}
  @keyframes sheen {{ 0%, 12% {{ transform: translateX(-330px); }} 55%, 100% {{ transform: translateX(330px); }} }}
  .tw {{ animation: tw 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  @keyframes tw {{ 0%, 100% {{ opacity: 0; transform: scale(.3) rotate(0deg); }} 50% {{ opacity: 1; transform: scale(1) rotate(45deg); }} }}
  .wave, .lens {{ transform-box: fill-box; transform-origin: center; animation-duration: 3.6s; animation-iteration-count: infinite; }}
  .wave {{ animation-name: wave; animation-timing-function: linear; opacity: 0; }}
  @keyframes wave {{
    0% {{ opacity: 0; transform: scaleY(0); }} 1% {{ opacity: 1; transform: scaleY(1); }}
    3% {{ transform: scaleY(-.86); }} 5% {{ transform: scaleY(.74); }} 7% {{ transform: scaleY(-.63); }} 9% {{ transform: scaleY(.53); }}
    11% {{ transform: scaleY(-.44); }} 13.5% {{ transform: scaleY(.36); }} 16% {{ transform: scaleY(-.28); }} 19% {{ transform: scaleY(.2); }}
    22% {{ transform: scaleY(-.14); }} 26% {{ opacity: 1; transform: scaleY(.08); }} 31%, 100% {{ opacity: 0; transform: scaleY(0); }}
  }}
  .lens {{ animation-name: lens; animation-timing-function: ease-out; opacity: 0; }}
  @keyframes lens {{ 0% {{ opacity: 0; transform: scaleY(0); }} 1% {{ opacity: .55; transform: scaleY(1); }} 31%, 100% {{ opacity: 0; transform: scaleY(0); }} }}
  .pole {{ animation: pole 3.6s ease-out infinite; }}
  @keyframes pole {{ 0%, 100% {{ fill: #cdbf8e; }} 2% {{ fill: #fff3c4; }} 30% {{ fill: #cdbf8e; }} }}
  .bar {{ transform-box: fill-box; transform-origin: bottom; animation: bar 1s ease-in-out infinite alternate; }}
  @keyframes bar {{ from {{ transform: scaleY(.12); }} to {{ transform: scaleY(1); }} }}
  @media (prefers-reduced-motion: reduce) {{ .float, .halo, .sheen, .tw, .wave, .lens, .pole, .bar {{ animation: none; }} }}
</style>
<rect width="{W}" height="{H}" rx="20" fill="url(#stage)"/>
<rect width="{W}" height="{H}" rx="20" fill="url(#dots)"/>
<ellipse class="halo" cx="440" cy="270" rx="520" ry="250" fill="url(#halo)" opacity=".45"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="#ffcf70" stroke-opacity=".16"/>
''')

# equalizer along the bottom
n = 84
for k in range(n):
    bw = (W - 140) / n
    h = 6 + 24 * abs(math.sin(k * 0.33)) * random.uniform(.45, 1)
    add(f'<rect class="bar" x="{70 + k * bw:.1f}" y="{518 - h:.1f}" width="{bw - 4:.1f}" height="{h:.1f}" rx="1.5" fill="url(#eq)" fill-opacity=".55" '
        f'style="animation-duration:{random.uniform(.45, 1.2):.2f}s;animation-delay:-{random.uniform(0, 1.2):.2f}s"/>')

add('<g class="float">')
add(f'<g transform="translate(600 246) rotate(-4) scale({K}) translate(-294.5 0)">')

# ---- silhouettes with a soft drop shadow
add('<g filter="url(#drop)">')
for x, y in POSTS:                                              # tuner keys behind the headstock
    add(f'<rect x="{x - 1.8}" y="{-(y + 22):.1f}" width="3.6" height="10" fill="#3a3c42"/>'
        f'<rect x="{x - 5.5}" y="{-(y + 33):.1f}" width="11" height="14" rx="5" fill="url(#black)" stroke="#5a5d64" stroke-width=".6"/>')
add(f'<path d="{body_d}" fill="url(#gold)"/>')
add(f'<path d="{neck_d}" fill="#c99b58"/>')
add(f'<path d="{head_d}" fill="url(#maple)"/>')
add('</g>')

# ---- body paint: highlight, metal flake, rolled edge, travelling sheen
add('<g clip-path="url(#bodyClip)">')
add('<rect x="-200" y="-170" width="400" height="340" fill="url(#goldHi)"/>')
add('<rect x="-200" y="-170" width="400" height="340" filter="url(#flakeDark)" opacity=".4"/>')
add('<rect x="-200" y="-170" width="400" height="340" filter="url(#flake)" opacity=".55"/>')
add(f'<path d="{body_d}" fill="none" stroke="#8a4600" stroke-opacity=".55" stroke-width="11" filter="url(#blur3)"/>')
add(f'<path d="{body_d}" fill="none" stroke="#ffe08a" stroke-opacity=".55" stroke-width="2.2" transform="translate(1.2 1.6)" filter="url(#blur1)"/>')
add('<g transform="rotate(20)"><rect class="sheen" x="-70" y="-260" width="140" height="520" fill="url(#sheen)"/></g>')
for _ in range(16):                                             # twinkling flakes
    x, y = random.uniform(-180, 5), random.uniform(-150, 150)
    if abs(y) < 45 and x > -80 or (y < -70 and -125 < x):
        continue
    r = random.uniform(2.2, 4.2)
    add(f'<path class="tw" style="animation-delay:-{random.uniform(0, 2.4):.2f}s;animation-duration:{random.uniform(1.8, 3.4):.2f}s" '
        f'd="M{x:.1f} {y - r:.1f} L{x + r * .22:.1f} {y - r * .22:.1f} L{x + r:.1f} {y:.1f} L{x + r * .22:.1f} {y + r * .22:.1f} L{x:.1f} {y + r:.1f} L{x - r * .22:.1f} {y + r * .22:.1f} L{x - r:.1f} {y:.1f} L{x - r * .22:.1f} {y - r * .22:.1f} Z" fill="#fff8dc"/>')
add('</g>')
add(f'<path d="{body_d}" fill="none" stroke="#5e2f00" stroke-opacity=".8" stroke-width=".8"/>')

# ---- control plate, knobs, selector
add('<g filter="url(#small)"><rect x="-136.5" y="74.5" width="161" height="33" rx="16.5" fill="url(#black)" stroke="#4a4c53" stroke-width=".6"/></g>')
add('<rect x="-131" y="77" width="150" height="1.2" rx=".6" fill="#fff" fill-opacity=".22"/>')
for x in (-114, -52):
    add(f'<g filter="url(#small)"><circle cx="{x}" cy="91" r="10.4" fill="#08080a" stroke="#2c2e33" stroke-width="2" stroke-dasharray="1 1.1"/>'
        f'<circle cx="{x}" cy="91" r="8.6" fill="url(#knob)"/><circle cx="{x}" cy="91" r="8.6" fill="none" stroke="#6c7078" stroke-opacity=".5" stroke-width=".5"/></g>')
add('<rect x="-18" y="89.6" width="30" height="2.8" rx="1.4" fill="#000"/>'
    '<g filter="url(#small)"><path d="M-3 91 L7 84" stroke="#b9bdc6" stroke-width="1.6" stroke-linecap="round"/><ellipse cx="8" cy="83.4" rx="4.6" ry="3.4" fill="#0b0b0d" stroke="#3a3c42" stroke-width=".5"/></g>')
for x in (-128, 16):
    add(f'<circle cx="{x}" cy="91" r="1.7" fill="#000" stroke="#55585f" stroke-width=".4"/>')

# ---- bridge plate, bridge pickup, brass saddles
add('<g filter="url(#small)"><rect x="-76" y="-40" width="94" height="79" rx="2.5" fill="url(#black)" stroke="#4a4c53" stroke-width=".6"/></g>')
add('<rect x="-74" y="-38.4" width="90" height="1.1" fill="#fff" fill-opacity=".2"/>')
for x, y in [(-72, 35), (-72, -35), (14, 35), (14, -35)]:
    add(f'<circle cx="{x}" cy="{y}" r="1.7" fill="#000" stroke="#55585f" stroke-width=".4"/>')
add('<g transform="rotate(8 -5 0)"><rect x="-14" y="-35" width="18" height="70" rx="4" fill="#050506" stroke="#2e3035" stroke-width=".7"/>')
for i in range(6):
    add(f'<circle class="pole" style="animation-delay:{i * .07:.2f}s" cx="-5" cy="{-26.25 + i * 10.5:.2f}" r="2.1" fill="#cdbf8e"/>')
add('</g>')
for i in range(6):
    y = -26.25 + i * 10.5
    add(f'<rect x="-61" y="{y - 4.6:.2f}" width="14" height="9.2" rx="1.2" fill="url(#brass)" stroke="#6d4d10" stroke-width=".4"/>'
        f'<circle cx="-66" cy="{y:.2f}" r="1.5" fill="#1a1a1d"/><rect x="-72" y="{y - .7:.2f}" width="7" height="1.4" fill="#2b2c31"/>')

# ---- pickguard: dark brushed aluminium
add(f'<g filter="url(#small)"><path d="{guard_d}" fill="url(#guard)"/></g>')
add(f'<g clip-path="url(#guardClip)"><rect x="0" y="-130" width="190" height="220" fill="url(#brush)"/>'
    f'<rect x="60" y="-130" width="46" height="220" fill="#fff" fill-opacity=".06" transform="skewX(-18)" filter="url(#blur3)"/></g>')
add(f'<path d="{guard_d}" fill="none" stroke="#9a9ea7" stroke-opacity=".55" stroke-width=".7"/>')
for x, y in [(160, 46), (130, 74), (66, 76), (18, 74), (17, 8), (17, -60), (17, -110), (70, -117), (128, -118), (166, -112), (134, -84), (126, -48)]:
    add(f'<circle cx="{x}" cy="{-y}" r="2" fill="#0a0a0c" stroke="#6a6d75" stroke-width=".4"/><path d="M{x - 1.1} {-y} h2.2 M{x} {-y - 1.1} v2.2" stroke="#4b4e55" stroke-width=".4"/>')

# ---- neck pickup: champagne cover
add('<g filter="url(#small)"><rect x="102" y="-35" width="18" height="70" rx="8" fill="url(#champ)" stroke="#7a6c40" stroke-width=".5"/></g>')
add('<rect x="105" y="-31" width="12" height="62" rx="5.5" fill="none" stroke="#fffbe6" stroke-opacity=".7" stroke-width=".6"/>')
for y in (-39.5, 39.5):
    add(f'<circle cx="111" cy="{y}" r="1.6" fill="#0a0a0c" stroke="#6a6d75" stroke-width=".4"/>')

# ---- ebony fretboard, frets, bar inlays, nut
add(f'<path d="{fb_d}" fill="url(#ebony)"/>')
add(f'<path d="M{FB_END} {-half_w(FB_END) + 1.2:.1f} L{NUT} {-half_w(NUT) + 1.2:.1f}" stroke="#fff" stroke-opacity=".10" stroke-width="1"/>')
for nfr in (3, 5, 7, 9, 12, 15, 17, 19, 21):
    x = (fret(nfr) + fret(nfr - 1)) / 2
    hh = 15 if nfr == 12 else 6.5
    add(f'<rect x="{x - 1.9:.1f}" y="{-hh}" width="3.8" height="{2 * hh}" rx=".5" fill="#f3f0e8"/>')
for nfr in range(1, 23):
    x = fret(nfr)
    add(f'<rect x="{x - 1.1:.1f}" y="{-half_w(x) + .3:.1f}" width="2.2" height="{2 * half_w(x) - .6:.1f}" fill="url(#fretm)"/>')
add(f'<rect x="{NUT - .5}" y="{-half_w(NUT) - .4:.1f}" width="3.4" height="{2 * half_w(NUT) + .8:.1f}" rx=".6" fill="#f4eedd"/>')

# ---- headstock: grain, tuner posts, string tree, name decal
add('<g clip-path="url(#headClip)">')
for i in range(7):
    y = -40 + i * 11 + random.uniform(-2, 2)
    add(f'<path d="M590 {y:.1f} C650 {y - 5:.1f} 720 {y + 5:.1f} 790 {y - 2:.1f}" fill="none" stroke="#8a5f28" stroke-opacity=".16" stroke-width="{random.uniform(.6, 1.6):.1f}"/>')
add(f'<path d="{head_d}" fill="none" stroke="#fff3d2" stroke-opacity=".5" stroke-width="2" transform="translate(-.8 1.4)" filter="url(#blur1)"/>')
add('</g>')
add(f'<path d="{head_d}" fill="none" stroke="#7d5722" stroke-opacity=".8" stroke-width=".7"/>')
for x, y in POSTS:
    add(f'<g filter="url(#small)"><circle cx="{x}" cy="{-y}" r="5.4" fill="url(#black)" stroke="#55585f" stroke-width=".5"/></g>'
        f'<circle cx="{x}" cy="{-y}" r="2.9" fill="url(#knob)"/><circle cx="{x}" cy="{-y}" r=".9" fill="#000"/>')
add('<g filter="url(#small)"><circle cx="668" cy="-2" r="2.6" fill="url(#knob)" stroke="#55585f" stroke-width=".4"/></g>')
add('<text x="706" y="17" text-anchor="middle" font-family="\'Snell Roundhand\', \'Brush Script MT\', \'Segoe Script\', cursive" font-style="italic" font-weight="700" font-size="12" fill="#2a1a08" fill-opacity=".85">jo-jordan</text>')

# ---- strings: saddle -> nut -> tuner post, low E on top
gauge = [1.5, 1.3, 1.1, .85, .7, .6]
for i in range(6):
    ax, ay = SADDLE + 5, -(26.25 - 10.5 * i)
    bx, by = NUT, -(17.5 - 7 * i)
    px, py = POSTS[i][0], -POSTS[i][1]
    col = "#d9c9a2" if i < 3 else "#eef0f4"
    add(f'<path d="M{ax} {ay:.2f} L{bx} {by:.2f} L{px} {py + 2.6:.1f}" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="{gauge[i]}" transform="translate(0 1.3)"/>')
    add(f'<path d="M{ax} {ay:.2f} L{bx} {by:.2f} L{px} {py + 2.6:.1f}" fill="none" stroke="{col}" stroke-width="{gauge[i]}"/>')
for i in range(6):
    ax, ay = SADDLE + 5, -(26.25 - 10.5 * i)
    bx, by = NUT, -(17.5 - 7 * i)
    length, ang = math.hypot(bx - ax, by - ay), math.degrees(math.atan2(by - ay, bx - ax))
    amp = 3.4 - i * .32
    d = f"{i * .07:.2f}s"
    add(f'<g transform="translate({ax} {ay:.2f}) rotate({ang:.3f})">'
        f'<path class="lens" style="animation-delay:{d}" d="M0 0 Q{length / 2:.1f} {-2 * amp:.2f} {length:.1f} 0 Q{length / 2:.1f} {2 * amp:.2f} 0 0 Z" fill="#ffd978" fill-opacity=".5"/>'
        f'<g class="wave" style="animation-delay:{d}"><path d="M0 0 Q{length / 2:.1f} {-2 * amp:.2f} {length:.1f} 0" fill="none" stroke="#fff6d6" stroke-width="{gauge[i] + .5:.2f}"/>'
        f'<path d="M0 0 Q{length / 2:.1f} {2 * amp:.2f} {length:.1f} 0" fill="none" stroke="none"/></g></g>')

add('</g></g></svg>')
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(o) + "\n")
