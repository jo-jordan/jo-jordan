#!/usr/bin/env python3
"""Draw assets/guitar.svg: the animated butterscotch T-style guitar on the profile README.

    python3 scripts/guitar.py assets/guitar.svg

Body, headstock and pickguard outlines come from scripts/guitar_outline.json.
Frets are placed with the 12th-root-of-two rule between the nut and the saddles.
The guitar turns about the neck axis. It is built from flat slices at different
depths, so it keeps its thickness through the turn and shows its back.
"""
import json
import math
import os
import random
import re
import sys

random.seed(8)
HERE = os.path.dirname(os.path.abspath(__file__))
O = json.load(open(os.path.join(HERE, "guitar_outline.json")))

VB = (232, -44, 594, 1500)                 # viewBox: x, y, width, height
CX = 531.75                                # centre line of the neck
NUT, SADDLE, FB_END = 236.0, 1173.0, 900.0
SCALE = SADDLE - NUT
fret = lambda n: NUT + SCALE * (1 - 2 ** (-n / 12))
half_w = lambda y: 32.75 + (44.7 - 32.75) * (y - NUT) / (FB_END - NUT)
STR_SADDLE = [489.5 + 16.9 * i for i in range(6)]              # low E on the left
STR_NUT = [CX - 26.5 + 10.6 * i for i in range(6)]
POSTS = [(504 + 11.06 * i, 175 - 32 * i) for i in range(6)]    # low E nearest the nut
GAUGE = [2.5, 2.2, 1.9, 1.5, 1.25, 1.05]

poly = lambda pts: "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
body_d, head_d, guard_d, back_d = O["body"], O["head"], O["guard"], O["body_back"]
neck_d = poly([(CX - half_w(NUT), NUT - 2), (CX + half_w(NUT), NUT - 2), (CX + half_w(FB_END), FB_END - 3), (CX + half_w(FB_END) - 3, FB_END),
               (CX - half_w(FB_END) + 3, FB_END), (CX - half_w(FB_END), FB_END - 3)])

T = 6.0                                    # seconds per turn
Z_BODY, Z_NECK, Z_HEAD = (-32, 32), (6, 42), (15, 35)          # depth of each part: back face, front face
Z_KEYS = 25                                # tuner shafts sit halfway through the headstock
BODY_L, NECK_L, HEAD_L = list(range(-30, 31, 5)), list(range(8, 41, 4)), list(range(17, 34, 4))   # slices between the faces
A_BODY, A_HEAD = [-230, -190, -130, -70, 0, 80, 150, 200, 235], [-25, -5, 15, 35, 55]             # where the side walls are sampled
E = "cubic-bezier(.37, 0, .63, 1)"         # sine easing, so scaleX follows cos and the slides follow sin
zc = lambda v: ("z" if v >= 0 else "zm") + str(abs(int(v)))
cc = lambda v: ("c" if v >= 0 else "cm") + str(abs(int(v)))


def mix(a, b, t):
    pa, pb = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(u + (v - u) * t) for u, v in zip(pa, pb))


def shader(zr, back, front, edge):
    """Colour of a slice at depth z: lighter next to either face, where the edge rolls over."""
    return lambda z: edge if min(z - zr[0], zr[1] - z) <= 4 else mix(back, front, (z - zr[0]) / (zr[1] - zr[0]))


body_shade = shader(Z_BODY, "#d08c17", "#ecae29", "#f6c446")
neck_shade = shader(Z_NECK, "#d39a36", "#ecb94f", "#f7cc68")
head_shade = shader(Z_HEAD, "#d8a23c", "#efbd55", "#f9d079")


def span(d, xs):
    """Longest stretch of the vertical line x = xs that lies inside outline d."""
    pts = [tuple(float(v) for v in a.split()[-2:]) for _, a in re.findall(r"([MLCQ])([^MLCQZ]*)", d)]
    ys = sorted(p[1] + (q[1] - p[1]) * (xs - p[0]) / (q[0] - p[0]) for p, q in zip(pts, pts[1:] + pts[:1]) if (p[0] - xs) * (q[0] - xs) < 0)
    pairs = [(ys[i], ys[i + 1]) for i in range(0, len(ys) - 1, 2)]
    return max(pairs, key=lambda s: s[1] - s[0]) if pairs else None


