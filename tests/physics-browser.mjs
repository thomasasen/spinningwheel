import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';

const require=createRequire(import.meta.url);
const physics=require('../wheel-physics.js');
function wedges(sizes){
  const total=sizes.reduce((a,b)=>a+b,0);
  let start=-90-(360*sizes[0]/total)/2;
  return sizes.map(v=>{const size=360*v/total;const r={start,end:start+size,center:start+size/2,size};start+=size;return r;});
}
function seeded(i){
  let state=(i+1)>>>0;
  return ()=>{
    state=(Math.imul(state,1664525)+1013904223)>>>0;
    return state/4294967296;
  };
}
const geo=wedges(Array(8).fill(1));
const winners=new Set(),offsets=[];
for(let i=0;i<350;i++){
  const state=physics.create({
    angle:i*17.317,power:(i%101)/100,duration:3+(i%6),
    coast:(i*19)%101,pointerIntensity:60,pointerSpring:65,
    geometry:geo,random:seeded(i)
  });
  const initial=state.angle;
  physics.finish(state);
  assert.equal(state.done,true);
  assert.equal(state.velocity,0);
  assert.ok(state.angle>initial,'mechanical spin must advance the wheel');
  assert.ok(state.contacts>0,'segment contacts must contribute energy loss');
  assert.ok(state.elapsed<=state.limitSeconds+1e-3);
  const winner=physics.sectorAt(state.angle,geo);
  winners.add(winner);
  const sector=geo[winner];
  const offset=(((-90-state.angle-sector.start)%360)+360)%360;
  assert.ok(offset>=0&&offset<sector.size+1e-5,'final angle, not a preselected index, determines result');
  offsets.push(offset/sector.size);
}
assert.ok(winners.size===8,'the emergent winner must vary across all eight sectors');
assert.ok(offsets.filter(x=>x<.3||x>.7).length>100,
  'physical landings must span the wedges, not always the sector center');
assert.ok(offsets.some(x=>x<.08),'physical landings should sometimes approach a boundary');
assert.ok(offsets.some(x=>x>.92),'physical landings should sometimes approach the other boundary');

// 0-area sectors are never selected in a genuinely geometrical wheel.
const wedgeWithZero=wedges([0,1,3,0,1]);
for(let i=0;i<65;i++){
  const state=physics.create({geometry:wedgeWithZero,angle:i*13,power:.35,random:seeded(i)});
  physics.finish(state);
  const winner=physics.sectorAt(state.angle,wedgeWithZero);
  assert.ok(wedgeWithZero[winner].size>0);
}
for(const duration of [3,6,30]){
  for(const coast of [0,65,100]){
    const state=physics.create({geometry:geo,power:.8,duration,coast,random:seeded(duration+coast)});
    physics.finish(state);
    assert.ok(state.done&&Number.isFinite(state.angle)&&Number.isFinite(state.elapsed));
  }
}
console.log('PASS: 350 real physical runouts, no target center, friction, collisions, duration extremes, zero-area wedges.');

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'no-preference'});
const errors=[];
page.on('pageerror',error=>errors.push(error.message));
await page.route(/https?:\/\//,route=>route.abort());
try{
  await page.goto(pathToFileURL(resolve('index.html')).href,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>Boolean(window.__casinoNoirDebug));
  assert.equal(await page.locator('#spinMode').inputValue(),'physical');
  const before=await page.evaluate(()=>window.__casinoNoirDebug.controlledWinnerSelections);
  await page.locator('#spinHub').click();
  await page.waitForFunction(()=>window.__casinoNoirDebug.lastWinner!==null&&!window.__casinoNoirDebug.isSpinning,{timeout:30000});
  const result=await page.evaluate(()=>{
    const d=window.__casinoNoirDebug;
    const winner=d.lastWinner,sector=d.ranges()[winner];
    const offset=(((-90-d.rotation-sector.start)%360)+360)%360;
    return {winner,mode:d.lastMode,contacts:d.lastPhysicsContacts,
      controlledSelections:d.controlledWinnerSelections,offset,size:sector.size,
      restingVelocity:d.lastPhysicalVelocity};
  });
  assert.equal(result.mode,'physical');
  assert.equal(result.controlledSelections,before,'physical mode must never invoke controlled winner selection');
  assert.ok(result.contacts>0);
  assert.equal(result.restingVelocity,0);
  assert.ok(result.offset<result.size);
  await page.locator('#toggleEditor').click();
  await page.locator('#spinMode').selectOption('weighted');
  assert.match(await page.locator('#spinModeHint').textContent(),/gesteuerte Darstellung/);
  await page.locator('#closeEditor').click();
  await page.locator('#spinHub').click();
  await page.waitForFunction(()=>window.__casinoNoirDebug.lastMode==='weighted'&&!window.__casinoNoirDebug.isSpinning,{timeout:25000});
  const after=await page.evaluate(()=>window.__casinoNoirDebug.controlledWinnerSelections);
  assert.equal(after,before+1,'controlled mode must call weighted CSPRNG draw once');
  await page.reload({waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>Boolean(window.__casinoNoirDebug));
  assert.equal(await page.evaluate(()=>window.__casinoNoirDebug.config.spinMode),'weighted',
    'selected mode must persist in browser storage');
  await page.locator('#toggleEditor').click();
  await page.locator('#spinMode').selectOption('physical');
  await page.reload({waitUntil:'domcontentloaded'});
  assert.equal(await page.evaluate(()=>window.__casinoNoirDebug.config.spinMode),'physical',
    'returning to real physics must persist');

  assert.deepEqual(errors,[]);
  console.log('PASS: Chromium physical result follows wheel angle; weighted mode remains explicit.');
}finally{await browser.close();}
