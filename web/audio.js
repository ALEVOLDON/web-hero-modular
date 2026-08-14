/** Live generative patch + analyser. Starts only after a user gesture. */

const PENT = [110, 130.81, 146.83, 164.81, 196, 220, 246.94, 293.66];

export function createPatch() {
  const state = {
    ctx: null,
    analyser: null,
    master: null,
    filter: null,
    oscA: null,
    oscB: null,
    lfo: null,
    clock: null,
    mode: "off",
    step: 0,
    onset: false,
    mic: null,
    timer: 0,
    freqData: null,
    timeData: null,
  };

  async function ensure() {
    if (state.ctx) return state.ctx;
    const ctx = new AudioContext();
    const master = ctx.createGain();
    master.gain.value = 0.11;
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.72;
    master.connect(analyser);
    analyser.connect(ctx.destination);

    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = 900;
    filter.Q.value = 8;
    filter.connect(master);

    const oscA = ctx.createOscillator();
    const oscB = ctx.createOscillator();
    oscA.type = "sawtooth";
    oscB.type = "triangle";
    oscA.frequency.value = PENT[0];
    oscB.frequency.value = PENT[0] * 1.005;
    const gA = ctx.createGain();
    const gB = ctx.createGain();
    gA.gain.value = 0.22;
    gB.gain.value = 0.16;
    oscA.connect(gA).connect(filter);
    oscB.connect(gB).connect(filter);

    const lfo = ctx.createOscillator();
    const lfoGain = ctx.createGain();
    lfo.type = "sine";
    lfo.frequency.value = 0.13;
    lfoGain.gain.value = 480;
    lfo.connect(lfoGain).connect(filter.frequency);

    const click = ctx.createGain();
    click.gain.value = 0;
    const noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 0.05, ctx.sampleRate);
    const data = noiseBuf.getChannelData(0);
    for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / data.length);
    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuf;
    noise.loop = true;
    const noiseG = ctx.createGain();
    noiseG.gain.value = 0.012;
    noise.connect(noiseG).connect(master);

    oscA.start();
    oscB.start();
    lfo.start();
    noise.start();

    state.ctx = ctx;
    state.analyser = analyser;
    state.master = master;
    state.filter = filter;
    state.oscA = oscA;
    state.oscB = oscB;
    state.lfo = lfo;
    state.freqData = new Uint8Array(analyser.frequencyBinCount);
    state.timeData = new Uint8Array(analyser.fftSize);

    const stepMs = 320;
    state.timer = window.setInterval(() => {
      if (state.mode !== "patch") return;
      state.step = (state.step + 1) % 8;
      state.onset = true;
      const f = PENT[state.step] * (Math.random() < 0.18 ? 0.5 : 1);
      const t = ctx.currentTime;
      oscA.frequency.setTargetAtTime(f, t, 0.04);
      oscB.frequency.setTargetAtTime(f * (state.step % 2 ? 1.5 : 1.005), t, 0.05);
      filter.Q.setTargetAtTime(4 + Math.random() * 8, t, 0.08);
    }, stepMs);

    return ctx;
  }

  async function setMode(mode) {
    await ensure();
    if (state.ctx.state === "suspended") await state.ctx.resume();
    state.mode = mode;
    if (mode === "patch") {
      stopMic();
      state.master.gain.setTargetAtTime(0.11, state.ctx.currentTime, 0.05);
    } else if (mode === "mic") {
      state.master.gain.setTargetAtTime(0.0, state.ctx.currentTime, 0.08);
      await startMic();
    } else {
      stopMic();
      state.master.gain.setTargetAtTime(0.0, state.ctx.currentTime, 0.08);
      state.mode = "off";
    }
  }

  async function startMic() {
    if (state.mic) return;
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    const src = state.ctx.createMediaStreamSource(stream);
    src.connect(state.analyser);
    state.mic = { stream, src };
  }

  function stopMic() {
    if (!state.mic) return;
    state.mic.stream.getTracks().forEach((t) => t.stop());
    try { state.mic.src.disconnect(); } catch {}
    state.mic = null;
  }

  function sample() {
    const empty = { bass: 0, mid: 0, high: 0, rms: 0, step: state.step, onset: false, bins: null };
    if (!state.analyser) return empty;
    state.analyser.getByteFrequencyData(state.freqData);
    state.analyser.getByteTimeDomainData(state.timeData);
    const bins = state.freqData;
    const n = bins.length;
    let bass = 0, mid = 0, high = 0;
    const bN = Math.max(1, Math.floor(n * 0.08));
    const mN = Math.max(1, Math.floor(n * 0.35));
    for (let i = 0; i < bN; i++) bass += bins[i];
    for (let i = bN; i < mN; i++) mid += bins[i];
    for (let i = mN; i < n; i++) high += bins[i];
    bass /= bN * 255;
    mid /= (mN - bN) * 255;
    high /= (n - mN) * 255;
    let rms = 0;
    for (let i = 0; i < state.timeData.length; i++) {
      const v = (state.timeData[i] - 128) / 128;
      rms += v * v;
    }
    rms = Math.sqrt(rms / state.timeData.length);
    const onset = state.onset;
    state.onset = false;
    return { bass, mid, high, rms, step: state.step, onset, bins };
  }

  return { setMode, sample, get mode() { return state.mode; }, get step() { return state.step; } };
}
