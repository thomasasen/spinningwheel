"""Browser regression for full icon search, virtual scrolling, cache and fallback."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
BASE=Path(__file__).resolve().parents[1]
HTML=(BASE/'casino-noir-standalone.html').read_text()
# 4,304 entries like the official Rounded catalog; includes names starting with digits.
NAMES=['10k','123','3d_rotation','diamond','favorite','workspace_premium','star','rocket_launch','pet_supplies'] + [f'example_symbol_{i:04d}' for i in range(4295)]
assert len(NAMES)==len(set(NAMES))==4304
CATALOG='\n'.join(f'{name} e{(i%4096):03x}' for i,name in enumerate(NAMES))+'\n'
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  page=await browser.new_page(viewport={'width':1280,'height':850},reduced_motion='reduce')
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.route('**/fonts.googleapis.com/**',lambda route:route.abort())
  await page.route('**/fonts.gstatic.com/**',lambda route:route.abort())
  await page.route('**/MaterialSymbolsRounded*',lambda route:route.fulfill(status=200,body=CATALOG,headers={'content-type':'text/plain','access-control-allow-origin':'*'}))
  await page.evaluate("""() => {window.__storage={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem(k){return window.__storage[k] ?? null},setItem(k,v){window.__storage[k]=String(v)},removeItem(k){delete window.__storage[k]}}});}""")
  await page.set_content(HTML,wait_until='domcontentloaded')
  await page.wait_for_function('window.__casinoNoirDebug.iconCatalogReady===true',timeout=15000)
  assert await page.evaluate('window.__casinoNoirDebug.iconCatalogCount')==4304
  await page.locator('#toggleEditor').click()
  await page.locator('.segment-icon-btn').first.click()
  assert '4.304' in await page.locator('#iconCatalogStatus').inner_text()
  assert 0 < await page.locator('button[data-icon]').count() < 100
  assert '4.304 Treffer' in await page.locator('#iconResultCount').inner_text()
  await page.locator('#iconGrid').evaluate('(el) => { el.scrollTop=el.scrollHeight }')
  await page.wait_for_timeout(100)
  assert await page.locator('button[data-icon]').last.get_attribute('data-icon') == 'workspace_premium'
  assert await page.locator('button[data-icon]').count() < 100
  await page.locator('#iconSearch').fill('diamond')
  assert await page.locator('button[data-icon]').count()==1
  assert await page.locator('button[data-icon=diamond]').count()==1
  await page.locator('#iconSearch').fill('10k')
  assert await page.locator('button[data-icon="10k"]').count()==1
  await page.locator('button[data-icon="10k"]').click()
  assert await page.evaluate('window.__casinoNoirDebug.config.segments[0].icon')=='10k'
  await page.locator('.segment-icon-btn').first.click()
  await page.locator('#iconSearch').fill('workspace_premium')
  assert await page.locator('button[data-icon=workspace_premium]').count()==1
  await page.locator('#closeIconModal').click()
  assert await page.evaluate("JSON.parse(localStorage.getItem('casino-noir-material-symbols-rounded-codepoints-v2')).entries.length")==4304
  # Cache remains searchable with blocked network after reload.
  await page.route('**/MaterialSymbolsRounded*',lambda route:route.abort())
  await page.set_content(HTML,wait_until='domcontentloaded') if page.url.startswith('http') else await page.set_content(HTML,wait_until='domcontentloaded')
  await page.wait_for_function('window.__casinoNoirDebug.iconCatalogCount === 4304',timeout=5000)
  await page.locator('#toggleEditor').click()
  await page.locator('.segment-icon-btn').first.click()
  assert '4.304' in await page.locator('#iconCatalogStatus').inner_text()
  assert not errors,errors
  print('full catalog + virtual scrolling + names starting digits + caching: PASS')
  await page.close()
  # New browser context: no cached catalog, sources unavailable -> keep working favorites.
  ctx=await browser.new_context()
  p2=await ctx.new_page()
  await p2.route('**/fonts.googleapis.com/**',lambda route:route.abort())
  await p2.route('**/MaterialSymbolsRounded*',lambda route:route.abort())
  await p2.set_content(HTML,wait_until='domcontentloaded')
  await p2.wait_for_function("document.querySelector('#iconCatalogStatus') !== null",timeout=4000)
  await p2.locator('#toggleEditor').click()
  await p2.locator('.segment-icon-btn').first.click()
  await p2.wait_for_function("document.querySelector('#iconCatalogStatus').dataset.status === 'error'",timeout=5000)
  assert await p2.locator('button[data-icon=star]').count()==1
  assert await p2.locator('#retryIconCatalog').is_visible()
  print('network error, favorite icons, retry: PASS')
  await browser.close()
asyncio.run(main())