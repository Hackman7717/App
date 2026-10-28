/* Offline-Betrieb: Alle Dateien der App liegen im Cache. Neue Versionen werden im Hintergrund geladen
   und erst übernommen, wenn du in der App auf „Jetzt aktualisieren“ tippst. */
const VERSION = '1.8.0';
const CACHE = 'trainingsbuch-' + VERSION;
const SCOPE = new URL(self.registration.scope).pathname;
const FILES = [
  './', './index.html', './manifest.webmanifest',
  './icons/icon-180.png', './icons/icon-192.png', './icons/icon-512.png', './icons/icon-maskable-512.png', './icons/favicon-32.png',
  './fonts/saira-condensed-600.woff', './fonts/saira-condensed-700.woff', './fonts/saira-condensed-800.woff', './fonts/public-sans.woff'
];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES.map(u => new Request(u, { cache: 'reload' })))));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('trainingsbuch-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('message', e => { if (e.data === 'skipWaiting') self.skipWaiting(); });
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET') return;
  const url = new URL(r.url);
  // Nur Dateien der App selbst. Andere Pfade derselben Adresse (z. B. /App-Daten/ mit der Lebensmittel-Datenbank) gehen am Cache vorbei.
  if (url.origin !== self.location.origin || !url.pathname.startsWith(SCOPE)) return;
  if (r.mode === 'navigate') {
    e.respondWith(caches.match('./index.html').then(m => m || fetch(r)));
    return;
  }
  e.respondWith(caches.match(r, { ignoreSearch: true }).then(m => m || fetch(r).then(res => {
    if (res.ok && res.type === 'basic') { const copy = res.clone(); caches.open(CACHE).then(c => c.put(r, copy)); }
    return res;
  })));
});
