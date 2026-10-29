"""Testa channels-all.m3u e gera channels.m3u (https, funciona no site) e channels-http.m3u.
Um canal so sai da lista depois de FALHAS_MAX testes seguidos com falha (contador em status.json)."""
import json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor

FALHAS_MAX = 3
ORIGIN = 'https://jacimarlirio-bola.github.io'
HDR = {'User-Agent': 'Mozilla/5.0', 'Origin': ORIGIN}


def ler(path):
    lines = open(path, encoding='utf-8').read().splitlines()
    out, i = [], 1
    while i < len(lines):
        if lines[i].startswith('#EXTINF'):
            blk = [lines[i]]
            i += 1
            while i < len(lines) and not lines[i].startswith('http'):
                blk.append(lines[i])
                i += 1
            if i < len(lines):
                blk.append(lines[i])
                out.append(blk)
        i += 1
    return out


def testa(blk):
    url = blk[-1]
    for _ in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=12) as r:
                cors = r.headers.get('Access-Control-Allow-Origin')
                head = r.read(2048).decode('utf-8', 'ignore')
            if cors and head.lstrip().startswith('#EXTM3U'):
                return True
        except Exception:
            pass
    return False


def gravar(path, blocos):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('#EXTM3U\n')
        for b in blocos:
            f.write('\n'.join(b) + '\n')


def main():
    canais = ler('channels-all.m3u')
    try:
        falhas = json.load(open('status.json', encoding='utf-8'))
    except Exception:
        falhas = {}
    with ThreadPoolExecutor(40) as ex:
        ok = list(ex.map(testa, canais))
    novo, https, http, removidos = {}, [], [], []
    for b, bom in zip(canais, ok):
        url = b[-1]
        n = 0 if bom else falhas.get(url, 0) + 1
        if n >= FALHAS_MAX:
            removidos.append(b[0].split(',')[-1])
            novo[url] = n
            continue
        novo[url] = n
        (https if url.startswith('https:') else http).append(b)
    gravar('channels.m3u', https)
    gravar('channels-http.m3u', http)
    json.dump(novo, open('status.json', 'w', encoding='utf-8'), indent=0)
    print(f'{len(canais)} testados | {len(https)} no site | {len(http)} http | {len(removidos)} removidos')
    for n in removidos:
        print('  removido:', n)


main()
