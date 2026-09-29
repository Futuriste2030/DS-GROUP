/* BS GROUP — main script (vanilla JS) */

/* Helpers globaux — DOIVENT rester au top-level (hors DOMContentLoaded) :
   des blocs autonomes (wizard devis, partage, upload...) appellent S() et
   showToast() depuis leurs propres scopes. */
// i18n — même logique que DIGI-AGENCY : la langue vient de <html lang>
// (FR sans préfixe / EN /en/ / AR /ar/) et les chaînes traduites sont
// injectées par Django dans window.BSG_STRINGS (partials/_js_i18n.html).
const BSG_LANG = (document.documentElement.lang || "fr")
  .slice(0, 2)
  .toLowerCase();
const BSG_LOCALE =
  { fr: "fr-FR", en: "en-US", ar: "ar-MA" }[BSG_LANG] || "fr-FR";
const BSG_STRINGS = window.BSG_STRINGS || {};
const S = (key, fb) => {
  const v = BSG_STRINGS[key];
  return v === undefined || v === null || v === "" ? fb : v;
};

const showToast = (message) => {
  const toast = document.createElement("div");
  toast.className = "toast-success";
  toast.setAttribute("role", "status");
  toast.innerHTML =
    '<svg viewBox="0 0 24 24" fill="none" stroke="#c9a227" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5 shrink-0"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>' +
    "<span></span>";
  toast.querySelector("span").textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("hide");
    setTimeout(() => toast.remove(), 450);
  }, 3600);
};

