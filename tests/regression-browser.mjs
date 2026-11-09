import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const browser=await chromium.launch({headless:true});
const context=await browser.newContext({reducedMotion:'reduce',viewport:{width:1240,height:920}});
const page=await context.newPage(), errors=[];
page.on('pageerror',err=>errors.push(err.stack||err.message));
await page.route(/https?:\/\//,route=>route.abort());
try{
  // Seed the previous v1 browser storage before the upgraded application starts.
  await page.addInitScript(()=>{
    if(!localStorage.getItem('casino-noir-wheel-profiles-v2')){
      const base={version:1,palette:'noir',duration:4,coast:70,sound:false,winnerEffect:'outline',winnerStrength:'subtle',winnerSound:'off',
        segments:[{id:'legacy-1',label:'Altgewinn',icon:'star',showLabel:true,showIcon:true,color:'#981439'}]};
      localStorage.setItem('casino-noir-wheel-studio-v1',JSON.stringify(base));
    }
  });
  await page.goto(pathToFileURL(resolve('index.html')).href);
  await page.waitForFunction(()=>Boolean(window.__casinoNoirDebug));
  assert.deepEqual(await page.evaluate(()=>{
    const cfg=window.__casinoNoirDebug.config;
    return [cfg.segments.length,cfg.segments[0].label,cfg.segments[0].weight,cfg.duration,cfg.coast,cfg.sound];
  }),[1,'Altgewinn',1,4,70,false],'v1 settings and segment migrate without loss');
  await page.locator('#toggleEditor').click();
  await page.locator('#segmentList input[data-field="weight"]').fill('-1');
  await page.locator('#segmentList input[data-field="weight"]').dispatchEvent('change');
  assert.equal(await page.locator('#segmentList input[data-field="weight"]').inputValue(),'1','negative weight must be rejected');
  const bad={version:2,segments:[{label:'Invalid',weight:-5}]};
  await page.locator('#importFile').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(bad))});
  await page.waitForFunction(()=>document.querySelector('#toast')?.textContent?.includes('Import fehlgeschlagen'),null,{timeout:4000});
  assert.match(await page.locator('#toast').innerText(),/Import fehlgeschlagen/);
  assert.equal(await page.locator('#segmentList .segment-card').count(),1,'failed import cannot change current config');
  // 100 segments stress geometry and rendering. All visual contents stay in the editor.
  for(let i=1;i<100;i++)await page.locator('#addSegment').click();
  assert.equal(await page.locator('#segmentList .segment-card').count(),100);
  assert.match(await page.locator('#stageCount').innerText(),/100 SEGMENTE/);
  await page.locator('#sizeMode').selectOption('proportional');
  await page.locator('#closeEditor').click();
  await page.locator('#spinHub').click();
  await page.waitForFunction(()=>window.__casinoNoirDebug.lastWinner!==null&&!window.__casinoNoirDebug.isSpinning,{timeout:10000});
  const placement=await page.evaluate(()=>{
    const api=window.__casinoNoirDebug, winner=api.lastWinner, sector=api.ranges()[winner];
    const under=(((-90-api.rotation)%360)+360)%360;
    const offset=((under-sector.start)%360+360)%360;
    return {winner,count:api.config.segments.length,offset,size:sector.size};
  });
  assert.ok(placement.winner>=0&&placement.winner<100);
  assert.ok(placement.offset>=0&&placement.offset<placement.size+1e-6,'pointer must be inside selected wedge');
  assert.deepEqual(errors,[],'no uncaught JavaScript errors');
  console.log('PASS: v1 migration, invalid weight and JSON, 100 segments, pointer outcome.');
}finally{await browser.close();}
