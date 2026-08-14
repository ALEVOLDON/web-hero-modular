/**
 * Modular Genesis - Module Definitions, Educational Metadata & Signal Path
 */

const EN_BASE = "https://alevoldon.github.io/Modular-Genesis";
const RU_BASE = "https://alevoldon.github.io/Modular-Genesis/ru";

export const MODULES = {
  CLK: {
    id: "CLK",
    name: { en: "Master Clock & Trigger Generator", ru: "Мастер-клок и генератор триггеров" },
    role: { en: "Heartbeat of the modular rack", ru: "Пульс и ритмическая основа всей системы" },
    desc: {
      en: "Generates high-precision master clock pulses, Euclidean rhythm divisions, and reset triggers. Drives the sequencers, S&H samplers, and envelope gates.",
      ru: "Формирует высокоточные синхроимпульсы, деления темпа и триггеры сброса. Управляет секвенсорами, блоками Sample & Hold и генераторами огибающих."
    },
    hue: 0x22d3ee,
    accent: [0.20, 0.92, 0.72],
    lesson: {
      en: `${EN_BASE}/course/sequencing-01-clock-trigger-gate/`,
      ru: `${RU_BASE}/course/sequencing-01-clock-trigger-gate/`,
    },
    patch: {
      en: `${EN_BASE}/patches/sequencing-8-step-bassline-v01/`,
      ru: `${RU_BASE}/patches/sequencing-8-step-bassline-v01/`,
    },
  },
  VCO: {
    id: "VCO",
    name: { en: "Dual Morphing Oscillator", ru: "Двойной морфинг-осциллятор" },
    role: { en: "Primary Sound Generation Core", ru: "Основной источник звуковых колебаний" },
    desc: {
      en: "Analog core producing continuously morphable Saw, Triangle, Square, and PWM waveforms. Features 1V/Oct tracking, hard sync, and linear FM modulation.",
      ru: "Аналоговое ядро с плавным морфингом между пилой, треугольником, меандром и ШИМ. Поддерживает трекинг 1В/окт, жесткую синхронизацию и линейную ЧМ."
    },
    hue: 0xf97316,
    accent: [1.00, 0.48, 0.10],
    lesson: {
      en: `${EN_BASE}/course/foundations-03-first-subtractive-patch/`,
      ru: `${RU_BASE}/course/foundations-03-first-subtractive-patch/`,
    },
    patch: {
      en: `${EN_BASE}/patches/foundations-basic-voice-v01/`,
      ru: `${RU_BASE}/patches/foundations-basic-voice-v01/`,
    },
  },
  FLT: {
    id: "FLT",
    name: { en: "Resonant Multimode Filter (VCF)", ru: "Резонансный мультирежимный фильтр (VCF)" },
    role: { en: "Harmonic Shaping & Timbral Sculpting", ru: "Спектральная и тембральная формовка" },
    desc: {
      en: "24dB/oct ladder filter topology with smooth nonlinear saturation, self-oscillating resonance, and bipolar CV modulation input for expressive sweeps.",
      ru: "Лестничный фильтр 24 дБ/окт с аналоговым насыщением, самовозбуждающимся резонансом и биполярной модуляцией среза для динамичных свитчей."
    },
    hue: 0x38bdf8,
    accent: [0.25, 0.72, 1.00],
    lesson: {
      en: `${EN_BASE}/course/foundations-03-first-subtractive-patch/`,
      ru: `${RU_BASE}/course/foundations-03-first-subtractive-patch/`,
    },
    patch: {
      en: `${EN_BASE}/patches/foundations-filter-sweep-study-v01/`,
      ru: `${RU_BASE}/patches/foundations-filter-sweep-study-v01/`,
    },
  },
  ENV: {
    id: "ENV",
    name: { en: "Dual ADSR Envelope Generator", ru: "Двойной генератор огибающих ADSR" },
    role: { en: "Dynamic Amplitude & Filter Modulation", ru: "Динамическая модуляция громкости и фильтра" },
    desc: {
      en: "Fast-response 4-stage envelope generator with exponential curves. Converts binary gate triggers into organic continuous modulation curves.",
      ru: "Четырехстадийный генератор огибающей с экспоненциальными кривыми. Превращает триггерные импульсы в плавные контуры громкости и тембра."
    },
    hue: 0xec4899,
    accent: [0.95, 0.22, 0.55],
    lesson: {
      en: `${EN_BASE}/course/foundations-04-envelopes-and-lfo/`,
      ru: `${RU_BASE}/course/foundations-04-envelopes-and-lfo/`,
    },
    patch: {
      en: `${EN_BASE}/patches/foundations-basic-voice-v01/`,
      ru: `${RU_BASE}/patches/foundations-basic-voice-v01/`,
    },
  },
  LFO: {
    id: "LFO",
    name: { en: "Dual Multi-Wave LFO", ru: "Двойной многоволновой LFO" },
    role: { en: "Slow Modulation & Cyclic Evolution", ru: "Медленная модуляция и циклические фазы" },
    desc: {
      en: "Ultra-wide range low frequency oscillator capable of producing subtle vibrato, pulsing tremolo, and slow evolving timbral drift across the rack.",
      ru: "Широкодиапазонный низкочастотный осциллятор для создания вибрато, тремоло и непрерывно эволюционирующих текстурных сдвигов."
    },
    hue: 0xa855f7,
    accent: [0.75, 0.35, 1.00],
    lesson: {
      en: `${EN_BASE}/course/foundations-04-envelopes-and-lfo/`,
      ru: `${RU_BASE}/course/foundations-04-envelopes-and-lfo/`,
    },
    patch: {
      en: `${EN_BASE}/patches/generative-generative-ambient-v01/`,
      ru: `${RU_BASE}/patches/generative-generative-ambient-v01/`,
    },
  },
  RND: {
    id: "RND",
    name: { en: "Sample & Hold / Random Generator", ru: "Sample & Hold и генератор случайности" },
    role: { en: "Generative Probability & Controlled Chaos", ru: "Генеративная вероятность и контролируемый хаос" },
    desc: {
      en: "Dual S&H with analog noise generator, slew limiter, and quantized random voltage outputs. The foundation of autonomous generative patches.",
      ru: "Блок Sample & Hold с генератором аналогового шума, сглаживанием (slew) и квантованными ступенями. Основа самогенерирующихся музыкальных патчей."
    },
    hue: 0xeab308,
    accent: [0.95, 0.85, 0.15],
    lesson: {
      en: `${EN_BASE}/course/generative-01-random-and-sample-hold/`,
      ru: `${RU_BASE}/course/generative-01-random-and-sample-hold/`,
    },
    patch: {
      en: `${EN_BASE}/patches/generative-probability-grid-v01/`,
      ru: `${RU_BASE}/patches/generative-probability-grid-v01/`,
    },
  },
  MIX: {
    id: "MIX",
    name: { en: "4-Channel Performance Mixer", ru: "4-канальный микшер и сумматор" },
    role: { en: "Audio Summing & Level Management", ru: "Сведение сигналов и управление балансом" },
    desc: {
      en: "Low-noise DC-coupled summing mixer with smooth linear faders, master level control, and headroom saturation for the hybrid Ableton Live bridge.",
      ru: "Малошумящий суммирующий микшер с линейными фейдерами, мастер-уровнем и мягким запасом по перегрузке для интеграции с Ableton Live."
    },
    hue: 0x22c55e,
    accent: [0.35, 1.00, 0.45],
    lesson: {
      en: `${EN_BASE}/course/hybrid-01-routing-vcv-into-ableton/`,
      ru: `${RU_BASE}/course/hybrid-01-routing-vcv-into-ableton/`,
    },
    patch: {
      en: `${EN_BASE}/patches/performances-hybrid-live-set-v01/`,
      ru: `${RU_BASE}/patches/performances-hybrid-live-set-v01/`,
    },
  },
  VIS: {
    id: "VIS",
    name: { en: "Visualizer & Scope Bridge", ru: "Осциллограф и визуальный мост" },
    role: { en: "Real-time Audiovisual Signal Analysis", ru: "Анализ аудиосигнала и визуальная реактивность" },
    desc: {
      en: "Dual-channel oscilloscope, FFT spectrum analyzer, and CV-to-visual mapping engine. Bridges audio signals into generative visual representations.",
      ru: "Двухканальный осциллограф, спектральный FFT-анализатор и модуль маппинга CV в генеративную 3D/2D графику."
    },
    hue: 0x06b6d4,
    accent: [0.20, 0.85, 1.00],
    lesson: {
      en: `${EN_BASE}/course/audiovisual-01-audio-reactive-visuals/`,
      ru: `${RU_BASE}/course/audiovisual-01-audio-reactive-visuals/`,
    },
    patch: {
      en: `${EN_BASE}/patches/performances-drone-performance-core-v01/`,
      ru: `${RU_BASE}/patches/performances-drone-performance-core-v01/`,
    },
  },
};

