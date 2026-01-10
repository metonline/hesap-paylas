// Service Worker - PWA desteği
const CACHE_NAME = 'hesap-paylas-v2';

// GitHub Pages pathed deployment'ı handle et
const isGitHubPages = self.location.hostname === 'metonline.github.io';
const basePath = isGitHubPages ? '/hesap-paylas' : '';

const ASSETS_TO_CACHE = [
  basePath + '/',
  basePath + '/index.html',
  basePath + '/styles.css',
  basePath + '/script.js',
  basePath + '/manifest.json'
];

// Service Worker kurulum
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      // Hataları yakala, fallback kullan
      return cache.addAll(ASSETS_TO_CACHE).catch(error => {
        console.warn('Cache addAll hatası (beklenen):', error);
        // Hata oluşsa bile devam et
        return Promise.resolve();
      });
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
  // API istekleri network-only - cache yapma
  if (event.request.url.includes('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // GET istekleri için cache-first strateji (sadece assets için)
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
