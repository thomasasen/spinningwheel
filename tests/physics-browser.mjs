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
  assert.ok(state.elapsed<180,'mechanical wheel must settle within a finite practical duration');
  assert.ok(state.restSeconds>=physics.REST_HOLD_SECONDS-1e-3,
    'winner may only be declared after a sustained stationary interval');
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
const spread=Math.max(...offsets)-Math.min(...offsets);
console.log('Physical landing coverage:',{min:Math.min(...offsets),max:Math.max(...offsets),spread});
assert.ok(spread>.18,'mechanical landing positions must vary within wedges');

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

// Validate that the solver does not snap from noticeable motion to a winner,
// even near the configured safety window and with unusual segment sizes.
const coastTrace=[];
const smooth=physics.create({
  angle:13.7,geometry:geo,power:.62,duration:6,coast:65,
  pointerIntensity:60,pointerSpring:65,random:seeded(197)
});
let lastMovingSpeed=Infinity;
for(let i=0;i<25000&&!smooth.done;i++){
  lastMovingSpeed=Math.abs(smooth.velocity);
  physics.advance(smooth,1/120);
  if(i%12===0)coastTrace.push({elapsed:smooth.elapsed,speed:Math.abs(smooth.velocity)});
}
assert.ok(smooth.done,'smooth coast must actually finish');
assert.ok(lastMovingSpeed<=physics.REST_SPEED+.00001,
  'the final transition must be below the imperceptible rest threshold');
assert.ok(coastTrace.some(point=>point.speed>10&&point.speed<50),
  'real motion must be visible as the wheel passes through its low-speed phase');
assert.ok(coastTrace.some(point=>point.speed>.15&&point.speed<2),
  'late angular momentum must taper into very slow visible motion');
assert.ok(smooth.restSeconds>=physics.REST_HOLD_SECONDS-1e-3);
const extended=physics.create({geometry:geo,power:1,duration:30,coast:100,random:seeded(99)});
// A past regression forcibly set velocity to zero at a fixed elapsed limit.
extended.safetyStartSeconds=.05;
physics.advance(extended,.1);
assert.ok(extended.elapsed>extended.safetyStartSeconds&&!extended.done&&extended.velocity>100,
  'a time limit must never abruptly stop a moving wheel');
physics.finish(extended);
assert.ok(extended.restSeconds>=physics.REST_HOLD_SECONDS-1e-3);
for(const duration of [3,6,15,30])for(const coast of [0,65,100]){
  const state=physics.create({geometry:geo,power:.9,duration,coast,random:seeded(duration*10+coast)});
  physics.finish(state);
  assert.ok(state.done&&state.restSeconds>=physics.REST_HOLD_SECONDS-1e-3,
    'rest validation must hold at all friction and inertia extremes');
  assert.ok(Number.isFinite(state.angle)&&Number.isFinite(state.elapsed));
}
console.log('PASS: gradual low-speed coast, no timed hard stop, sustained mechanical rest before winner.');


// The visible rim studs and simulated ratchet must have identical divisions.
const pegs=physics.buildPegAngles(geo,7);
assert.equal(pegs.length,56,'eight segments must create 56 real teeth');
assert.equal(physics.buildPegAngles(geo,4).length,32);
assert.equal(physics.buildPegAngles(geo,12).length,96);
assert.equal(physics.buildPegAngles(wedges([0,1,3,0,1]),7).length,21,
  'zero-area sectors cannot create phantom teeth');
assert.ok(physics.buildPegAngles(wedges(Array(5000).fill(1)),7).length<=336,
  'extreme segment counts must not overload the rendering/simulation');

// A near-rest collision should cause only a short, smoothly damped backward
// excursion and not an extended reverse spin or a second strike of that tooth.
const rebound=physics.create({geometry:geo,subdivisions:7,power:.5,random:seeded(82)});
rebound.angle=0;
rebound.velocity=16;
let impactAt=null,reverseDetected=false;
for(let i=0;i<1500&&!rebound.done;i++){
  const beforeVelocity=rebound.velocity;
  physics.advance(rebound,1/240);
  if(beforeVelocity>0&&rebound.velocity<0){
    impactAt=rebound.elapsed;
    reverseDetected=true;
  }
}
assert.ok(reverseDetected,'slow tooth contact must still allow a natural reversal');
assert.ok(rebound.done,'the backward rebound must come to rest');
assert.ok(rebound.elapsed-impactAt<1.4,
  'a rebound should settle rapidly after its final tooth impact');
assert.equal(rebound.contacts,1,'a single tooth must not be struck repeatedly on the reverse crossing');
assert.ok(rebound.restSeconds>=physics.REST_HOLD_SECONDS-1e-3);
console.log('PASS: real subsegment teeth, bounded density and quickly damped reverse rebound.');

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'no-preference'});
const errors=[];
page.on('pageerror',error=>errors.push(error.message));
await page.route(/https?:\/\//,route=>route.abort());
try{
  await page.goto(pathToFileURL(resolve('index.html')).href,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>Boolean(window.__casinoNoirDebug));
  assert.equal(await page.locator('#spinMode').inputValue(),'physical');
  assert.equal(await page.locator('#subdivisions').inputValue(),'7');
  assert.equal(await page.locator('[data-ratchet-tooth]').count(),56);
  await page.locator('#toggleEditor').click();
  await page.locator('#subdivisions').evaluate(input=>{
    input.value='4';
    input.dispatchEvent(new Event('input',{bubbles:true}));
  });
  assert.equal(await page.locator('[data-ratchet-tooth]').count(),32);
  assert.equal(await page.evaluate(()=>window.__casinoNoirDebug.config.subdivisions),4);
  await page.locator('#subdivisions').evaluate(input=>{
    input.value='7';
    input.dispatchEvent(new Event('input',{bubbles:true}));
  });
  await page.locator('#closeEditor').click();

  const before=await page.evaluate(()=>window.__casinoNoirDebug.controlledWinnerSelections);
  await page.locator('#spinHub').click();
  await page.waitForFunction(()=>{
    const state=window.__casinoNoirDebug.currentPhysicalState;
    return Boolean(state&&!state.done&&Math.abs(state.velocity)>physicsRestThreshold()&&Math.abs(state.velocity)<4);
    function physicsRestThreshold(){return window.CasinoWheelPhysics.REST_SPEED;}
  },null,{timeout:30000});
  const lateCoast=await page.evaluate(()=>{
    const api=window.__casinoNoirDebug;
    return {stillSpinning:api.isSpinning,winner:api.lastWinner,state:api.currentPhysicalState,
      text:document.querySelector('#statusText').textContent};
  });
  assert.equal(lateCoast.stillSpinning,true,'a wheel moving slowly is still spinning');
  assert.equal(lateCoast.winner,null,'never reveal winner during final coasting');
  assert.ok(lateCoast.state.velocity!==0&&lateCoast.state.restSeconds<windowPhysicsRestHold(),
    'wheel has not yet reached sustained rest');
  function windowPhysicsRestHold(){return physics.REST_HOLD_SECONDS;}
  await page.waitForFunction(()=>window.__casinoNoirDebug.lastWinner!==null&&!window.__casinoNoirDebug.isSpinning,null,{timeout:30000});
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
