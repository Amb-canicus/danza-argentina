from scrapling.fetchers import StealthyFetcher
from bs4 import BeautifulSoup

page = StealthyFetcher.fetch('http://www.alternativateatral.com/buscar.asp?objetivo=obras&texto=danza', headless=True, network_idle=True)
soup = BeautifulSoup(page.html_content, 'html.parser')

for item in soup.select('article, .obra, li, tr')[:30]:
    texto = item.get_text(separator=' ', strip=True)
    if len(texto) < 20:
        continue
    print(f"--- TAG: {item.name} | CLASS: {item.get('class', '')} ---")
    print(f"  {texto[:150]}")
    print()
