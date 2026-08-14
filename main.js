import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";
import gsap from "gsap";
import { MODULES, moduleIdFromObject } from "./modules.js";
import { createPatch } from "./audio.js";
import { applyLang, currentLang, t } from "./i18n.js";

// Scene State
let scene, camera, renderer;
let rig, rackGroup;
let model;
let raycaster, pointer;
let patch;

const controls = [];
const faders = [];
const leds = [];
const screens = {};
const moduleMeshes = {};
const pulsePoints = [];

let currentMode = "look"; // 'look' (Explore) or 'learn' (Inspect)
let currentShot = "overview";
let hoveredModule = null;
let focusedModule = null;

let targetRotX = 0;
let targetRotY = 0;
let mouseX = 0;
let mouseY = 0;

const cameraTarget = new THREE.Vector3(0.22, -0.02, 0.0);

// Camera Shot Presets
const SHOTS = {
  overview: { pos: [0.12, 0.24, 1.35], look: [0.22, -0.02, 0.0], tilt: 1.0 },
  knobs: { pos: [-0.08, 0.16, 0.82], look: [-0.02, 0.02, 0.0], tilt: 0.4 },
  cables: { pos: [0.28, 0.06, 0.88], look: [0.24, -0.10, 0.0], tilt: 0.5 },
  into: { pos: [0.18, 0.08, 0.65], look: [0.18, 0.0, 0.0], tilt: 0.3 },
};

// Module Focus Zoom Targets (X coordinate in rack space)
const MODULE_BOUNDS = {
  CLK: { x: -0.44 },
  VCO: { x: -0.30 },
  FLT: { x: -0.17 },
  ENV: { x: -0.05 },
  LFO: { x: 0.06 },
  RND: { x: 0.17 },
  MIX: { x: 0.30 },
  VIS: { x: 0.45 },
};

// Canvas Dynamic Scope & Screen Textures
function createScopeCanvas(width = 256, height = 128) {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  return { canvas, ctx, texture };
}

const scopeVCO = createScopeCanvas(256, 128);
const scopeVIS = createScopeCanvas(384, 192);
const scopeCLK = createScopeCanvas(256, 96);

function init() {
  const canvas = document.getElementById("stage");
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x06090e);
  scene.fog = new THREE.FogExp2(0x06090e, 0.16);

  camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.08, 30);
  camera.position.set(...SHOTS.overview.pos);
  camera.lookAt(cameraTarget);

  renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: false,
    powerPreference: "high-performance",
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.25;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // Scene Hierarchy
  rig = new THREE.Group();
  scene.add(rig);

  rackGroup = new THREE.Group();
  // Tilt rack 65 deg so faceplates face camera with natural ergonomic slant
  rackGroup.rotation.x = THREE.MathUtils.degToRad(62);
  rackGroup.rotation.y = THREE.MathUtils.degToRad(-12);
  rackGroup.position.set(0.22, 0.04, 0.0);
  rig.add(rackGroup);

  setupLighting();
  setupStudioFloor();
  setupInteractivity();
  setupAudio();
  loadModel();

  window.addEventListener("resize", onResize);
  requestAnimationFrame(tick);
}

function setupLighting() {
  const ambient = new THREE.AmbientLight(0x1e293b, 1.8);
  scene.add(ambient);

  const keyLight = new THREE.DirectionalLight(0xffffff, 3.2);
  keyLight.position.set(2.5, 4.2, 3.0);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.width = 2048;
  keyLight.shadow.mapSize.height = 2048;
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x38bdf8, 2.2);
  fillLight.position.set(-3.2, 1.8, 1.8);
  scene.add(fillLight);

  const rimLight = new THREE.DirectionalLight(0x22d3ee, 3.5);
  rimLight.position.set(0.0, 3.2, -2.2);
  scene.add(rimLight);

  const warmPoint = new THREE.PointLight(0xf97316, 1.8, 4.5);
  warmPoint.position.set(0.3, 0.8, 0.9);
  scene.add(warmPoint);
}

