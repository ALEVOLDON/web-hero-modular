import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import gsap from "gsap";
import { createPatch } from "./audio.js";
import { MODULES, moduleIdFromObject } from "./modules.js";
import { applyLang, currentLang, t } from "./i18n.js";

const canvas = document.querySelector("#stage");
const bootEl = document.querySelector("#boot");
const bootFill = document.querySelector("#boot-fill");
const bootStatus = document.querySelector(".boot-status");
const btnEnter = document.querySelector("#btn-enter");
const btnForce3d = document.querySelector("#btn-force-3d");
const poster = document.querySelector("#poster");
const tip = document.querySelector("#tip");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const coarse = window.matchMedia("(pointer: coarse)").matches;
const narrow = window.matchMedia("(max-width: 800px)").matches;
const lowMem = typeof navigator.deviceMemory === "number" && navigator.deviceMemory < 4;
const preferPoster = (coarse || narrow || lowMem) && !new URLSearchParams(location.search).has("3d");

const SHOTS = {
  overview: { pos: [1.42, 0.78, 1.92], look: [0.28, -0.02, 0] },
  knobs: { pos: [0.55, 0.82, 0.95], look: [0.35, 0.08, 0] },
  cables: { pos: [0.72, 0.22, 1.35], look: [0.18, -0.22, 0] },
  into: { pos: [1.15, 0.42, 0.78], look: [0.4, 0.04, 0] },
};

const patch = createPatch();
const look = new THREE.Vector3(0, 0.04, 0);
const pointer = { x: 0, y: 0 };
let introDone = false;
let activeShot = "overview";
let idleTimer = 0;
let renderer, scene, camera, composer, bloom, root, model;
let controls = [];
let faders = [];
let leds = [];
let screens = [];
let faces = new Map();
let currents = [];
let hovered = null;
let webglReady = false;

function setBoot(pct, label) {
  if (bootFill) bootFill.style.width = `${Math.round(pct * 100)}%`;
  if (label && bootStatus) bootStatus.textContent = label;
}

function hideBoot() {
  bootEl.classList.add("is-gone");
}

function usePoster() {
  poster.hidden = false;
  canvas.style.display = "none";
  setBoot(1, t("bootReady"));
  btnEnter.hidden = false;
  btnForce3d.hidden = false;
}

function isControlMesh(obj) {
  const labels = [obj.name, obj.parent && obj.parent.name];
  return labels.some((n) => n && /^(Knob|FaderCap|LED)_/i.test(n) && !/Stem|Ptr/i.test(n));
}

function frameObject(object) {
  const skip = /floor|backdrop|hud|table/i;
  object.traverse((child) => {
    if (child.isMesh && skip.test(child.name)) child.visible = false;
    if (child.name && child.name.startsWith("Path_")) child.visible = false;
  });
  const box = new THREE.Box3().setFromObject(object);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  object.position.sub(center);
  object.position.x += 0.42;
  object.position.y -= 0.04;
  const maxSize = Math.max(size.x, size.y, size.z) || 1;
  object.scale.setScalar(2.15 / maxSize);
  object.rotation.y = THREE.MathUtils.degToRad(-16);
}

function collectRig(object) {
  const clkLeds = [];
  object.traverse((child) => {
    if (!child.isMesh) return;
    if (isControlMesh(child)) {
      const mat = child.material;
      if (mat && mat.emissive) {
        child.material = mat.clone();
        const hex = child.material.emissive.getHex() || 0xff8a2a;
        child.material.color = new THREE.Color(hex).multiplyScalar(0.38);
        child.material.emissive = new THREE.Color(hex).multiplyScalar(0.55);
        child.material.emissiveIntensity = 0.2;
        child.material.metalness = 0.28;
        child.material.roughness = 0.5;
        child.material.toneMapped = true;
        const rec = { mesh: child, mat: child.material, baseZ: child.rotation.z, intensity: 0.2 };
        controls.push(rec);
      }
    }
    if (/^FaderCap_/i.test(child.name)) {
      faders.push({ mesh: child, baseY: child.position.y });
    }
    if (/^LED_CLK_/i.test(child.name)) {
      const n = Number((child.name.match(/LED_CLK_(\d+)/) || [])[1]);
      clkLeds[n] = child;
    } else if (/^LED_/i.test(child.name)) {
      leds.push(child);
    }
    if (/^Screen_/i.test(child.name)) {
      if (child.material) child.material = child.material.clone();
      screens.push(child);
    }
    if (/^Module_[A-Z]+_Face$/.test(child.name)) {
      const id = moduleIdFromObject(child);
      if (id) {
        if (child.material) child.material = child.material.clone();
        faces.set(id, child);
      }
    }
    if (/^(Cable_|Tip_|Sleeve_)/.test(child.name)) {
      child.raycast = () => {};
    }
  });
  leds = clkLeds.filter(Boolean).concat(leds);
}