wave_steps = [(0, 0), (1, 1), (2.8, -.86), (4.6, .74), (6.4, -.63), (8.2, .53), (10, -.44), (12, .36), (14.5, -.28), (17, .2), (20, -.14), (24, .08)]
k = 4 / T                                  # the strum keeps its length whatever the turn takes
STYLE = f"""
  .float {{ animation: float 7s ease-in-out infinite; }}
  @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
  /* One turn about the neck axis every {T:g} s. Every part is a stack of slices; a slice at depth z is drawn at x*cos + z*sin. */
  .spin {{ animation: spin {T:g}s infinite; }}
  @keyframes spin {{ 0%, 100% {{ transform: scaleX(1); animation-timing-function: {E}; }} 50% {{ transform: scaleX(-1); animation-timing-function: {E}; }} }}
  .side {{ transform: scaleX(0); animation: side {T:g}s {-T / 4:g}s infinite; }}
  @keyframes side {{ 0%, 100% {{ transform: scaleX(-1); animation-timing-function: {E}; }} 50% {{ transform: scaleX(1); animation-timing-function: {E}; }} }}
  .z {{ animation-duration: {T:g}s; animation-delay: {-T / 4:g}s; animation-iteration-count: infinite; }}
  .c {{ animation-duration: {T:g}s; animation-iteration-count: infinite; }}
""" + "".join(
    f"  .{zc(z)} {{ animation-name: {zc(z)}; }} @keyframes {zc(z)} {{ 0%, 100% {{ transform: translateX({-z}px); animation-timing-function: {E}; }} 50% {{ transform: translateX({z}px); animation-timing-function: {E}; }} }}\n"
    for z in sorted(set(BODY_L + NECK_L + HEAD_L + list(Z_BODY + Z_NECK + Z_HEAD) + [0, Z_KEYS]))
) + "".join(
    f"  .{cc(a)} {{ animation-name: {cc(a)}; }} @keyframes {cc(a)} {{ 0%, 100% {{ transform: translateX({a}px); animation-timing-function: {E}; }} 50% {{ transform: translateX({-a}px); animation-timing-function: {E}; }} }}\n"
    for a in sorted(set(A_BODY + A_HEAD)) if a
) + f"""  .front {{ animation: front {T:g}s step-end infinite; }}
  @keyframes front {{ 0% {{ opacity: 1; }} 25% {{ opacity: 0; }} 75%, 100% {{ opacity: 1; }} }}
  .back {{ opacity: 0; animation: back {T:g}s step-end infinite; }}
  @keyframes back {{ 0% {{ opacity: 0; }} 25% {{ opacity: 1; }} 75%, 100% {{ opacity: 0; }} }}
  .sheen {{ animation: sheen 8s ease-in-out infinite; }}
  @keyframes sheen {{ 0%, 15% {{ transform: translateX(-420px); }} 55%, 100% {{ transform: translateX(420px); }} }}
  .glint {{ transform-box: fill-box; transform-origin: center; animation: glint {T:g}s ease-in-out infinite; opacity: 0; }}
  @keyframes glint {{ 0%, 60%, 100% {{ opacity: 0; transform: scale(.2) rotate(0deg); }} 80% {{ opacity: 1; transform: scale(1) rotate(45deg); }} }}
  .wave, .lens {{ transform-box: fill-box; transform-origin: center; animation-duration: {T:g}s; animation-iteration-count: infinite; opacity: 0; }}
  .wave {{ animation-name: wave; animation-timing-function: linear; }}
  @keyframes wave {{ {" ".join(f"{p * k:.2f}% {{ opacity: {1 if p else 0}; transform: scaleY({v}); }}" for p, v in wave_steps)} {29 * k:.2f}%, 100% {{ opacity: 0; transform: scaleY(0); }} }}
  .lens {{ animation-name: lens; animation-timing-function: ease-out; }}
  @keyframes lens {{ 0% {{ opacity: 0; transform: scaleY(0); }} {k:.2f}% {{ opacity: 1; transform: scaleY(1); }} {29 * k:.2f}%, 100% {{ opacity: 0; transform: scaleY(0); }} }}
  @media (prefers-reduced-motion: reduce) {{ .float, .spin, .side, .z, .c, .front, .back, .sheen, .glint, .wave, .lens {{ animation: none; }} }}
"""

o = []
add = o.append


def open_face(z):
    """Start a group drawn on the plane at depth z."""
    add(f'<g class="z {zc(z)}"><g transform="translate({CX} 0)"><g class="spin"><g transform="translate({-CX} 0)">')


def close_face():
    add('</g></g></g></g>')


