"""Testa a lista M3U e grava channels.m3u só com os canais que funcionam no navegador."""
import sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

SRC = sys.argv[1] if len(sys.argv) > 1 else 'https://iptv-org.github.io/iptv/countries/br.m3u'
OUT = 'channels.m3u'
UA = {'User-Agent': 'Mozilla/5.0', 'Origin': 'http://172.20.10.3:8080'}


def parse(text):
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if l.startswith('#EXTINF'):
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith('#')):
                j += 1
            if j < len(lines) and lines[j].startswith('http'):
                yield l, lines[j].strip()


def ok(item):
    info, url = item
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=8) as r:
            cors = r.headers.get('Access-Control-Allow-Origin')
            head = r.read(2048).decode('utf-8', 'ignore')
        return item if cors and head.lstrip().startswith('#EXTM3U') else None
    except Exception:
        return None


def main():
    text = urllib.request.urlopen(urllib.request.Request(SRC, headers=UA), timeout=30).read().decode('utf-8', 'ignore')
    items = list(parse(text))
    print(f'Testando {len(items)} canais...')
    with ThreadPoolExecutor(40) as ex:
        good = [x for x in ex.map(ok, items) if x]
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for info, url in good:
            f.write(info + '\n' + url + '\n')
    print(f'{len(good)} funcionando -> {OUT}')


main()