document.addEventListener("DOMContentLoaded", () => {
  /* Constante vidéo partagée (Hero + Why Choose Us + Video Showcase) */
  // ⚠️ Remplacer par l'URL de votre vidéo (MP4) —
  // pour YouTube : remplacer le <video> du HTML par une <iframe> embed.
  const VIDEO_SRC =
    "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4";

  // 0. Preloader — progression simulée + évènement load
  const preloader = document.getElementById("preloader");
  const preBar = document.getElementById("preloader-bar");
  const prePercent = document.getElementById("preloader-percent");
  const preLabel = document.getElementById("preloader-label");
  const preHook = document.getElementById("preloader-hook");

  if (preloader && preBar) {
    document.body.classList.add("is-loading");

    const stageLabels = [
      S("preloader0", "Laying the foundation..."), // 0 – 33 %
      S("preloader1", "Raising the structure..."), // 34 – 66 %
      S("preloader2", "Adding final touches..."), // 67 – 100 %
    ];

    let preProgress = 0;
    let pageLoaded = document.readyState === "complete";
    let preloaderDone = false;

    if (!pageLoaded) {
      window.addEventListener("load", () => {
        pageLoaded = true;
      });
    }

    // Filet de sécurité : ne jamais bloquer plus de 6 s
    setTimeout(() => {
      pageLoaded = true;
    }, 6000);

    const renderPreloader = () => {
      const p = Math.round(preProgress);
      preBar.style.width = p + "%";
      prePercent.textContent = p + "%";
      preLabel.textContent =
        stageLabels[Math.min(Math.floor(p / 34), stageLabels.length - 1)];
      if (preHook) preHook.style.transform = `translateY(-${p * 0.35}px)`;
    };

    const finishPreloader = () => {
      if (preloaderDone) return;
      preloaderDone = true;

      setTimeout(() => {
        preloader.classList.add("done");
        document.body.classList.remove("is-loading");
        setTimeout(() => preloader.remove(), 800);
      }, 350);
    };

    const preloaderTick = setInterval(() => {
      const ceiling = pageLoaded ? 100 : 90;
      preProgress = Math.min(preProgress + Math.random() * 8 + 3, ceiling);
      renderPreloader();

      if (preProgress >= 100) {
        clearInterval(preloaderTick);
        finishPreloader();
      }
    }, 120);
  }

  // 1. Initialisation des icônes Lucide
  if (window.lucide) {
    lucide.createIcons();
  }

  // 2. Sélecteur de langue (FR sans préfixe / EN /en/ / AR /ar/) — style DIGI-AGENCY
  const LANG_PREFIXES = ["en", "ar"]; // fr = défaut sans préfixe
  const langBtn = document.getElementById("lang-btn");
  const langMenu = document.getElementById("lang-menu");
  const langCurrent = document.getElementById("lang-current");

  const getLangFromPath = () => {
    const seg = window.location.pathname.split("/").filter(Boolean)[0];
    return LANG_PREFIXES.includes(seg) ? seg : "fr";
  };

  const buildPathForLang = (lang) => {
    const { pathname, search, hash } = window.location;
    // Strip préfixe existant (/en ou /ar)
    const stripped = pathname.replace(/^\/(en|ar)(?=\/|$)/, "") || "/";
    if (lang === "fr") return stripped + search + hash; // défaut sans préfixe
    const clean = stripped.startsWith("/") ? stripped : "/" + stripped;
    return "/" + lang + (clean === "/" ? "/" : clean) + search + hash;
  };

  const paintLang = (lang) => {
    if (langCurrent) langCurrent.textContent = lang.toUpperCase();
    document.documentElement.setAttribute("lang", lang);
    if (langMenu) {
      langMenu
        .querySelectorAll(".lang-option")
        .forEach((o) =>
          o.classList.toggle("lang-option--active", o.dataset.lang === lang),
        );
    }
  };

  if (langBtn && langMenu) {
    paintLang(getLangFromPath());

    langBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      langMenu.classList.toggle("hidden");
    });

    langMenu.querySelectorAll(".lang-option").forEach((option) => {
      option.addEventListener("click", () => {
        const lang = option.dataset.lang;
        paintLang(lang);
        langMenu.classList.add("hidden");
        const target = buildPathForLang(lang);
        if (target !== window.location.pathname + window.location.search + window.location.hash) {
          window.location.href = target;
        }
      });
    });

    document.addEventListener("click", () => langMenu.classList.add("hidden"));
  }

  // 3. Menu mobile
  const menuBtn = document.getElementById("mobile-menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      mobileMenu.classList.toggle("hidden");
    });

    mobileMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => mobileMenu.classList.add("hidden"));
    });

    document.addEventListener("click", () =>
      mobileMenu.classList.add("hidden"),
    );

    // 3b. Menu mobile — accordéons (fermés par défaut, ouverture au clic)
    mobileMenu.querySelectorAll("[data-mobile-toggle]").forEach((toggle) => {
      toggle.addEventListener("click", (e) => {
        e.stopPropagation(); // ne pas refermer tout le menu
        const item = toggle.closest("[data-mobile-dropdown]");
        if (!item) return;
        const submenu = item.querySelector(".mobile-submenu");
        const isOpen = item.classList.toggle("dropdown-open");
        toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        if (submenu) submenu.classList.toggle("hidden", !isOpen);
      });
    });
  }

  // 3c. Navigation desktop — parents déroulants (boutons sans href, ouverture au clic)
  const dropdownToggles = document.querySelectorAll("[data-dropdown-toggle]");

  if (dropdownToggles.length) {
    dropdownToggles.forEach((toggle) => {
      toggle.addEventListener("click", (e) => {
        e.stopPropagation();
        const item = toggle.closest("li.relative.group");
        if (!item) return;
        const wasOpen = item.classList.contains("dropdown-open");
        // un seul déroulant ouvert à la fois
        document
          .querySelectorAll("li.relative.group.dropdown-open")
          .forEach((i) => {
            i.classList.remove("dropdown-open");
            const t = i.querySelector("[data-dropdown-toggle]");
            if (t) t.setAttribute("aria-expanded", "false");
          });
        if (!wasOpen) {
          item.classList.add("dropdown-open");
          toggle.setAttribute("aria-expanded", "true");
        }
      });
    });

    document.addEventListener("click", () => {
      document
        .querySelectorAll("li.relative.group.dropdown-open")
        .forEach((i) => {
          i.classList.remove("dropdown-open");
          const t = i.querySelector("[data-dropdown-toggle]");
          if (t) t.setAttribute("aria-expanded", "false");
        });
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        document
          .querySelectorAll("li.relative.group.dropdown-open")
          .forEach((i) => {
            i.classList.remove("dropdown-open");
            const t = i.querySelector("[data-dropdown-toggle]");
            if (t) t.setAttribute("aria-expanded", "false");
          });
      }
    });
  }

  // 4. Modal vidéo — URL admin (data-video-url, cf. DIGI-AGENCY), MP4 ou YouTube
  const playBtn = document.getElementById("video-play-btn");
  const plansBtn = document.getElementById("plans-play-btn");
  const modal = document.getElementById("video-modal");
  const backdrop = document.getElementById("video-modal-backdrop");
  const closeBtn = document.getElementById("video-modal-close");
  const video = document.getElementById("video-player");
  const videoFrame = document.getElementById("video-iframe");

  const toYouTubeEmbed = (url) => {
    if (!url) return null;
    let m = url.match(/[?&]v=([A-Za-z0-9_-]{6,})/);
    if (!m) m = url.match(/youtu\.be\/([A-Za-z0-9_-]{6,})/);
    if (!m) m = url.match(/\/embed\/([A-Za-z0-9_-]{6,})/);
    if (!m) m = url.match(/\/shorts\/([A-Za-z0-9_-]{6,})/);
    return m ? "https://www.youtube.com/embed/" + m[1] : null;
  };

  const openModal = (bannerUrl) => {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    document.body.style.overflow = "hidden";
    // Priorité : URL de la bannière cliquée (pages détail) > URL modale > démo.
    const given = typeof bannerUrl === "string" ? bannerUrl : "";
    const adminUrl =
      given.trim() ||
      (modal.dataset.videoUrl || "").trim() ||
      VIDEO_SRC;
    const embed = toYouTubeEmbed(adminUrl);
    if (embed && videoFrame) {
      if (video) {
        video.pause();
        video.removeAttribute("src");
        video.classList.add("hidden");
      }
      videoFrame.classList.remove("hidden");
      videoFrame.src = embed + "?autoplay=1&rel=0";
    } else if (video) {
      if (videoFrame) {
        videoFrame.removeAttribute("src");
        videoFrame.classList.add("hidden");
      }
      video.classList.remove("hidden");
      if (!video.src) video.src = adminUrl;
      video.play().catch(() => {});
    }
    closeBtn.focus();
  };

  const closeModal = () => {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    document.body.style.overflow = "";
    if (video) video.pause();
    if (videoFrame) videoFrame.removeAttribute("src");
  };

  if (modal) {
    if (playBtn) playBtn.addEventListener("click", () => openModal());
    if (plansBtn) plansBtn.addEventListener("click", () => openModal());
    // Déclencheurs génériques (bannières vidéo des pages détail, cf. DIGI-AGENCY) :
    // le clic sur la bannière (ou son bouton play) ouvre la modale avec son URL.
    document.querySelectorAll("[data-video-banner]").forEach((banner) => {
      if (banner === modal) return;
      banner.addEventListener("click", () =>
        openModal(banner.dataset.videoUrl || ""),
      );
    });
    closeBtn.addEventListener("click", closeModal);
    backdrop.addEventListener("click", closeModal);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !modal.classList.contains("hidden"))
        closeModal();
    });
  }

  // 5. Compteurs animés des statistiques
  const counters = document.querySelectorAll("[data-count]");

  const animateCounter = (el) => {
    const target = parseInt(el.dataset.count, 10);
    const suffix = el.dataset.suffix || "";
    const duration = 1600;
    const start = performance.now();

    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      el.textContent = Math.round(target * eased) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  if ("IntersectionObserver" in window && counters.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.4 },
    );

    counters.forEach((counter) => io.observe(counter));
  }

  // 6. Section About — slider Mission / Vision (depuis les data-attributes
  // renseignés par Django/SiteSettings ; jamais de contenu démo en prod)
  const aboutContentEl = document.getElementById("about-slide-content");
  const aboutSlides = [
    {
      label: (aboutContentEl?.dataset.missionTitle || "").trim(),
      text: (aboutContentEl?.dataset.missionText || "").trim(),
    },
    {
      label: (aboutContentEl?.dataset.visionTitle || "").trim(),
      text: (aboutContentEl?.dataset.visionText || "").trim(),
    },
  ].filter((s) => s.text !== "");

  let aboutIndex = 0;
  const aboutTextEl = document.getElementById("about-slide-text");
  const aboutLabelEl = document.getElementById("about-slide-label");
  const aboutPrevBtn = document.getElementById("about-prev");
  const aboutNextBtn = document.getElementById("about-next");
  const aboutSliderCard = document.getElementById("about-slider-card");

  // Sans contenu réel (SiteSettings vide) : on masque le slider, pas de démo.
  if (aboutSlides.length === 0) {
    aboutSliderCard?.classList.add("hidden");
  } else if (aboutSlides.length === 1) {
    aboutPrevBtn?.classList.add("hidden");
    aboutNextBtn?.classList.add("hidden");
  }

  const showAboutSlide = (index) => {
    aboutIndex = (index + aboutSlides.length) % aboutSlides.length;
    aboutContentEl.classList.add("about-fade-out");

    setTimeout(() => {
      aboutTextEl.textContent = aboutSlides[aboutIndex].text;
      aboutLabelEl.textContent = aboutSlides[aboutIndex].label;
      aboutContentEl.classList.remove("about-fade-out");
    }, 250);
  };

  if (aboutContentEl && aboutPrevBtn && aboutNextBtn && aboutSlides.length) {
    aboutPrevBtn.addEventListener("click", () =>
      showAboutSlide(aboutIndex - 1),
    );
    aboutNextBtn.addEventListener("click", () =>
      showAboutSlide(aboutIndex + 1),
    );
  }

  // 7. Section Services — gestion de la carte active
  const serviceCards = document.querySelectorAll("[data-service-card]");

  const activateService = (card) => {
    serviceCards.forEach((c) => c.classList.remove("active"));
    card.classList.add("active");
  };

  if (serviceCards.length) {
    serviceCards.forEach((card) => {
      card.addEventListener("mouseenter", () => activateService(card));
      card.addEventListener("click", () => activateService(card));
      card.addEventListener("focusin", () => activateService(card));
    });
  }

  // 8. Section Process — étape active
  const processSteps = document.querySelectorAll("[data-process-step]");

  const activateStep = (step) => {
    processSteps.forEach((s) => s.classList.remove("active"));
    step.classList.add("active");
  };

  if (processSteps.length) {
    processSteps.forEach((step) => {
      step.addEventListener("click", () => activateStep(step));
      step.addEventListener("mouseenter", () => activateStep(step));
    });
  }

  // 9. Section Projects — apparition des cartes au scroll
  const projectCards = document.querySelectorAll(".project-card");

  if ("IntersectionObserver" in window && projectCards.length) {
    const projectIO = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("project-visible");
            projectIO.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 },
    );

    projectCards.forEach((card, i) => {
      card.style.transitionDelay = `${i * 120}ms`;
      projectIO.observe(card);
    });
  } else {
    projectCards.forEach((card) => card.classList.add("project-visible"));
  }

  // 10. Why Choose Us — bouton play (réutilise la modal partagée)
  const whyPlayBtn = document.getElementById("why-play-btn");

  if (whyPlayBtn && modal && video) {
    whyPlayBtn.addEventListener("click", () => openModal());
  }

  // 11. Contact — validation du formulaire + toast
  const setFieldError = (input, msg) => {
    const errorEl = input.parentElement.querySelector(".error-msg");
    if (msg) {
      input.classList.add("input-error");
      if (errorEl) {
        errorEl.textContent = msg;
        errorEl.classList.remove("hidden");
      }
    } else {
      input.classList.remove("input-error");
      if (errorEl) errorEl.classList.add("hidden");
    }
  };

  const contactForm = document.getElementById("contact-form");

  if (contactForm) {
    contactForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      let isValid = true;
      const inputs = contactForm.querySelectorAll(".form-input");

      inputs.forEach((input) => {
        const value = input.value.trim();
        let msg = "";

        if (!value) {
          msg = S("formRequired", "This field is required.");
        } else if (input.type === "email" && !/^\S+@\S+\.\S+$/.test(value)) {
          msg = S("formEmail", "Please enter a valid email address.");
        } else if (
          input.dataset.type === "phone" &&
          value.replace(/\D/g, "").length < 7
        ) {
          msg = S("formPhone", "Please enter a valid phone number.");
        }

        setFieldError(input, msg);
        if (msg) isValid = false;
      });

      if (!isValid) return;

      // POST réel backend → redirect serveur thanks/<reference>
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const originalLabel = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = S("sending", "Sending...");
      try {
        const data = new FormData(contactForm);
        const res = await fetch(contactForm.action || window.location.pathname, { method: "POST", body: data });
        if (res.redirected) { window.location.href = res.url; return; }
        if (res.ok) { window.location.href = "/thanks/"; return; }
      } catch (e) {}
      submitBtn.disabled = false;
      submitBtn.textContent = originalLabel;
      showToast(S("contactSent", "Message sent successfully! We'll get back to you soon."));
    });

    contactForm.querySelectorAll(".form-input").forEach((input) => {
      input.addEventListener("input", () => setFieldError(input, ""));
    });
  }

  // 12. Section Team — membre actif
  const teamCards = document.querySelectorAll("[data-team-card]");

  const activateTeamMember = (card) => {
    teamCards.forEach((c) => c.classList.remove("active"));
    card.classList.add("active");
  };

  if (teamCards.length) {
    teamCards.forEach((card) => {
      card.addEventListener("mouseenter", () => activateTeamMember(card));
      card.addEventListener("click", () => activateTeamMember(card));
      card.addEventListener("focusin", () => activateTeamMember(card));
    });
  }

  // 13. Section Testimonials — carrousel avec dots
  // Données réelles via json_script (vue index) ; section masquée si vide.
  // Aucun contenu démo en production.
  const testimonialsData = (() => {
    try {
      const el = document.getElementById("testimonials-data");
      const parsed = el ? JSON.parse(el.textContent) : [];
      return Array.isArray(parsed) ? parsed.filter((t) => t && t.text) : [];
    } catch (e) {
      return [];
    }
  })();

  const testiTrack = document.getElementById("testi-track");
  const testiDots = document.getElementById("testi-dots");
  const testiSection = document.getElementById("testimonials");

  if (testiTrack && testiDots && testimonialsData.length) {
    const starIcon = '<i data-lucide="star" class="w-4 h-4 fill-current"></i>';

    const esc = (v) =>
      String(v ?? "").replace(/[&<>"']/g, (c) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[c]);

    const avatarHTML = (t) => {
      if (t.avatar) {
        return `<img src="${esc(t.avatar)}" alt="${esc(t.name)}" class="w-11 h-11 rounded-full object-cover ring-2 ring-white/15" loading="lazy" />`;
      }
      const initials = String(t.name || "?")
        .split(/\s+/)
        .map((w) => w[0])
        .join("")
        .slice(0, 2)
        .toUpperCase();
      return `<span class="w-11 h-11 rounded-full bg-[#c9a227] text-white font-black flex items-center justify-center ring-2 ring-white/15" aria-hidden="true">${esc(initials)}</span>`;
    };

    const cardHTML = (t) => {
      const rating = Number(t.rating) || 0;
      return `
      <article class="bg-white/[0.06] rounded-[20px] p-6 md:p-7 hover:bg-white/[0.09] transition-colors h-full">
        <div class="flex items-center gap-2.5">
          <span class="flex items-center gap-0.5 text-[#c9a227]">${starIcon.repeat(Math.max(0, Math.min(5, Math.round(rating))))}</span>
          <span class="text-white font-bold text-sm">${rating.toFixed(1)}</span>
        </div>
        <h3 class="mt-3.5 text-white font-extrabold text-[17px]">${esc(t.title)}</h3>
        <p class="mt-2.5 text-[13px] text-slate-400 leading-relaxed">${esc(t.text)}</p>
        <div class="mt-6 flex items-center gap-3.5">
          ${avatarHTML(t)}
          <div>
            <p class="text-white font-bold text-sm">${esc(t.name)}</p>
            <p class="text-[11px] text-slate-400">${esc(t.role)}</p>
          </div>
        </div>
      </article>`;
    };

    const pageCount = Math.ceil(testimonialsData.length / 2);
    for (let p = 0; p < pageCount; p++) {
      const page = document.createElement("div");
      page.className =
        "w-full shrink-0 grid grid-cols-1 md:grid-cols-2 gap-6 px-0.5";
      page.innerHTML = testimonialsData
        .slice(p * 2, p * 2 + 2)
        .map(cardHTML)
        .join("");
      testiTrack.appendChild(page);
    }

    const dots = [];
    for (let p = 0; p < pageCount; p++) {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.setAttribute("role", "tab");
      dot.setAttribute("aria-label", `Page ${p + 1}`);
      dot.addEventListener("click", () => {
        goToTestiPage(p);
        restartAutoplay();
      });
      testiDots.appendChild(dot);
      dots.push(dot);
    }

    let testiIndex = 0;
    const goToTestiPage = (index) => {
      testiIndex = (index + pageCount) % pageCount;
      testiTrack.style.transform = `translateX(-${testiIndex * 100}%)`;
      dots.forEach((d, i) => d.classList.toggle("active", i === testiIndex));
    };

    let autoplayId = null;
    const startAutoplay = () => {
      autoplayId = setInterval(() => goToTestiPage(testiIndex + 1), 5000);
    };
    const stopAutoplay = () => {
      clearInterval(autoplayId);
    };
    const restartAutoplay = () => {
      stopAutoplay();
      startAutoplay();
    };

    if (testiSection) {
      testiSection.addEventListener("mouseenter", stopAutoplay);
      testiSection.addEventListener("mouseleave", startAutoplay);
    }

    goToTestiPage(0);
    startAutoplay();
    if (window.lucide) lucide.createIcons();
  }

  // 14. Section Blogs — carte active
  const blogCards = document.querySelectorAll("[data-blog-card]");

  const activateBlog = (card) => {
    blogCards.forEach((c) => c.classList.remove("active"));
    card.classList.add("active");
  };

  if (blogCards.length) {
    blogCards.forEach((card) => {
      card.addEventListener("mouseenter", () => activateBlog(card));
      card.addEventListener("click", () => activateBlog(card));
    });
  }

  // 15. Section FAQ — accordéon (un seul ouvert)
  const faqItems = document.querySelectorAll("[data-faq]");

  if (faqItems.length) {
    faqItems.forEach((item) => {
      const btn = item.querySelector(".faq-question");
      if (!btn) return;

      btn.addEventListener("click", () => {
        const wasOpen = item.classList.contains("open");
        faqItems.forEach((i) => i.classList.remove("open"));
        if (!wasOpen) item.classList.add("open");
      });
    });
  }

  // 16. Newsletters (section + footer) — POST backend + toast (design intact)
  const postForm = (form) => {
    const data = new FormData(form);
    const action = form.getAttribute("action") || "/newsletter/";
    fetch(action, { method: "POST", body: data, headers: { "X-Requested-With": "XMLHttpRequest" } }).catch(() => {});
  };
  const handleNewsletter = (formId, inputId, successMsg) => {
    const form = document.getElementById(formId);
    const input = document.getElementById(inputId);
    if (!form || !input) return;

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const value = input.value.trim();

      if (!value || !/^\S+@\S+\.\S+$/.test(value)) {
        form.classList.add("newsletter-error");
        input.focus();
        setTimeout(() => form.classList.remove("newsletter-error"), 600);
        return;
      }

      postForm(form);
      input.value = "";
      showToast(
        successMsg ||
          S("newsletterDone", "Subscribed successfully! Welcome to our newsletter."),
      );
    });
  };

  handleNewsletter(
    "newsletter-form",
    "newsletter-email",
    S("newsletterDone", "Subscribed successfully! Welcome to our newsletter."),
  );
  handleNewsletter(
    "footer-newsletter-form",
    "footer-newsletter-email",
    S("newsletterDone", "Subscribed successfully! Welcome to our newsletter."),
  );
  handleNewsletter(
    "notify-form",
    "notify-email",
    S("notifyDone", "Thanks! We will notify you at launch."),
  );

  // 17. Back to Top — anneau de progression + scroll fluide
  const backToTop = document.getElementById("back-to-top");
  const bttProgress = document.getElementById("btt-progress");
  const BTT_CIRCUMFERENCE = 2 * Math.PI * 22; // ≈ 138.23 (r = 22)

  if (backToTop) {
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;

    const updateBackToTop = () => {
      const scrollTop = window.scrollY;
      const docHeight =
        document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? Math.min(scrollTop / docHeight, 1) : 0;

      if (bttProgress) {
        bttProgress.style.strokeDashoffset = BTT_CIRCUMFERENCE * (1 - progress);
      }

      backToTop.classList.toggle("visible", scrollTop > 400);
    };

    backToTop.addEventListener("click", () => {
      window.scrollTo({
        top: 0,
        behavior: prefersReducedMotion ? "auto" : "smooth",
      });
    });

    window.addEventListener("scroll", updateBackToTop, { passive: true });
    window.addEventListener("resize", updateBackToTop);
    updateBackToTop();
  }

  // 18. Cookie Banner — consentement RGPD
    const CONSENT_KEY = "bsgroup-cookie-consent";
    const CONSENT_ID_KEY = "bsgroup-cookie-consent-id";
    const ID_COOKIE = "consent_id";
    const ID_MAX_AGE = 60 * 60 * 24 * 395;
  const cookieBanner = document.getElementById("cookie-banner");
  const cookieModal = document.getElementById("cookie-modal");
  const cookieReopenBtn = document.getElementById("cookie-reopen");

  if (cookieBanner && cookieModal) {
    const cookieBackdrop = document.getElementById("cookie-modal-backdrop");
    const cookieModalClose = document.getElementById("cookie-modal-close");
    const cookieToggles = cookieModal.querySelectorAll(".cookie-toggle-input");

    const getConsentId = () => {
      try {
        const ls = localStorage.getItem(CONSENT_ID_KEY);
        if (ls) return ls;
      } catch (e) {}
      const m = document.cookie.match(/(?:^|;\s*)consent_id=([^;]+)/);
      return m ? decodeURIComponent(m[1]) : null;
    };

    const setConsentId = (cid) => {
      if (!cid) return;
      try {
        localStorage.setItem(CONSENT_ID_KEY, cid);
      } catch (e) {}
      try {
        document.cookie =
          ID_COOKIE + "=" + encodeURIComponent(cid) + "; path=/; max-age=" + ID_MAX_AGE + "; SameSite=Lax";
      } catch (e) {}
      try {
        window.__consentId = cid;
      } catch (e) {}
    };

    const getCsrfToken = () => {
      const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
      return m ? decodeURIComponent(m[1]) : "";
    };

    // Envoi serveur pour preuve RGPD en DB (le serveur crée/retourne le consent_id stable)
    const postConsent = (analytics, marketing, action) => {
      fetch("/api/cookie-consent/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          statistics: !!analytics,
          marketing: !!marketing,
          consent_id: getConsentId(),
          action: action || "save",
        }),
      })
        .then((r) => r.json())
        .then((d) => {
          if (d && d.consent_id) setConsentId(d.consent_id);
        })
        .catch(() => {});
    };

    const getConsent = () => {
      try {
        return JSON.parse(localStorage.getItem(CONSENT_KEY));
      } catch (e) {
        return null;
      }
    };

    const saveConsent = (prefs, action) => {
      localStorage.setItem(
        CONSENT_KEY,
        JSON.stringify({ ...prefs, date: new Date().toISOString() }),
      );
      postConsent(prefs.analytics, prefs.marketing, action);
    };

    const hideBanner = () => cookieBanner.classList.remove("visible");
    const showBanner = () => cookieBanner.classList.add("visible");

    const openCookieModal = () => {
      const consent = getConsent();
      const state = consent || {
        necessary: true,
        preferences: false,
        analytics: false,
        marketing: false,
      };
      cookieToggles.forEach((t) => {
        t.checked = !!state[t.dataset.category];
      });

      cookieModal.classList.remove("hidden");
      cookieModal.classList.add("flex");
      document.body.style.overflow = "hidden";
    };

    const closeCookieModal = () => {
      cookieModal.classList.add("hidden");
      cookieModal.classList.remove("flex");
      document.body.style.overflow = "";
      if (!getConsent()) showBanner();
    };

    const applyConsent = (prefs, action) => {
      saveConsent(prefs, action);
      hideBanner();
      cookieModal.classList.add("hidden");
      cookieModal.classList.remove("flex");
      document.body.style.overflow = "";
      if (cookieReopenBtn) {
        cookieReopenBtn.classList.remove("hidden");
        cookieReopenBtn.classList.add("flex");
      }
      if (typeof showToast === "function")
        showToast(S("cookieSaved", "Cookie preferences saved."));
    };

    document.getElementById("cookie-accept").addEventListener("click", () => {
      applyConsent(
        {
          necessary: true,
          preferences: true,
          analytics: true,
          marketing: true,
        },
        "accept_all",
      );
    });

    document.getElementById("cookie-reject").addEventListener("click", () => {
      applyConsent(
        {
          necessary: true,
          preferences: false,
          analytics: false,
          marketing: false,
        },
        "reject_all",
      );
    });

    document
      .getElementById("cookie-customize")
      .addEventListener("click", () => {
        hideBanner();
        openCookieModal();
      });

    document.getElementById("cookie-save").addEventListener("click", () => {
      const prefs = { necessary: true };
      cookieToggles.forEach((t) => {
        if (!t.disabled) prefs[t.dataset.category] = t.checked;
      });
      applyConsent(prefs, "save_prefs");
    });

    document
      .getElementById("cookie-accept-all")
      .addEventListener("click", () => {
        cookieToggles.forEach((t) => {
          t.checked = true;
        });
        applyConsent(
          {
            necessary: true,
            preferences: true,
            analytics: true,
            marketing: true,
          },
          "accept_all",
        );
      });

    cookieModalClose.addEventListener("click", closeCookieModal);
    cookieBackdrop.addEventListener("click", closeCookieModal);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !cookieModal.classList.contains("hidden"))
        closeCookieModal();
    });

    if (cookieReopenBtn) {
      cookieReopenBtn.addEventListener("click", openCookieModal);
    }

    const showReopen = () => {
      if (cookieReopenBtn) {
        cookieReopenBtn.classList.remove("hidden");
        cookieReopenBtn.classList.add("flex");
      }
    };

    if (getConsent()) {
      showReopen();
    } else {
      const tryShowBanner = () => {
        if (document.body.classList.contains("is-loading")) {
          setTimeout(tryShowBanner, 250);
        } else {
          showBanner();
        }
      };
      setTimeout(tryShowBanner, 800);
    }

    // Vérité serveur : synchronise la copie locale avec la DB au chargement.
    fetch("/api/cookie-consent/", { headers: { "X-CSRFToken": getCsrfToken() } })
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d && d.has_consented) {
          try {
            localStorage.setItem(
              CONSENT_KEY,
              JSON.stringify({
                necessary: true,
                preferences: getConsent()?.preferences ?? true,
                analytics: !!d.statistics,
                marketing: !!d.marketing,
                date: new Date().toISOString(),
              }),
            );
          } catch (e) {}
          if (d.consent_id) setConsentId(d.consent_id);
          hideBanner();
          showReopen();
          return;
        }
        const c0 = getConsent();
        if (c0) {
          // Choix local jamais synchronisé : on le pousse une fois.
          postConsent(c0.analytics, c0.marketing, "sync");
        }
      })
      .catch(() => {});
  }

  // 19. Chatbot — assistant virtuel avec réponses simulées
  const chatLauncher = document.getElementById("chat-launcher");
  const chatPanel = document.getElementById("chat-panel");
  const chatCloseBtn = document.getElementById("chat-close");
  const chatBadge = document.getElementById("chat-badge");
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatQuick = document.getElementById("chat-quick-replies");

  if (chatLauncher && chatPanel) {
    let chatOpened = false;
    let isBotTyping = false;

    const nowTime = () =>
      new Date().toLocaleTimeString(BSG_LOCALE, {
        hour: "2-digit",
        minute: "2-digit",
      });

    const scrollChat = () => {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    const addMessage = (text, sender) => {
      const msg = document.createElement("div");
      msg.className = `chat-msg ${sender}`;

      const bubble = document.createElement("div");
      bubble.className = "chat-bubble";
      bubble.textContent = text;

      const time = document.createElement("span");
      time.className = "chat-time";
      time.textContent = nowTime();

      msg.append(bubble, time);
      chatMessages.appendChild(msg);
      scrollChat();
    };

    const showTyping = () => {
      isBotTyping = true;
      const el = document.createElement("div");
      el.className = "chat-msg bot";
      el.id = "chat-typing";
      el.innerHTML =
        '<div class="chat-bubble chat-bubble--typing">' +
        '<span class="typing-dots" aria-hidden="true"><span></span><span></span><span></span></span>' +
        '<em class="typing-label">' +
        S("chatTyping", "Thinking...").replace(/</g, "&lt;") +
        "</em>" +
        "</div>";
      chatMessages.appendChild(el);
      scrollChat();
    };

    const stopTyping = () => {
      document.getElementById("chat-typing")?.remove();
      isBotTyping = false;
    };

    const getBotReply = (raw) => {
      const t = raw.toLowerCase();

      if (
        /(bonjour|salut|hello|hi\b|hey|coucou|bonsoir|good morning|good afternoon|good evening|what are your services|marhaba|مرحبا|سلام|صباح|مساء)/.test(
          t,
        )
      )
        return S(
          "chatHello",
          "Hello and welcome to BS GROUP! How can I help you today?",
        );
      if (
        /(prix|devis|tarif|coût|cout|combien|budget|price|pricing|quote|quotation|cost|i would like a quote|سعر|أسعار|عرض سعر|تكلفة)/.test(
          t,
        )
      )
        return S(
          "chatQuote",
          "For a free detailed quote, fill in the contact form or call us. We reply within 24 hours!",
        );
      if (
        /(service|prestation|construction|rénovation|renovation|projet|travaux|services|project|works|what are your services|بناء|مشاريع|خدمات|إنشاءات)/.test(
          t,
        )
      )
        return S(
          "chatServices",
          "We cover residential and commercial construction, concrete works, renovation and pre-construction. What kind of project do you have in mind?",
        );
      if (
        /(contact|téléphone|telephone|email|mail|joindre|rendez-vous|rdv|adresse|phone|call|address|how can i contact you|اتصل|هاتف|بريد|عنوان|تواصل)/.test(
          t,
        )
      )
        return S(
          "chatContact",
          "You can reach us by phone, email or via the contact form. We reply within 24 hours!",
        );
      if (
        /(merci|thanks|thank you|super|parfait|great|perfect|شكرا)/.test(t)
      )
        return S(
          "chatThanks",
          "You are most welcome! Feel free to ask if you have any other questions.",
        );

      const fallback = [
        S(
          "chatFb0",
          "Thanks for your message! A member of the BS GROUP team will get back to you very soon.",
        ),
        S(
          "chatFb1",
          "Great question! For an accurate answer, our experts can call you back — leave your details in the contact form.",
        ),
        S(
          "chatFb2",
          "Noted! Did you know BS GROUP has completed 640+ projects with 25 years of experience?",
        ),
        S(
          "chatFb3",
          "Noted! Our team is reviewing your message and will send you a full answer shortly.",
        ),
      ];
      return fallback[Math.floor(Math.random() * fallback.length)];
    };

    const getCsrfToken = () => {
      const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
      return m ? decodeURIComponent(m[1]) : "";
    };

    const getChatSessionId = () => {
      try {
        let sid = localStorage.getItem("bsg_sid");
        if (!sid) {
          sid =
            "bsg-" +
            Date.now().toString(36) +
            "-" +
            Math.random().toString(36).slice(2, 10);
          localStorage.setItem("bsg_sid", sid);
        }
        return sid;
      } catch (e) {
        return "bsg-" + Date.now().toString(36);
      }
    };

    // Backend Gemini (RAG sur contenus DB, cf. app chatbot) — même logique que DIGI-AGENCY.
    const askApi = async (userText) => {
      const res = await fetch("/api/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          message: userText,
          lang: BSG_LANG,
          session_id: getChatSessionId(),
        }),
      });
      const data = await res.json();
      if (data && data.success && data.answer) return data.answer;
      throw new Error((data && data.error) || "chat-api-error");
    };

    // Streaming SSE (POST /api/chat/stream/) : affiche les tokens au fil de
    // l'eau au lieu d'attendre la réponse complète. Repli sur askApi si le
    // flux est indisponible (proxy qui bufférise, erreur réseau...).
    const streamAskApi = async (userText, onToken) => {
      const res = await fetch("/api/chat/stream/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({
          message: userText,
          lang: BSG_LANG,
          session_id: getChatSessionId(),
        }),
      });
      if (!res.ok || !res.body) throw new Error("chat-stream-unavailable");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      let done = false;
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        if (readerDone) break;
        buf += decoder.decode(value, { stream: true });
        const events = buf.split("\n\n");
        buf = events.pop();
        for (const evt of events) {
          for (const line of evt.split("\n")) {
            const t = line.trim();
            if (!t.startsWith("data:")) continue;
            let payload = null;
            try {
              payload = JSON.parse(t.slice(5).trim());
            } catch (e) {
              continue;
            }
            if (payload && typeof payload.text === "string" && payload.text) {
              onToken(payload.text);
            }
            if (payload && payload.done) done = true;
            if (payload && payload.error) throw new Error("chat-api-error");
          }
        }
      }
    };

    const respondTo = (userText) => {
      showTyping();
      // Bulle bot créée tout de suite, remplie token par token.
      const msg = document.createElement("div");
      msg.className = "chat-msg bot";
      const bubble = document.createElement("div");
      bubble.className = "chat-bubble";
      const time = document.createElement("span");
      time.className = "chat-time";
      time.textContent = nowTime();
      msg.append(bubble, time);
      chatMessages.appendChild(msg);
      scrollChat();

      let gotToken = false;
      const finishStream = () => {
        stopTyping();
        if (!gotToken) msg.remove();
      };
      streamAskApi(userText, (tok) => {
        if (!gotToken) {
          gotToken = true;
          stopTyping();
        }
        bubble.textContent += tok;
        scrollChat();
      })
        .then(finishStream)
        .catch(() => {
          // Repli synchrone classique
          finishStream();
          askApi(userText)
            .then((answer) => addMessage(answer, "bot"))
            .catch(() => addMessage(getBotReply(userText), "bot"));
        });
    };

    const openChat = () => {
      chatPanel.classList.add("open");
      chatPanel.setAttribute("aria-hidden", "false");
      chatLauncher.classList.add("hide");
      chatBadge?.classList.add("gone");

      if (!chatOpened) {
        chatOpened = true;
        setTimeout(() => {
          showTyping();
          setTimeout(() => {
            stopTyping();
            addMessage(
              S(
                "chatGreeting",
                "Hello! I am the BS GROUP virtual assistant. Ask me about our services, quotes or timelines!",
              ),
              "bot",
            );
          }, 1600);
        }, 400);
      }
      setTimeout(() => chatInput.focus(), 350);
    };

    const closeChat = () => {
      chatPanel.classList.remove("open");
      chatPanel.setAttribute("aria-hidden", "true");
      chatLauncher.classList.remove("hide");
    };

    chatLauncher.addEventListener("click", openChat);
    chatCloseBtn.addEventListener("click", closeChat);

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && chatPanel.classList.contains("open"))
        closeChat();
    });

    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = chatInput.value.trim();
      if (!text || isBotTyping) return;

      addMessage(text, "user");
      chatInput.value = "";
      chatQuick?.classList.add("gone");
      respondTo(text);
    });

    chatQuick?.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (isBotTyping) return;
        addMessage(btn.dataset.quick, "user");
        chatQuick.classList.add("gone");
        respondTo(btn.dataset.quick);
      });
    });
  }

  // 20. Page Header — titre & fil d'Ariane dynamiques
  const pageHeader = document.getElementById("page-header");

  if (pageHeader) {
    const pageTitle = pageHeader.dataset.pageTitle || "Page";
    const headerTitleEl = document.getElementById("page-header-title");
    const headerCurrentEl = document.getElementById("page-header-current");

    // Ne jamais écraser le contenu serveur par le repli "Page" :
    // une traduction vide doit laisser le HTML intact.
    if (pageTitle && pageTitle !== "Page") {
      if (headerTitleEl) headerTitleEl.textContent = pageTitle;
      if (headerCurrentEl) headerCurrentEl.textContent = pageTitle;

      document.title = `${pageTitle} | BS GROUP`;
    }
  }

  // 21. Video Showcase — bouton play (réutilise la modal partagée)
  const plansPlayBtn = document.getElementById("plans-play-btn");

  if (plansPlayBtn && modal && video) {
    plansPlayBtn.addEventListener("click", () => openModal());
  }

  // 22. Section Awards — pagination synchronisée du carrousel
  const awardsTrack = document.getElementById("awards-track");
  const awardDots = document.querySelectorAll("[data-award-dot]");

  if (awardsTrack && awardDots.length) {
    const awardCards = awardsTrack.querySelectorAll(".award-card");

    const activateAwardDot = (index) => {
      awardDots.forEach((d, i) => d.classList.toggle("active", i === index));
    };

    awardDots.forEach((dot, i) => {
      dot.addEventListener("click", () => {
        const card = awardCards[i];
        if (!card) return;
        const offset = card.offsetLeft - awardCards[0].offsetLeft;
        awardsTrack.scrollTo({ left: offset, behavior: "smooth" });
        activateAwardDot(i);
      });
    });

    let awardSpyRaf = null;
    awardsTrack.addEventListener(
      "scroll",
      () => {
        if (awardSpyRaf) return;
        awardSpyRaf = requestAnimationFrame(() => {
          awardSpyRaf = null;
          const x = awardsTrack.scrollLeft;
          let best = 0;
          let minDist = Infinity;
          awardCards.forEach((card, i) => {
            const dist = Math.abs(
              card.offsetLeft - awardCards[0].offsetLeft - x,
            );
            if (dist < minDist) {
              minDist = dist;
              best = i;
            }
          });
          activateAwardDot(best);
        });
      },
      { passive: true },
    );
  }

  // 23. Section Timeline — apparition des étapes au scroll
  const timelineItems = document.querySelectorAll(".timeline-item");

  if ("IntersectionObserver" in window && timelineItems.length) {
    const timelineIO = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("timeline-visible");
            timelineIO.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 },
    );

    timelineItems.forEach((item) => timelineIO.observe(item));
  } else {
    timelineItems.forEach((item) => item.classList.add("timeline-visible"));
  }

  // 23b. Copyright dynamique — année en cours
  const getCurrentYear = () => new Date().getFullYear();

  const updateCopyrightYear = () => {
    const year = getCurrentYear();

    // 1) Spans dédiés : <span class="copyright-year">2025</span>
    document
      .querySelectorAll(".copyright-year, #copyright-year")
      .forEach((el) => {
        el.textContent = year;
      });

    // 2) Filet de sécurité : remplace toute année statique "© 2025"
    // dans le footer si aucun span dédié n'existe sur la page.
    if (!document.querySelector(".copyright-year, #copyright-year")) {
      document.querySelectorAll("footer p").forEach((p) => {
        if (/copyright/i.test(p.textContent || "")) {
          p.innerHTML = p.innerHTML.replace(/©\s*\d{4}/, `© ${year}`);
        }
      });
    }
  };

  updateCopyrightYear();
});
// 24. Page Projects — filtres + apparition des cartes
const ppFilters = document.querySelectorAll("[data-pp-filter]");
const ppCards = document.querySelectorAll("[data-pp-item]");