def rim(href, zs, shade):
    """The wall between the two faces of a part: its outline repeated at each depth in zs, far to near."""
    for z in zs:
        add(f'<g class="z {zc(z)}"><g transform="translate({CX} 0)"><g class="spin"><use xlink:href="#{href}" x="{-CX}" fill="{shade(z)}"/></g></g></g>')


def side_wall(a, y0, y1, zr, fill, rx):
    """What is left of a part when it is seen edge-on: the plane x = CX + a, as wide as the part is deep."""
    inner = f'<g transform="translate({CX} 0)"><g class="side"><rect x="{zr[0]}" y="{y0:.0f}" width="{zr[1] - zr[0]}" height="{y1 - y0:.0f}" rx="{rx}" fill="{fill}"/></g></g>'
    add(f'<g class="c {cc(a)}">{inner}</g>' if a else inner)


def screw(x, y, r=3.4):
    add(f'<circle cx="{x}" cy="{y + .8}" r="{r + .4}" fill="#000" fill-opacity=".22"/><circle cx="{x}" cy="{y}" r="{r}" fill="url(#dome)" stroke="#7d7f81" stroke-width=".5"/>'
        f'<path d="M{x - r * .6:.1f} {y - r * .6:.1f} L{x + r * .6:.1f} {y + r * .6:.1f} M{x + r * .6:.1f} {y - r * .6:.1f} L{x - r * .6:.1f} {y + r * .6:.1f}" stroke="#6f7173" stroke-width=".7"/>')


def glint(x, y, r, delay):
    add(f'<path class="glint" style="animation-delay:{delay}s" d="M{x} {y - r} L{x + r * .16:.1f} {y - r * .16:.1f} L{x + r} {y} L{x + r * .16:.1f} {y + r * .16:.1f} L{x} {y + r} '
        f'L{x - r * .16:.1f} {y + r * .16:.1f} L{x - r} {y} L{x - r * .16:.1f} {y - r * .16:.1f} Z" fill="#fff"/>')


