const fs = require('fs');
const path = require('path');
const https = require('https');

const ICONS_DIR = path.join(__dirname, '../static/icons/lucide');
// jsdelivr (paquet lucide-static) : sert les anciens ET nouveaux noms,
// contrairement à raw.githubusercontent qui ne garde que les canoniques.
const BASE_URL = 'https://cdn.jsdelivr.net/npm/lucide-static/icons';

// Icônes réellement utilisées dans les templates
const ICONS = [
  'sparkles', 'check', 'check-circle-2', 'chevron-left', 'chevron-right',
  'chevron-down', 'chevron-up', 'arrow-right', 'arrow-left', 'arrow-down',
  'arrow-up', 'home', 'building-2', 'book-open', 'users', 'calculator',
  'layers', 'briefcase', 'help-circle', 'mail', 'phone', 'map-pin',
  'clock', 'mail-check', 'badge-check', 'hash', 'rotate-ccw',
  'navigation', 'fuel', 'wrench', 'shapes', 'hard-hat',
  'heart-pulse', 'graduation-cap', 'piggy-bank', 'calendar-check',
  'baby', 'rocket', 'headphones', 'paperclip', 'file-text',
  'x', 'play', 'search-x', 'message-circle', 'send',
  'facebook', 'twitter', 'linkedin', 'instagram', 'youtube',
  'pinterest', 'star', 'truck', 'shield-check', 'clock',
  'trending-up', 'target', 'award', 'zap', 'cog',
  'download', 'upload', 'eye', 'eye-off', 'copy',
  'edit', 'trash', 'plus', 'minus', 'filter',
  'sun', 'moon', 'globe', 'menu', 'maximize', 'minimize',
  'external-link', 'link', 'unlink', 'share', 'share-2',
  'layout', 'sidebar', 'panel-left', 'panel-right', 'align-left',
  'align-center', 'align-right', 'indent', 'outdent', 'type',
  'bold', 'italic', 'underline', 'strikethrough', 'code',
  'terminal', 'database', 'server', 'hard-drive', 'cpu',
  'monitor', 'smartphone', 'tablet', 'laptop', 'watch',
  'camera', 'mic', 'mic-off', 'speaker', 'volume', 'volume-2',
  'volume-x', 'headphones', 'music', 'skip-back', 'skip-forward',
  'play', 'pause', 'stop', 'square', 'circle', 'triangle',
  'diamond', 'hexagon', 'octagon', 'pentagon', 'star',
  'heart', 'user', 'users', 'user-plus', 'user-minus',
  'user-check', 'user-x', 'user-cog', 'log-in', 'log-out',
  'lock', 'unlock', 'key', 'shield', 'shield-check',
  'shield-alert', 'shield-x', 'fingerprint', 'eye', 'eye-off',
  'scan', 'qr-code', 'barcode', 'ticket', 'tag', 'tags',
  'bookmark', 'bookmark-minus', 'bookmark-plus', 'bookmark-x',
  'flag', 'mail', 'mail-plus', 'mail-minus', 'mail-x',
  'mail-check', 'mail-open', 'mail-question', 'mail-search',
  'send', 'send-horizontal', 'inbox', 'outbox', 'archive',
  'archive-restore', 'trash', 'trash-2', 'rotate-ccw', 'rotate-cw',
  'refresh-cw', 'refresh-ccw', 'history', 'clock', 'alarm-clock',
  'calendar', 'calendar-days', 'calendar-range', 'calendar-check',
  'calendar-minus', 'calendar-plus', 'calendar-x', 'calendar-search',
  'timer', 'stopwatch', 'hourglass', 'sunrise', 'sunset',
  'cloud', 'cloud-drizzle', 'cloud-lightning', 'cloud-rain',
  'cloud-snow', 'cloud-fog', 'wind', 'tornado', 'thermometer',
  'droplets', 'droplet', 'wave', 'waves', 'umbrella'
];