if (ppFilters.length && ppCards.length) {
  // Apparition au scroll (cascade)
  if ("IntersectionObserver" in window) {
    const ppIO = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("pp-visible");
            ppIO.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 },
    );

    ppCards.forEach((card, i) => {
      card.style.transitionDelay = `${(i % 3) * 90}ms`; // décalage par colonne
      ppIO.observe(card);
    });
  } else {
    ppCards.forEach((card) => card.classList.add("pp-visible"));
  }

  // Filtrage par catégorie
  ppFilters.forEach((btn) => {
    btn.addEventListener("click", () => {
      ppFilters.forEach((b) => b.classList.remove("pp-active"));
      btn.classList.add("pp-active");

      const filter = btn.dataset.ppFilter;
      ppCards.forEach((card) => {
        const match = filter === "all" || card.dataset.category === filter;
        card.classList.toggle("pp-hidden", !match);
        if (match) card.classList.add("pp-visible"); // déjà révélée = visible direct
      });
    });
  });
}
// 25. Page Blogs — filtres + pagination dynamique
const bpCards = document.querySelectorAll("[data-bp-item]");
const bpFilterBtns = document.querySelectorAll("[data-bp-filter]");
const bpPagination = document.getElementById("bp-pagination");
const bpGrid = document.getElementById("bp-grid");
const BP_PER_PAGE = 6;

