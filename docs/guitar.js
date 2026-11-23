// Gold T-style electric guitar in 3D. Units are millimetres.
// Body outline, pickguard and hardware positions are traced from a front photo;
// fret positions use a real 648 mm (25.5") scale with 22 frets.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const query = new URLSearchParams(location.search);
const RENDER = query.has('render'); // deterministic frames for the README preview
if (RENDER) document.documentElement.classList.add('render');

// ------------------------------------------------------------ renderer
const canvas = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: RENDER });
renderer.setPixelRatio(RENDER ? 1 : Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.25;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(studio(), 0.02).texture;
scene.background = backdrop();

const camera = new THREE.PerspectiveCamera(28, 1, 10, 8000);

const key = new THREE.DirectionalLight(0xfff1dc, 1.3);
key.position.set(-900, 900, 250);
scene.add(key);
const rim = new THREE.DirectionalLight(0xffb347, 2.5);
rim.position.set(700, -300, -400);
scene.add(rim);
const fill = new THREE.DirectionalLight(0xe4e2ff, 0.45);
fill.position.set(600, 200, 600);
scene.add(fill);

// ------------------------------------------------------------ textures
// reflections come from a dark studio with a few softboxes
function studio() {
  const s = new THREE.Scene();
  s.background = new THREE.Color(0x0d0a07);
  const panel = (w, h, color, k, pos) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(color).multiplyScalar(k), side: THREE.DoubleSide }));
    m.position.set(...pos);
    m.lookAt(0, 0, 0);
    s.add(m);
  };
  panel(8, 1.6, 0xffe6bf, 3.2, [0, 4.5, 3.5]);     // long overhead strip
  panel(1.8, 7, 0xffc070, 2.4, [-5.5, 0.5, 2.5]);  // warm side strip
  panel(1.2, 5, 0xc9d6ff, 0.9, [5.5, 1, -1]);      // cool rim strip
  panel(12, 4, 0x6a4a28, 1.1, [0, -5, 1]);         // floor bounce
  panel(9, 6, 0xfff2dc, 0.75, [1, 0.5, 6]);          // soft front fill
  return s;
}
function backdrop() {
  const c = document.createElement('canvas');
  c.width = 1024; c.height = 512;
  const g = c.getContext('2d');
  const r = g.createRadialGradient(560, 250, 20, 512, 256, 620);
  r.addColorStop(0, '#3a2810');
  r.addColorStop(0.35, '#1a130c');
  r.addColorStop(1, '#09080b');
  g.fillStyle = r;
  g.fillRect(0, 0, 1024, 512);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function seeded(seed) {
  return () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
}

// metal-flake sparkle: random tilted normals
function flakeNormal() {
  const n = 512, c = document.createElement('canvas');
  c.width = c.height = n;
  const g = c.getContext('2d'), img = g.createImageData(n, n), rnd = seeded(7);
  for (let i = 0; i < n * n; i++) {
    const strong = rnd() < 0.08;
    const s = strong ? 120 : 26;
    img.data[i * 4] = 128 + (rnd() - 0.5) * s;
    img.data[i * 4 + 1] = 128 + (rnd() - 0.5) * s;
    img.data[i * 4 + 2] = 255;
    img.data[i * 4 + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1 / 90, 1 / 90);
  return t;
}

// brushed aluminium: streaks along the neck axis
function brushed() {
  const w = 1024, h = 256, c = document.createElement('canvas');
  c.width = w; c.height = h;
  const g = c.getContext('2d'), rnd = seeded(3);
  g.fillStyle = '#8a8a8a';
  g.fillRect(0, 0, w, h);
  for (let i = 0; i < 2600; i++) {
    const v = 90 + rnd() * 110 | 0;
    g.fillStyle = `rgba(${v},${v},${v},${0.25 + rnd() * 0.4})`;
    g.fillRect(rnd() * w, rnd() * h, 60 + rnd() * 400, 1);
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1 / 260, 1 / 120);
  return t;
}

// ------------------------------------------------------------ materials
const M = {
  body: new THREE.MeshPhysicalMaterial({
    color: 0xe39a00, metalness: 0.7, roughness: 0.36, clearcoat: 1, clearcoatRoughness: 0.03,
    normalMap: flakeNormal(), normalScale: new THREE.Vector2(0.5, 0.5),
  }),
  guard: new THREE.MeshPhysicalMaterial({ color: 0x6b6e74, metalness: 0.6, roughness: 0.48, roughnessMap: brushed(), clearcoat: 0.2 }),
  blackChrome: new THREE.MeshStandardMaterial({ color: 0x141518, metalness: 0.95, roughness: 0.22 }),
  plastic: new THREE.MeshStandardMaterial({ color: 0x0c0c0e, metalness: 0.1, roughness: 0.45 }),
  champagne: new THREE.MeshStandardMaterial({ color: 0xd9c79c, metalness: 1, roughness: 0.22 }),
  brass: new THREE.MeshStandardMaterial({ color: 0xcaa14c, metalness: 1, roughness: 0.28 }),
  maple: new THREE.MeshPhysicalMaterial({ color: 0xb8864a, metalness: 0, roughness: 0.5, clearcoat: 0.15, clearcoatRoughness: 0.35 }),
  ebony: new THREE.MeshStandardMaterial({ color: 0x1a1513, metalness: 0, roughness: 0.55 }),
  nickel: new THREE.MeshStandardMaterial({ color: 0xdfe2e8, metalness: 1, roughness: 0.18 }),
  pearl: new THREE.MeshPhysicalMaterial({ color: 0xf4f1ea, roughness: 0.25, iridescence: 0.6, clearcoat: 0.5 }),
  knobTop: new THREE.MeshStandardMaterial({ color: 0x3a3c42, metalness: 1, roughness: 0.3 }),
  bone: new THREE.MeshStandardMaterial({ color: 0xf1ead8, roughness: 0.5 }),
};

M.guard.envMapIntensity = 0.7;

// ------------------------------------------------------------ helpers
const guitar = new THREE.Group();   // rotated by the cursor
const model = new THREE.Group();    // offset so the guitar is centred
guitar.add(model);
scene.add(guitar);
model.position.x = -295;

function smoothOutline(points, samples) {
  const curve = new THREE.CatmullRomCurve3(points.map(([x, y]) => new THREE.Vector3(x, y, 0)), false, 'centripetal');
  return curve.getPoints(samples).map((p) => new THREE.Vector2(p.x, p.y));
}

function slab(outline, depth, bevel, mat, z) {
  const geo = new THREE.ExtrudeGeometry(new THREE.Shape(outline), {
    depth, bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 4, curveSegments: 1,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.z = z;
  model.add(mesh);
  return mesh;
}

function box(w, h, d, r, mat, x, y, z, rotZ = 0) {
  const mesh = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 3, r), mat);
  mesh.position.set(x, y, z);
  mesh.rotation.z = rotZ;
  model.add(mesh);
  return mesh;
}

function cyl(r, len, mat, x, y, z, axis = 'z', seg = 24) {
  const geo = new THREE.CylinderGeometry(r, r, len, seg);
  if (axis === 'z') geo.rotateX(Math.PI / 2);
  if (axis === 'x') geo.rotateZ(Math.PI / 2);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  model.add(mesh);
  return mesh;
}

// ------------------------------------------------------------ body (front face at z = 0)
const BODY = [
  [188, 28], [193, 101], [164, 141], [133, 150], [48, 157], [-32, 160], [-120, 156], [-165, 141], [-190, 80],
  [-195, 0], [-190, -82], [-169, -143], [-120, -160], [-32, -163], [48, -161], [133, -154], [176, -138],
  [189, -122], [186, -108], [174, -100], [150, -90], [130, -70], [126, -50], [133, -28],
];
const bodyOutline = [...smoothOutline(BODY, 260), new THREE.Vector2(190, -28), new THREE.Vector2(190, 28)];
slab(bodyOutline, 40, 2.5, M.body, -42.5);

// pickguard: brushed dark aluminium
const GUARD = [
  [170, 27], [168, 48], [146, 72], [119, 81], [60, 82], [14, 80], [11, 40], [10, -18], [10, -80],
  [11, -116], [48, -121], [110, -125], [146, -123], [170, -118], [177, -112], [170, -105], [148, -96],
  [127, -76], [120, -50], [123, -27],
];
const guardOutline = [...smoothOutline(GUARD, 200), new THREE.Vector2(123, 24), new THREE.Vector2(170, 24)];
slab(guardOutline, 1.4, 0.6, M.guard, 0.6);
for (const [x, y] of [[160, 46], [130, 74], [66, 76], [18, 74], [17, 8], [17, -60], [17, -110], [70, -117], [128, -118], [166, -112], [134, -84], [126, -48]]) {
  cyl(1.9, 1.2, M.nickel, x, y, 2.9);
}

// neck pickup: champagne cover
box(18, 70, 9, 3.5, M.champagne, 111, 0, 4);

// bridge: black plate, bridge pickup, brass saddles
box(94, 79, 2, 1, M.blackChrome, -29, 0.5, 1);
for (const [x, y] of [[-72, 35], [-72, -34], [14, 35], [14, -34]]) cyl(1.6, 0.8, M.nickel, x, y, 2.2);
const bp = box(18, 70, 9, 3, M.plastic, -5, 0, 5.5, THREE.MathUtils.degToRad(-8));
for (let i = 0; i < 6; i++) {
  const y = 26.25 - i * 10.5, a = bp.rotation.z;
  cyl(2, 1, M.champagne, -5 - y * Math.sin(a), y * Math.cos(a), 10.1);
}
const SADDLE_X = -54;
for (let i = 0; i < 6; i++) box(14, 9.4, 7, 1.6, M.brass, SADDLE_X, 26.25 - i * 10.5, 5.5);

// control plate, knobs and the pickup selector
{
  const plate = new THREE.Shape();
  plate.absarc(8, -91, 16.5, -Math.PI / 2, Math.PI / 2, false);
  plate.absarc(-120, -91, 16.5, Math.PI / 2, Math.PI * 1.5, false);
  const geo = new THREE.ExtrudeGeometry(plate, { depth: 1.4, bevelEnabled: true, bevelThickness: 0.5, bevelSize: 0.5, bevelSegments: 3 });
  const mesh = new THREE.Mesh(geo, M.blackChrome);
  mesh.position.z = 0.5;
  model.add(mesh);
}
for (const x of [-52, -114]) {
  const g = new THREE.CylinderGeometry(9.5, 9.5, 12, 48, 1);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {                  // knurled sides
    const a = Math.atan2(p.getZ(i), p.getX(i)), r = Math.hypot(p.getX(i), p.getZ(i));
    if (r > 9) { const k = 1 + 0.035 * Math.sign(Math.sin(a * 24)); p.setX(i, p.getX(i) * k); p.setZ(i, p.getZ(i) * k); }
  }
  g.computeVertexNormals();
  g.rotateX(Math.PI / 2);
  const knob = new THREE.Mesh(g, M.blackChrome);
  knob.position.set(x, -91, 8);
  model.add(knob);
  cyl(8.4, 0.6, M.knobTop, x, -91, 14.2, 'z', 48);
}
{
  const lever = cyl(1.2, 14, M.nickel, 0, -91, 7, 'z');
  lever.rotation.y = 0.5;
  const tip = new THREE.Mesh(new THREE.CapsuleGeometry(3.2, 7, 4, 12), M.plastic);
  tip.position.set(4, -91, 14);
  tip.rotation.x = Math.PI / 2;
  model.add(tip);
}
cyl(3.6, 4, M.blackChrome, -195, 0, -21, 'x');             // strap button
cyl(5.5, 3, M.blackChrome, -70, -163, -21, 'y');           // output jack

// ------------------------------------------------------------ neck, fretboard, frets
const NUT_X = 594, SCALE = 648, FB_END = 128;
const fretX = (n) => NUT_X - SCALE * (1 - 2 ** (-n / 12));
const halfW = (x) => THREE.MathUtils.lerp(28, 21.4, (x - FB_END) / (NUT_X - FB_END));

{ // C-shaped neck shaft
  const N = 48, R = 20, pos = [], idx = [];
  for (let i = 0; i <= N; i++) {
    const x = THREE.MathUtils.lerp(118, NUT_X + 2, i / N), w = halfW(x), d = THREE.MathUtils.lerp(23, 21, i / N);
    for (let j = 0; j <= R; j++) {
      const a = Math.PI * j / R;
      pos.push(x, w * Math.cos(a), 6 - d * Math.sin(a));
    }
  }
  for (let i = 0; i < N; i++) for (let j = 0; j < R; j++) {
    const a = i * (R + 1) + j, b = a + R + 1;
    idx.push(a, b, a + 1, b, b + 1, a + 1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  model.add(new THREE.Mesh(g, M.maple));
}
slab([new THREE.Vector2(FB_END, -halfW(FB_END)), new THREE.Vector2(NUT_X, -halfW(NUT_X)),
      new THREE.Vector2(NUT_X, halfW(NUT_X)), new THREE.Vector2(FB_END, halfW(FB_END))], 6, 0, M.ebony, 6);
for (let n = 1; n <= 22; n++) {
  const x = fretX(n);
  cyl(1.15, 2 * halfW(x) - 0.6, M.nickel, x, 0, 12, 'y', 12);
}
for (const n of [3, 5, 7, 9, 12, 15, 17, 19, 21]) {
  const x = (fretX(n) + fretX(n - 1)) / 2;
  box(3.6, n === 12 ? 30 : 13, 0.4, 0.15, M.pearl, x, 0, 12.05);
}
box(3, 2 * halfW(NUT_X), 4.5, 0.6, M.bone, NUT_X + 1.5, 0, 13);

// headstock and tuners
const HEAD = [[594, -21.4], [630, -23], [690, -25], [740, -22], [772, -8], [784, 12], [780, 34], [762, 44], [700, 46], [650, 44], [620, 36], [600, 25], [594, 21.4]];
slab(smoothOutline(HEAD, 120), 13, 1.5, M.maple, -8.5);
const POSTS = Array.from({ length: 6 }, (_, i) => [625 + 25 * i, 30]);
for (const [x, y] of POSTS) {
  cyl(5.2, 1.6, M.blackChrome, x, y, 5.8);
  cyl(3, 12, M.blackChrome, x, y, 11);
  box(14, 14, 10, 2, M.blackChrome, x, y + 4, -14.5);
  cyl(1.6, 14, M.blackChrome, x, y + 16, -14.5, 'y');
  box(11, 4, 17, 1.8, M.blackChrome, x, y + 25, -14.5);
}

// ------------------------------------------------------------ strings
const NOTES = [82.41, 110, 146.83, 196, 246.94, 329.63];      // E2 A2 D3 G3 B3 E4
const RADII = [0.78, 0.68, 0.58, 0.46, 0.38, 0.32];
const strings = [];
const hits = [];
for (let i = 0; i < 6; i++) {
  const a = new THREE.Vector3(SADDLE_X + 5, 26.25 - 10.5 * i, 9.6);
  const b = new THREE.Vector3(NUT_X, 17.5 - 7 * i, 15.4);
  const len = a.distanceTo(b);
  const mat = new THREE.MeshStandardMaterial({ color: i < 3 ? 0xd2c3a2 : 0xe8ebf0, metalness: 1, roughness: 0.25, emissive: 0xffa53a, emissiveIntensity: 0 });
  const uniforms = { uAmp: { value: 0 }, uPhase: { value: 0 }, uLen: { value: len } };
  mat.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, uniforms);
    shader.vertexShader = 'uniform float uAmp; uniform float uPhase; uniform float uLen;\n' + shader.vertexShader.replace(
      '#include <begin_vertex>',
      '#include <begin_vertex>\nfloat u = clamp(transformed.x / uLen, 0.0, 1.0);\n' +
      'transformed.y += uAmp * sin(3.14159265 * u) * sin(uPhase + u * 2.0);\n' +
      'transformed.z += 0.35 * uAmp * sin(3.14159265 * u) * cos(uPhase * 1.31);');
  };
  const geo = new THREE.CylinderGeometry(RADII[i], RADII[i], len, 8, 96, true);
  geo.rotateZ(-Math.PI / 2);
  geo.translate(len / 2, 0, 0);
  const s = new THREE.Mesh(geo, mat);
  s.position.copy(a);
  s.quaternion.setFromUnitVectors(new THREE.Vector3(1, 0, 0), b.clone().sub(a).normalize());
  s.frustumCulled = false;
  model.add(s);

  const hitGeo = new THREE.CylinderGeometry(4.5, 4.5, len, 6);
  hitGeo.rotateZ(-Math.PI / 2);
  hitGeo.translate(len / 2, 0, 0);
  const hit = new THREE.Mesh(hitGeo, new THREE.MeshBasicMaterial({ visible: false }));
  hit.position.copy(a);
  hit.quaternion.copy(s.quaternion);
  hit.userData.string = i;
  model.add(hit);
  hits.push(hit);

  // nut to tuner post
  const [px, py] = POSTS[i];
  const p = new THREE.Vector3(px, py, 15);
  const tail = new THREE.Mesh(new THREE.CylinderGeometry(RADII[i], RADII[i], b.distanceTo(p), 6), mat);
  tail.position.copy(b).add(p).multiplyScalar(0.5);
  tail.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), p.clone().sub(b).normalize());
  model.add(tail);

  strings.push({ mat, uniforms, plucked: -1e9, strength: 0, omega: 2 * Math.PI * (9 + i * 1.7) });
}
cyl(2.2, 4, M.blackChrome, 668, 2, 12);                       // string tree

