import {build} from 'esbuild';
import fs from 'node:fs';
await build({stdin:{contents:"import mermaid from 'mermaid';window.PaperMermaid=mermaid;",resolveDir:process.cwd()},bundle:true,minify:true,format:'iife',platform:'browser',target:'es2020',outfile:'src/paperweave/static/mermaid.bundle.js',legalComments:'eof'});
fs.copyFileSync('node_modules/mermaid/LICENSE','licenses/Mermaid-MIT.txt');
console.log('Built single-file offline Mermaid bundle.');