function setupStudioFloor() {
  const geo = new THREE.PlaneGeometry(20, 20);
  const mat = new THREE.MeshStandardMaterial({
    color: 0x06090e,
    roughness: 0.7,
    metalness: 0.2,
  });
  const floor = new THREE.Mesh(geo, mat);
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.45;
  floor.receiveShadow = true;
  scene.add(floor);
}

function loadModel() {
  const draco = new DRACOLoader();
  draco.setDecoderPath("https://unpkg.com/three@0.160.0/examples/jsm/libs/draco/");
  const loader = new GLTFLoader();
  loader.setDRACOLoader(draco);

  const fill = document.getElementById("boot-fill");
  const status = document.getElementById("boot-status");
  const enterBtn = document.getElementById("btn-enter");

  loader.load(
    "hero.glb",
    (gltf) => {
      model = gltf.scene;

      model.traverse((child) => {
        if (!child.isMesh) return;
        child.castShadow = true;
        child.receiveShadow = true;

        // Clamp texture wrapping
        if (child.material && child.material.map) {
          child.material.map.wrapS = THREE.ClampToEdgeWrapping;
          child.material.map.wrapT = THREE.ClampToEdgeWrapping;
          child.material.map.needsUpdate = true;
        }

        // Collect Knobs
        if (name.startsWith("Knob_")) {
          controls.push({
            mesh: child,
            baseZ: child.rotation.z,
            name: name,
            speed: (Math.random() * 0.8 + 0.4) * (Math.random() < 0.5 ? 1 : -1),
          });
        }

        // Collect Faders
        if (name.startsWith("FaderCap_")) {
          faders.push({
            mesh: child,
            baseY: child.position.y,
            name: name,
          });
        }

        // Collect LEDs
        if (name.startsWith("LED_")) {
          leds.push(child);
        }

        // Apply Live Dynamic Screens
        if (name.startsWith("Screen_")) {
          if (name.includes("VIS")) {
            child.material = new THREE.MeshBasicMaterial({ map: scopeVIS.texture });
            screens.vis = child;
          } else if (name.includes("VCO")) {
            child.material = new THREE.MeshBasicMaterial({ map: scopeVCO.texture });
            screens.vco = child;
          } else if (name.includes("CLK")) {
            child.material = new THREE.MeshBasicMaterial({ map: scopeCLK.texture });
            screens.clk = child;
          }
        }

        // Identify module faces for raycasting & highlighting
        if (name.includes("_Face") || name.includes("_Body")) {
          const modId = moduleIdFromObject(child);
          if (modId) {
            if (!moduleMeshes[modId]) moduleMeshes[modId] = [];
            moduleMeshes[modId].push(child);
            child.userData.moduleId = modId;
          }
        }
      });

      setupCablePulses();
      rackGroup.add(model);

      if (fill) fill.style.width = "100%";
      if (status) status.textContent = t("bootReady");
      if (enterBtn) {
        enterBtn.style.display = "inline-flex";
        enterBtn.onclick = () => dismissBoot();
      }
    },
    (xhr) => {
      if (xhr.lengthComputable && fill) {
        const pct = Math.round((xhr.loaded / xhr.total) * 100);
        fill.style.width = `${pct}%`;
      }
    },
    (err) => {
      console.error("GLTF load error:", err);
      if (status) status.textContent = "Error loading 3D asset.";
    }
  );
}

function dismissBoot() {
  const boot = document.getElementById("boot");
  if (boot) boot.classList.add("is-gone");
  if (patch && patch.mode === "off") {
    patch.setMode("patch");
    updateAudioButtons("patch");
  }
}

function setupCablePulses() {
  fetch("cables.json")
    .then((r) => r.json())
    .then((data) => {
      if (!data.cables) return;
      const sphereGeo = new THREE.SphereGeometry(0.005, 12, 12);

      data.cables.forEach((cab, i) => {
        const pts = cab.points.map((p) => new THREE.Vector3(...p));
        const curve = new THREE.CatmullRomCurve3(pts);
        const col = cab.color || [0.2, 0.8, 1.0];
        const pulseMat = new THREE.MeshBasicMaterial({
          color: new THREE.Color(...col),
        });
        const pulseMesh = new THREE.Mesh(sphereGeo, pulseMat);
        rackGroup.add(pulseMesh);

        pulsePoints.push({
          mesh: pulseMesh,
          curve,
          t: Math.random(),
          speed: 0.12 + (i % 5) * 0.03,
        });
      });
    })
    .catch((e) => console.warn("Cables json error:", e));
}