if (bpCards.length && bpFilterBtns.length && bpPagination) {
  let bpFilter = "all";
  let bpPage = 1;

  const bpScrollToGrid = () => {
    bpGrid.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const renderBpPagination = (totalPages) => {
    if (bpPagination.querySelector("a")) return;
    bpPagination.innerHTML = "";

    if (totalPages <= 1) {
      bpPagination.classList.add("hidden");
      return;
    }
    bpPagination.classList.remove("hidden");

    const makeBtn = (label) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "bp-page-btn";
      b.innerHTML = label;
      return b;
    };

    // Flèche précédente
    const prev = makeBtn(
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>',
    );
    prev.disabled = bpPage === 1;
    prev.setAttribute("aria-label", "Page précédente");
    prev.addEventListener("click", () => {
      if (bpPage > 1) {
        bpPage--;
        bpApply(true);
        bpScrollToGrid();
      }
    });
    bpPagination.appendChild(prev);

    // Numéros de page
    for (let p = 1; p <= totalPages; p++) {
      const b = makeBtn(String(p));
      if (p === bpPage) b.classList.add("bp-current");
      b.setAttribute("aria-label", `Page ${p}`);
      b.addEventListener("click", () => {
        if (p !== bpPage) {
          bpPage = p;
          bpApply(true);
          bpScrollToGrid();
        }
      });
      bpPagination.appendChild(b);
    }

    // Flèche suivante
    const next = makeBtn(
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
    );
    next.disabled = bpPage === totalPages;
    next.setAttribute("aria-label", "Page suivante");
    next.addEventListener("click", () => {
      if (bpPage < totalPages) {
        bpPage++;
        bpApply(true);
        bpScrollToGrid();
      }
    });
    bpPagination.appendChild(next);
  };

  const bpApply = (animate) => {
    const matching = Array.from(bpCards).filter(
      (c) => bpFilter === "all" || c.dataset.bpItem === bpFilter,
    );
    const totalPages = Math.max(1, Math.ceil(matching.length / BP_PER_PAGE));
    if (bpPage > totalPages) bpPage = totalPages;

    const pageItems = matching.slice(
      (bpPage - 1) * BP_PER_PAGE,
      bpPage * BP_PER_PAGE,
    );

    bpCards.forEach((card) => {
      const show = pageItems.includes(card);
      card.classList.toggle("bp-hidden", !show);
      if (!show) return;

      if (animate) {
        // Rejoue la transition d'apparition
        card.classList.remove("bp-visible");
        void card.offsetWidth; // force le reflow
        card.classList.add("bp-visible");
      } else {
        card.classList.add("bp-visible");
      }
    });

    // Décalage en cascade sur la page visible
    pageItems.forEach((card, i) => {
      card.style.transitionDelay = `${i * 70}ms`;
    });

    renderBpPagination(totalPages);
  };

  bpFilterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      bpFilterBtns.forEach((b) => b.classList.remove("pp-active"));
      btn.classList.add("pp-active");
      bpFilter = btn.dataset.bpFilter;
      bpPage = 1; // un filtre ramène toujours à la première page
      bpApply(true);
    });
  });

  // État initial (cascade au chargement)
  requestAnimationFrame(() => bpApply(false));
}
// 26. Page Blog Detail — partage réseaux sociaux
const shareButtons = document.querySelectorAll("[data-share]");

