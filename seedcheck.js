// P11 — regenerate every published seed from the build under test.
// Slices the world model out of the file and runs it with no DOM.
const fs = require('fs');

const html = fs.readFileSync(process.argv[2], 'utf8');
const claimed = JSON.parse(process.argv[3]);
const script = (html.match(/<script[^>]*>([\s\S]*?)<\/script>/g) || [])
  .map(s => s.replace(/<\/?script[^>]*>/g, '')).join('\n');
const lines = script.split('\n');

function slice(startsWith, endStartsWith) {
  const i = lines.findIndex(l => l.startsWith(startsWith));
  const j = lines.findIndex((l, k) => k > i && l.startsWith(endStartsWith));
  if (i < 0 || j < 0) throw new Error('could not slice ' + startsWith);
  return lines.slice(i, j).join('\n');
}

let core = slice('const CFG = {', 'function stars(n){')
         + '\nfunction stars(n){ return n; }\n';
const sun = slice('function sunGeom(turn){', 'function connectedSet(){');

// The slice touches the canvas once at load; nothing it needs is on it.
core = core
  .replace(/^const cv = document\.getElementById\('cv'\);/m,
           "const cv = {getContext(){return {};}, style:{}, width:0, height:0};")
  .replace(/^const ctx = cv\.getContext\('2d'\);/m, 'const ctx = {};');

const api = new Function(sun + '\n' + core +
  '; return {generateSite, codeToSeed};')();

let bad = 0, n = 0;
for (const [code, stars] of Object.entries(claimed)) {
  n++;
  const site = api.generateSite(api.codeToSeed(code));
  const ok = site && site.ok && site.code === code && site.difficulty.stars === stars;
  if (!ok) {
    bad++;
    console.log(`  ${code}: claimed ${stars}*, got ` +
      (site && site.ok ? `${site.difficulty.stars}* as ${site.code}` : 'no site'));
  }
}
console.log(`${n} codes checked, ${bad} wrong`);
process.exit(bad ? 1 : 0);