function setupInteractivity() {
  raycaster = new THREE.Raycaster();
  pointer = new THREE.Vector2();

  window.addEventListener("pointermove", (e) => {
    mouseX = (e.clientX / window.innerWidth) * 2 - 1;
    mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    pointer.x = mouseX;
    pointer.y = mouseY;

    const shotConfig = SHOTS[currentShot] || SHOTS.overview;
    const tiltScale = focusedModule ? 0.2 : shotConfig.tilt;

    targetRotY = mouseX * 0.14 * tiltScale;
    targetRotX = -mouseY * 0.09 * tiltScale;

    checkRaycast();
  });

  window.addEventListener("click", (e) => {
    if (e.target.closest("nav, .dock, .inspector-card, #btn-unfocus, #boot")) return;
    if (hoveredModule) {
      focusModule(hoveredModule);
    }
  });

  document.getElementById("mode-look")?.addEventListener("click", () => setMode("look"));
  document.getElementById("mode-learn")?.addEventListener("click", () => setMode("learn"));

  document.querySelectorAll("[data-shot]").forEach((btn) => {
    btn.addEventListener("click", () => setShot(btn.dataset.shot));
  });

  document.getElementById("lang-en")?.addEventListener("click", () => setLanguage("en"));
  document.getElementById("lang-ru")?.addEventListener("click", () => setLanguage("ru"));

  document.getElementById("btn-unfocus")?.addEventListener("click", () => unfocusModule());
}

function setMode(mode) {
  currentMode = mode;
  document.getElementById("mode-look")?.setAttribute("aria-selected", mode === "look");
  document.getElementById("mode-learn")?.setAttribute("aria-selected", mode === "learn");
  
  const metaText = document.getElementById("meta-text");
  if (metaText) {
    metaText.textContent = mode === "look" ? t("metaLook") : t("metaLearn");
  }

  if (mode === "look" && !focusedModule) {
    hideInspector();
  }
}

function setShot(shotKey) {
  if (!SHOTS[shotKey]) return;
  currentShot = shotKey;
  focusedModule = null;
  document.getElementById("btn-unfocus").style.display = "none";

  document.querySelectorAll("[data-shot]").forEach((b) => {
    b.setAttribute("aria-selected", b.dataset.shot === shotKey);
  });

  const shot = SHOTS[shotKey];
  gsap.to(camera.position, {
    x: shot.pos[0],
    y: shot.pos[1],
    z: shot.pos[2],
    duration: 1.2,
    ease: "power3.inOut",
  });

  gsap.to(cameraTarget, {
    x: shot.look[0],
    y: shot.look[1],
    z: shot.look[2],
    duration: 1.2,
    ease: "power3.inOut",
  });

  gsap.to(rackGroup.position, {
    x: 0.24,
    y: -0.05,
    z: 0.0,
    duration: 1.2,
    ease: "power3.inOut",
  });
}

function setLanguage(lang) {
  localStorage.setItem("mg-lang", lang);
  document.getElementById("lang-en")?.setAttribute("aria-checked", lang === "en");
  document.getElementById("lang-ru")?.setAttribute("aria-checked", lang === "ru");
  applyLang(lang);
  if (hoveredModule) updateInspector(hoveredModule);
}

function checkRaycast() {
  if (!model) return;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(model.children, true);

  if (hits.length > 0) {
    let hitObj = hits[0].object;
    const modId = moduleIdFromObject(hitObj);

    if (modId) {
      if (hoveredModule !== modId) {
        hoveredModule = modId;
        highlightModule(modId);
        updateInspector(modId);
      }
      return;
    }
  }

  if (hoveredModule && !focusedModule) {
    unhighlightAll();
    hoveredModule = null;
    if (currentMode === "look") {
      hideInspector();
    }
  }
}

