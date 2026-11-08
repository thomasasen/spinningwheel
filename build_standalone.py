from pathlib import Path
import re
base=Path(__file__).resolve().parent
html=(base/'index.html').read_text()
css=(base/'styles.css').read_text()
js=(base/'app.js').read_text()
html=html.replace('<link rel="stylesheet" href="styles.css">',f'<style>\n{css}\n</style>')
html,n=re.subn(r'<script defer src="app\\.js(?:\\?[^"<>]*)?"></script>','',html)
assert n==1, 'App script reference not found'
html=html.replace('</body>',f'<script>\n{js}\n</script>\n</body>')
(base/'casino-noir-standalone.html').write_text(html)
print('standalone',len(html),'bytes')
