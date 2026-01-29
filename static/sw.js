// Service Worker para Biblioteca Pessoal PWA
const CACHE_NAME = 'biblioteca-pessoal-v1';
const STATIC_ASSETS = [
    '/',
    '/biblioteca',
    '/fila',
    '/diario',
    '/estatisticas',
    '/notas',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/logo.png',
    '/static/manifest.json'
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Cache aberto');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Ativação e limpeza de caches antigos
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((cacheName) => cacheName !== CACHE_NAME)
                    .map((cacheName) => caches.delete(cacheName))
            );
        }).then(() => self.clients.claim())
    );
});

// Estratégia Network First com fallback para cache
self.addEventListener('fetch', (event) => {
    // Ignorar requisições de API (sempre buscar da rede)
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return new Response(JSON.stringify({ error: 'Offline' }), {
                        headers: { 'Content-Type': 'application/json' },
                        status: 503
                    });
                })
        );
        return;
    }

    // Para assets estáticos e páginas: Network First
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Clone a resposta para guardar no cache
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseClone);
                });
                return response;
            })
            .catch(() => {
                // Se não conseguir da rede, tenta do cache
                return caches.match(event.request)
                    .then((response) => {
                        if (response) {
                            return response;
                        }
                        // Fallback para página offline
                        if (event.request.mode === 'navigate') {
                            return caches.match('/');
                        }
                        return new Response('Conteúdo não disponível offline', {
                            status: 503,
                            statusText: 'Service Unavailable'
                        });
                    });
            })
    );
});

// Receber mensagens do app principal
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
