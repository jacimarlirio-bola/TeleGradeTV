const CACHE = 'minha-tv-v7';
const FILES = ['./', 'index.html', 'manifest.json', 'icon.svg'];

self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))));
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return; // streams e listas sempre da rede
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
