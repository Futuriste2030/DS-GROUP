/**
 * Lucide Icons Loader - Charge les icônes SVG depuis le dossier local
 * Remplace le CDN unpkg.com/lucide@latest
 */

(function() {
  'use strict';

  const ICONS_PATH = window.LUCIDE_ICONS_PATH || '/static/icons/lucide';
  const ICON_CACHE = new Map();

  // Remplace <i data-lucide="icon-name"> par le SVG inline
  function replaceLucideIcons() {
    const elements = document.querySelectorAll('[data-lucide]');

    elements.forEach(async (el) => {
      const iconName = el.getAttribute('data-lucide');
      if (!iconName) return;

      // Classes et attributs à préserver
      const classes = el.className || '';
      const style = el.style.cssText || '';
      const ariaLabel = el.getAttribute('aria-label') || '';
      const ariaHidden = el.getAttribute('aria-hidden') || 'true';

      try {
        const svg = await loadIcon(iconName);
        if (svg) {
          // Cloner le SVG pour éviter les modifications sur le cache
          const svgClone = svg.cloneNode(true);

          // Appliquer les classes et styles
          if (classes) {
            svgClone.setAttribute('class', classes);
          }
          if (style) {
            svgClone.setAttribute('style', style);
          }
          svgClone.setAttribute('aria-hidden', ariaHidden);
          if (ariaLabel) {
            svgClone.setAttribute('aria-label', ariaLabel);
          }

          // Remplacer l'élément
          el.replaceWith(svgClone);
        }
      } catch (err) {
        console.warn(`Lucide: impossible de charger l'icône "${iconName}"`, err);
      }
    });
  }

  async function loadIcon(name) {
    if (ICON_CACHE.has(name)) {
      return ICON_CACHE.get(name);
    }

    const url = `${ICONS_PATH}/${name}.svg`;

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const svgText = await response.text();

      // Parser le SVG
      const parser = new DOMParser();
      const doc = parser.parseFromString(svgText, 'image/svg+xml');
      const svg = doc.documentElement;

      // Normaliser le SVG
      svg.removeAttribute('xmlns');
      svg.removeAttribute('xmlns:xlink');
      svg.setAttribute('width', '100%');
      svg.setAttribute('height', '100%');
      svg.setAttribute('fill', 'none');
      svg.setAttribute('stroke', 'currentColor');
      svg.setAttribute('stroke-width', '2');
      svg.setAttribute('stroke-linecap', 'round');
      svg.setAttribute('stroke-linejoin', 'round');

      ICON_CACHE.set(name, svg);
      return svg;
    } catch (err) {
      console.warn(`Lucide: icône "${name}" non trouvée à ${url}`);
      ICON_CACHE.set(name, null);
      return null;
    }
  }

  // Précharger les icônes visibles au chargement initial
  function preloadVisibleIcons() {
    const elements = document.querySelectorAll('[data-lucide]');
    const names = [...new Set(Array.from(elements).map(el => el.getAttribute('data-lucide')).filter(Boolean))];

    // Précharger en arrière-plan (sans bloquer)
    names.forEach(name => {
      if (!ICON_CACHE.has(name)) {
        fetch(`${ICONS_PATH}/${name}.svg`).catch(() => {});
      }
    });
  }

  // Initialisation
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      preloadVisibleIcons();
      replaceLucideIcons();
    });
  } else {
    preloadVisibleIcons();
    replaceLucideIcons();
  }

  // Exposer pour les ajouts dynamiques
  window.lucide = {
    createIcon: loadIcon,
    replace: replaceLucideIcons,
  };
})();