function stringState(now) {
  for (const s of strings) {
    const t = now - s.plucked;
    const env = t >= 0 ? s.strength * Math.exp(-t * 1.6) : 0;
    s.uniforms.uAmp.value = env * 1.6;
    s.uniforms.uPhase.value = t * s.omega;
    s.mat.emissiveIntensity = env * 1.4;
  }
}

// ------------------------------------------------------------ sound (Karplus-Strong plucked string)
let audio = null, out = null, soundOn = false;
const buffers = [];
function startAudio() {
  if (audio) return audio.resume();
  audio = new AudioContext();
  const drive = audio.createWaveShaper();
  const curve = new Float32Array(1024);
  for (let i = 0; i < 1024; i++) { const x = i / 512 - 1; curve[i] = Math.tanh(2.2 * x); }
  drive.curve = curve;
  const tone = audio.createBiquadFilter();
  tone.type = 'lowpass'; tone.frequency.value = 3800; tone.Q.value = 0.8;
  const delay = audio.createDelay(); delay.delayTime.value = 0.21;
  const fb = audio.createGain(); fb.gain.value = 0.28;
  const wet = audio.createGain(); wet.gain.value = 0.22;
  const master = audio.createGain(); master.gain.value = 0.55;
  out = audio.createGain(); out.gain.value = 0.9;
  out.connect(drive).connect(tone).connect(master).connect(audio.destination);
  tone.connect(delay).connect(fb).connect(delay);
  delay.connect(wet).connect(audio.destination);
}
function pluckSound(i, strength) {
  if (!audio || !soundOn) return;
  if (!buffers[i]) {
    const sr = audio.sampleRate, len = Math.floor(sr * 2.6), N = Math.round(sr / NOTES[i]);
    const ring = new Float32Array(N), data = new Float32Array(len), rnd = seeded(31 + i);
    let prev = 0;
    for (let k = 0; k < N; k++) { prev = 0.55 * prev + 0.45 * (rnd() * 2 - 1); ring[k] = prev; }
    for (let k = 0, p = 0; k < len; k++) {
      const q = (p + 1) % N;
      data[k] = ring[p];
      ring[p] = 0.4985 * (ring[p] + ring[q]);
      p = q;
    }
    const buf = audio.createBuffer(1, len, sr);
    buf.copyToChannel(data, 0);
    buffers[i] = buf;
  }
  const src = audio.createBufferSource();
  src.buffer = buffers[i];
  const g = audio.createGain();
  g.gain.value = 0.35 + 0.5 * strength;
  src.connect(g).connect(out);
  src.start();
}

