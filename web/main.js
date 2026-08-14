import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import gsap from "gsap";

const canvas = document.querySelector("#stage");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const renderer = new THREE.WebGLRenderer({
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

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x04070b);
scene.fog = new THREE.Fog(0x04070b, 6, 18);

const camera = new THREE.PerspectiveCamera(28, window.innerWidth / window.innerHeight, 0.05, 40);
camera.position.set(1.15, 0.72, 1.55);
camera.lookAt(0, 0.05, 0);

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

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.42, 0.45, 0.78);
composer.addPass(bloom);

const root = new THREE.Group();
scene.add(root);

const pointer = { x: 0, y: 0 };
let introDone = false;
window.addEventListener("pointermove", (e) => {
  pointer.x = (e.clientX / window.innerWidth) * 2 - 1;
  pointer.y = (e.clientY / window.innerHeight) * 2 - 1;
});

function frameObject(object) {
  const skip = /floor|backdrop|hud/i;
  object.traverse((child) => {
    if (child.isMesh && skip.test(child.name)) child.visible = false;
  });
  const box = new THREE.Box3().setFromObject(object);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  object.position.sub(center);
  const maxSize = Math.max(size.x, size.y, size.z) || 1;
  object.scale.setScalar(2.8 / maxSize);
  object.rotation.y = THREE.MathUtils.degToRad(-16);
}

function pulseControl(state) {
  const rest = Math.random() < 0.35;
  gsap.to(state, {
    intensity: rest ? 0.1 + Math.random() * 0.12 : 0.85 + Math.random() * 0.75,
    duration: 0.55 + Math.random() * 1.4,
    ease: "sine.inOut",
    onUpdate: () => {
      state.mat.emissiveIntensity = state.intensity;
    },
    onComplete: () => pulseControl(state),
  });
}

function isControlMesh(obj) {
  const labels = [obj.name, obj.parent && obj.parent.name];
  return labels.some((n) => n && /^(Knob|FaderCap|LED)_/i.test(n) && !/Stem/i.test(n));
}

function lightModularControls(model) {
  const hues = [0xff8a2a, 0x3ecbff, 0xff4d8d, 0x5dff9a, 0xffe14a];
  const controls = [];
  model.traverse((child) => {
    if (child.isMesh && isControlMesh(child)) controls.push(child);
  });
  controls.forEach((child, i) => {
    const hex = hues[i % hues.length];
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(hex).multiplyScalar(0.38),
      emissive: new THREE.Color(hex).multiplyScalar(0.55),
      emissiveIntensity: 0.2,
      metalness: 0.28,
      roughness: 0.5,
      toneMapped: true,
    });
    child.material = mat;
    const state = { mat, intensity: 0.2 };
    gsap.delayedCall(Math.random() * 1.8, () => pulseControl(state));
  });
  console.info("[hero] controls", controls.length);
}

function playIntro() {
  const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
  tl.fromTo(
    camera.position,
    { x: 1.9, y: 1.15, z: 2.4 },
    {
      x: 1.05,
      y: 0.62,
      z: 1.35,
      duration: reduceMotion ? 0.2 : 2.4,
      onComplete: () => { introDone = true; },
    },
    0
  );
  tl.from(".eyebrow, h1, .lede, .actions", {
    y: 28,
    opacity: 0,
    duration: 0.9,
    stagger: 0.08,
  }, 0.35);
  if (!reduceMotion) {
    tl.to(root.rotation, { y: "+=0.18", duration: 10, ease: "sine.inOut", yoyo: true, repeat: -1 }, 2.2);
    tl.to(root.position, { y: 0.04, duration: 4.5, ease: "sine.inOut", yoyo: true, repeat: -1 }, 2.2);
    tl.to(warm, { intensity: 4.2, duration: 2.4, yoyo: true, repeat: -1, ease: "sine.inOut" }, 2.4);
  }
}

function tick() {
  if (introDone) {
    const targetX = 1.05 + pointer.x * 0.22;
    const targetY = 0.62 - pointer.y * 0.12;
    camera.position.x += (targetX - camera.position.x) * 0.045;
    camera.position.y += (targetY - camera.position.y) * 0.045;
  }
  camera.lookAt(0, 0.04, 0);
  composer.render();
  requestAnimationFrame(tick);
}

async function boot() {
  const loader = new GLTFLoader();
  try {
    const gltf = await loader.loadAsync("./hero.glb?v=4");
    const model = gltf.scene;
    model.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
        if (child.material) {
          child.material.envMapIntensity = 0.9;
          if (child.material.emissive) {
            child.material.emissiveIntensity = Math.max(child.material.emissiveIntensity || 0, 0.6);
          }
        }
      }
    });
    frameObject(model);
    lightModularControls(model);
    root.add(model);
  } catch (err) {
    console.warn("GLB missing or blocked, using fallback rig", err);
    const geo = new THREE.BoxGeometry(1.6, 0.22, 0.8);
    const mat = new THREE.MeshStandardMaterial({ color: 0x1a1f26, metalness: 0.85, roughness: 0.28 });
    root.add(new THREE.Mesh(geo, mat));
  }
  playIntro();
  tick();
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  composer.setSize(window.innerWidth, window.innerHeight);
  bloom.setSize(window.innerWidth, window.innerHeight);
});

boot();
