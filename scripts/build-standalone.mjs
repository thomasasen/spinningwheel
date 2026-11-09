/**
 * Rebuild the self-contained Casino Noir HTML from the modular release.
 * No downloads, dependencies, or external code are used during bundling.
 * Usage: node scripts/build-standalone.mjs [project-directory]
 */
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const base=process.argv[2] ? resolve(process.argv[2]) :
  resolve(fileURLToPath(new URL('..',import.meta.url)));
const read=name=>readFileSync(resolve(base,name),'utf8');
let html=read('index.html');
const css=read('styles.css');
const physics=read('wheel-physics.js');
const app=read('app.js');
const icons=read('icon-search-index.json');
const data=JSON.parse(icons);
if(data.version!==1||!Array.isArray(data.icons)||data.icons.length<3800)
  throw Error('Ungültiger Symbol-Suchindex; Standalone nicht erstellt.');
function replaceExactlyOnce(text,pattern,replacement,name){
  const matches=[...text.matchAll(pattern)];
  if(matches.length!==1)throw Error(name+': erwartet genau eine Stelle, gefunden '+matches.length);
  return text.replace(pattern,replacement);
}
html=replaceExactlyOnce(html,/<link\s+rel="stylesheet"\s+href="styles\.css[^"]*"\s*\/?>/g,
  ()=>'<style>\n'+css+'\n</style>','Stylesheet');
const deferred=/<script\s+defer\s+src="(?:wheel-physics|app)\.js[^"]*"><\/script>/g;
const tags=[...html.matchAll(deferred)];
if(tags.length!==2||!tags[0][0].includes('wheel-physics')||!tags[1][0].includes('app.js'))
  throw Error('Unerwartete Script-Reihenfolge in index.html');
html=html.replace(deferred,'');
function inlineScript(source){
  // Never allow an embedded JS literal to close its HTML script element.
  return '<script>\n'+source.replace(/<\/script/gi,'<\\/script')+'\n</script>';
}
const inlineIcons='<script id="iconSearchIndexData" type="application/json">\n'+
  icons.replace(/</g,'\\u003c')+'\n</script>';
const bundle='\n<!-- Built from the current modular Casino Noir sources. -->\n'+
  inlineIcons+'\n'+inlineScript(physics)+'\n'+inlineScript(app)+'\n';
html=replaceExactlyOnce(html,/<\/body>/g,()=>bundle+'</body>','Ende des Dokuments');
if(html.includes('src="app.js')||html.includes('src="wheel-physics.js')||
   html.includes('href="styles.css'))
  throw Error('Nicht alle modularen Assets wurden eingebettet.');
writeFileSync(resolve(base,'casino-noir-standalone.html'),html,'utf8');
console.log('Casino Noir Standalone generiert: '+Buffer.byteLength(html)+' Bytes, '+data.icons.length+' Symbol-Metadaten.');
