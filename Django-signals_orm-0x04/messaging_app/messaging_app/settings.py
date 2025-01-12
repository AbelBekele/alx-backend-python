CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Optional: Add cache middleware if you want site-wide caching
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    # ... existing middleware ...
    'django.middleware.cache.FetchFromCacheMiddleware',
]

# Cache timeout in seconds
CACHE_MIDDLEWARE_SECONDS = 60 