export const CONTROLS = {
  CLK: [
    { key: "RATE", title: { en: "Master Tempo", ru: "Основной темп" }, desc: { en: "Sets the master clock BPM and pulse rate.", ru: "Регулирует темп мастер-часов (BPM) и скорость генерации импульсов." } },
    { key: "DIV", title: { en: "Clock Divider", ru: "Делитель частоты" }, desc: { en: "Selects metric subdivisions (1/2, 1/4, 1/8, dotted).", ru: "Выбирает метрические доли (1/2, 1/4, 1/8, триоли)." } },
  ],
  VCO: [
    { key: "FREQ", title: { en: "Pitch / Coarse", ru: "Высота тона" }, desc: { en: "Main oscillator frequency. Accepts 1V/Oct CV.", ru: "Базовая частота генератора. Принимает управляющее напряжение 1В/Окт." } },
    { key: "FINE", title: { en: "Fine Detune", ru: "Микроподстройка" }, desc: { en: "Fine tuning for thick harmonic beating and chorusing.", ru: "Тонкая подстройка для создания жирного аналогового унисона." } },
    { key: "SHP", title: { en: "Wave Morph", ru: "Морфинг формы" }, desc: { en: "Continuous crossfade between Sine, Triangle, Saw, and Pulse.", ru: "Плавное перетекание между синусом, треугольником, пилой и импульсом." } },
  ],
  FLT: [
    { key: "CUT", title: { en: "Cutoff Frequency", ru: "Частота среза" }, desc: { en: "Filter cutoff point that shapes the harmonic spectrum.", ru: "Точка среза фильтра, определяющая яркость и характер тембра." } },
    { key: "RES", title: { en: "Resonance / Q", ru: "Резонанс (Q)" }, desc: { en: "Harmonic boost at the cutoff frequency.", ru: "Подъем частот на точке среза вплоть до автогенерации синусоиды." } },
    { key: "DRV", title: { en: "Drive & Saturate", ru: "Аналоговый драйв" }, desc: { en: "Warm input pre-filter saturation.", ru: "Мягкое аналоговое насыщение перед каскадом фильтрации." } },
  ],
  ENV: [
    { key: "A", title: { en: "Attack Time", ru: "Атака" }, desc: { en: "Rise time from silence to peak amplitude.", ru: "Время нарастания сигнала от тишины до максимального пика." } },
    { key: "D", title: { en: "Decay Time", ru: "Спад" }, desc: { en: "Time to drop from peak to sustain level.", ru: "Время перехода от пикового значения к уровню поддержки." } },
    { key: "S", title: { en: "Sustain Level", ru: "Поддержка" }, desc: { en: "Held level while gate is active.", ru: "Громкость звука, пока удерживается клавиша или гейт-сигнал." } },
    { key: "R", title: { en: "Release Time", ru: "Затухание" }, desc: { en: "Fade-out time after gate release.", ru: "Длительность плавного затухания звука после отпускания гейта." } },
  ],
  LFO: [
    { key: "RATE", title: { en: "LFO Speed", ru: "Скорость LFO" }, desc: { en: "Modulation cycle frequency (0.05 Hz to 40 Hz).", ru: "Частота цикла модуляции (от сверхмедленного до слышимого)." } },
    { key: "SHP", title: { en: "Waveform", ru: "Форма LFO" }, desc: { en: "Triangle, Ramp, or Square modulation wave.", ru: "Выбор модулирующей волны: треугольник, пила или прямоугольник." } },
  ],
  RND: [
    { key: "RATE", title: { en: "Sample Clock", ru: "Частота сэмплирования" }, desc: { en: "Clock rate for generating new discrete random voltages.", ru: "Частота генерации новых случайных значений напряжения." } },
    { key: "SPR", title: { en: "Spread / Slew", ru: "Сглаживание и диапазон" }, desc: { en: "Voltage range spread and slew portamento.", ru: "Ширина диапазона напряжений и время плавного скольжения (slew)." } },
  ],
  MIX: [
    { key: "LVL", title: { en: "Master Output Level", ru: "Мастер-громкость" }, desc: { en: "Final stereo mix gain to monitoring and DAW.", ru: "Итоговый уровень громкости мастер-шины." } },
  ],
  VIS: [
    { key: "GAIN", title: { en: "Input Sensitivity", ru: "Чувствительность" }, desc: { en: "Input amplitude multiplier for the visualizer.", ru: "Коэффициент усиления входящего сигнала для визуализации." } },
    { key: "SMOOTH", title: { en: "Scope Persistence", ru: "Сглаживание осциллографа" }, desc: { en: "Visual decay and phosphor trail length.", ru: "Инерция и длина светового следа на экране осциллографа." } },
  ],
};

