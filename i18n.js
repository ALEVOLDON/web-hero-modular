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
    meta: "Move the cursor · live scene",
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
    meta: "Наведи курсор · сцена живая",
  },
};

function currentLang() {
  const fromUrl = new URLSearchParams(location.search).get("lang");
  if (fromUrl === "ru" || fromUrl === "en") return fromUrl;
  const saved = localStorage.getItem("mg-lang");
  if (saved === "ru" || saved === "en") return saved;
  return "en";
}

export function applyLang(lang) {
  const t = copy[lang] || copy.en;
  document.documentElement.lang = t.lang;
  document.title = t.title;
  const desc = document.querySelector('meta[name="description"]');
  if (desc) desc.setAttribute("content", t.description);

  const set = (sel, value, attr) => {
    const el = document.querySelector(sel);
    if (!el) return;
    if (attr) el.setAttribute(attr, value);
    else el.textContent = value;
  };

  set("[data-i18n=navCourse]", t.navCourse);
  set("[data-i18n=navPatches]", t.navPatches);
  set("[data-i18n=navGithub]", t.navGithub);
  set("[data-i18n=navCourse]", t.hrefCourse, "href");
  set("[data-i18n=navPatches]", t.hrefPatches, "href");
  set("[data-i18n=eyebrow]", t.eyebrow);
  set("[data-i18n=lede]", t.lede);
  set("[data-i18n=ctaCourse]", t.ctaCourse);
  set("[data-i18n=ctaCourse]", t.hrefCourse, "href");
  set("[data-i18n=ctaPlan]", t.ctaPlan);
  set("[data-i18n=ctaPlan]", t.hrefPlan, "href");
  set("[data-i18n=meta]", t.meta);

  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.setAttribute("aria-current", btn.dataset.lang === lang ? "true" : "false");
  });

  localStorage.setItem("mg-lang", lang);
  const url = new URL(location.href);
  url.searchParams.set("lang", lang);
  history.replaceState(null, "", url);
}

function boot() {
  applyLang(currentLang());
  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.addEventListener("click", () => applyLang(btn.dataset.lang));
  });
}

boot();
