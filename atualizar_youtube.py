"""Descobre o video ao vivo de cada canal do YouTube e gera youtube.m3u (embed direto do video).
Canal que nao estiver ao vivo na hora sai da lista e volta na proxima execucao."""
import re, urllib.request
from concurrent.futures import ThreadPoolExecutor

# (nome, grupo, canal do YouTube ou None, video fixo ou None)
CANAIS = [
    ('TV Senado', 'Legislative', 'UCLgti7NuK0RuW9wty-fxPjQ', None),
    ('TV Câmara', 'Legislative', 'UC-ZkSRh-7UEuwXJQ9UMCFJA', None),
    ('TV Justiça', 'Legislative', None, 'XfwDB9udBLw'),
    ('CNN Brasil', 'News', 'UCvdwhh_fDyWccR42-rReZLw', None),
    ('Band Jornalismo', 'News', 'UCoa-D_VfMkFrCYodrOC9-mA', None),
    ('SBT News', 'News', 'UC376n347Ob5Lwzq2WGzF1AA', None),
    ('Record News', 'News', 'UCuiLR4p6wQ3xLEm15pEn1Xw', None),
    ('Jovem Pan News', 'News', 'UCP391YRAjSOdM_bwievgaZA', None),
    ('Canal Gov', 'Public', 'UCjaWLFTNqLkq3ZY2BJ4NYRg', None),
    ('TV Aparecida', 'Religious', 'UCfYrK5JU5EznsnK3wQE7iIg', None),
]
HDR = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'pt-BR', 'Cookie': 'CONSENT=YES+1; SOCS=CAI'}


def pagina(url):
    for _ in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=20) as r:
                return r.read().decode('utf-8', 'ignore')
        except Exception:
            pass
    return ''


def video_ao_vivo(canal):
    p = pagina(f'https://www.youtube.com/channel/{canal}/live')
    m = re.search(r'<link rel="canonical" href="https://www\.youtube\.com/watch\?v=([\w-]{11})"', p)
    if m and '"isLive":true' in p and '"playableInEmbed":true' in p:
        return m.group(1)


def resolve(c):
    nome, grupo, canal, fixo = c
    vid = fixo or video_ao_vivo(canal)
    return (nome, grupo, vid)


def main():
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(resolve, CANAIS))
    with open('youtube.m3u', 'w', encoding='utf-8', newline='\n') as f:
        f.write('#EXTM3U\n')
        for nome, grupo, vid in res:
            if vid:
                f.write(f'#EXTINF:-1 group-title="{grupo}",{nome} (YouTube)\nhttps://www.youtube.com/embed/{vid}\n')
            print(('ok     ' if vid else 'offline'), nome, vid or '')


main()
