from scrapling.fetchers import StealthyFetcher
from bs4 import BeautifulSoup

page = StealthyFetcher.fetch('http://www.alternativateatral.com/convocatorias.php?pais=1&clasificacion=14', headless=True, network_idle=True)
soup = BeautifulSoup(page.html_content, 'html.parser')

cuerpo = soup.select_one('div.cuerpo')
if cuerpo:
    items = cuerpo.find_all(['div', 'li', 'tr', 'p'], recursive=False)
    print(f"Hijos directos: {len(items)}")
    for item in items[:5]:
        print(f"\n--- [{item.name}] ---")
        print(item.get_text(separator=' | ', strip=True)[:200])
        links = item.find_all('a', href=True)
        for a in links:
            print(f"  LINK: {a['href']} → {a.get_text(strip=True)[:60]}")