function collectPaths(object) {
  const buckets = {};
  object.traverse((child) => {
    const m = /^Path_(\d+)_(\d+)$/.exec(child.name || "");
    if (!m) return;
    (buckets[m[1]] ||= [])[Number(m[2])] = child.position.clone();
  });
  return Object.keys(buckets)
    .sort((a, b) => Number(a) - Number(b))
    .map((k) => buckets[k].filter(Boolean));
}

function spawnCurrents(object, sidecar) {
  let paths = collectPaths(object);
  if (!paths.length && sidecar?.cables) {
    paths = sidecar.cables.map((c) => c.points.map((p) => new THREE.Vector3(p[0], p[1], p[2])));
  }
  const colors = sidecar?.cables?.map((c) => new THREE.Color(c.color[0], c.color[1], c.color[2])) || [];
  paths.forEach((pts, i) => {
    if (!pts || pts.length < 2) return;
    const curve = new THREE.CatmullRomCurve3(pts, false, "catmullrom", 0.35);
    const geo = new THREE.SphereGeometry(0.02, 10, 10);
    const col = colors[i] || new THREE.Color(0x6ee0ff);
    for (let k = 0; k < 2; k++) {
      const mat = new THREE.MeshBasicMaterial({ color: col, toneMapped: false });
      const ball = new THREE.Mesh(geo, mat);
      object.add(ball);
      currents.push({ curve, ball, t: (i * 0.13 + k * 0.5) % 1, speed: 0.18 + (i % 4) * 0.04 });
    }
  });
}

function markShot(name) {
  activeShot = name;
  document.querySelectorAll(".shots [data-shot]").forEach((btn) => {
    btn.setAttribute("aria-selected", btn.dataset.shot === name ? "true" : "false");
  });
}

function goShot(name, dur = 1.35) {
  const shot = SHOTS[name] || SHOTS.overview;
  markShot(name);
  idleTimer = 0;
  gsap.to(camera.position, {
    x: shot.pos[0],
    y: shot.pos[1],
    z: shot.pos[2],
    duration: reduceMotion ? 0.2 : dur,
    ease: "power3.inOut",
  });
  gsap.to(look, {
    x: shot.look[0],
    y: shot.look[1],
    z: shot.look[2],
    duration: reduceMotion ? 0.2 : dur,
    ease: "power3.inOut",
  });
}

function playIntro() {
  const start = SHOTS.overview;
  camera.position.set(1.95, 1.2, 2.45);
  const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
  tl.to(camera.position, {
    x: start.pos[0],
    y: start.pos[1],
    z: start.pos[2],
    duration: reduceMotion ? 0.2 : 2.4,
    onComplete: () => { introDone = true; },
  }, 0);
  tl.fromTo(
    ".eyebrow, h1, .lede, .actions, .dock, .meta",
    { y: 24, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.9, stagger: 0.07 },
    0.3
  );
  if (!reduceMotion && root) {
    tl.to(root.rotation, { y: "+=0.16", duration: 11, ease: "sine.inOut", yoyo: true, repeat: -1 }, 2.2);
    tl.to(root.position, { y: 0.03, duration: 4.6, ease: "sine.inOut", yoyo: true, repeat: -1 }, 2.2);
  }
}

function setAudioMode(mode) {
  document.querySelector("#btn-patch")?.setAttribute("aria-pressed", mode === "patch" ? "true" : "false");
  document.querySelector("#btn-mic")?.setAttribute("aria-pressed", mode === "mic" ? "true" : "false");
  document.querySelector("#btn-mute")?.setAttribute("aria-pressed", mode === "off" ? "true" : "false");
  return patch.setMode(mode).catch((err) => {
    console.warn("[audio]", err);
    if (mode === "mic") setAudioMode("patch");
  });
}

