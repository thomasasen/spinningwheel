from pathlib import Path
import re
base=Path(__file__).resolve().parent
html=(base/'index.html').read_text()
css=(base/'styles.css').read_text()
js=(base/'app.js').read_text()
html,n=re.subn(r'<link rel="stylesheet" href="styles\.css(?:\?[^"<>]*)?">',lambda _m:f'<style>\n{css}\n</style>',html)
assert n==1, 'Stylesheet reference not found'
html,n=re.subn(r'<script defer src="app\.js(?:\?[^"<>]*)?"></script>','',html)
assert n==1, 'App script reference not found'
index=(base/'icon-search-index.json').read_text(encoding='utf-8').replace('<','\\u003c')
html=html.replace('</body>',f'<script type="application/json" id="iconSearchIndexData">{index}</script>\n<script>\n{js}\n</script>\n</body>')
(base/'casino-noir-standalone.html').write_text(html)
print('standalone',len(html),'bytes')