export const FADERS = {
  MIX: [
    { key: "CH1", title: { en: "Ch 1: VCO Direct", ru: "Кан 1: Осциллятор" }, desc: { en: "Direct raw analog oscillator level.", ru: "Уровень прямого сигнала с осциллятора." } },
    { key: "CH2", title: { en: "Ch 2: Sub Voice", ru: "Кан 2: Суб-бас" }, desc: { en: "Sub-octave bass foundation.", ru: "Уровень суб-октавного басового слоя." } },
    { key: "CH3", title: { en: "Ch 3: Filtered Bus", ru: "Кан 3: Фильтрованный сигнал" }, desc: { en: "Resonant ladder filter output.", ru: "Уровень обработанного лестничным фильтром сигнала." } },
    { key: "CH4", title: { en: "Ch 4: Texture / Noise", ru: "Кан 4: Текстура и шум" }, desc: { en: "Generative noise and modulation return.", ru: "Уровень генеративных текстур и возврата эффектов." } },
  ],
};

export function moduleIdFromObject(obj) {
  let curr = obj;
  while (curr) {
    const match = /(?:Module|FaceM|Panel)_([A-Z]+)/i.exec(curr.name || "");
    if (match && MODULES[match[1].toUpperCase()]) {
      return match[1].toUpperCase();
    }
    curr = curr.parent;
  }
  return null;
}