// Anciens noms (utilisés dans les templates / la DB) -> nom canonique actuel.
// Le fichier est enregistré SOUS L'ANCIEN NOM pour ne rien changer ailleurs.
const ALIASES = {
  'alert-triangle': 'triangle-alert',
  'check-circle-2': 'circle-check-big',
  'help-circle': 'circle-help',
  'bar-chart-3': 'chart-column',
  'upload-cloud': 'cloud-upload',
};

// Icônes utilisées dans les templates mais absentes de ICONS ci-dessus
// (vérifié par croisement data-lucide <-> static/icons/lucide).
const EXTRA_ICONS = [
  'alert-triangle', 'banknote', 'bar-chart-3', 'bot', 'building',
  'check-circle-2', 'chevrons-right', 'circle-slash', 'clipboard-list',
  'cookie', 'credit-card', 'file-badge', 'file-clock', 'headset',
  'help-circle', 'landmark', 'leaf', 'megaphone', 'pencil', 'scale',
  'settings-2', 'stamp', 'trash-2', 'upload-cloud', 'wallet',
];

const ALL_ICONS = [...new Set([...ICONS, ...EXTRA_ICONS])];

function downloadIcon(iconName) {
  // Le fichier final garde toujours l'ancien nom (compat templates/DB).
  const filePath = path.join(ICONS_DIR, `${iconName}.svg`);

  const tryFetch = (url) => new Promise((resolve, reject) => {
    // Écrit d'abord en temporaire : un échec ne détruit jamais l'existant.
    const tmpPath = `${filePath}.tmp`;
    const file = fs.createWriteStream(tmpPath);
    const req = https.get(url, (response) => {
      if (response.statusCode === 200) {
        response.pipe(file);
        file.on('finish', () => {
          file.close();
          fs.rename(tmpPath, filePath, (err) => {
            if (err) reject(err);
            else resolve(iconName);
          });
        });
      } else {
        response.resume();
        file.close(() => fs.unlink(tmpPath, () => {}));
        reject(new Error(`${iconName}: ${response.statusCode}`));
      }
    });
    req.on('error', (err) => {
      file.close(() => fs.unlink(tmpPath, () => {}));
      reject(err);
    });
    req.setTimeout(15000, () => {
      req.destroy();
      file.close(() => fs.unlink(tmpPath, () => {}));
      reject(new Error(`${iconName}: timeout`));
    });
  });

  // Essaie l'ancien nom puis le nom canonique (renommages lucide).
  async function downloadWithFallback() {
    const urls = [`${BASE_URL}/${iconName}.svg`];
    if (ALIASES[iconName]) urls.push(`${BASE_URL}/${ALIASES[iconName]}.svg`);
    let lastErr = new Error(`${iconName}: no candidate`);
    for (const url of urls) {
      try {
        await tryFetch(url);
        return iconName;
      } catch (err) {
        lastErr = err;
      }
    }
    throw lastErr;
  }

  return downloadWithFallback();
}

async function main() {
  if (!fs.existsSync(ICONS_DIR)) {
    fs.mkdirSync(ICONS_DIR, { recursive: true });
  }

  console.log(`Téléchargement de ${ALL_ICONS.length} icônes Lucide...`);

  let success = 0;
  let failed = 0;
  const failedNames = [];

  // Télécharger par petits lots pour ne pas surcharger (anti rate-limit)
  for (let i = 0; i < ALL_ICONS.length; i += 5) {
    const batch = ALL_ICONS.slice(i, i + 5);
    const promises = batch.map(icon => downloadIcon(icon).catch(err => ({ error: err.message, icon })));
    const results = await Promise.all(promises);

    for (const result of results) {
      if (result.error) {
        failed++;
        failedNames.push(result.icon);
        process.stdout.write('F');
      } else {
        success++;
        process.stdout.write('.');
      }
    }
    await new Promise((r) => setTimeout(r, 800));
  }

  console.log(`\nTerminé: ${success} succès, ${failed} échecs`);
  if (failedNames.length) console.log('Échecs:', failedNames.join(', '));
  console.log(`Icônes dans: ${ICONS_DIR}`);
}

main();