add(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{VB[2]}" height="{VB[3]}" viewBox="{VB[0]} {VB[1]} {VB[2]} {VB[3]}" role="img" aria-label="Butterscotch T-style electric guitar with a white pickguard, maple neck and chrome hardware, turning slowly; its strings are strummed each time it faces front">
<defs>
  <path id="body" d="{body_d}"/>
  <path id="head" d="{head_d}"/>
  <path id="guard" d="{guard_d}"/>
  <path id="neck" d="{neck_d}"/>
  <path id="bodyBack" d="{back_d}"/>
  <clipPath id="bodyBackClip"><use xlink:href="#bodyBack"/></clipPath>
  <clipPath id="bodyClip"><use xlink:href="#body"/></clipPath>
  <clipPath id="headClip"><use xlink:href="#head"/></clipPath>
  <clipPath id="guardClip"><use xlink:href="#guard"/></clipPath>
  <clipPath id="neckClip"><use xlink:href="#neck"/></clipPath>

  <linearGradient id="butter" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fbc640"/><stop offset=".5" stop-color="#f8be36"/><stop offset="1" stop-color="#f1b02b"/></linearGradient>
  <linearGradient id="maple" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#eeb748"/><stop offset=".12" stop-color="#f8c95e"/><stop offset=".88" stop-color="#f8c95e"/><stop offset="1" stop-color="#e9ae40"/></linearGradient>
  <linearGradient id="neckBack" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#d79c36"/><stop offset=".3" stop-color="#f6c75c"/><stop offset=".5" stop-color="#fcd983"/><stop offset=".72" stop-color="#f3bf52"/><stop offset="1" stop-color="#cf9330"/></linearGradient>
  <linearGradient id="sideBody" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f3bd3c"/><stop offset=".13" stop-color="#d08c17"/><stop offset=".86" stop-color="#eaab28"/><stop offset="1" stop-color="#f8c94e"/></linearGradient>
  <linearGradient id="sideMaple" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f5c765"/><stop offset=".2" stop-color="#d39a36"/><stop offset=".85" stop-color="#ecb94f"/><stop offset="1" stop-color="#f9d079"/></linearGradient>
  <linearGradient id="headMaple" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbd27c"/><stop offset="1" stop-color="#f3bc55"/></linearGradient>
  <linearGradient id="guardFill" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbf9f3"/><stop offset="1" stop-color="#ece8dd"/></linearGradient>
  <linearGradient id="chromeV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fcfcfc"/><stop offset=".42" stop-color="#c3c5c6"/><stop offset=".55" stop-color="#8f9193"/><stop offset=".72" stop-color="#d6d7d8"/><stop offset="1" stop-color="#f1f1f1"/></linearGradient>
  <linearGradient id="chromeH" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f6f6f6"/><stop offset=".4" stop-color="#b9bbbc"/><stop offset=".6" stop-color="#8f9193"/><stop offset="1" stop-color="#e4e5e5"/></linearGradient>
  <linearGradient id="plate" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eeeeee"/><stop offset=".5" stop-color="#cfd0d0"/><stop offset="1" stop-color="#b9babb"/></linearGradient>
  <linearGradient id="plateIn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d2d3d3"/><stop offset="1" stop-color="#e3e4e4"/></linearGradient>
  <radialGradient id="dome" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#c2c4c5"/><stop offset="1" stop-color="#77797b"/></radialGradient>
  <radialGradient id="knobTop" cx=".4" cy=".35" r=".75"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#d0d1d2"/><stop offset="1" stop-color="#a3a5a6"/></radialGradient>
  <linearGradient id="fretm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fdfdfb"/><stop offset=".5" stop-color="#cfd0ce"/><stop offset="1" stop-color="#8e8f8d"/></linearGradient>
  <linearGradient id="pickup" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3a3c"/><stop offset=".3" stop-color="#19191a"/><stop offset="1" stop-color="#0b0b0c"/></linearGradient>
  <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".42"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>

  <filter id="drop" x="-15%" y="-5%" width="130%" height="112%"><feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#000" flood-opacity=".28"/></filter>
  <filter id="lift" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="1.6" stdDeviation="1.6" flood-color="#3a2a00" flood-opacity=".4"/></filter>
  <filter id="b1"><feGaussianBlur stdDeviation="1"/></filter>
  <filter id="b2"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="b5"><feGaussianBlur stdDeviation="5"/></filter>
</defs>
<style>{STYLE}</style>
<g class="float">
''')


# ---------------------------------------------------------------- pieces shared by the front and the back
def keys():                                                     # tuner shafts and buttons, behind the headstock
  for x, y in POSTS:
    bx, by = x - 39, y - 14
    add(f'<path d="M{x - 12:.1f} {y - 4.3:.1f} L{bx:.1f} {by:.1f}" stroke="url(#chromeV)" stroke-width="7.5"/>'
        f'<g transform="rotate(19.7 {bx:.1f} {by:.1f})"><ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="12.5" ry="16.5" fill="url(#chromeV)" stroke="#77797b" stroke-width=".8"/>'
        f'<ellipse cx="{bx - 3:.1f}" cy="{by - 5:.1f}" rx="5" ry="6" fill="#fff" fill-opacity=".75"/></g>')


def strap_buttons():
  add('<rect x="397.5" y="741" width="9" height="9" fill="#9a9c9e"/><ellipse cx="402" cy="741.5" rx="11" ry="4.6" fill="url(#chromeV)" stroke="#77797b" stroke-width=".6"/>')
  add('<rect x="533" y="1414" width="9" height="9" fill="#9a9c9e"/><ellipse cx="537.5" cy="1425.5" rx="11" ry="4.6" fill="url(#chromeV)" stroke="#77797b" stroke-width=".6"/>')


def head_finish():
  add('<g clip-path="url(#headClip)">')
  for i in range(8):
    x = 470 + i * 15 + random.uniform(-3, 3)
    add(f'<path d="M{x:.0f} 240 C{x + 14:.0f} 150 {x + 30:.0f} 60 {x + 44:.0f} -30" fill="none" stroke="#c98f2a" stroke-opacity="{random.uniform(.08, .2):.2f}" stroke-width="{random.uniform(.7, 1.8):.1f}"/>')
  add('<use xlink:href="#head" fill="none" stroke="#c98a22" stroke-opacity=".5" stroke-width="12" filter="url(#b2)" transform="translate(-4 -3)"/>')
  add('<use xlink:href="#head" fill="none" stroke="#fff6d8" stroke-opacity=".85" stroke-width="3.5" filter="url(#b2)" transform="translate(4 4)"/>')
  add('</g>')
  add('<use xlink:href="#head" fill="none" stroke="#b9801c" stroke-opacity=".75" stroke-width="1"/>')


# ================================================================ side walls, seen when the guitar is edge-on
for a in A_BODY:
    s = span(back_d, CX + a)
    if s and s[1] - s[0] > 60:
        side_wall(a, s[0] + 3, s[1] - 3, Z_BODY, "url(#sideBody)", 5)
side_wall(0, NUT, FB_END, Z_NECK, "url(#sideMaple)", 3)
for a in A_HEAD:
    s = span(head_d, CX + a)
    if s and s[1] - s[0] > 30:
        side_wall(a, s[0] + 2, s[1] - 2, Z_HEAD, "url(#sideMaple)", 3)

# ================================================================ front of the guitar
add('<g class="front">')
open_face(Z_KEYS)
keys()
close_face()
open_face(0)
strap_buttons()
close_face()

# ---------------------------------------------------------------- body: grain, rolled edge, gloss
rim("neck", [z for z in NECK_L if z < Z_BODY[1]], neck_shade)   # the neck heel sits in a pocket: the body hides this part of it
rim("bodyBack", BODY_L, body_shade)
open_face(Z_BODY[1])
add('<use xlink:href="#body" fill="url(#butter)"/>')
add('<g clip-path="url(#bodyClip)">')
for i in range(22):
    x = 275 + i * 24 + random.uniform(-8, 8)
    w1, w2 = random.uniform(-7, 7), random.uniform(-7, 7)
    add(f'<path d="M{x:.0f} 730 C{x + w1:.0f} 960 {x + w2:.0f} 1200 {x + random.uniform(-5, 5):.0f} 1440" fill="none" stroke="#d6921a" stroke-opacity="{random.uniform(.08, .2):.2f}" stroke-width="{random.uniform(.8, 2.6):.1f}"/>')
add('<use xlink:href="#body" fill="none" stroke="#c97f10" stroke-opacity=".55" stroke-width="26" filter="url(#b5)" transform="translate(-9 -6)"/>')
add('<use xlink:href="#body" fill="none" stroke="#ffe9a6" stroke-opacity=".75" stroke-width="5" filter="url(#b2)" transform="translate(10 7)"/>')
add('<use xlink:href="#body" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.6" filter="url(#b1)" transform="translate(9 6)"/>')
add('<g transform="rotate(22 528 1090)"><rect class="sheen" x="478" y="640" width="100" height="900" fill="url(#sheen)"/></g>')
add('</g>')
add('<use xlink:href="#body" fill="none" stroke="#bf7d12" stroke-opacity=".7" stroke-width="1"/>')

# ---------------------------------------------------------------- pickguard
add('<g filter="url(#lift)"><use xlink:href="#guard" fill="url(#guardFill)"/></g>')
add('<g clip-path="url(#guardClip)"><use xlink:href="#guard" fill="none" stroke="#fff" stroke-width="3" transform="translate(1.5 1.5)"/>'
    '<use xlink:href="#guard" fill="none" stroke="#bdb8aa" stroke-opacity=".8" stroke-width="2.4" transform="translate(-1 -1)"/></g>')
add('<use xlink:href="#guard" fill="none" stroke="#a8a394" stroke-opacity=".7" stroke-width=".8"/>')
for x, y in [(710, 793), (473, 823), (588, 884), (415, 933), (710, 910), (420, 1063), (621, 1063), (708, 1063)]:
    screw(x, y)

# ---------------------------------------------------------------- neck pickup
add('<g filter="url(#lift)"><rect x="472" y="907" width="118" height="24" rx="10" fill="url(#chromeV)" stroke="#77797b" stroke-width=".8"/></g>')
add('<rect x="479" y="910.5" width="104" height="4" rx="2" fill="#fff" fill-opacity=".85"/>')

# ---------------------------------------------------------------- bridge: plate, pickup, three barrel saddles
add('<g filter="url(#lift)"><rect x="462.5" y="1057" width="136" height="162" rx="6" fill="url(#plate)" stroke="#808284" stroke-width=".9"/></g>')
add('<rect x="468.5" y="1061" width="124" height="151" rx="3" fill="url(#plateIn)" stroke="#fff" stroke-opacity=".8" stroke-width="1.2"/>')
add('<path d="M468.5 1212 V1064 a3 3 0 0 1 3 -3 H590" fill="none" stroke="#8c8e90" stroke-opacity=".7" stroke-width="1"/>')
add('<g transform="rotate(18.3 530 1100)"><rect x="465" y="1083" width="130" height="34" rx="17" fill="url(#pickup)" stroke="#000" stroke-width=".6"/>'
    '<rect x="476" y="1086" width="108" height="3" rx="1.5" fill="#fff" fill-opacity=".14"/>')
for i in range(6):
    add(f'<circle cx="{484.4 + i * 18.24:.1f}" cy="1100" r="4.6" fill="url(#dome)" stroke="#55575a" stroke-width=".5"/>')
add('</g>')
for x, y in [(535, 1075), (487.7, 1112.7), (557.7, 1135.7)]:
    screw(x, y, 3.8)
for k in range(3):
    cx = (STR_SADDLE[2 * k] + STR_SADDLE[2 * k + 1]) / 2
    zig = " ".join(f"L{cx + (4.2 if j % 2 else -4.2):.1f} {1184 + j * 2.6:.1f}" for j in range(11))
    add(f'<rect x="{cx - 1.6:.1f}" y="1180" width="3.2" height="40" fill="#8b8d8f"/>'
        f'<path d="M{cx:.1f} 1182 {zig}" fill="none" stroke="#6d6f71" stroke-width="1.7" stroke-linejoin="round"/>'
        f'<path d="M{cx - .8:.1f} 1182 {zig}" fill="none" stroke="#f2f2f2" stroke-opacity=".6" stroke-width=".6" transform="translate(-.6 -.5)"/>'
        f'<rect x="{cx - 4.5:.1f}" y="1217" width="9" height="6" rx="2" fill="url(#chromeH)" stroke="#6f7173" stroke-width=".5"/>')
    add(f'<g filter="url(#lift)"><rect x="{cx - 16.2:.1f}" y="1165" width="32.4" height="16" rx="5" fill="url(#chromeV)" stroke="#6f7173" stroke-width=".6"/></g>'
        f'<circle cx="{cx - 11.5:.1f}" cy="1173" r="1.7" fill="#1c1c1d"/><circle cx="{cx + 11.5:.1f}" cy="1173" r="1.7" fill="#1c1c1d"/>')
for x in (474.5, 514.5, 548.5, 586.5):
    screw(x, 1200, 3.6)

# ---------------------------------------------------------------- control plate: selector and two knobs
add('<g filter="url(#lift)"><rect x="646" y="1042" width="55" height="273" rx="27.5" fill="url(#plate)" stroke="#808284" stroke-width=".9"/></g>')
add('<rect x="649.5" y="1045.5" width="48" height="266" rx="24" fill="none" stroke="#fff" stroke-opacity=".75" stroke-width="1.2"/>')
for y in (1053, 1136, 1304):
    screw(673.3, y, 3.6)
add('<rect x="671.6" y="1079" width="3.6" height="46" rx="1.8" fill="#101011"/>')
add('<g filter="url(#lift)"><rect x="664.5" y="1087" width="18" height="25" rx="5" fill="url(#pickup)" stroke="#000" stroke-width=".5"/></g><rect x="667" y="1089.5" width="13" height="3" rx="1.5" fill="#fff" fill-opacity=".25"/>')
for cy in (1171.5, 1266.5):
    cx = 675.5
    add(f'<ellipse cx="{cx}" cy="{cy + 5}" rx="21" ry="20" fill="#000" fill-opacity=".28" filter="url(#b2)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="20" fill="#8d8f91" stroke="#5f6163" stroke-width=".7"/>'
        f'<circle cx="{cx}" cy="{cy}" r="19" fill="none" stroke="#e9e9e9" stroke-width="2.4" stroke-dasharray="1.1 1.4"/>'
        f'<circle cx="{cx}" cy="{cy - 1.5}" r="16" fill="url(#knobTop)" stroke="#7b7d7f" stroke-width=".6"/>'
        f'<path d="M{cx} {cy - 1.5} L{cx - 6} {cy - 17.2} A16 16 0 0 1 {cx + 6} {cy - 17.2} Z M{cx} {cy - 1.5} L{cx + 6} {cy + 14.2} A16 16 0 0 1 {cx - 6} {cy + 14.2} Z" fill="#fff" fill-opacity=".55"/>'
        f'<path d="M{cx} {cy - 1.5} L{cx - 15.7} {cy - 5} A16 16 0 0 0 {cx - 15.7} {cy + 2} Z M{cx} {cy - 1.5} L{cx + 15.7} {cy - 5} A16 16 0 0 1 {cx + 15.7} {cy + 2} Z" fill="#6d6f71" fill-opacity=".28"/>')
close_face()

# ---------------------------------------------------------------- headstock: tuner posts
rim("head", HEAD_L, head_shade)
open_face(Z_HEAD[1])
add('<use xlink:href="#head" fill="url(#headMaple)"/>')
head_finish()
for x, y in POSTS:
    add(f'<g filter="url(#lift)"><circle cx="{x:.1f}" cy="{y}" r="11.5" fill="url(#chromeH)" stroke="#6f7173" stroke-width=".7"/></g>'
        f'<circle cx="{x:.1f}" cy="{y}" r="8" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1"/>'
        f'<circle cx="{x:.1f}" cy="{y}" r="6.2" fill="url(#dome)" stroke="#6f7173" stroke-width=".6"/>')
close_face()

# ---------------------------------------------------------------- neck: maple board, frets, dots, nut
rim("neck", [z for z in NECK_L if z >= Z_BODY[1]], neck_shade)  # only this much of the neck stands proud of the body
open_face(Z_NECK[1])
add('<g filter="url(#lift)"><use xlink:href="#neck" fill="url(#maple)"/></g>')   # over the pickguard and the neck pocket
add('<g clip-path="url(#neckClip)">')
for i in range(7):
    x = CX - 36 + i * 12 + random.uniform(-3, 3)
    add(f'<path d="M{x:.0f} 230 C{x + random.uniform(-3, 3):.0f} 460 {x + random.uniform(-3, 3):.0f} 700 {x + random.uniform(-4, 4):.0f} 905" fill="none" stroke="#c98f2a" stroke-opacity="{random.uniform(.08, .18):.2f}" stroke-width="{random.uniform(.7, 1.8):.1f}"/>')
add('</g>')
add('<use xlink:href="#neck" fill="none" stroke="#b9801c" stroke-opacity=".75" stroke-width="1"/>')
for n in (3, 5, 7, 9, 15, 17, 19, 21):
    add(f'<circle cx="{CX}" cy="{(fret(n) + fret(n - 1)) / 2:.1f}" r="{5 if n < 21 else 4.4}" fill="#15130f"/>')
y12 = (fret(12) + fret(11)) / 2
add(f'<circle cx="{CX - 15}" cy="{y12:.1f}" r="5" fill="#15130f"/><circle cx="{CX + 15}" cy="{y12:.1f}" r="5" fill="#15130f"/>')
for n in range(1, 22):
    y, w = fret(n), half_w(fret(n))
    add(f'<rect x="{CX - w + .6:.1f}" y="{y + 1.2:.1f}" width="{2 * w - 1.2:.1f}" height="1.6" fill="#7a5a12" fill-opacity=".35"/>'
        f'<rect x="{CX - w + .4:.1f}" y="{y - 1.5:.1f}" width="{2 * w - .8:.1f}" height="3" rx="1" fill="url(#fretm)"/>')
add(f'<rect x="{CX - half_w(NUT) - .5:.1f}" y="{NUT - 5}" width="{2 * half_w(NUT) + 1:.1f}" height="9" rx="1.5" fill="#f7f3e6" stroke="#b9b29c" stroke-width=".6"/>'
    f'<rect x="{CX - half_w(NUT):.1f}" y="{NUT + 4}" width="{2 * half_w(NUT):.1f}" height="2.5" fill="#7a5a12" fill-opacity=".3"/>')

# ---------------------------------------------------------------- strings: saddle -> nut -> tuner post
for i in range(6):
    px, py = POSTS[i]
    d = f"M{STR_SADDLE[i]:.1f} {SADDLE} L{STR_NUT[i]:.1f} {NUT} L{px:.1f} {py}"
    add(f'<path d="{d}" fill="none" stroke="#3a2a00" stroke-opacity=".28" stroke-width="{GAUGE[i]}" transform="translate(2 1.5)"/>'
        f'<path d="{d}" fill="none" stroke="#8e8e8b" stroke-width="{GAUGE[i]}" stroke-linejoin="round"/>'
        f'<path d="{d}" fill="none" stroke="#f4f4f2" stroke-opacity=".8" stroke-width="{GAUGE[i] * .35:.2f}" transform="translate(-.4 0)"/>')
for i in range(6):
    ax, ay, bx, by = STR_SADDLE[i], SADDLE, STR_NUT[i], NUT
    length, ang = math.hypot(bx - ax, by - ay), math.degrees(math.atan2(by - ay, bx - ax))
    amp = 4.6 - i * .42
    dl = f"{i * .06 - T / 12:.2f}s"                  # strummed as the front swings into view
    add(f'<g transform="translate({ax:.1f} {ay}) rotate({ang:.3f})">'
        f'<path class="lens" style="animation-delay:{dl}" d="M0 0 Q{length / 2:.1f} {-2 * amp:.2f} {length:.1f} 0 Q{length / 2:.1f} {2 * amp:.2f} 0 0 Z" fill="#77776f" fill-opacity=".3"/>'
        f'<g class="wave" style="animation-delay:{dl}"><path d="M0 0 Q{length / 2:.1f} {-2 * amp:.2f} {length:.1f} 0" fill="none" stroke="#6f6f6b" stroke-width="{GAUGE[i]:.2f}"/>'
        f'<path d="M0 0 Q{length / 2:.1f} {2 * amp:.2f} {length:.1f} 0" fill="none" stroke="none"/></g></g>')

# ---------------------------------------------------------------- chrome glints
glint(POSTS[5][0] - 42, POSTS[5][1] - 20, 13, 0)
glint(469, 1062, 11, 1.4)
glint(668, 1161, 12, 2.6)
close_face()
add('</g>')

# ================================================================ back of the guitar
add('<g class="back">')
open_face(Z_KEYS)
keys()
close_face()
open_face(0)
strap_buttons()
close_face()

rim("head", HEAD_L[::-1], head_shade)
open_face(Z_HEAD[0])
add('<use xlink:href="#head" fill="url(#headMaple)"/>')
head_finish()
for x, y in POSTS:                                              # tuner housings
    add(f'<g transform="rotate(19.1 {x:.1f} {y})" filter="url(#lift)"><rect x="{x - 12.5:.1f}" y="{y - 16}" width="25" height="32" rx="3.5" fill="url(#plate)" stroke="#77797b" stroke-width=".8"/>'
        f'<rect x="{x - 9.5:.1f}" y="{y - 13}" width="19" height="26" rx="2" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="1"/>'
        f'<circle cx="{x:.1f}" cy="{y}" r="5.2" fill="url(#dome)" stroke="#77797b" stroke-width=".5"/></g>')
close_face()

rim("neck", NECK_L[::-1], neck_shade)
open_face(Z_NECK[0])
add('<use xlink:href="#neck" fill="url(#neckBack)"/>')
add(f'<rect x="{CX - 2.8}" y="262" width="5.6" height="520" rx="2.8" fill="#5b3414"/><rect x="{CX - 2.8}" y="262" width="1.4" height="520" rx=".7" fill="#fff" fill-opacity=".18"/>')
add('<use xlink:href="#neck" fill="none" stroke="#b9801c" stroke-opacity=".75" stroke-width="1"/>')
close_face()

rim("bodyBack", BODY_L[::-1], body_shade)
open_face(Z_BODY[0])
add('<use xlink:href="#bodyBack" fill="url(#butter)"/>')
add('<g clip-path="url(#bodyBackClip)">')
for i in range(22):
    x = 275 + i * 24 + random.uniform(-8, 8)
    add(f'<path d="M{x:.0f} 730 C{x + random.uniform(-7, 7):.0f} 960 {x + random.uniform(-7, 7):.0f} 1200 {x + random.uniform(-5, 5):.0f} 1440" fill="none" stroke="#d6921a" stroke-opacity="{random.uniform(.08, .2):.2f}" stroke-width="{random.uniform(.8, 2.6):.1f}"/>')
add('<use xlink:href="#bodyBack" fill="none" stroke="#c97f10" stroke-opacity=".55" stroke-width="26" filter="url(#b5)" transform="translate(9 -6)"/>')
add('<use xlink:href="#bodyBack" fill="none" stroke="#ffe9a6" stroke-opacity=".75" stroke-width="5" filter="url(#b2)" transform="translate(-10 7)"/>')
add('<use xlink:href="#bodyBack" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.6" filter="url(#b1)" transform="translate(-9 6)"/>')
add('</g>')
add('<use xlink:href="#bodyBack" fill="none" stroke="#bf7d12" stroke-opacity=".7" stroke-width="1"/>')
add(f'<g filter="url(#lift)"><rect x="{CX - 37}" y="787" width="74" height="92" rx="9" fill="url(#plate)" stroke="#808284" stroke-width=".9"/></g>'
    f'<rect x="{CX - 33.5}" y="790.5" width="67" height="85" rx="6.5" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="1.2"/>')
for dx in (-25, 25):                                            # neck plate screws
    for y in (800, 866):
        screw(CX + dx, y, 5)
for x in STR_SADDLE:                                            # string ferrules
    add(f'<circle cx="{x:.1f}" cy="1201" r="6.2" fill="#000" fill-opacity=".25"/><circle cx="{x:.1f}" cy="1200" r="5.6" fill="url(#dome)" stroke="#6f7173" stroke-width=".6"/><circle cx="{x:.1f}" cy="1200" r="2.3" fill="#2a2a2b"/>')
close_face()
add('</g>')

add('</g></svg>')
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(o) + "\n")
