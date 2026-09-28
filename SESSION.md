# État session — DS-GROUP (reprise : relire ce fichier + `python manage.py check`)

## Fait (front)
- Responsive 324px : switch langue (topbar allégée), hero (accroche/pills/titre), tous les `<p>` (13.5px), preloader recentré.
- About : 2e paragraphe (page about uniquement) ; labels Mission/Vision une ligne ; slider texte 14px.
- Careers home : hachures `features-hatch` retirées de `#careers-home`.
- About showcase : bandeau stats sous la vidéo en mobile (plus de masquage Play) ; 32px à 768px ; `plans-play-btn` branché à la modale.
- `projet-detail.html` : « Plan, Build, Succeed » en blanc.
- Blog-detail : sidebars sticky (gauche partage + droite widgets, sticky naturel).
- Contact/quote : CTA header uniformisés (« Demander un devis », ancre `#quote` sur devis).
- Filigranes `section-tag` étendus à toutes les pages/sections.

## Fait (backend Django 5.2, Python 3.14)
- Projet `bsgroup` + 8 apps (`core` + 7 métier) : `main` (home, about, faqs, légales, coming), `services` (services+detail slug), `team` (team+detail slug, testimonials), `projects` (projets+detail slug), `blog` (blogs+detail slug, filtre/recherche/pagination), `careers` (careers+detail slug, apply, success), `contact` (contact, devis, thanks/<ref>, thank-devis/<ref>, newsletter).
- Layout pro : `static/{css,js,img}` + `templates/<app>/` + `{% static %}`/`{% url %}` partout.
- `templates/base.html` + `partials/_preloader|_header|_footer.html` (header actifs dynamiques via `resolver_match` ; footer = newsletter + footer + cookie + chatbot + back-to-top + scripts).
- 34 templates : 23 pages en `{% extends %}` + 3 partials + `contact/thank-devis.html` + 6 `email/mail-*.html` + `base.html` ; video-modal reste dans contenu index/about ; form coming `notify-form` + handler JS.
- Vérifié : 20/20 routes 200 (+ /en/, /ar/), 1 seul header/footer/preloader par page, actifs OK, `node --check` OK.
- Lancer : `python manage.py runserver`. `ALLOWED_HOSTS` inclut 127.0.0.1/localhost/testserver.

