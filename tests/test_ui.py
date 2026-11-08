import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path('/mnt/data/spinningwheel-casino-noir/casino-noir-standalone.html').read_text(encoding='utf-8')
STORAGE={}
OUT=Path('/mnt/data')
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,width,height in [('desktop',1440,1024),('mobile',390,844)]:
   page=await browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,reduced_motion='reduce',accept_downloads=True)
   errors=[]
   page.on('pageerror',lambda err:errors.append(str(err)))
   await page.route('https://fonts.googleapis.com/**',lambda route:route.abort())
   await page.route('https://fonts.gstatic.com/**',lambda route:route.abort())
   await page.evaluate("""() => {window.__storage={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__storage[k] ?? null},setItem(k,v){window.__storage[k]=String(v)},removeItem(k){delete window.__storage[k]}}});}""")
   await page.set_content(HTML,wait_until='domcontentloaded')
   await page.wait_for_selector('.segment-card',state='attached')
   await page.locator('#toggleEditor').click()
   assert await page.locator('.segment-card').count()==8
   assert await page.locator('#rotatingWheel path').count()>=8
   await page.screenshot(path=str(OUT/f'casino-noir-configurable-{label}.png'),full_page=True)
   await page.locator('#closeEditor').click()
   # click elsewhere => no spin
   outside=await page.locator('#wheelSvg').bounding_box()
   await page.mouse.click(outside['x']+outside['width']*.25,outside['y']+outside['height']*.5)
   assert not await page.evaluate('window.__casinoNoirDebug.isSpinning')
   # click the center, wait for reduced-motion complete
   await page.locator('#spinHub').click()
   await page.wait_for_timeout(850)
   assert not await page.evaluate('window.__casinoNoirDebug.isSpinning')
   idx=await page.evaluate('window.__casinoNoirDebug.lastWinner')
   assert 0<=idx<8,idx
   deg=await page.evaluate('window.__casinoNoirDebug.rotation')
   n=8
   target=((round(-((deg%360)+360)%360/(360/n))%n)+n)%n
   assert target==idx,(target,idx,deg)
   assert 'Ergebnis:' in await page.locator('#statusText').inner_text()
   # add/duplicate/delete, toggles, icon picker
   await page.locator('#toggleEditor').click()
   await page.locator('#addSegment').click()
   assert await page.locator('.segment-card').count()==9
   await page.locator('.segment-card').last.locator('input[data-field=label]').fill('Mein Hauptgewinn')
   assert await page.evaluate('window.__casinoNoirDebug.config.segments.at(-1).label')=='Mein Hauptgewinn'
   await page.locator('.segment-card').last.locator('input[data-field=showIcon]').uncheck()
   assert await page.evaluate('window.__casinoNoirDebug.config.segments.at(-1).showIcon')==False
   await page.locator('.segment-card').last.locator('button[data-action=icon]').click()
   assert await page.locator('#iconModal').is_visible()
   await page.locator('#iconSearch').fill('diamond')
   assert await page.locator('button[data-icon=diamond]').count()==1
   await page.locator('button[data-icon=diamond]').click()
   assert await page.evaluate('window.__casinoNoirDebug.config.segments.at(-1).icon')=='diamond'
   assert await page.evaluate('window.__casinoNoirDebug.config.segments.at(-1).showIcon')==True
   # localStorage survives reload
   await page.set_content(HTML,wait_until='domcontentloaded')
   await page.locator('#toggleEditor').click()
   assert await page.locator('.segment-card').count()==9
   assert await page.evaluate('window.__casinoNoirDebug.config.segments.at(-1).label')=='Mein Hauptgewinn'
   # edit with HTML to verify XSS-safe handling
   await page.locator('.segment-card').first.locator('input[data-field=label]').fill('<img src=x onerror=alert(1)>')
   assert await page.locator('#segmentList img').count()==0
   await page.locator('.segment-card').first.locator('button[data-action=duplicate]').click()
   assert await page.locator('.segment-card').count()==10
   await page.locator('.segment-card').first.locator('button[data-action=delete]').click()
   assert await page.locator('.segment-card').count()==9
   # Large number of segments and adaptive labeling via programmatic import-like persisted data
   await page.evaluate('''() => {let c=window.__casinoNoirDebug.config;while(c.segments.length<90)c.segments.push({...c.segments[0],id:'many'+c.segments.length});localStorage.setItem('casino-noir-wheel-studio-v1',JSON.stringify(c));}''')
   await page.set_content(HTML,wait_until='domcontentloaded')
   assert await page.locator('.segment-card').count()==90
   assert await page.locator('#densityNotice').is_visible()
   await page.locator('#showOnlyWheel').click()
   assert await page.locator('#presentation').is_visible()
   await page.locator('#spinHub').click()
   await page.wait_for_timeout(780)
   assert not await page.evaluate('window.__casinoNoirDebug.isSpinning')
   idx=await page.evaluate('window.__casinoNoirDebug.lastWinner')
   deg=await page.evaluate('window.__casinoNoirDebug.rotation')
   n=90
   target=((round(-((deg%360)+360)%360/(360/n))%n)+n)%n
   assert target==idx,(target,idx,deg)
   await page.locator('#closePresentation').click()
   assert not await page.locator('#presentation').is_visible()
   # test reset no browser dialog issue
   await page.locator('#toggleEditor').click()
   page.once('dialog',lambda dlg:asyncio.create_task(dlg.accept()))
   await page.locator('#resetConfig').click()
   assert await page.locator('.segment-card').count()==8
   # empty wheel works
   await page.evaluate('''() => {let c=window.__casinoNoirDebug.config;c.segments=[];localStorage.setItem('casino-noir-wheel-studio-v1',JSON.stringify(c));}''')
   await page.set_content(HTML,wait_until='domcontentloaded')
   await page.locator('#toggleEditor').click()
   assert await page.locator('.segment-card').count()==0
   assert await page.locator('#spinHub').is_disabled()
   await page.locator('#addSegment').click()
   assert await page.locator('.segment-card').count()==1
   assert not await page.locator('#spinHub').is_disabled()
   await page.locator('#closeEditor').click()
   await page.locator('#spinHub').click()
   await page.wait_for_timeout(650)
   assert await page.evaluate('window.__casinoNoirDebug.lastWinner')==0
   assert not errors,errors
   print(label,'PASSED',{'rotation':round(deg,2),'lastIndex':idx,'issues':errors})
   await page.close()
  await browser.close()
asyncio.run(main())