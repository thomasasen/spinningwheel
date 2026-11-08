"""Test six truly distinct winner treatments, selected wedge and preview with menu open."""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'casino-noir-standalone.html').read_text()
MODES={
'outline':('.winner-outline-trace',1),
'spotlight':('.winner-spot-beam',1),
'lift':('.winner-lift',1),
'lights':('.winner-marquee-bulb',56),
'celebration':('.winner-firework-star, .winner-firework-dot',20),
'cinematic':('.winner-cinema-orbit',1)}
async def test():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for device,viewport in [('desktop',{'width':1440,'height':900}),('mobile',{'width':390,'height':844})]:
   ctx=await browser.new_context(viewport=viewport,accept_downloads=True)
   page=await ctx.new_page()
   errors=[]
   page.on('pageerror',lambda ex:errors.append(str(ex)))
   await page.route('https://**/*',lambda route:route.abort())
   await page.set_content(HTML,wait_until='domcontentloaded')
   await page.locator('#toggleEditor').click()
   for mode,(selector,mincount) in MODES.items():
    await page.locator('#winnerEffect').select_option(mode)
    await page.locator('#previewWinnerEffect').click()
    await page.wait_for_timeout(240)
    assert await page.locator('#editorPanel').is_visible(),device+': menu hidden'
    assert await page.locator('#editorBackdrop').evaluate('(e)=>getComputedStyle(e).backdropFilter')=='none',mode
    assert await page.locator('#winnerHighlight').get_attribute('data-effect')==mode
    assert await page.locator('#winnerStage').get_attribute('data-effect')==mode
    assert await page.locator(selector).count()>=mincount,(mode,selector)
    assert await page.locator('#winnerStage').is_visible(),mode
    assert await page.evaluate('window.__casinoNoirDebug.isSpinning')==False
    if device=='desktop':
     await page.screenshot(path=str(ROOT/f'casino-preview-{mode}.png'))
    await page.keyboard.press('Escape')
    assert 'blur' in await page.locator('#editorBackdrop').evaluate('(e)=>getComputedStyle(e).backdropFilter'),mode
   # Smoke geometry and persistent settings
   for n in [1,3,8,12,20,21,72,90,140]:
    segs=[{'label':f'Feld {i}', 'icon':'star','showLabel':True,'showIcon':True,'color':'#901536' if i%2 else '#131114'} for i in range(n)]
    await page.locator('#importFile').set_input_files({'name':'wheel.json','mimeType':'application/json','buffer':json.dumps({'segments':segs,'duration':3,'coast':90,'sound':False,'winnerEffect':'cinematic','winnerStrength':'refined','winnerSound':'off','palette':'noir'}).encode()})
    await page.wait_for_function('(n)=>window.__casinoNoirDebug.config.segments.length===n',arg=n)
    await page.locator('#previewWinnerEffect').click()
    assert await page.locator('#winnerHighlight').get_attribute('data-effect')=='cinematic'
    assert await page.locator('#winner-highlight-sentinel').count()==0
    await page.keyboard.press('Escape')
   await page.locator('#closeEditor').click()
   await page.locator('#spinHub').click()
   await page.wait_for_function('!window.__casinoNoirDebug.isSpinning',timeout=15000)
   win=await page.evaluate('window.__casinoNoirDebug.lastWinner')
   assert await page.evaluate('window.__casinoNoirDebug.highlightedWinner')==win
   assert await page.locator('#winnerStage').is_visible()
   assert not errors,errors
   await ctx.close()
   print('OK',device,'all six distinct classes + 9 segment counts + winner spin')
  await browser.close()
if __name__=='__main__': asyncio.run(test())