## Fait (logique DIGI-AGENCY répliquée, design detail intact)
- Traduction FR/EN/AR, 2 couches comme DIGI : (1) `.po` statiques `{% trans %}`/`gettext` → `locale/fr+en+ar/LC_MESSAGES/django.po/.mo` (25 entrées, compilés via polib car gettext absent Windows), header/footer/base traduits (Home→Accueil→الرئيسية, Request a Quote→Demander un devis→اطلب عرض سعر, RTL sur AR) ; (2) admin DB `modeltranslation` (champs `_fr/_en/_ar`, onglets `TabbedTranslationAdmin`). FR défaut sans préfixe, EN `/en/`, AR `/ar/`, `LocaleMiddleware` + `i18n_patterns`, switch JS par préfixe.
- `{% trans %}` étendus (27/09, logique DIGI msgid=EN) : `base.html` (fallbacks title/meta/OG/Twitter), `_preloader.html`, `_header.html` (Menu mobile, About/Pages), `_footer.html` (newsletter, CTA « Let's Connect there », nav, mini-newsletter, copyright, back-to-top, cookie banner+modal, chat panel+quick replies+placeholder). JS via `partials/_js_i18n.html` (`window.BSG_STRINGS`, langue courante) + `script.js` patché (preloader, chatbot FR/EN/AR dont marque Conztru→BS GROUP, validations, toasts, thanks, consentement ; locale dates via `<html lang>` comme DIGI). `locale/.../django.po/.mo` = 269 entrées, compilés via `python compile_translations.py` (stdlib, sans gettext).
- Dynamique par slug : Service (+features/benefits/steps), Project (+points/steps), Post (tags/categories/recent/related), TeamMember (+experiences/certifications/skills parse + Testimonial), JobOpening (+responsibilities/requirements/nice + Perk/CareerPage/Application), SiteSettings singleton + FAQ/Partner/Stats/Skills/Process/Feature/LegalPage.
- Home + About dynamisés (design intact, fallbacks `{% empty %}`) : hero (`hero_badge/title/description`), stats boucle, about (`about_*`, vision/mission, images), process/features/FAQ/skills boucles, team boucle slug. About admin = `SiteSettings` (section About) + `SiteStat/SkillBar/ProcessStep/Feature/FAQ/TeamMember` (pas de modèle `About` dédié, comme DIGI).
- Formulaires → DB + emails HTML console (logique DIGI : 2 mails/formulaire via `templates/email/`) : contact (réf `MS-YYYY-NNNN`), devis/quote wizard (réf `QT-YYYY-NNNN`, détails projet enrichis), newsletter, notify coming, candidatures avec CV (réf `BS-YYYY-...`). Devis → même adresse interne que contact (`CONTACT_EMAIL`). Redirects : contact/candidature → `thanks/<reference>/`, devis → `thank-devis/<reference>/` (404 si ref inconnue, `thanks/` générique conservé). JS suit le redirect serveur (`response.url`), plus de fausse ref locale ; `thanks.html`/`thank-devis.html` affichent la ref serveur (`data-server-ref`).
- Détails : HTML/classes/ids 100% inchangés, seules variables `{{ }}`/`{% for %}` injectées + fallbacks statiques en `{% empty %}`. Listes + index en boucles dynamiques.
- `handler404/500` branchés (`main/404.html`), `media/` servi, `core/seo.py` + `core/utils.sender_address` + `core/context_processors.get_site_settings`. Slugs sécurisés anti-`''` (fallback fr→en→défaut + unicité).
- Vérifié (24/09) : `migrate` OK (`contact.0002` refs appliquée), `check` 0 erreur, `node --check` OK, `/`, `/about/`, `/services/`, `/en/`, `/ar/` 200, 5 détails slug 200 FR+EN, FR `Accueil/Demander un devis` + EN `Home/Request a Quote` + AR `اتصل بنا` + RTL OK, dynamique admin FR/EN/AR OK, contact POST 302 → `/thanks/MS-.../` 200 + 2 mails HTML, devis POST 302 → `/thank-devis/QT-.../` 200 + 2 mails HTML (interne = `CONTACT_EMAIL`), thanks/thank-devis fake → 404, newsletter POST + sauvegarde, 404 → 404 custom.
- Lancer : `python manage.py runserver`, admin `/admin/` (1 superuser existe, SiteSettings singleton, contenus traduisibles FR/EN/AR).

## Fait (chatbot Gemini, parité DIGI-AGENCY)
- `.env` (gitignoré) + `settings.py` via `python-decouple` (SECRET_KEY/DEBUG/HOSTS/CANONICAL_DOMAIN/emails) + `requirements.txt` (`python-decouple`, `google-genai`), même clé `GEMINI_API_KEY` que DIGI.
- Nouvelle app `chatbot` : `Conversation/Message/ChatbotKnowledge` (+ admin, migration `0001` appliquée), RAG `services/search.py` adapté aux modèles BS (services/projets/blog/team/main/careers + singleton SiteSettings, FR/EN/AR, garde anti-champ-inexistant), `services/context.py` (prompt système BS GROUP, messages FR/EN/AR), `services/gemini.py` (sync + stream, retry), `views.py` (`POST /api/chat/` + `/api/chat/stream/`, rate-limit, sessions), monté sur `path('api/')` hors i18n.
- Frontend `script.js` : le chat appelle `/api/chat/` (langue + session + CSRF), repli hors-ligne sur réponses locales si API KO.
- Vérifié : `migrate` OK, `check` 0 erreur, `node --check` OK, `POST /api/chat/` 200 `success:true` (réponse « no info » car DB locale vide → grounding OK), 400 vide, 405 GET.
- Reste : remplir contenus via admin (+ entrées ChatbotKnowledge) pour des réponses ancrées.

## Fait (vidéo admin + cookies RGPD, parité DIGI-AGENCY)
- Vidéo : `SiteSettings` a désormais un fieldset « Vidéo du site » (`about_video_url` + `about_video_cover` avec help_texts) ; modales index/about portent `data-video-url` + `<iframe>` YouTube ; covers showcase/why = `about_video_cover` → `about_image_1` → démo ; JS modale lit l'URL admin (MP4 direct ou YouTube watch/youtu.be/embed/shorts → embed autoplay), stop à la fermeture, repli démo si vide.
- Cookies : modèles `CookieConsent`/`CookieConsentLog` (+ admin preuves + inline logs, migration `main.0002` appliquée, `makemigrations --check` clean), `core/middleware.py` (lecture sans créer de session), settings `COOKIE_*`/`CONSENT_*`, `POST/GET /api/cookie-consent/`, commande `cleanup_consents`, JS bannière + page cookies synchronisés serveur (statistics=analytics, marketing=marketing, actions accept_all/reject_all/save_prefs/sync, `window.__consentId`).
- Vérifié : `migrate` OK, `check` 0 erreur, `node --check` OK, cookie GET 200 `has_consented False` → POST 200 + cookie `consent_id` → GET `has_consented True`, 400 JSON invalide, modale `data-video-url` + `video-iframe` rendus, `{%` à 0, admins 302 login, `cleanup_consents --dry-run` OK.
- Vidéo hero dédiée : champs `hero_video_url`/`hero_video_cover` (migration `main.0003` appliquée, fieldset Hero admin), cadre hero + modale index = hero → repli About → démo ; aria play + showcase About traduits ; `.po/.mo` = 269 entrées, FR/EN/AR 200 vérifiés.
- Vidéo détails (parité DIGI) : `Service`/`Project` += `video_cover`/`video_cover_alt` (traduit FR/EN/AR)/`video_url` (migrations `services.0002`+`projects.0002` appliquées, champs visibles en admin par défaut), bannière vidéo conditionnelle + modale sur service-detail/projet-detail, JS générique (`[data-video-banner]` → modale avec son URL, garde anti-event), modales request traduites ; `.po/.mo` = 269 entrées ; vérifié 200 FR/EN + data-video-url YouTube/MP4 + objets test supprimés.

## Fait (déploiement production — 28/09)
- **Docker** : `Dockerfile` multi-stage (builder→runtime), `docker-entrypoint.sh` (migrate, compilemessages, collectstatic, superuser optionnel), `docker-compose.yml` (web+nginx+certbot, SQLite volume), `nginx/conf.d/bsgroup.conf` (HTTPS, HSTS, CSP, rate limiting `/api/chat/` `/api/cookie-consent/`, cache static/media, www→non-www), `.dockerignore`, `.env.prod.example`.
- **Settings prod** : `CSRF_TRUSTED_ORIGINS`, `SECURE_SSL_REDIRECT`, HSTS, cookies sécurisés, WhiteNoise + `CompressedManifestStaticFilesStorage`, SQLite via `dj-database-url` (volume persistant), SMTP via env.
- **Assets locaux** (pas CDN) : Tailwind build local (`npm run build` → `static/css/tailwind.css`), Lucide 181 SVG locaux (`static/icons/lucide/`) + `lucide-loader.js`, Google Fonts CDN + `preconnect` + fallback `static/css/fonts.css`.
- **SEO dynamique** : `SEOMixin` sur tous modèles (meta_title/description, og_*, twitter_card, canonical, noindex), `seo_for()`, sitemaps canoniques HTTPS + hreflang FR/EN/AR, fallbacks auto (title→meta_title, excerpt→meta_description).
- **WebP auto** : `WebPConversionMixin` sur tous modèles images (Service, Project, Post, TeamMember, Testimonial, Partner, SiteSettings, CareerPage) — redimension 1920px max → WebP qualité 82 → extension `.webp` à l'upload.
- **Traductions** : 269 entrées FR/EN/AR compilées, templates i18n mis à jour (contact, devis, thanks, thank-devis, 404, blog-detail).
- **Emails SMTP testés** (réel `bsgroup.ml:465` SSL) : contact/devis/candidature → 2 emails chacun (user + équipe/RH vers bonnes adresses `contact@bsgroup.ml` / `hr@bsgroup.ml`).

## Fait (chatbot Gemini, parité DIGI-AGENCY)
- `.env` (gitignoré) + `settings.py` via `python-decouple` (SECRET_KEY/DEBUG/HOSTS/CANONICAL_DOMAIN/emails) + `requirements.txt` (`python-decouple`, `google-genai`), même clé `GEMINI_API_KEY` que DIGI.
- Nouvelle app `chatbot` : `Conversation/Message/ChatbotKnowledge` (+ admin, migration `0001` appliquée), RAG `services/search.py` adapté aux modèles BS (services/projets/blog/team/main/careers + singleton SiteSettings, FR/EN/AR, garde anti-champ-inexistant), `services/context.py` (prompt système BS GROUP, messages FR/EN/AR), `services/gemini.py` (sync + stream, retry), `views.py` (`POST /api/chat/` + `/api/chat/stream/`, rate-limit, sessions), monté sur `path('api/')` hors i18n.
- Frontend `script.js` : le chat appelle `/api/chat/` (langue + session + CSRF), repli hors-ligne sur réponses locales si API KO.
- Vérifié : `migrate` OK, `check` 0 erreur, `node --check` OK, `POST /api/chat/` 200 `success:true` (réponse « no info » car DB locale vide → grounding OK), 400 vide, 405 GET.
- Reste : remplir contenus via admin (+ entrées ChatbotKnowledge) pour des réponses ancrées.

## Fait (vidéo admin + cookies RGPD, parité DIGI-AGENCY)
- Vidéo : `SiteSettings` a désormais un fieldset « Vidéo du site » (`about_video_url` + `about_video_cover` avec help_texts) ; modales index/about portent `data-video-url` + `<iframe>` YouTube ; covers showcase/why = `about_video_cover` → `about_image_1` → démo ; JS modale lit l'URL admin (MP4 direct ou YouTube watch/youtu.be/embed/shorts → embed autoplay), stop à la fermeture, repli démo si vide.
- Cookies : modèles `CookieConsent`/`CookieConsentLog` (+ admin preuves + inline logs, migration `main.0002` appliquée, `makemigrations --check` clean), `core/middleware.py` (lecture sans créer de session), settings `COOKIE_*`/`CONSENT_*`, `POST/GET /api/cookie-consent/`, commande `cleanup_consents`, JS bannière + page cookies synchronisés serveur (statistics=analytics, marketing=marketing, actions accept_all/reject_all/save_prefs/sync, `window.__consentId`).
- Vérifié : `migrate` OK, `check` 0 erreur, `node --check` OK, cookie GET 200 `has_consented False` → POST 200 + cookie `consent_id` → GET `has_consented True`, 400 JSON invalide, modale `data-video-url` + `video-iframe` rendus, `{%` à 0, admins 302 login, `cleanup_consents --dry-run` OK.
- Vidéo hero dédiée : champs `hero_video_url`/`hero_video_cover` (migration `main.0003` appliquée, fieldset Hero admin), cadre hero + modale index = hero → repli About → démo ; aria play + showcase About traduits ; `.po/.mo` = 269 entrées, FR/EN/AR 200 vérifiés.
- Vidéo détails (parité DIGI) : `Service`/`Project` += `video_cover`/`video_cover_alt` (traduit FR/EN/AR)/`video_url` (migrations `services.0002`+`projects.0002` appliquées, champs visibles en admin par défaut), bannière vidéo conditionnelle + modale sur service-detail/projet-detail, JS générique (`[data-video-banner]` → modale avec son URL, garde anti-event), modales request traduites ; `.po/.mo` = 269 entrées ; vérifié 200 FR/EN + data-video-url YouTube/MP4 + objets test supprimés.

## À faire (demain — déploiement)
1. Sur serveur : `cp .env.prod.example .env.prod` + éditer secrets (SECRET_KEY, EMAIL_HOST_PASSWORD=Noreply@bsgroup223, GEMINI_API_KEY, HR_EMAIL=hr@bsgroup.ml, etc.)
2. `npm run build` (Tailwind + assets)
3. `docker compose --env-file .env.prod up -d --build`
4. Premier déploiement seulement : créer superuser si pas dans `.env.prod`
5. Tester `https://bsgroup.ml` + formulaires (contact, devis, candidature)
6. Vérifier emails reçus dans `contact@bsgroup.ml`, `hr@bsgroup.ml`, `abdoulaye208.mac@gmail.com`

## À faire (optionnel)
1. Étendre `{% trans %}` aux derniers templates restants si besoin.
2. Remplir contenus réels via admin + `collectstatic` prod + SMTP prod (actuellement console pour dev).
3. Ajouter entrées `ChatbotKnowledge` via admin pour réponses ancrées.

## Autre
- Logique source : `DIGI-AGENCY` (modeltranslation 5 langues fr/en/it/es/ar + dynamique slug + emails). DS-GROUP = même logique en FR/EN/AR, design BS GROUP intact.
- `python manage.py check` → 0 erreurs. `npm run build` → OK. Traductions compilées. Migrations à jour.