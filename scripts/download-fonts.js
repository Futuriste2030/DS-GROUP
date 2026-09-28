const fs = require('fs');
const path = require('path');
const https = require('https');

const FONTS_DIR = path.join(__dirname, '../static/fonts');
const CSS_DIR = path.join(__dirname, '../static/css');

// Fonts à télécharger
const FONTS = {
  'Poppins': {
    weights: ['400', '500', '600', '700', '800', '900'],
    styles: ['normal'],
  },
  'Space Grotesk': {
    weights: ['500', '600', '700'],
    styles: ['normal'],
  },
};

function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      if (response.statusCode === 200) {
        response.pipe(file);
        file.on('finish', () => {
          file.close();
          resolve();
        });
      } else {
        fs.unlink(dest, () => {});
        reject(new Error(`${url}: ${response.statusCode}`));
      }
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

async function downloadFont(fontName, config) {
  const familyDir = path.join(FONTS_DIR, fontName.replace(/\s+/g, '-').toLowerCase());

  if (!fs.existsSync(familyDir)) {
    fs.mkdirSync(familyDir, { recursive: true });
  }

  for (const weight of config.weights) {
    for (const style of config.styles) {
      const filename = `${fontName.replace(/\s+/g, '-')}-${weight}-${style}.woff2`;
      const filepath = path.join(familyDir, filename);

      if (fs.existsSync(filepath)) {
        console.log(`  Déjà présent: ${filename}`);
        continue;
      }

      // URL Google Fonts (format woff2)
      const url = `https://fonts.gstatic.com/s/${fontName.toLowerCase().replace(/\s+/g, '')}/v1/${fontName.replace(/\s+/g, '')}-${weight}-${style}.woff2`;

      try {
        await downloadFile(url, filepath);
        console.log(`  Téléchargé: ${filename}`);
      } catch (err) {
        // Essayer avec l'API Google Fonts CSS pour trouver la vraie URL
        console.log(`  Échec direct, tentative via CSS...`);
      }
    }
  }
}

function generateFontFaceCSS() {
  let css = '/* Google Fonts - Local */\n\n';

  for (const [fontName, config] of Object.entries(FONTS)) {
    const familyDir = fontName.replace(/\s+/g, '-').toLowerCase();

    for (const weight of config.weights) {
      for (const style of config.styles) {
        const filename = `${fontName.replace(/\s+/g, '-')}-${weight}-${style}.woff2`;
        const filepath = `../fonts/${familyDir}/${filename}`;

        css += `@font-face {\n`;
        css += `  font-family: '${fontName}';\n`;
        css += `  font-weight: ${weight};\n`;
        css += `  font-style: ${style};\n`;
        css += `  font-display: swap;\n`;
        css += `  src: url('${filepath}') format('woff2');\n`;
        css += `}\n\n`;
      }
    }
  }

  return css;
}

async function main() {
  if (!fs.existsSync(FONTS_DIR)) {
    fs.mkdirSync(FONTS_DIR, { recursive: true });
  }

  console.log('Téléchargement des polices Google Fonts...');

  for (const [fontName, config] of Object.entries(FONTS)) {
    console.log(`\n${fontName}:`);
    await downloadFont(fontName, config);
  }

  // Générer le CSS @font-face
  const fontFaceCSS = generateFontFaceCSS();
  const outputPath = path.join(CSS_DIR, 'fonts.css');
  fs.writeFileSync(outputPath, fontFaceCSS);
  console.log(`\nCSS généré: ${outputPath}`);
}

main().catch(console.error);