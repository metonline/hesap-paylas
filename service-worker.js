// Service Worker - PWA desteği
const CACHE_NAME = 'hesap-paylas-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/styles.css',
  '/script.js',
  '/manifest.json'
];

// Service Worker kurulum
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// Service Worker aktivasyon
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Network first, then cache stratejisi
self.addEventListener('fetch', event => {
  // GET istekleri için cache-first strateji
  if (event.request.method === 'GET') {
    event.respondWith(
      caches.match(event.request).then(response => {
        if (response) {
          // Cache'den return et
          return response;
        }
        
        return fetch(event.request).then(response => {
          // Başarılı response'u cache'le (chrome-extension ve data: URL'leri exclude et)
          if (!response || response.status !== 200 || response.type === 'error' || 
              event.request.url.startsWith('chrome-extension://') || 
              event.request.url.startsWith('data:')) {
            return response;
          }
          
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
          
          return response;
        }).catch(() => {
          // Offline olduğunda cache'den geri dön
          return caches.match(event.request);
        });
      })
    );
  }
});

// Background sync (gelecek)
self.addEventListener('sync', event => {
  if (event.tag === 'sync-orders') {
    event.waitUntil(
      // Senkronizasyon mantığı
      Promise.resolve()
    );
  }
});
