import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';

const browser=await chromium.launch({headless:true});
const url=pathToFileURL(resolve('index.html')).href;
async function collectFrames(page,count=80){
  return page.evaluate(async frameCount=>{
    const pointer=document.querySelector('#fixedPointer');
    const samples=[];
    for(let i=0;i<frameCount;i++){
      await new Promise(resolve=>requestAnimationFrame(resolve));
      const transform=pointer.getAttribute('transform')||'';
      const angle=Number(/rotate\\((-?[\\d.]+)/.exec(transform)?.[1]||0);
      samples.push({angle,transform});
    }
    return samples;
  },count);
}
function peak(samples){return Math.max(...samples.map(x=>Math.abs(x.angle)));}
const page=await browser.newPage({reducedMotion:'no-preference',viewport:{width:1280,height:850}});
const errors=[];
page.on('pageerror',e=>errors.push(e.stack||e.message));
await page.route(/https?:\\/\\//,route=>route.abort());
try{
  await page.goto(url,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>Boolean(window.__casinoNoirDebug));
  await page.locator('#toggleEditor').click();
  const preview=page.locator('#previewPointer');
  await assert.equal(await preview.isVisible(),true);
  await preview.click();
  assert.equal(await page.locator('#editorBackdrop').evaluate(node=>node.classList.contains('is-pointer-preview')),true,'preview removes backdrop blur');
  const sample=await collectFrames(page,84);
  const amplitude=peak(sample);
  assert.ok(amplitude>=4,'default pointer needs visible angular excursion, got '+amplitude);
  assert.ok(sample.some(x=>x.angle<-3),'pointer must swing when struck');
  assert.ok(Math.abs(sample.at(-1).angle)<1,'pointer must settle after the collision');
  assert.equal(await page.locator('#pointerHinge').count(),1,'fixed decorative hinge must exist');
  const [spring,damping]=await Promise.all([
    page.locator('#pointerSpring').inputValue(),page.locator('#pointerDamping').inputValue()
  ]);
  assert.equal(spring,'65');assert.equal(damping,'60');
  await page.locator('#pointerIntensity').evaluate(element=>{
    element.value='0';element.dispatchEvent(new Event('input',{bubbles:true}));
  });
  await preview.click();
  const disabled=await collectFrames(page,16);
  assert.ok(peak(disabled)<.5,'0% intensity disables motion');
  await page.locator('#pointerIntensity').evaluate(element=>{
    element.value='100';element.dispatchEvent(new Event('input',{bubbles:true}));
  });
  await page.locator('#closeEditor').click();
  const before=await page.evaluate(()=>window.__casinoNoirDebug.pointerContactCount);
  await page.locator('#spinHub').click();
  const spinSamples=await page.evaluate(async()=>{
    const out=[];
    const ptr=document.querySelector('#fixedPointer');
    for(let i=0;i<210;i++){
      await new Promise(r=>requestAnimationFrame(r));
      const tr=ptr.getAttribute('transform')||'';
      out.push(Number(/rotate\\((-?[\\d.]+)/.exec(tr)?.[1]||0));
    }
    return out;
  });
  const after=await page.evaluate(()=>({
    count:window.__casinoNoirDebug.pointerContactCount,
    winner:window.__casinoNoirDebug.lastWinner,
    spinning:window.__casinoNoirDebug.isSpinning
  }));
  assert.ok(after.count>before,'real segment contacts must trigger the pointer');
  assert.ok(Math.max(...spinSamples.map(Math.abs))>3,'real spin must visibly move the pointer');
  assert.equal(after.spinning,false,'spin must finish');
  assert.ok(Number.isInteger(after.winner),'real spin must still determine winner');
  assert.deepEqual(errors,[],'no uncaught JavaScript exceptions');
  console.log('PASS: visible SVG pointer deflection, damping, live segment contacts, preview, 0% intensity.');
}finally{await page.close();}

const reduced=await browser.newPage({reducedMotion:'reduce'});
const reducedErrors=[];
reduced.on('pageerror',e=>reducedErrors.push(e.message));
await reduced.route(/https?:\\/\\//,route=>route.abort());
try{
  await reduced.goto(url,{waitUntil:'domcontentloaded'});
  await reduced.locator('#toggleEditor').click();
  await reduced.locator('#previewPointer').click();
  const sample=await collectFrames(reduced,18);
  assert.ok(peak(sample)===0,'reduced motion must suppress pointer animation');
  assert.match(await reduced.locator('#toast').innerText(),/reduzierte Bewegung/);
  assert.deepEqual(reducedErrors,[]);
  console.log('PASS: reduced-motion accessibility behavior.');
}finally{await reduced.close();await browser.close();}