if (shareButtons.length) {
  shareButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const network = btn.dataset.share;
      const pageUrl = encodeURIComponent(window.location.href);
      const pageTitle = encodeURIComponent(document.title);

      if (network === "copy") {
        // Copie du lien dans le presse-papier
        const fullUrl = window.location.href;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard
            .writeText(fullUrl)
            .then(() => {
              if (typeof showToast === "function")
                showToast(S("linkCopied", "Article link copied to clipboard!"));
            })
            .catch(() => {});
        } else {
          // Fallback anciens navigateurs
          const temp = document.createElement("input");
          temp.value = fullUrl;
          document.body.appendChild(temp);
          temp.select();
          document.execCommand("copy");
          temp.remove();
          if (typeof showToast === "function")
            showToast(S("linkCopied", "Article link copied to clipboard!"));
        }
        return;
      }

      // Pop-ups de partage (Facebook / Twitter / LinkedIn)
      const shareUrls = {
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${pageUrl}`,
        twitter: `https://twitter.com/intent/tweet?url=${pageUrl}&text=${pageTitle}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${pageUrl}`,
      };

      if (shareUrls[network]) {
        window.open(
          shareUrls[network],
          "share-popup",
          "width=620,height=540,menubar=no,toolbar=no",
        );
      }
    });
  });
}
// 27. Page Careers — filtres des offres par département
const cjFilters = document.querySelectorAll("[data-cj-filter]");
const cjCards = document.querySelectorAll("[data-cj-item]");
const cjCount = document.getElementById("cj-count");
const cjEmpty = document.getElementById("cj-empty");

if (cjFilters.length && cjCards.length) {
  cjFilters.forEach((btn) => {
    btn.addEventListener("click", () => {
      cjFilters.forEach((b) => b.classList.remove("pp-active"));
      btn.classList.add("pp-active");

      const filter = btn.dataset.cjFilter;
      let visible = 0;

      cjCards.forEach((card) => {
        const match = filter === "all" || card.dataset.cjItem === filter;
        card.classList.toggle("hidden", !match);
        if (match) {
          visible++;
          card.classList.add("timeline-visible"); // assure l'affichage même si non encore scrollée
        }
      });

      if (cjCount) cjCount.textContent = visible;
      if (cjEmpty) cjEmpty.classList.toggle("hidden", visible > 0);
    });
  });
}
// 28. Page Career Detail — candidature, upload CV, save job
const applicationForm = document.getElementById("application-form");

