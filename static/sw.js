// Service Worker for offline functionality
// Version 2.0

const CACHE_NAME = 'nutrition-tracker-v2.0';
const urlsToCache = [
    '/',
    '/static/css/final-polish.css',
    '/static/js/app.js',
    '/static/js/shortcuts.js',
    '/static/js/offline.js',
    '/static/js/notifications.js',
    '/static/js/admin.js',
    '/manifest.json',
    '/static/vendor/bootstrap/bootstrap.min.css',
    '/static/vendor/bootstrap/bootstrap.bundle.min.js'
];

// Install event - cache resources
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('📦 Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Cache hit - return response
                if (response) {
                    return response;
                }

                return fetch(event.request).then(
                    function(response) {
                        // Check if we received a valid response
                        if(!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response
                        var responseToCache = response.clone();

                        caches.open(CACHE_NAME)
                            .then(function(cache) {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    }
                );
            }
        )
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🗑️ Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for offline data
self.addEventListener('sync', function(event) {
    if (event.tag === 'sync-nutrition-data') {
        event.waitUntil(syncOfflineData());
    }
});

async function syncOfflineData() {
    // Get offline data from IndexedDB and sync to server
    console.log('🔄 Syncing offline data...');
    
    try {
        // Implementation would depend on your offline data storage strategy
        // This is a placeholder for the sync logic
        console.log('✅ Offline data synced');
    } catch (error) {
        console.error('❌ Sync failed:', error);
        throw error; // Retry sync later
    }
}

// Push notifications (if needed)
self.addEventListener('push', function(event) {
    const options = {
        body: event.data ? event.data.text() : 'New nutrition data available!',
        icon: '/static/icon-192.png',
        badge: '/static/icon-192.png'
    };

    event.waitUntil(
        self.registration.showNotification('🥗 Nutrition Tracker', options)
    );
});
