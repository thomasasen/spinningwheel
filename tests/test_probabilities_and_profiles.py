"""Casino Noir integration and statistical checks. Run: python tests/test_probabilities_and_profiles.py"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = Path(__file__).resolve().parents[1]
HTML = (BASE / 'casino-noir-standalone.html').read_text(encoding='utf-8')
STORAGE = '''() => {
  window.__testStorage = {};
  Object.defineProperty(window,'localStorage',{configurable:true,value:{
    getItem(k){return window.__testStorage[k] ?? null},
    setItem(k,v){window.__testStorage[k]=String(v)},
    removeItem(k){delete window.__testStorage[k]}
  }});
}'''

async def load(browser, size=(1280,900), reduced='reduce'):
    page = await browser.new_page(viewport={'width':size[0],'height':size[1]}, reduced_motion=reduced, accept_downloads=True)
    errors=[]
    page.on('pageerror', lambda error: errors.append(str(error)))
    await page.route('https://**/*',lambda route:route.abort())
    await page.evaluate(STORAGE)
    await page.set_content(HTML,wait_until='domcontentloaded')
    assert not errors, errors
    return page,errors

async def test_statistics(page):
    cases=[
      {'name':'equal','weights':[1,1,1,1],'draws':100_000},
      {'name':'weighted','weights':[1,3,2,4],'draws':100_000},
      {'name':'excluded','weights':[0,1,0,3],'draws':100_000},
      {'name':'single','weights':[0,0,10,0],'draws':100_000},
      {'name':'many','weights':[i%9+1 for i in range(101)],'draws':100_000},
      {'name':'extreme','weights':[1,1000000,0,0],'draws':100_000}
    ]
    summaries=await page.evaluate('''cases => {
      const results=[];
      const c=window.__casinoNoirDebug.config;
      for(const test of cases){
        const base=c.segments[0];
        c.segments=test.weights.map((weight,i)=>({...base,id:'stat-'+i,weight,label:'Prize '+i}));
        const counts=test.weights.map(()=>0);
        for(let j=0;j<test.draws;j++)counts[window.__casinoNoirDebug.drawWeightedWinner()]++;
        results.push({name:test.name,weights:test.weights,counts:counts,draws:test.draws});
      }
      return results;
    }''', cases)
    for result in summaries:
        total=sum(result['weights'])
        assert sum(result['counts'])==result['draws'],result
        for weight,got in zip(result['weights'],result['counts']):
            expected=result['draws']*weight/total
            sigma=(result['draws']*(weight/total)*(1-weight/total))**.5
            tolerance=max(6*sigma, 3)
            assert abs(got-expected)<=tolerance,(result['name'],weight,got,expected,tolerance)
        print('STAT',result['name'],result['counts'])

async def test_ui_and_geometry(browser):
    page,errors=await load(browser)
    await page.locator('#toggleEditor').click()
    for i,weight in enumerate([1,3,2,4,0,0,0,0]):
        await page.locator('.segment-card input[data-field="weight"]').nth(i).fill(str(weight))
    assert await page.locator('.segment-chance').first.inner_text()=='10 %'
    assert await page.locator('.segment-chance').nth(1).inner_text()=='30 %'
    assert await page.locator('.segment-chance.is-excluded').count()==4
    await page.locator('#proportionalMode').select_option('proportional')
    spans=await page.evaluate('window.__casinoNoirDebug.segmentLayout().map(s=>s.span)')
    assert all(abs(a-b)<1e-8 for a,b in zip(spans,[36,108,72,144,0,0,0,0])),spans
    assert await page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    await page.locator('#closeEditor').click()
    await page.locator('#spinHub').click()
    await page.wait_for_function('!window.__casinoNoirDebug.isSpinning',timeout=4000)
    result=await page.evaluate('''() => {
      const d=window.__casinoNoirDebug;
      const target=d.segmentLayout()[d.lastWinner];
      return {winner:d.lastWinner,pointed:d.segmentLayout()[d.lastWinner].center,
        geometry:d.segmentLayout(),rotation:d.rotation,
        pointer:d.pointerAngle,clicked:d.lastPower};
    }''')
    assert result['winner'] in range(4),result
    selected=await page.evaluate('''() => {
      const d=window.__casinoNoirDebug,layout=d.segmentLayout();
      const a=(((-d.rotation+layout[0].span/2)%360)+360)%360;
      return layout.findIndex(s=>a>=s.start-1e-8&&a<s.end+1e-8);
    }''')
    assert selected==result['winner'],(selected,result)
    await page.locator('#toggleEditor').click()
    for i in range(8):await page.locator('.segment-card input[data-field="weight"]').nth(i).fill('0')
    assert await page.locator('#spinHub').is_disabled()
    assert 'Keine Ziehung möglich' in await page.locator('#probabilitySummary').inner_text()
    assert not errors,errors
    await page.close()
    print('UI / proportional geometry / zero weights PASS')

async def test_profiles_and_import(browser):
    page,errors=await load(browser,size=(390,844))
    await page.locator('#toggleEditor').click()
    await page.locator('.segment-card input[data-field="label"]').first.fill('Rad A')
    await page.locator('#newProfile').click()
    assert await page.locator('#profilePicker option').count()==2
    assert await page.locator('.segment-card input[data-field="label"]').first.input_value()=='Hauptgewinn'
    await page.locator('.segment-card input[data-field="label"]').first.fill('Rad B')
    await page.locator('#profilePicker').select_option(index=0)
    assert await page.locator('.segment-card input[data-field="label"]').first.input_value()=='Rad A'
    await page.locator('#profilePicker').select_option(index=1)
    assert await page.locator('.segment-card input[data-field="label"]').first.input_value()=='Rad B'
    await page.locator('#duplicateProfile').click()
    assert await page.locator('#profilePicker option').count()==3
    await page.locator('#profileName').fill('Meine Kopie')
    await page.locator('#renameProfile').click()
    assert await page.locator('#profilePicker option').last.inner_text()=='Meine Kopie'
    async with page.expect_download() as task: await page.locator('#exportAllJson').click()
    exported=json.loads(Path(await (await task.value).path()).read_text(encoding='utf-8'))
    assert exported['version']==2 and len(exported['configurations'])==3
    assert exported['configurations'][0]['config']['segments'][0]['label']=='Rad A'
    async with page.expect_download() as task: await page.locator('#exportJson').click()
    single=json.loads(Path(await (await task.value).path()).read_text(encoding='utf-8'))
    assert single['segments'][0]['label']=='Rad B' and single['name']=='Meine Kopie'
    before=await page.locator('#profilePicker option').count()
    await page.locator('#importFile').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"version":99,"segments":[]}'})
    assert await page.locator('#profilePicker option').count()==before
    await page.locator('#importMode').select_option('new')
    await page.locator('#importFile').set_input_files({'name':'valid.json','mimeType':'application/json','buffer':json.dumps(single).encode()})
    assert await page.locator('#profilePicker option').count()==4
    assert await page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    saved=await page.evaluate('window.__testStorage')
    assert 'casino-noir-wheel-studio-workspace-v2' in saved
    await page.set_content(HTML,wait_until='domcontentloaded')
    await page.locator('#toggleEditor').click()
    assert await page.locator('#profilePicker option').count()==4
    assert await page.locator('.segment-card input[data-field="label"]').first.input_value()=='Rad B'
    await page.locator('#importFile').set_input_files({'name':'collection.json','mimeType':'application/json','buffer':json.dumps(exported).encode()})
    assert await page.locator('#profilePicker option').count()==4
    await page.evaluate('''() => {
      localStorage.setItem=(key,value)=>{if(key==='casino-noir-wheel-studio-workspace-v2')throw Error('quota');window.__testStorage[key]=String(value)};
    }''')
    await page.locator('.segment-card input[data-field="label"]').first.fill('Speicherfehler')
    assert 'Speicherung nicht möglich' in await page.locator('#saveIndicator').inner_text()
    assert not errors,errors
    await page.close()
    print('Profiles / export / import / migration / blocked storage / mobile PASS')

async def test_motion(browser):
    page,errors=await load(browser,reduced='no-preference')
    curve=await page.evaluate('''() => {
      const p=window.__casinoNoirDebug.motionProgress;
      return [0,.0001,.01,.07,.075,.2,.5,.9,.99,1].map(t=>p(t,65));
    }''')
    assert curve[0]==0 and abs(curve[-1]-1)<1e-10 and all(b>=a for a,b in zip(curve,curve[1:])),curve
    assert curve[1]-curve[0]<curve[3]-curve[2],curve
    await page.locator('#toggleEditor').click()
    await page.locator('#spinDuration').fill('3')
    await page.locator('#pointerIntensity').fill('100')
    await page.locator('#closeEditor').click()
    await page.locator('#spinHub').click()
    await page.wait_for_function('!window.__casinoNoirDebug.isSpinning',timeout=4500)
    assert 0<=await page.evaluate('window.__casinoNoirDebug.lastWinner')<8
    assert not errors,errors
    await page.close()
    print('Motion continuity / realtime spin PASS')

async def main():
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        page,errors=await load(browser)
        await test_statistics(page)
        assert not errors,errors
        await page.close()
        await test_ui_and_geometry(browser)
        await test_profiles_and_import(browser)
        await test_motion(browser)
        await browser.close()

if __name__=='__main__':asyncio.run(main())
