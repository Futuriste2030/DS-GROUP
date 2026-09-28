const fs = require('fs');
const path = require('path');
const https = require('https');

const ICONS_DIR = path.join(__dirname, '../static/icons/lucide');
const BASE_URL = 'https://raw.githubusercontent.com/lucide-icons/lucide/main/icons';

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

function downloadIcon(iconName) {
  const url = `${BASE_URL}/${iconName}.svg`;
  const filePath = path.join(ICONS_DIR, `${iconName}.svg`);

  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filePath);
    const req = https.get(url, (response) => {
      if (response.statusCode === 200) {
        response.pipe(file);
        file.on('finish', () => {
          file.close();
          resolve(iconName);
        });
      } else {
        fs.unlink(filePath, () => {});
        reject(new Error(`${iconName}: ${response.statusCode}`));
      }
    });
    req.on('error', (err) => {
      fs.unlink(filePath, () => {});
      reject(err);
    });
    req.setTimeout(10000, () => {
      req.destroy();
      fs.unlink(filePath, () => {});
      reject(new Error(`${iconName}: timeout`));
    });
  });
}

async function main() {
  if (!fs.existsSync(ICONS_DIR)) {
    fs.mkdirSync(ICONS_DIR, { recursive: true });
  }

  console.log(`Téléchargement de ${ICONS.length} icônes Lucide...`);

  let success = 0;
  let failed = 0;

  // Télécharger par lots de 10 pour ne pas surcharger
  for (let i = 0; i < ICONS.length; i += 10) {
    const batch = ICONS.slice(i, i + 10);
    const promises = batch.map(icon => downloadIcon(icon).catch(err => ({ error: err.message, icon })));
    const results = await Promise.all(promises);

    for (const result of results) {
      if (result.error) {
        failed++;
        process.stdout.write('F');
      } else {
        success++;
        process.stdout.write('.');
      }
    }
  }

  console.log(`\nTerminé: ${success} succès, ${failed} échecs`);
  console.log(`Icônes dans: ${ICONS_DIR}`);
}

main();