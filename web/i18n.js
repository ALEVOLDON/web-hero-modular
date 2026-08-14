const copy = {
  en: {
    lang: "en",
    title: "Modular Genesis",
    description:
      "An open project on modular synthesis, generative systems, and a hybrid VCV Rack + Ableton Live pipeline.",
    navCourse: "Course",
    navPatches: "Patches",
    navGithub: "GitHub",
    hrefCourse: "https://alevoldon.github.io/Modular-Genesis/course",
    hrefPatches: "https://alevoldon.github.io/Modular-Genesis/patches",
    hrefPlan: "https://alevoldon.github.io/Modular-Genesis/roadmap",
    eyebrow: "VCV Rack · Ableton Live · Audiovisual",
    lede:
      "An open portal on modular synthesis and generative music. Lessons, patches, and the hybrid pipeline are built as one system — from a signal in VCV to the visual layer.",
    ctaCourse: "Browse the course",
    ctaPlan: "Open the roadmap",
    meta: "Move the cursor · the case turns",
    metaLook: "Move the cursor · the case turns",
    metaLearn: "Hover a knob or module · read the patch",
    modeLook: "Look",
    modeLearn: "Learn",
    shotOverview: "Overview",
    shotKnobs: "Knobs",
    shotCables: "Cables",
    shotInto: "Into",
    audioPatch: "Patch",
    audioMic: "Mic",
    audioMute: "Mute",
    bootLoad: "Compiling the patch…",
    bootReady: "Patch compiled",
    bootEnter: "Enter the lab",
    boot3d: "Launch 3D",
    tipLesson: "Open lesson",
    tipPatch: "Open patch",
    CLK_name: "CLK",
    CLK_title: "Clock & sequencer",
    CLK_lede: "Clock, reset, trigger, and gate — the spine of a generative system.",
    VCO_name: "VCO",
    VCO_title: "Oscillator",
    VCO_lede: "First subtractive voice. Frequency, shape, and 1V/oct into the filter.",
    FLT_name: "VCF",
    FLT_title: "Filter",
    FLT_lede: "Cutoff, resonance, and FM. The place where a drone becomes a phrase.",
    ENV_name: "ENV",
    ENV_title: "Envelope",
    ENV_lede: "Attack, decay, sustain, release — shape the gate into motion.",
    LFO_name: "LFO",
    LFO_title: "Low-frequency oscillator",
    LFO_lede: "Slow modulation. Triangle and square into anything that can listen.",
    RND_name: "S&H",
    RND_title: "Random & sample-and-hold",
    RND_lede: "Probability and mutation. The patch starts to write itself.",
    MIX_name: "MIX",
    MIX_title: "Mix & hybrid out",
    MIX_lede: "Sum the voices, then hand the bus to Ableton Live.",
    VIS_name: "VIS",
    VIS_title: "Audiovisual",
    VIS_lede: "Audio in, graphics out. The same signal that you hear moves the scene.",
  },
  ru: {
    lang: "ru",
    title: "Modular Genesis",
    description:
      "Открытый проект о модульном синтезе, generative-системах и гибридном пайплайне VCV Rack + Ableton Live.",
    navCourse: "Курс",
    navPatches: "Патчи",
    navGithub: "GitHub",
    hrefCourse: "https://alevoldon.github.io/Modular-Genesis/ru/course",
    hrefPatches: "https://alevoldon.github.io/Modular-Genesis/ru/patches",
    hrefPlan: "https://alevoldon.github.io/Modular-Genesis/ru/roadmap",
    eyebrow: "VCV Rack · Ableton Live · Audiovisual",
    lede:
      "Открытый портал о модульном синтезе и generative-музыке. Уроки, патчи и гибридный пайплайн собираются как одна система — от сигнала в VCV до визуального слоя.",
    ctaCourse: "Смотреть курс",
    ctaPlan: "Открыть план",
    meta: "Веди курсор · кейс поворачивается",
    metaLook: "Веди курсор · кейс поворачивается",
    metaLearn: "Наведи на ручку или модуль · читай патч",
    modeLook: "Обзор",
    modeLearn: "Урок",
    shotOverview: "Общий",
    shotKnobs: "Ручки",
    shotCables: "Кабели",
    shotInto: "В рэк",
    audioPatch: "Патч",
    audioMic: "Микрофон",
    audioMute: "Тихо",
    bootLoad: "Собираю патч…",
    bootReady: "Патч собран",
    bootEnter: "Войти в лабораторию",
    boot3d: "Запустить 3D",
    tipLesson: "Открыть урок",
    tipPatch: "Открыть патч",
    CLK_name: "CLK",
    CLK_title: "Часы и секвенсор",
    CLK_lede: "Clock, reset, trigger и gate — позвоночник generative-системы.",
    VCO_name: "VCO",
    VCO_title: "Осциллятор",
    VCO_lede: "Первый субтрактивный голос. Частота, форма и 1V/oct в фильтр.",
    FLT_name: "VCF",
    FLT_title: "Фильтр",
    FLT_lede: "Cutoff, резонанс и FM. Здесь дрон становится фразой.",
    ENV_name: "ENV",
    ENV_title: "Огибающая",
    ENV_lede: "Attack, decay, sustain, release — из гейта получается движение.",
    LFO_name: "LFO",
    LFO_title: "Низкочастотный осциллятор",
    LFO_lede: "Медленная модуляция. Треугольник и квадрат в любой вход.",
    RND_name: "S&H",
    RND_title: "Random и sample-and-hold",
    RND_lede: "Вероятность и мутация. Патч начинает писать сам себя.",
    MIX_name: "MIX",
    MIX_title: "Микс и hybrid out",
    MIX_lede: "Свести голоса и отдать шину в Ableton Live.",
    VIS_name: "VIS",
    VIS_title: "Audiovisual",
    VIS_lede: "Звук на входе, графика на выходе. Тот же сигнал двигает сцену.",
  },
};

export function currentLang() {
  const fromUrl = new URLSearchParams(location.search).get("lang");
  if (fromUrl === "ru" || fromUrl === "en") return fromUrl;
  const saved = localStorage.getItem("mg-lang");
  if (saved === "ru" || saved === "en") return saved;
  return "en";
}

export function t(key, lang = currentLang()) {
  const pack = copy[lang] || copy.en;
  return pack[key] ?? copy.en[key] ?? key;
}

export function applyLang(lang) {
  const pack = copy[lang] || copy.en;
  document.documentElement.lang = pack.lang;
  document.title = pack.title;
  const desc = document.querySelector('meta[name="description"]');
  if (desc) desc.setAttribute("content", pack.description);

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n;
    if (pack[key] != null) el.textContent = pack[key];
  });
  document.querySelectorAll("[data-i18n-href]").forEach((el) => {
    const key = el.dataset.i18nHref;
    if (pack[key] != null) el.setAttribute("href", pack[key]);
  });

  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.setAttribute("aria-current", btn.dataset.lang === lang ? "true" : "false");
  });

  localStorage.setItem("mg-lang", lang);
  const url = new URL(location.href);
  url.searchParams.set("lang", lang);
  history.replaceState(null, "", url);
  document.dispatchEvent(new CustomEvent("mg-lang", { detail: lang }));
}

function boot() {
  applyLang(currentLang());
  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.addEventListener("click", () => applyLang(btn.dataset.lang));
  });
}

boot();