function highlightModule(modId) {
  unhighlightAll();
  const meshes = moduleMeshes[modId];
  if (!meshes) return;

  meshes.forEach((m) => {
    if (m.material && m.material.emissive) {
      m.material.emissive.setHex(0x22d3ee);
      m.material.emissiveIntensity = 0.55;
    }
  });
}

function unhighlightAll() {
  Object.values(moduleMeshes).forEach((list) => {
    list.forEach((m) => {
      if (m.material && m.material.emissive) {
        m.material.emissive.setHex(0x000000);
        m.material.emissiveIntensity = 0.0;
      }
    });
  });
}

function updateInspector(modId) {
  const mod = MODULES[modId];
  if (!mod) return;

  const lang = currentLang();
  const card = document.getElementById("inspector");
  const badge = document.getElementById("card-badge");
  const role = document.getElementById("card-role");
  const title = document.getElementById("card-title");
  const desc = document.getElementById("card-desc");
  const lessonBtn = document.getElementById("card-lesson");
  const patchBtn = document.getElementById("card-patch");

  if (!card) return;

  card.style.display = "flex";
  if (badge) badge.textContent = `● ${mod.id}`;
  if (role) role.textContent = mod.role[lang] || mod.role.en;
  if (title) title.textContent = mod.name[lang] || mod.name.en;
  if (desc) desc.textContent = mod.desc[lang] || mod.desc.en;

  if (lessonBtn) {
    lessonBtn.href = mod.lesson[lang] || mod.lesson.en;
  }
  if (patchBtn) {
    patchBtn.href = mod.patch[lang] || mod.patch.en;
  }
}

function hideInspector() {
  const card = document.getElementById("inspector");
  if (card) card.style.display = "none";
}

function focusModule(modId) {
  focusedModule = modId;
  const bound = MODULE_BOUNDS[modId];
  if (!bound) return;

  document.getElementById("btn-unfocus").style.display = "inline-flex";
  updateInspector(modId);

  // Zoom camera smoothly into the module
  const targetX = bound.x + 0.15;
  gsap.to(camera.position, {
    x: targetX,
    y: 0.12,
    z: 0.62,
    duration: 1.0,
    ease: "power3.out",
  });

  gsap.to(cameraTarget, {
    x: targetX,
    y: 0.0,
    z: 0.0,
    duration: 1.0,
    ease: "power3.out",
  });

  gsap.to(rackGroup.position, {
    x: 0.24 - bound.x * 0.45,
    y: -0.05,
    z: 0.0,
    duration: 1.0,
    ease: "power3.out",
  });
}

function unfocusModule() {
  focusedModule = null;
  document.getElementById("btn-unfocus").style.display = "none";
  setShot(currentShot);
  if (currentMode === "look") {
    hideInspector();
  }
}

function setupAudio() {
  patch = createPatch();

  const btnPatch = document.getElementById("btn-patch");
  const btnMic = document.getElementById("btn-mic");
  const btnMute = document.getElementById("btn-mute");

  btnPatch?.addEventListener("click", async () => {
    await patch.setMode("patch");
    updateAudioButtons("patch");
  });

  btnMic?.addEventListener("click", async () => {
    await patch.setMode("mic");
    updateAudioButtons("mic");
  });

  btnMute?.addEventListener("click", async () => {
    await patch.setMode("off");
    updateAudioButtons("off");
  });
}

function updateAudioButtons(mode) {
  document.getElementById("btn-patch")?.setAttribute("aria-selected", mode === "patch");
  document.getElementById("btn-mic")?.setAttribute("aria-selected", mode === "mic");
  document.getElementById("btn-mute")?.setAttribute("aria-selected", mode === "off");
}