function fillTip(id) {
  const spec = MODULES[id];
  if (!spec) return;
  const lang = currentLang();
  tip.querySelector(".tip-id").textContent = t(`${id}_name`);
  tip.querySelector(".tip-title").textContent = t(`${id}_title`);
  tip.querySelector(".tip-lede").textContent = t(`${id}_lede`);
  const lesson = tip.querySelector('[data-tip="lesson"]');
  const p = tip.querySelector('[data-tip="patch"]');
  lesson.textContent = t("tipLesson");
  p.textContent = t("tipPatch");
  lesson.href = spec.lesson[lang] || spec.lesson.en;
  p.href = spec.patch[lang] || spec.patch.en;
  tip.hidden = false;
}

function highlight(id) {
  faces.forEach((mesh, key) => {
    if (!mesh.material) return;
    const on = key === id;
    gsap.to(mesh.material, { emissiveIntensity: on ? 0.85 : 0.28, duration: 0.2 });
  });
  hovered = id;
  document.body.classList.toggle("is-pick", Boolean(id));
  if (id) fillTip(id);
}

function pick(clientX, clientY) {
  if (!camera || !model) return null;
  const ndc = new THREE.Vector2(
    (clientX / window.innerWidth) * 2 - 1,
    -(clientY / window.innerHeight) * 2 + 1,
  );
  const ray = new THREE.Raycaster();
  ray.setFromCamera(ndc, camera);
  const hits = ray.intersectObject(model, true);
  for (const hit of hits) {
    const id = moduleIdFromObject(hit.object);
    if (id) return id;
  }
  return null;
}

function driveAudio() {
  const s = patch.sample();
  const live = s.rms > 0.02 || s.bass + s.mid > 0.08 || patch.mode === "patch";
  const pulse = live ? 0.25 + s.rms * 4.2 + s.mid * 1.4 : 0.18;
  controls.forEach((rec, i) => {
    const wobble = 0.55 + Math.sin(performance.now() * 0.0016 + i) * 0.2;
    rec.mat.emissiveIntensity = THREE.MathUtils.clamp(pulse * wobble + (i % 8 === s.step ? 0.55 : 0), 0.08, 1.8);
    rec.mesh.rotation.z = rec.baseZ + s.mid * 0.9 + Math.sin(performance.now() * 0.0008 + i) * 0.15;
  });
  faders.forEach((f, i) => {
    const target = f.baseY + (s.bass * 0.035 - 0.012) + ((s.step + i) % 4) * 0.004;
    f.mesh.position.y += (target - f.mesh.position.y) * 0.12;
  });
  leds.forEach((led, i) => {
    if (!led.material) return;
    const on = i < 8 ? i === s.step : s.high > 0.12;
    led.material.emissiveIntensity = on ? 2.2 : 0.12;
  });
  screens.forEach((scr) => {
    if (scr.material && "emissiveIntensity" in scr.material) {
      scr.material.emissiveIntensity = 1.4 + s.high * 3.5;
    }
  });
  if (bloom) bloom.strength = 0.34 + s.rms * 0.55;
  currents.forEach((c) => {
    c.t = (c.t + 0.004 * c.speed * (0.7 + s.rms * 8 + (s.onset ? 1.4 : 0))) % 1;
    const p = c.curve.getPointAt(c.t);
    c.ball.position.copy(p);
    const sc = 0.7 + s.rms * 2.4;
    c.ball.scale.setScalar(sc);
  });
  return s;
}

function tick() {
  if (webglReady) {
    if (introDone && activeShot === "overview") {
      const shot = SHOTS.overview;
      const targetX = shot.pos[0] + pointer.x * 0.22;
      const targetY = shot.pos[1] - pointer.y * 0.12;
      camera.position.x += (targetX - camera.position.x) * 0.045;
      camera.position.y += (targetY - camera.position.y) * 0.045;
    }
    driveAudio();
    if (!reduceMotion && introDone) {
      idleTimer += 1 / 60;
      if (idleTimer > 9) {
        const order = ["overview", "knobs", "cables", "into"];
        const next = order[(order.indexOf(activeShot) + 1) % order.length];
        goShot(next, 1.8);
      }
    }
    camera.lookAt(look);
    composer.render();
  }
  requestAnimationFrame(tick);
}