if (applicationForm) {
  const afFileInput = document.getElementById("af-file");
  const afDropzone = document.getElementById("af-dropzone");
  const afFileBadge = document.getElementById("af-file-badge");
  const afFileName = document.getElementById("af-file-name");
  const afFileRemove = document.getElementById("af-file-remove");
  const afConsent = document.getElementById("af-consent");
  let afFileSelected = null;

  // Upload : affichage du fichier sélectionné
  if (afFileInput) {
    afFileInput.addEventListener("change", () => {
      const file = afFileInput.files[0];
      if (!file) return;

      if (file.size > 5 * 1024 * 1024) {
        if (typeof showToast === "function")
          showToast(S("fileTooLarge", "File too large — maximum size is 5 MB."));
        afFileInput.value = "";
        return;
      }

      afFileSelected = file;
      afFileName.textContent = `${file.name} (${(file.size / 1024).toFixed(0)} KB)`;
      afFileBadge.classList.remove("hidden");
      afFileBadge.classList.add("flex");
      afDropzone.classList.add("hidden");
    });

    // Drag & drop visuel (styles inline, zéro CSS nouveau)
    ["dragenter", "dragover"].forEach((evt) => {
      afDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        afDropzone.style.borderColor = "#c9a227";
        afDropzone.style.backgroundColor = "rgba(241, 90, 36, 0.06)";
      });
    });
    ["dragleave", "drop"].forEach((evt) => {
      afDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        afDropzone.style.borderColor = "";
        afDropzone.style.backgroundColor = "";
      });
    });
    afDropzone.addEventListener("drop", (e) => {
      const file = e.dataTransfer.files[0];
      if (file) {
        // Transfère le fichier dans l'input pour unified handling
        const dt = new DataTransfer();
        dt.items.add(file);
        afFileInput.files = dt.files;
        afFileInput.dispatchEvent(new Event("change"));
      }
    });
  }

  // Retirer le fichier
  afFileRemove?.addEventListener("click", () => {
    afFileSelected = null;
    afFileInput.value = "";
    afFileBadge.classList.add("hidden");
    afFileBadge.classList.remove("flex");
    afDropzone.classList.remove("hidden");
  });

  // Soumission avec validation
  applicationForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    let isValid = true;

    // Champs texte (réutilise setFieldError du bloc 11)
    applicationForm.querySelectorAll(".form-input").forEach((input) => {
      const value = input.value.trim();
      let msg = "";

      if (input.tagName === "SELECT" && !value) {
        msg = S("selectPosition", "Please select a position.");
      } else if (input.tagName === "SELECT") {
        msg = "";
      } else if (!value) {
        msg = S("formRequired", "This field is required.");
      } else if (input.type === "email" && !/^\S+@\S+\.\S+$/.test(value)) {
        msg = S("formEmail", "Please enter a valid email address.");
      } else if (
        input.dataset.type === "phone" &&
        value.replace(/\D/g, "").length < 7
      ) {
        msg = S("formPhone", "Please enter a valid phone number.");
      }

      setFieldError(input, msg);
      if (msg) isValid = false;
    });

    // Fichier CV requis
    const fileErrorEl = document
      .getElementById("af-dropzone")
      ?.parentElement.querySelector(".error-msg");
    if (!afFileSelected) {
      if (fileErrorEl) {
        fileErrorEl.textContent = S(
          "attachResume",
          "Please attach your resume (PDF, DOC or DOCX).",
        );
        fileErrorEl.classList.remove("hidden");
      }
      isValid = false;
    } else if (fileErrorEl) {
      fileErrorEl.classList.add("hidden");
    }

    // Consentement requis
    const consentErrorEl = afConsent
      ?.closest("div")
      .querySelector(".error-msg");
    if (afConsent && !afConsent.checked) {
      if (consentErrorEl) {
        consentErrorEl.textContent = S(
          "privacyContinue",
          "Please accept the Privacy Policy to continue.",
        );
        consentErrorEl.classList.remove("hidden");
      }
      isValid = false;
    } else if (consentErrorEl) {
      consentErrorEl.classList.add("hidden");
    }

    if (!isValid) return;

    // POST réel backend → redirect serveur thanks/<reference>
    const submitBtn = applicationForm.querySelector('button[type="submit"]');
    const originalHTML = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.textContent = S("submitting", "Submitting...");
    try {
      const data = new FormData(applicationForm);
      const res = await fetch(applicationForm.action || window.location.pathname, { method: "POST", body: data });
      if (res.redirected) { window.location.href = res.url; return; }
      if (res.ok) { window.location.href = "/thanks/"; return; }
    } catch (e) {}
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalHTML;
    if (window.lucide) lucide.createIcons();
    if (typeof showToast === "function")
      showToast(
        S(
          "applicationSent",
          "Application submitted! Our recruiter will contact you soon.",
        ),
      );
  });
}

// Save Job (bookmark)
const saveJobBtn = document.getElementById("save-job-btn");

if (saveJobBtn) {
  let jobSaved = false;
  saveJobBtn.addEventListener("click", () => {
    jobSaved = !jobSaved;
    saveJobBtn.style.borderColor = jobSaved ? "#c9a227" : "";
    saveJobBtn.style.backgroundColor = jobSaved ? "#c9a227" : "";
    saveJobBtn.style.color = jobSaved ? "#ffffff" : "";
    if (typeof showToast === "function") {
      showToast(
        jobSaved
          ? S("jobSaved", "Job saved to your favorites.")
          : S("jobUnsaved", "Job removed from your favorites."),
      );
    }
  });
}
// 29. Page Team — filtres par département
const tmFilters = document.querySelectorAll("[data-tm-filter]");
const tmCards = document.querySelectorAll("[data-tm-item]");
const tmCount = document.getElementById("tm-count");

if (tmFilters.length && tmCards.length) {
  tmFilters.forEach((btn) => {
    btn.addEventListener("click", () => {
      tmFilters.forEach((b) => b.classList.remove("pp-active"));
      btn.classList.add("pp-active");

      const filter = btn.dataset.tmFilter;
      let visible = 0;

      tmCards.forEach((card) => {
        const match = filter === "all" || card.dataset.tmItem === filter;
        card.classList.toggle("hidden", !match);
        if (match) {
          visible++;
          card.classList.add("timeline-visible"); // assure l'affichage même hors viewport
        }
      });

      if (tmCount) tmCount.textContent = visible;
    });
  });
}
// 30. Page FAQ — filtres de catégories
const fqFilters = document.querySelectorAll("[data-fq-filter]");
const fqItems = document.querySelectorAll("[data-fq-item]");
const fqEmpty = document.getElementById("fq-empty");

if (fqFilters.length && fqItems.length) {
  fqFilters.forEach((btn) => {
    btn.addEventListener("click", () => {
      fqFilters.forEach((b) => b.classList.remove("pp-active"));
      btn.classList.add("pp-active");

      const filter = btn.dataset.fqFilter;
      let visible = 0;

      fqItems.forEach((item) => {
        const match = filter === "all" || item.dataset.fqItem === filter;
        item.classList.toggle("hidden", !match);
        if (match) visible++;
      });

      // Ferme tous les accordéons lors d'un changement de catégorie
      // (évite un item ouvert invisible qui dérouterait)
      fqItems.forEach((i) => i.classList.remove("open"));

      if (fqEmpty) fqEmpty.classList.toggle("hidden", visible > 0);
    });
  });
}
// 32. Page Quote — assistant multi-étapes (version autonome)
const initQuoteWizard = () => {
  const quoteForm = document.getElementById("quote-form");
  if (!quoteForm) return;

  /* Helper local : ne dépend plus de setFieldError (bloc 11) */
  const qSetError = (input, msg) => {
    const errorEl = input.parentElement.querySelector(".error-msg");
    if (msg) {
      input.classList.add("input-error");
      if (errorEl) {
        errorEl.textContent = msg;
        errorEl.classList.remove("hidden");
      }
    } else {
      input.classList.remove("input-error");
      if (errorEl) errorEl.classList.add("hidden");
    }
  };

  const qToast = (msg) => {
    if (typeof showToast === "function") showToast(msg);
  };

  const qPanels = quoteForm.querySelectorAll("[data-qstep]");
  const qSteps = document.querySelectorAll("[data-q-indicator]");
  const qBar = document.getElementById("quote-progress-bar");
  const qBack = document.getElementById("quote-back");
  const qNext = document.getElementById("quote-next");
  const qTotal = qPanels.length;
  let qCurrent = 1;

  // Affiche une étape + met à jour stepper / barre / boutons
  const qShow = (n) => {
    qCurrent = Math.min(Math.max(n, 1), qTotal);
    qPanels.forEach((p) =>
      p.classList.toggle("hidden", Number(p.dataset.qstep) !== qCurrent),
    );

    qSteps.forEach((s) => {
      const num = Number(s.dataset.qIndicator);
      const dot = s.querySelector("[data-q-dot]");
      const label = s.querySelector("[data-q-label]");
      if (!dot) return;

      dot.classList.remove(
        "bg-white",
        "border-2",
        "border-gray-300",
        "text-slate-400",
        "bg-[#c9a227]",
        "text-white",
        "ring-4",
        "ring-[#c9a227]/20",
      );
      if (num < qCurrent) {
        dot.textContent = "✓";
        dot.classList.add("bg-[#c9a227]", "text-white");
      } else if (num === qCurrent) {
        dot.textContent = num;
        dot.classList.add(
          "bg-[#c9a227]",
          "text-white",
          "ring-4",
          "ring-[#c9a227]/20",
        );
      } else {
        dot.textContent = num;
        dot.classList.add(
          "bg-white",
          "border-2",
          "border-gray-300",
          "text-slate-400",
        );
      }
      if (label) {
        label.classList.toggle("text-[#0b1f35]", num === qCurrent);
        label.classList.toggle("text-slate-400", num !== qCurrent);
      }
    });

    if (qBar) qBar.style.width = `${(qCurrent / qTotal) * 100}%`;
    if (qBack) qBack.classList.toggle("invisible", qCurrent === 1);
    if (qNext) {
      qNext.textContent =
        qCurrent === qTotal
          ? S("quoteSubmit", "Submit Request")
          : qCurrent === qTotal - 1
            ? S("quoteReview", "Review My Request")
            : S("quoteContinue", "Continue");
    }
  };

  // Validation par étape
  const qValidateStep = (n) => {
    let ok = true;

    if (n === 1) {
      const chosen = quoteForm.querySelector(
        'input[name="projectType"]:checked',
      );
      const err = document.getElementById("q-step1-error");
      if (!chosen) {
        if (err) {
          err.textContent = S(
            "quoteType",
            "Please select a project type to continue.",
          );
          err.classList.remove("hidden");
        }
        ok = false;
      } else if (err) err.classList.add("hidden");
    } else if (n === 2 || n === 3) {
      const panel = quoteForm.querySelector(`[data-qstep="${n}"]`);
      panel.querySelectorAll(".form-input").forEach((input) => {
        const value = input.value.trim();
        let msg = "";
        if (input.required && !value)
          msg = S("formRequired", "This field is required.");
        else if (
          input.type === "email" &&
          value &&
          !/^\S+@\S+\.\S+$/.test(value)
        )
          msg = S("formEmail", "Please enter a valid email address.");
        else if (
          input.dataset.type === "phone" &&
          value &&
          value.replace(/\D/g, "").length < 7
        )
          msg = S("formPhone", "Please enter a valid phone number.");
        qSetError(input, msg);
        if (msg) ok = false;
      });
    } else if (n === 4) {
      const consent = document.getElementById("q-consent");
      const err = document.getElementById("q-consent-error");
      if (consent && !consent.checked) {
        if (err) {
          err.textContent = S(
            "quotePrivacy",
            "Please accept the Privacy Policy to submit.",
          );
          err.classList.remove("hidden");
        }
        ok = false;
      } else if (err) err.classList.add("hidden");
    }
    return ok;
  };

  // Génère le récapitulatif de l'étape 4
  const qBuildSummary = () => {
    const get = (id) => document.getElementById(id)?.value.trim() || "";
    const set = (id, v) => {
      const el = document.getElementById(id);
      if (el) el.textContent = v || "—";
    };

    set(
      "q-sum-type",
      quoteForm.querySelector('input[name="projectType"]:checked')?.value,
    );
    set("q-sum-location", get("qf-location"));
    set("q-sum-size", get("qf-size"));
    set("q-sum-budget", get("qf-budget"));
    set("q-sum-timeline", get("qf-timeline"));
    set("q-sum-name", get("qf-name"));
    set("q-sum-email", get("qf-email"));
    set("q-sum-phone", get("qf-phone"));
    set("q-sum-message", get("qf-description"));
  };

  // Soumission réelle backend → redirect serveur thank-devis/<reference>
  const qSubmit = async () => {
    qNext.disabled = true;
    qNext.textContent = S("submitting", "Submitting...");

    try {
      const fd = new FormData(quoteForm);
      // Mappe les champs du wizard vers les champs backend
      const getV = (n) => (fd.get(n) || "").toString().trim();
      if (!fd.get("name")) fd.set("name", getV("qf-name"));
      if (!fd.get("email")) fd.set("email", getV("qf-email"));
      if (!fd.get("phone")) fd.set("phone", getV("qf-phone"));
      if (!fd.get("message")) fd.set("message", getV("qf-description"));
      if (!fd.get("subject")) fd.set("subject", (fd.get("projectType") || "").toString());
      const res = await fetch(quoteForm.action || "/devis/", { method: "POST", body: fd });
      if (res.redirected) { window.location.href = res.url; return; }
      if (res.ok) { window.location.href = "/thank-devis/"; return; }
    } catch (e) {}
    // Fallback : carte succès locale (sans fausse référence serveur)
    qNext.disabled = false;
    qNext.textContent = S("quoteSubmit", "Submit Request");
    document.getElementById("quote-card").classList.add("hidden");
    const success = document.getElementById("quote-success");
    success.classList.remove("hidden");
    success.scrollIntoView({ behavior: "smooth", block: "start" });
    qToast(S("quoteDone", "Quote request submitted successfully!"));
  };

  // Navigation : le bouton submit gère tout (y compris Entrée)
  quoteForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!qValidateStep(qCurrent)) return;
    if (qCurrent === qTotal - 1) qBuildSummary();
    if (qCurrent === qTotal) {
      qSubmit();
      return;
    }
    qShow(qCurrent + 1);
  });

  qBack.addEventListener("click", () => qShow(qCurrent - 1));

  // Efface les erreurs dès correction
  quoteForm.querySelectorAll(".form-input").forEach((input) => {
    input.addEventListener("input", () => qSetError(input, ""));
    input.addEventListener("change", () => qSetError(input, ""));
  });

  // Upload optionnel (plans / photos)
  const qFileInput = document.getElementById("q-file");
  const qFileBadge = document.getElementById("q-file-badge");
  const qFileName = document.getElementById("q-file-name");
  const qFileRemove = document.getElementById("q-file-remove");

  if (qFileInput) {
    qFileInput.addEventListener("change", () => {
      const file = qFileInput.files[0];
      if (!file) return;
      if (file.size > 10 * 1024 * 1024) {
        qToast("File too large — maximum size is 10 MB.");
        qFileInput.value = "";
        return;
      }
      qFileName.textContent = `${file.name} (${(file.size / 1024).toFixed(0)} KB)`;
      qFileBadge.classList.remove("hidden");
      qFileBadge.classList.add("flex");
    });
    qFileRemove?.addEventListener("click", () => {
      qFileInput.value = "";
      qFileBadge.classList.add("hidden");
      qFileBadge.classList.remove("flex");
    });
  }

  // Recommencer une demande
  document.getElementById("q-restart")?.addEventListener("click", () => {
    quoteForm.reset();
    if (qFileInput) qFileInput.value = "";
    qFileBadge?.classList.add("hidden");
    qFileBadge?.classList.remove("flex");
    document.getElementById("quote-success").classList.add("hidden");
    document.getElementById("quote-card").classList.remove("hidden");
    qShow(1);
    document
      .getElementById("quote-card")
      .scrollIntoView({ behavior: "smooth", block: "start" });
  });

  qShow(1); // état initial normalisé
};

