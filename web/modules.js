const EN = "https://alevoldon.github.io/Modular-Genesis";
const RU = "https://alevoldon.github.io/Modular-Genesis/ru";

export const MODULES = {
  CLK: {
    id: "CLK",
    hue: 0x33ebba,
    lesson: {
      en: `${EN}/course/sequencing-01-clock-trigger-gate/`,
      ru: `${RU}/course/sequencing-01-clock-trigger-gate/`,
    },
    patch: {
      en: `${EN}/patches/sequencing-8-step-bassline-v01/`,
      ru: `${RU}/patches/sequencing-8-step-bassline-v01/`,
    },
  },
  VCO: {
    id: "VCO",
    hue: 0xff7a1a,
    lesson: {
      en: `${EN}/course/foundations-03-first-subtractive-patch/`,
      ru: `${RU}/course/foundations-03-first-subtractive-patch/`,
    },
    patch: {
      en: `${EN}/patches/foundations-basic-voice-v01/`,
      ru: `${RU}/patches/foundations-basic-voice-v01/`,
    },
  },
  FLT: {
    id: "FLT",
    hue: 0x40b8ff,
    lesson: {
      en: `${EN}/course/foundations-03-first-subtractive-patch/`,
      ru: `${RU}/course/foundations-03-first-subtractive-patch/`,
    },
    patch: {
      en: `${EN}/patches/foundations-filter-sweep-study-v01/`,
      ru: `${RU}/patches/foundations-filter-sweep-study-v01/`,
    },
  },
  ENV: {
    id: "ENV",
    hue: 0xf2388c,
    lesson: {
      en: `${EN}/course/foundations-04-envelopes-and-lfo/`,
      ru: `${RU}/course/foundations-04-envelopes-and-lfo/`,
    },
    patch: {
      en: `${EN}/patches/foundations-basic-voice-v01/`,
      ru: `${RU}/patches/foundations-basic-voice-v01/`,
    },
  },
  LFO: {
    id: "LFO",
    hue: 0xbf59ff,
    lesson: {
      en: `${EN}/course/foundations-04-envelopes-and-lfo/`,
      ru: `${RU}/course/foundations-04-envelopes-and-lfo/`,
    },
    patch: {
      en: `${EN}/patches/generative-generative-ambient-v01/`,
      ru: `${RU}/patches/generative-generative-ambient-v01/`,
    },
  },
  RND: {
    id: "RND",
    hue: 0xf2d926,
    lesson: {
      en: `${EN}/course/generative-01-random-and-sample-hold/`,
      ru: `${RU}/course/generative-01-random-and-sample-hold/`,
    },
    patch: {
      en: `${EN}/patches/generative-probability-grid-v01/`,
      ru: `${RU}/patches/generative-probability-grid-v01/`,
    },
  },
  MIX: {
    id: "MIX",
    hue: 0x59ff73,
    lesson: {
      en: `${EN}/course/hybrid-01-routing-vcv-into-ableton/`,
      ru: `${RU}/course/hybrid-01-routing-vcv-into-ableton/`,
    },
    patch: {
      en: `${EN}/patches/performances-hybrid-live-set-v01/`,
      ru: `${RU}/patches/performances-hybrid-live-set-v01/`,
    },
  },
  VIS: {
    id: "VIS",
    hue: 0x33d9ff,
    lesson: {
      en: `${EN}/course/audiovisual-01-audio-reactive-visuals/`,
      ru: `${RU}/course/audiovisual-01-audio-reactive-visuals/`,
    },
    patch: {
      en: `${EN}/patches/performances-drone-performance-core-v01/`,
      ru: `${RU}/patches/performances-drone-performance-core-v01/`,
    },
  },
};

export function moduleIdFromName(name) {
  if (!name) return null;
  const m = /Module_([A-Z]+)/.exec(name);
  if (m && MODULES[m[1]]) return m[1];
  const fromPart = /_(CLK|VCO|FLT|ENV|LFO|RND|MIX|VIS)(?:_|$)/.exec(name);
  return fromPart ? fromPart[1] : null;
}

export function moduleIdFromObject(obj) {
  let o = obj;
  while (o) {
    const id = moduleIdFromName(o.name);
    if (id) return id;
    o = o.parent;
  }
  return null;
}
