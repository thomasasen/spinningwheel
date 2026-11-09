import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({reducedMotion:'reduce',viewport:{width:1280,height:900}});
const errors=[];
page.on('pageerror',e=>errors.push(e.message));
await page.route(/https?:\/\//,route=>route.abort());
try{
  await page.goto(pathToFileURL(resolve('index.html')).href,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>Boolean(window.__casinoNoirDebug),{timeout:10000});
  await page.locator('#toggleEditor').click();
  await assert.doesNotReject(async()=>{
    await page.waitForSelector('#sizeMode');
    await page.waitForSelector('#profileSelect');
    await page.waitForSelector('#pointerSpring');
  });
  await page.locator('#spinMode').selectOption('weighted');
  await page.locator('#sizeMode').selectOption('proportional');
  const sampled=await page.evaluate(()=>{
    const api=window.__casinoNoirDebug;
    api.config.segments.forEach((s,i)=>s.weight=i===0?1:i===1?3:0);
    const values=Array(8).fill(0);
    for(let i=0;i<100000;i++)values[api.selectWinner()]++;
    return {values,geo:api.ranges(),cfg:api.config};
  });
  assert.equal(sampled.values.slice(2).reduce((a,b)=>a+b,0),0,'0 weights must never win');
  assert.ok(Math.abs(sampled.values[0]/100000-.25)<.012,'weighted 1:3 ratio');
  assert.ok(Math.abs(sampled.values[1]/100000-.75)<.012,'weighted 1:3 ratio');
  assert.ok(Math.abs(sampled.geo[0].size-90)<1e-6);
  assert.ok(Math.abs(sampled.geo[1].size-270)<1e-6);
  const stats=await page.evaluate(()=>{
    const api=window.__casinoNoirDebug;
    const run=(weights,count=100000)=>{
      api.config.segments.forEach((segment,i)=>segment.weight=weights[i]||0);
      const observed=Array(weights.length).fill(0);
      for(let i=0;i<count;i++)observed[api.selectWinner()]++;
      return observed;
    };
    const equal=run(Array(8).fill(1));
    const singleton=run([0,0,0,0,1,0,0,0]);
    const extreme=run([1000000,1,0,0,0,0,0,0]);
    api.config.segments.forEach(s=>s.weight=0);
    let zeroThrows=false;try{api.selectWinner();}catch{zeroThrows=true;}
    return {equal,singleton,extreme,zeroThrows};
  });
  assert.ok(stats.equal.every(value=>Math.abs(value-12500)<600),'equal weights should be uniformly distributed');
  assert.equal(stats.singleton[4],100000,'one eligible segment should always win');
  assert.equal(stats.extreme.slice(2).reduce((a,b)=>a+b,0),0,'excluded segments must never win');
  assert.equal(stats.zeroThrows,true,'all-zero weights must prevent a draw');
  await page.locator('#segmentList .segment-card').nth(0).locator('input[data-field="weight"]').fill('1');
  await page.locator('#segmentList .segment-card').nth(0).locator('input[data-field="weight"]').dispatchEvent('change');
  await page.locator('#segmentList .segment-card').nth(1).locator('input[data-field="weight"]').fill('0');
  await page.locator('#segmentList .segment-card').nth(1).locator('input[data-field="weight"]').dispatchEvent('change');
  for(let i=2;i<8;i++){
    await page.locator('#segmentList .segment-card').nth(i).locator('input[data-field="weight"]').fill('0');
    await page.locator('#segmentList .segment-card').nth(i).locator('input[data-field="weight"]').dispatchEvent('change');
  }
  await page.locator('#closeEditor').click();
  await page.locator('#spinHub').click();
  await page.waitForFunction(()=>window.__casinoNoirDebug.lastWinner!==null&&window.__casinoNoirDebug.spinning===false,{timeout:5000});
  const outcome=await page.evaluate(()=>({winner:window.__casinoNoirDebug.lastWinner,angle:window.__casinoNoirDebug.rotation}));
  assert.equal(outcome.winner,0,'the only eligible winner');
  assert.ok(Number.isFinite(outcome.angle),'final angle finite');
  await page.locator('#toggleEditor').click();
  await page.locator('#profileDuplicate').click();
  await assert.equal(await page.locator('#profileSelect option').count(),2);
  await page.reload({waitUntil:'domcontentloaded'});
  await page.locator('#toggleEditor').click();
  await assert.equal(await page.locator('#profileSelect option').count(),2);
  // The self-contained build has to include the real UI and metadata.
  const standalone=await browser.newPage({reducedMotion:'reduce',viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  const standaloneErrors=[];
  standalone.on('pageerror',error=>standaloneErrors.push(error.message));
  await standalone.route(/https?:\/\//,route=>route.abort());
  await standalone.goto(pathToFileURL(resolve('casino-noir-standalone.html')).href,{waitUntil:'domcontentloaded'});
  await standalone.waitForFunction(()=>Boolean(window.__casinoNoirDebug),{timeout:10000});
  const standaloneFeatures=await standalone.evaluate(()=>({
    weights:window.__casinoNoirDebug.config.segments.every(segment=>segment.weight===1),
    metadata:window.__casinoNoirDebug.iconSearchMetadataReady,
    overflow:document.documentElement.scrollWidth>innerWidth+2
  }));
  assert.equal(standaloneFeatures.weights,true,'standalone defaults migrate weights');
  assert.equal(standaloneFeatures.overflow,false,'standalone mobile viewport has no horizontal overflow');
  await standalone.locator('#toggleEditor').click();
  await standalone.waitForSelector('#profileSelect');
  await standalone.waitForSelector('#sizeMode');
  assert.deepEqual(standaloneErrors,[],'standalone should not throw errors');
  await standalone.close();
  assert.deepEqual(errors,[],'no uncaught JavaScript errors');
  console.log('PASS: Chromium modular + standalone mobile, geometry, 400000 weighted selections, zero weights, stop angle, local profiles.');
}finally{await browser.close();}