function initThree() {
  renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: false,
    powerPreference: "high-performance",
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x04070b);
  scene.fog = new THREE.Fog(0x04070b, 6, 18);

  camera = new THREE.PerspectiveCamera(28, window.innerWidth / window.innerHeight, 0.05, 40);
  camera.position.set(1.15, 0.72, 1.55);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.35;

  const key = new THREE.DirectionalLight(0xc8dcff, 2.2);
  key.position.set(2.2, 3.4, 2.6);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0x4db8ff, 1.4);
  rim.position.set(-3.2, 1.6, -1.2);
  scene.add(rim);
  const warm = new THREE.PointLight(0xff8a2a, 6, 8, 2);
  warm.position.set(1.4, 0.7, 0.8);
  scene.add(warm);
  scene.add(new THREE.AmbientLight(0x6f86a0, 0.18));

  composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  bloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.42, 0.45, 0.78);
  composer.addPass(bloom);

  root = new THREE.Group();
  scene.add(root);
}

async function loadModel() {
  const draco = new DRACOLoader();
  draco.setDecoderPath("https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/gltf/");
  const loader = new GLTFLoader();
  loader.setDRACOLoader(draco);
  const gltf = await loader.loadAsync("./hero.glb?v=10", (ev) => {
    if (ev.total) setBoot(0.1 + 0.8 * (ev.loaded / ev.total));
  });
  let sidecar = null;
  try {
    sidecar = await (await fetch("./cables.json")).json();
  } catch (err) {
    console.warn("cables.json", err);
  }
  model = gltf.scene;
  model.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
      if (child.material) {
        child.material.envMapIntensity = 0.9;
        if (child.material.emissive) {
          child.material.emissiveIntensity = Math.max(child.material.emissiveIntensity || 0, 0.55);
        }
      }
    }
  });
  frameObject(model);
  collectRig(model);
  spawnCurrents(model, sidecar);
  root.add(model);
  console.info("[hero] controls", controls.length, "currents", currents.length, "faces", faces.size);
}

function bindUi() {
  window.addEventListener("pointermove", (e) => {
    pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
    pointer.y = (e.clientY / window.innerHeight) * 2 - 1;
    if (!webglReady) return;
    const id = pick(e.clientX, e.clientY);
    if (id !== hovered) highlight(id);
  });
  canvas.addEventListener("click", (e) => {
    const id = pick(e.clientX, e.clientY);
    if (!id) return;
    const spec = MODULES[id];
    const lang = currentLang();
    fillTip(id);
    window.open(spec.lesson[lang] || spec.lesson.en, "_blank", "noopener");
  });
  document.querySelectorAll(".shots [data-shot]").forEach((btn) => {
    btn.addEventListener("click", () => goShot(btn.dataset.shot));
  });
  document.querySelectorAll(".actions [data-shot]").forEach((el) => {
    el.addEventListener("pointerenter", () => goShot(el.dataset.shot, 1.1));
  });
  document.querySelector("#btn-patch")?.addEventListener("click", () => setAudioMode("patch"));
  document.querySelector("#btn-mic")?.addEventListener("click", () => setAudioMode("mic"));
  document.querySelector("#btn-mute")?.addEventListener("click", () => setAudioMode("off"));
  document.addEventListener("mg-lang", () => { if (hovered) fillTip(hovered); });
  window.addEventListener("resize", () => {
    if (!camera || !renderer) return;
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    composer.setSize(window.innerWidth, window.innerHeight);
    bloom.setSize(window.innerWidth, window.innerHeight);
  });
}

async function enter(withAudio) {
  hideBoot();
  if (webglReady && !introDone) playIntro();
  if (withAudio !== false) await setAudioMode(reduceMotion ? "off" : "patch");
}

async function bootWebGL() {
  poster.hidden = true;
  canvas.style.display = "block";
  initThree();
  try {
    await loadModel();
    webglReady = true;
    setBoot(1, t("bootReady"));
    btnEnter.hidden = false;
  } catch (err) {
    console.warn("GLB failed", err);
    usePoster();
  }
}

async function boot() {
  applyLang(currentLang());
  bindUi();
  tick();
  setBoot(0.08, t("bootLoad"));
  if (preferPoster) {
    usePoster();
  } else {
    await bootWebGL();
  }
  btnEnter.addEventListener("click", () => enter(true));
  btnForce3d.addEventListener("click", async () => {
    btnForce3d.hidden = true;
    await bootWebGL();
    enter(true);
  });
}

boot();