/* Auto-exécution : marche collé DANS ou HORS du DOMContentLoaded principal */
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initQuoteWizard);
} else {
  initQuoteWizard();
}
// 33. Page CGU — scroll-spy du sommaire (version autonome)
const initCguToc = () => {
  const cguLinks = document.querySelectorAll("[data-cgu-link]");
  const cguSections = document.querySelectorAll(
    "#s1, #s2, #s3, #s4, #s5, #s6, #s7, #s8, #s9",
  );

  if (
    cguLinks.length &&
    cguSections.length &&
    "IntersectionObserver" in window
  ) {
    const activeClass = [
      "bg-white",
      "text-[#c9a227]",
      "shadow-sm",
      "border",
      "border-[#c9a227]/20",
    ];
    const baseClass = ["text-slate-500"];

    const cguIO = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const id = `#${entry.target.id}`;
          cguLinks.forEach((link) => {
            const isActive = link.getAttribute("href") === id;
            link.classList.remove(...activeClass, ...baseClass);
            if (isActive) {
              link.classList.add(...activeClass);
              link.classList.remove("hover:text-[#c9a227]");
            } else {
              link.classList.add(...baseClass, "hover:text-[#c9a227]");
            }
          });
        });
      },
      { rootMargin: "-25% 0px -65% 0px" },
    ); // section "active" dans le tiers haut du viewport

    cguSections.forEach((s) => cguIO.observe(s));
  }
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initCguToc);
} else {
  initCguToc();
}
// 34. Page Privacy — scroll-spy du sommaire (version autonome)
const initPvcToc = () => {
  const pvcLinks = document.querySelectorAll("[data-pvc-link]");
  const pvcSections = document.querySelectorAll(
    "#p1, #p2, #p3, #p4, #p5, #p6, #p7, #p8, #p9, #p10",
  );

  if (
    pvcLinks.length &&
    pvcSections.length &&
    "IntersectionObserver" in window
  ) {
    const activeClass = [
      "bg-white",
      "text-[#c9a227]",
      "shadow-sm",
      "border",
      "border-[#c9a227]/20",
    ];
    const baseClass = ["text-slate-500"];

    const pvcIO = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const id = `#${entry.target.id}`;
          pvcLinks.forEach((link) => {
            const isActive = link.getAttribute("href") === id;
            link.classList.remove(...activeClass, ...baseClass);
            if (isActive) {
              link.classList.add(...activeClass);
              link.classList.remove("hover:text-[#c9a227]");
            } else {
              link.classList.add(...baseClass, "hover:text-[#c9a227]");
            }
          });
        });
      },
      { rootMargin: "-25% 0px -65% 0px" },
    );

    pvcSections.forEach((s) => pvcIO.observe(s));
  }
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initPvcToc);
} else {
  initPvcToc();
}
// 35. Page Legal Notice — scroll-spy du sommaire (autonome)
const initLglToc = () => {
  const lglLinks = document.querySelectorAll("[data-lgl-link]");
  const lglSections = document.querySelectorAll(
    "#l1, #l2, #l3, #l4, #l5, #l6, #l7",
  );

  if (
    lglLinks.length &&
    lglSections.length &&
    "IntersectionObserver" in window
  ) {
    const activeClass = [
      "bg-white",
      "text-[#c9a227]",
      "shadow-sm",
      "border",
      "border-[#c9a227]/20",
    ];
    const baseClass = ["text-slate-500"];

    const lglIO = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const id = `#${entry.target.id}`;
          lglLinks.forEach((link) => {
            const isActive = link.getAttribute("href") === id;
            link.classList.remove(...activeClass, ...baseClass);
            if (isActive) {
              link.classList.add(...activeClass);
              link.classList.remove("hover:text-[#c9a227]");
            } else {
              link.classList.add(...baseClass, "hover:text-[#c9a227]");
            }
          });
        });
      },
      { rootMargin: "-25% 0px -65% 0px" },
    );

    lglSections.forEach((s) => lglIO.observe(s));
  }
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initLglToc);
} else {
  initLglToc();
}
// 36. Coming Soon — countdown + timer digital + progression (autonome)
const initComingSoon = () => {
  const cdDays = document.getElementById("cd-days");
  if (!cdDays) return; // page non concernée

  // ⚠️ CONFIGURATION — adapte ces 2 valeurs :
  const LAUNCH_DATE = new Date("2026-12-31T09:00:00"); // date & heure de lancement
  const SITE_PROGRESS = 72; // % d'avancement affiché

  const cdHours = document.getElementById("cd-hours");
  const cdMinutes = document.getElementById("cd-minutes");
  const cdSeconds = document.getElementById("cd-seconds");
  const cdWrap = document.getElementById("countdown");
  const cdLive = document.getElementById("cd-live");

  const dtHours = document.getElementById("dt-hours");
  const dtMinutes = document.getElementById("dt-minutes");
  const dtSeconds = document.getElementById("dt-seconds");
  const dtWrap = document.getElementById("digital-timer");

  const csBar = document.getElementById("cs-bar");
  const csPercent = document.getElementById("cs-percent");

  const pad = (n) => String(n).padStart(2, "0");

  // Compte à rebours + horloge digitale (retourne false si lancement atteint)
  const tick = () => {
    const diff = LAUNCH_DATE - new Date();

    if (diff <= 0) {
      // Lancement atteint : on masque les timers, on affiche le bouton "We're Live"
      if (cdWrap) cdWrap.classList.add("hidden");
      if (dtWrap) dtWrap.classList.add("hidden");
      if (cdLive) cdLive.classList.remove("hidden");
      return false;
    }

    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);

    // Cartes (jours séparés)
    if (cdDays) cdDays.textContent = pad(d);
    if (cdHours) cdHours.textContent = pad(h);
    if (cdMinutes) cdMinutes.textContent = pad(m);
    if (cdSeconds) cdSeconds.textContent = pad(s);

    // Horloge digitale (heures totales restantes, format HH:MM:SS)
    const totalHours = d * 24 + h;
    if (dtHours)
      dtHours.textContent = pad(totalHours > 99 ? totalHours : totalHours);
    if (dtMinutes) dtMinutes.textContent = pad(m);
    if (dtSeconds) dtSeconds.textContent = pad(s);

    return true;
  };

  if (tick()) {
    setInterval(tick, 1000);
  }

  // Barre de progression animée 0 → SITE_PROGRESS
  if (csBar && csPercent) {
    let p = 0;
    const barTick = setInterval(() => {
      p = Math.min(p + Math.random() * 6 + 2, SITE_PROGRESS);
      csBar.style.width = p + "%";
      csPercent.textContent = Math.round(p) + "%";
      if (p >= SITE_PROGRESS) clearInterval(barTick);
    }, 90);
  }
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initComingSoon);
} else {
  initComingSoon();
}
// 37. Thanks page — référence serveur prioritaire (thanks/<ref>, thank-devis/<ref>)
const initThanksPage = () => {
  const thanksSection = document.getElementById("thanks-hero");
  if (!thanksSection) return;

  const refCard = document.getElementById("thanks-ref-card");
  const refEl = document.getElementById("thanks-ref");
  // 1. Référence serveur (rendue par Django) → ne jamais générer de fausse ref
  const serverRef = (thanksSection.dataset.serverRef || "").trim();
  const serverKind = (thanksSection.dataset.kind || "").trim();
  if (serverRef) {
    if (refEl) refEl.textContent = serverRef;
    if (refCard) refCard.classList.remove("hidden");
    document.title = S("thanksTitleRef", "Thank You {ref} | BS GROUP").replace(
      "{ref}",
      serverRef,
    );
    return;
  }
  // 2. Fallback compat : page générique /thanks/ + ?type=&ref=
  const params = new URLSearchParams(window.location.search);
  const type = (params.get("type") || "general").toLowerCase();
  const urlRef = params.get("ref");

  const copy = {
    quote: {
      badge: S("badgeQuote", "Quote Request Received"),
      message: S(
        "msgQuote",
        "Thank you! Our estimation team is reviewing your project and will send you a detailed, fixed-price proposal within 24 hours.",
      ),
      refPrefix: "QT",
    },
    contact: {
      badge: S("badgeContact", "Message Sent Successfully"),
      message: S(
        "msgContact",
        "Thank you for reaching out! Your message is in our inbox — expect a reply from our team within 24 – 48 business hours.",
      ),
      refPrefix: "MS",
    },
    application: {
      badge: S("badgeApplication", "Application Submitted"),
      message: S(
        "msgApplication",
        "Thank you for applying! Our recruitment team will review your profile and contact you within 5 business days — whatever the outcome.",
      ),
      refPrefix: "AP",
    },
    newsletter: {
      badge: S("badgeNewsletter", "Subscription Confirmed"),
      message: S(
        "msgNewsletter",
        "You're on the list! Exclusive deals and construction insights are on their way to your inbox. Welcome aboard! 🎉",
      ),
      refPrefix: null, // pas de référence pour la newsletter
    },
    general: {
      badge: S("badgeGeneral", "Submission Confirmed"),
      message: S(
        "msgGeneral",
        "Your submission has been received. Our team will review it and get back to you shortly.",
      ),
      refPrefix: "RF",
    },
  };

  const c = copy[type] || copy.general;

  // Badge
  const badgeEl = document.getElementById("thanks-badge");
  if (badgeEl)
    badgeEl.childNodes[badgeEl.childNodes.length - 1].textContent =
      " " + c.badge;

  // Message
  const msgEl = document.getElementById("thanks-message");
  if (msgEl) msgEl.textContent = c.message;

  // Référence : fournie en URL uniquement ; sinon on garde le texte serveur (—)
  if (refCard && refEl) {
    if (c.refPrefix) {
      if (urlRef) refEl.textContent = urlRef;
      refCard.classList.remove("hidden");
    } else {
      refCard.classList.add("hidden");
    }
  }

  // Titre de l'onglet dynamique
  document.title = S("thanksTitle", `Thank You | BS GROUP`);
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initThanksPage);
} else {
  initThanksPage();
}

