// Service Worker - PWA desteği - AGGRESSIVE CACHE BUSTING
// IMPORTANT: This Service Worker only caches static assets, 
// HTML and JS are ALWAYS fetched from network
const CACHE_VERSION = '20260111-v5';
const CACHE_NAME = 'hesap-paylas-' + CACHE_VERSION;

// GitHub Pages pathed deployment'ı handle et
const isGitHubPages = self.location.hostname === 'metonline.github.io';
const basePath = isGitHubPages ? '/hesap-paylas' : '';

// ONLY cache CSS and manifest - NOT HTML or JS!
const ASSETS_TO_CACHE = [
  basePath + '/styles.css',
  basePath + '/manifest.json'
];

// Service Worker kurulum
self.addEventListener('install', event => {
  console.log('[SW] Installing Service Worker with cache:', CACHE_NAME);
  event.waitUntil(
    // First, delete ALL old caches
    caches.keys().then(cacheNames => {
      console.log('[SW] Found caches:', cacheNames);
      return Promise.all(
        cacheNames.map(name => {
          console.log('[SW] Deleting old cache:', name);
          return caches.delete(name);
        })
      );
    }).then(() => {
      // Then create new cache with ONLY CSS and manifest
      return caches.open(CACHE_NAME).then(cache => {
        console.log('[SW] Creating new cache and adding CSS/manifest only');
        return cache.addAll(ASSETS_TO_CACHE).catch(error => {
          console.warn('[SW] Cache addAll hatası (expected):', error);
          return Promise.resolve();
        });
      });
    })
  );
  self.skipWaiting();
});

// Service Worker aktivasyon
self.addEventListener('activate', event => {
  console.log('[SW] Activating Service Worker');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      console.log('[SW] Activate: Deleting old caches:', cacheNames);
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting cache:', cacheName);
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
  const url = event.request.url;
  
  // API istekleri ALWAYS network-only
  if (url.includes('/api/')) {
    console.log('[SW] Fetch (API - network-only):', url);
    event.respondWith(fetch(event.request));
    return;
  }
  
  // HTML ALWAYS network-only - NEVER cache index.html
  if (url.includes('index.html') || url.endsWith('/')) {
    console.log('[SW] Fetch (HTML - network-only):', url);
    event.respondWith(fetch(event.request).catch(() => {
      return caches.match('/index.html');
    }));
    return;
  }
  
  // script.js ALWAYS network-only - NEVER cache
  if (url.includes('script.js')) {
    console.log('[SW] Fetch (JS - network-only):', url);
    event.respondWith(fetch(event.request).catch(() => {
      return new Response('Service unavailable', { status: 503 });
    }));
    return;
  }
  
  // manifest.json ALWAYS network-only
  if (url.includes('manifest.json')) {
    console.log('[SW] Fetch (manifest - network-only):', url);
    event.respondWith(fetch(event.request));
    return;
  }
  
  // CSS - Cache with network fallback
  if (url.includes('.css')) {
    console.log('[SW] Fetch (CSS - cache first):', url);
    event.respondWith(
      caches.match(event.request).then(response => {
        if (response) {
          console.log('[SW] CSS served from cache');
          return response;
        }
        return fetch(event.request).then(response => {
          if (response && response.status === 200) {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseToCache);
            });
          }
          return response;
        }).catch(() => {
          console.error('[SW] CSS fetch failed, offline');
          return new Response('Offline', { status: 503 });
        });
      })
    );
    return;
  }
  
  // Other GET requests - Cache first with network fallback (fonts, images, etc)
  if (event.request.method === 'GET') {
    console.log('[SW] Fetch (GET - cache first):', url);
    event.respondWith(
      caches.match(event.request).then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request).then(response => {
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
          return response;
        }).catch(() => {
          return caches.match(event.request);
        });
      })
    );
    return;
  }
  
  // All other requests - just network
  event.respondWith(fetch(event.request));
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