function pluck(i, now, strength = 1) {
  const s = strings[i];
  s.plucked = now;
  s.strength = Math.min(1, strength);
  pluckSound(i, strength);
}

// ------------------------------------------------------------ layout
function resize(w, h) {
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  // fit ~1080 x 470 mm of guitar in view
  const vfov = THREE.MathUtils.degToRad(camera.fov);
  const dist = Math.max(470 / (2 * Math.tan(vfov / 2)), 1080 / (2 * Math.tan(vfov / 2) * camera.aspect));
  camera.position.set(0, 0, dist * 1.08);
  camera.lookAt(0, 0, 0);
  camera.updateProjectionMatrix();
}

// ------------------------------------------------------------ README frames
if (RENDER) {
  const w = +query.get('w') || 1200, h = +query.get('h') || 520;
  canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
  resize(w, h);
  const T = +query.get('T') || 4;
  window.__frame = (t) => {
    const ph = 2 * Math.PI * t / T;
    guitar.rotation.set(-0.22 + 0.07 * Math.sin(ph + 0.8), 0.32 * Math.sin(ph), -0.04 + 0.03 * Math.sin(ph));
    guitar.position.y = 6 * Math.sin(ph * 2);
    for (let i = 0; i < 6; i++) { strings[i].plucked = 0.35 + i * 0.045; strings[i].strength = 1; }
    stringState(t);
    renderer.render(scene, camera);
  };
  window.__ready = true;
} else {
  // ---------------------------------------------------------- live page
  resize(innerWidth, innerHeight);
  addEventListener('resize', () => resize(innerWidth, innerHeight));

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ray = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  let target = { yaw: 0, pitch: 0 }, yaw = 0, pitch = 0, spin = 0, spinVel = 0;
  let drag = null, lastHit = new Set(), lastPt = null;

  const soundBtn = document.getElementById('sound');
  soundBtn.addEventListener('click', () => {
    soundOn = !soundOn;
    if (soundOn) startAudio();
    soundBtn.setAttribute('aria-pressed', soundOn);
    soundBtn.textContent = soundOn ? 'Sound on' : 'Sound off';
  });

  function stringsUnder(x, y) {
    ndc.set((x / innerWidth) * 2 - 1, -(y / innerHeight) * 2 + 1);
    ray.setFromCamera(ndc, camera);
    return new Set(ray.intersectObjects(hits, false).map((h) => h.object.userData.string));
  }

  canvas.addEventListener('pointermove', (e) => {
    target.yaw = ((e.clientX / innerWidth) * 2 - 1) * 0.45;
    target.pitch = ((e.clientY / innerHeight) * 2 - 1) * 0.28;
    if (drag) {
      spinVel = (e.clientX - drag.x) * 0.006;
      spin += spinVel;
      drag.x = e.clientX;
      return;
    }
    // sweep across strings: sample along the pointer path so fast strums still hit
    const now = performance.now() / 1000, seen = new Set();
    const from = lastPt || { x: e.clientX, y: e.clientY };
    const speed = Math.hypot(e.clientX - from.x, e.clientY - from.y);
    for (let k = 1; k <= 6; k++) {
      const x = from.x + (e.clientX - from.x) * k / 6, y = from.y + (e.clientY - from.y) * k / 6;
      for (const i of stringsUnder(x, y)) {
        if (!lastHit.has(i) && !seen.has(i)) pluck(i, now, 0.45 + Math.min(speed, 60) / 110);
        seen.add(i);
      }
    }
    lastHit = seen;
    lastPt = { x: e.clientX, y: e.clientY };
  });
  canvas.addEventListener('pointerdown', (e) => {
    if (!soundOn && !audio) { soundBtn.click(); }      // first tap turns sound on
    const under = stringsUnder(e.clientX, e.clientY);
    if (under.size) { for (const i of under) pluck(i, performance.now() / 1000, 1); return; }
    drag = { x: e.clientX };
    canvas.setPointerCapture(e.pointerId);
    canvas.classList.add('dragging');
  });
  const end = () => { drag = null; canvas.classList.remove('dragging'); };
  canvas.addEventListener('pointerup', end);
  canvas.addEventListener('pointercancel', end);
  canvas.addEventListener('pointerleave', () => { lastHit = new Set(); lastPt = null; target.yaw = target.pitch = 0; });

  // a welcome strum
  setTimeout(() => { const now = performance.now() / 1000; for (let i = 0; i < 6; i++) pluck(i, now + i * 0.05, 0.8); }, 600);

  let prev = performance.now() / 1000;
  renderer.setAnimationLoop(() => {
    const now = performance.now() / 1000, dt = Math.min(0.05, now - prev);
    prev = now;
    if (!drag) { spinVel *= 0.94; spin += spinVel; spin *= reduce ? 1 : 0.985; }
    yaw += (target.yaw - yaw) * Math.min(1, dt * 5);
    pitch += (target.pitch - pitch) * Math.min(1, dt * 5);
    const idle = reduce ? 0 : Math.sin(now * 0.6);
    guitar.rotation.set(-0.2 + pitch, yaw + spin + 0.08 * idle, -0.04);
    guitar.position.y = reduce ? 0 : 6 * Math.sin(now * 0.9);
    stringState(now);
    renderer.render(scene, camera);
  });
}
