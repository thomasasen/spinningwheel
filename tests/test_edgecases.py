import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path('/mnt/data/spinningwheel-casino-noir/casino-noir-standalone.html').read_text()
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  page=await browser.new_page(viewport={'width':1280,'height':900},reduced_motion='reduce',accept_downloads=True)
  await page.route('https://fonts.googleapis.com/**',lambda route:route.abort())
  await page.route('https://fonts.gstatic.com/**',lambda route:route.abort())
  await page.evaluate("""() => {window.__storage={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__storage[k] ?? null},setItem(k,v){window.__storage[k]=String(v)},removeItem(k){delete window.__storage[k]}}});}""")
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content(HTML,wait_until='domcontentloaded')
  # Load crafted configs via the same UI import path, then test pointer/math.
  for count in [2,3,12,20,21,24,72,73,100,220]:
   data={'segments':[{'label':f'Prämie {i}','icon':'favorite','showLabel':True,'showIcon':True,'color':'#8b1640' if i%2 else '#171219'} for i in range(count)],'duration':4,'sound':False,'palette':'noir'}
   await page.locator('#importFile').set_input_files({'name':'test.json','mimeType':'application/json','buffer':json.dumps(data).encode()})
   await page.wait_for_timeout(80)
   actual=await page.locator('.segment-card').count()
   assert actual==count,(count,actual)
   assert await page.evaluate('window.__casinoNoirDebug.config.segments.length')==count
   await page.locator('#spinHub').click()
   await page.wait_for_timeout(510)
   winner=await page.evaluate('window.__casinoNoirDebug.lastWinner')
   angle=await page.evaluate('window.__casinoNoirDebug.rotation')
   target=((round(-((angle%360)+360)%360/(360/count))%count)+count)%count
   assert winner==target,(count,winner,target)
   print('count',count,'winner',winner)
  await page.locator('#toggleEditor').click()
  async with page.expect_download() as download_info:
   await page.locator('#exportJson').click()
  download=await download_info.value
  assert download.suggested_filename=='casino-noir-konfiguration.json'
  txt=Path(await download.path()).read_text()
  data=json.loads(txt)
  assert len(data['segments'])==220
  assert data['segments'][10]['label']=='Prämie 10'
  # Invalid import should leave current wheel intact.
  await page.locator('#importFile').set_input_files({'name':'broken.json','mimeType':'application/json','buffer':b'{oops'})
  await page.wait_for_timeout(100)
  assert await page.locator('.segment-card').count()==220
  assert not errors,errors
  print('Import/Export, invalid JSON, rotating pointer: PASSED')
  await browser.close()
asyncio.run(main())