function renderScreenWaves(audioSample, time) {
  // 1. VCO Oscilloscope Wave
  const ctxVCO = scopeVCO.ctx;
  ctxVCO.fillStyle = "rgba(4, 10, 16, 0.35)";
  ctxVCO.fillRect(0, 0, scopeVCO.canvas.width, scopeVCO.canvas.height);
  ctxVCO.strokeStyle = "#38bdf8";
  ctxVCO.lineWidth = 2.5;
  ctxVCO.beginPath();
  const w1 = scopeVCO.canvas.width;
  const h1 = scopeVCO.canvas.height;
  for (let x = 0; x < w1; x++) {
    const t = (x / w1) * Math.PI * 4 + time * 6;
    const wave = Math.sin(t) + 0.4 * Math.sin(t * 2.3 + audioSample.mid * 5);
    const y = h1 / 2 + wave * (h1 * 0.32 * (0.4 + audioSample.rms * 1.5));
    if (x === 0) ctxVCO.moveTo(x, y);
    else ctxVCO.lineTo(x, y);
  }
  ctxVCO.stroke();
  scopeVCO.texture.needsUpdate = true;

  // 2. VIS Spectrum Analyzer
  const ctxVIS = scopeVIS.ctx;
  ctxVIS.fillStyle = "rgba(6, 12, 20, 0.4)";
  ctxVIS.fillRect(0, 0, scopeVIS.canvas.width, scopeVIS.canvas.height);
  const w2 = scopeVIS.canvas.width;
  const h2 = scopeVIS.canvas.height;
  const numBars = 24;
  const barWidth = w2 / numBars - 3;
  for (let i = 0; i < numBars; i++) {
    const barHeight = Math.min(
      h2 * 0.85,
      (audioSample.bins ? audioSample.bins[i * 4] / 255 : Math.sin(time * 3 + i * 0.5) * 0.4 + 0.5) * h2 * 0.8
    );
    const grad = ctxVIS.createLinearGradient(0, h2, 0, 0);
    grad.addColorStop(0, "#22d3ee");
    grad.addColorStop(1, "#f97316");
    ctxVIS.fillStyle = grad;
    ctxVIS.fillRect(i * (barWidth + 3) + 4, h2 - barHeight - 8, barWidth, barHeight);
  }
  scopeVIS.texture.needsUpdate = true;

  // 3. CLK Step Sequencer
  const ctxCLK = scopeCLK.ctx;
  ctxCLK.fillStyle = "rgba(4, 10, 16, 0.5)";
  ctxCLK.fillRect(0, 0, scopeCLK.canvas.width, scopeCLK.canvas.height);
  const steps = 8;
  const stepW = scopeCLK.canvas.width / steps - 6;
  const currentStep = audioSample.step;
  for (let i = 0; i < steps; i++) {
    const isActive = i === currentStep;
    ctxCLK.fillStyle = isActive ? "#22d3ee" : "rgba(34, 211, 238, 0.15)";
    ctxCLK.fillRect(i * (stepW + 6) + 4, 12, stepW, scopeCLK.canvas.height - 24);
  }
  scopeCLK.texture.needsUpdate = true;
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function tick(now) {
  requestAnimationFrame(tick);
  const time = now * 0.001;

  // Parallax inertia
  rig.rotation.y += (targetRotY - rig.rotation.y) * 0.06;
  rig.rotation.x += (targetRotX - rig.rotation.x) * 0.06;

  // Camera lookAt tracking
  camera.lookAt(cameraTarget);

  // Audio Sampling
  const sample = patch ? patch.sample() : { bass: 0, mid: 0, high: 0, rms: 0, step: 0 };

  // Knobs rotation
  controls.forEach((ctrl, i) => {
    const mod = Math.sin(time * ctrl.speed + i * 1.3) * 0.4 + sample.mid * 0.3;
    ctrl.mesh.rotation.z = ctrl.baseZ + mod;
  });

  // Faders animation
  faders.forEach((fader, i) => {
    const mod = Math.sin(time * 1.5 + i * 0.8) * 0.015 + sample.bass * 0.01;
    fader.mesh.position.y = fader.baseY + mod;
  });

  // Cable voltage pulses
  pulsePoints.forEach((pulse) => {
    pulse.t = (pulse.t + pulse.speed * 0.016) % 1.0;
    const pt = pulse.curve.getPointAt(pulse.t);
    pulse.mesh.position.copy(pt);
  });

  renderScreenWaves(sample, time);

  renderer.render(scene, camera);
}

// Boot
applyLang(currentLang());
init();