// 38. Modal de demande (pages service-detail / projet-detail)
(() => {
  const modal = document.getElementById("request-modal");
  if (!modal) return;

  const form = document.getElementById("request-form");
  const subjectField = document.getElementById("request-subject");
  const errorBox = document.getElementById("request-error");

  const openModal = (subject) => {
    if (subjectField && subject) subjectField.value = subject;
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const first = modal.querySelector("#request-name");
    if (first) first.focus({ preventScroll: true });
  };

  const closeModal = () => {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  };

  document.querySelectorAll("[data-request-open]").forEach((btn) => {
    btn.addEventListener("click", () => {
      openModal(btn.getAttribute("data-request-subject") || "");
    });
  });

  modal.querySelectorAll("[data-request-close]").forEach((el) => {
    el.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("open")) closeModal();
  });

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      const name = (data.name || "").trim();
      const phone = (data.phone || "").replace(/[\s().-]/g, "");
      const email = (data.email || "").trim();
      const message = (data.message || "").trim();
      const ok =
        name.length > 1 &&
        phone.replace(/\+/g, "").length >= 6 &&
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) &&
        message.length > 1;
      if (!ok) {
        if (errorBox) errorBox.classList.remove("hidden");
        return;
      }
      if (errorBox) errorBox.classList.add("hidden");
      // POST réel backend devis → redirect serveur thank-devis/<reference>
      try {
        const fd = new FormData(form);
        const res = await fetch("/devis/", { method: "POST", body: fd });
        if (res.redirected) { window.location.href = res.url; return; }
        if (res.ok) { window.location.href = "/thank-devis/"; return; }
      } catch (e) {}
      window.location.href = "/thank-devis/";
    });
  }
})();

// 39. Page cookies — formulaire de modification du consentement (meme cle que la banniere)
(() => {
  const form = document.getElementById("consent-form");
  if (!form) return;

  const KEY = "bsgroup-cookie-consent";
  const toggles = form.querySelectorAll(".consent-toggle-input");
  const status = document.getElementById("consent-status");
  const saveBtn = document.getElementById("consent-save");
  const acceptBtn = document.getElementById("consent-accept-all");
  const rejectBtn = document.getElementById("consent-reject-all");

  const read = () => {
    try {
      return JSON.parse(localStorage.getItem(KEY));
    } catch (e) {
      return null;
    }
  };

  const paint = () => {
    const s = read() || {
      necessary: true,
      preferences: false,
      analytics: false,
      marketing: false,
    };
    toggles.forEach((t) => {
      t.checked = !!s[t.dataset.category];
    });
    if (status) {
      const cur = read();
      if (cur && cur.date) {
        const when = new Date(cur.date).toLocaleDateString(BSG_LOCALE, {
          day: "numeric",
          month: "short",
          year: "numeric",
        });
        const flag = (v) =>
          v ? S("onWord", "on") : S("offWord", "off");
        status.textContent = S(
          "consentSaved",
          "Current choice (saved {date}): Preferences {p} · Analytics {a} · Marketing {m}.",
        )
          .replace("{date}", when)
          .replace("{p}", flag(cur.preferences))
          .replace("{a}", flag(cur.analytics))
          .replace("{m}", flag(cur.marketing));
      } else {
        status.textContent = S(
          "consentNone",
          "No choice saved yet — only strictly necessary cookies are running.",
        );
      }
    }
  };

  const write = (prefs, action) => {
    localStorage.setItem(
      KEY,
      JSON.stringify({ ...prefs, date: new Date().toISOString() }),
    );
    // Sync serveur (preuve RGPD) — même endpoint que la bannière.
    try {
      const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
      const csrf = m ? decodeURIComponent(m[1]) : "";
      let cid = null;
      try {
        cid =
          localStorage.getItem("bsgroup-cookie-consent-id") ||
          (document.cookie.match(/(?:^|;\s*)consent_id=([^;]+)/) || [])[1] ||
          null;
        if (cid) cid = decodeURIComponent(cid);
      } catch (e) {}
      fetch("/api/cookie-consent/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify({
          statistics: !!prefs.analytics,
          marketing: !!prefs.marketing,
          consent_id: cid,
          action: action || "save",
        }),
      }).catch(() => {});
    } catch (e) {}
    paint();
  };

  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      const prefs = { necessary: true };
      toggles.forEach((t) => {
        if (!t.disabled) prefs[t.dataset.category] = t.checked;
      });
      write(prefs, "save_prefs");
    });
  }
  if (acceptBtn) {
    acceptBtn.addEventListener("click", () => {
      write({
        necessary: true,
        preferences: true,
        analytics: true,
        marketing: true,
      }, "accept_all");
    });
  }
  if (rejectBtn) {
    rejectBtn.addEventListener("click", () => {
      write({
        necessary: true,
        preferences: false,
        analytics: false,
        marketing: false,
      }, "reject_all");
    });
  }

  paint();
})();

// 40. Animations au scroll (GSAP ScrollTrigger, repli gracieux sans GSAP / reduced-motion)
(() => {
  const boot = () => {
    if (!window.gsap || !window.ScrollTrigger) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    gsap.registerPlugin(ScrollTrigger);

    // Titres de sections : montee en fondu
    gsap.utils.toArray("section h1, section h2").forEach((el) => {
      gsap.from(el, {
        y: 34,
        opacity: 0,
        duration: 0.9,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 88%", once: true },
      });
    });

    // Cards : apparition groupee en cascade (les reveals natifs projet/timeline sont exclus)
    const cards =
      "[data-service-card], [data-team-card], .blog-card, .bp-card, .faq-item, [data-process-step]";
    if (document.querySelector(cards)) {
      ScrollTrigger.batch(cards, {
        start: "top 92%",
        once: true,
        onEnter: (els) =>
          gsap.fromTo(
            els,
            { y: 40, opacity: 0 },
            {
              y: 0,
              opacity: 1,
              duration: 0.8,
              ease: "power3.out",
              stagger: 0.12,
              overwrite: true,
            },
          ),
      });
    }

    // Recalcule apres chargement complet (images, fonts, fin du preloader)
    window.addEventListener("load", () => ScrollTrigger.refresh());
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

// 41. Hero pills — carrousel une à une (desktop + responsive)
(() => {
  const viewport = document.querySelector(".hero-pills-viewport");
  if (!viewport) return;
  const track = viewport.querySelector(".hero-pills-track");
  const pills = track
    ? Array.from(track.querySelectorAll(".hero-pill"))
    : [];
  if (pills.length < 2) return;

  const prevBtn = document.querySelector(".hero-pills-prev");
  const nextBtn = document.querySelector(".hero-pills-next");
  const reducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  let index = 0;
  let paused = false;
  let timer = null;

  const goTo = (i) => {
    index = (i + pills.length) % pills.length;
    viewport.scrollTo({ left: pills[index].offsetLeft - 4, behavior: "smooth" });
  };

  const stop = () => {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  };

  const start = () => {
    stop();
    if (paused || reducedMotion || document.hidden) return;
    timer = setInterval(() => {
      if (!paused && !document.hidden) goTo(index + 1);
    }, 2800);
  };

  if (prevBtn) prevBtn.addEventListener("click", () => goTo(index - 1));
  if (nextBtn) nextBtn.addEventListener("click", () => goTo(index + 1));

  // Pause pendant l'interaction manuelle, reprise après
  viewport.addEventListener("pointerenter", () => {
    paused = true;
    stop();
  });
  viewport.addEventListener("pointerleave", () => {
    paused = false;
    // Recale l'index sur la pilule visible avant de reprendre
    const x = viewport.scrollLeft + 4;
    let best = 0;
    let minDist = Infinity;
    pills.forEach((p, i) => {
      const dist = Math.abs(p.offsetLeft - x);
      if (dist < minDist) {
        minDist = dist;
        best = i;
      }
    });
    index = best;
    start();
  });
  viewport.addEventListener("pointerdown", () => {
    paused = true;
    stop();
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stop();
    else if (!paused) start();
  });

  start();
})();
