"""
Constants and fallback utilities for the Python File Server.
"""

import gzip
from collections import OrderedDict
from pathlib import Path

# Base Paths
SCRIPT_DIR = Path(__file__).resolve().parent.parent
ICONS_DIRECTORY = SCRIPT_DIR / "icons"

# Maximum POST request size (Defaults to 64MB to protect memory pools)
MAX_POST_SIZE = 64 * 1024 * 1000

# Skip caching compressed output larger than this — big files would otherwise
# sit in memory forever just because they were requested once.
MAX_CACHEABLE_SIZE = 2 * 1024 * 1024  # 2MB


class SimpleCachedCompressor:
    """
    Size-bounded LRU cache for gzip-compressed bytes.

    Unlike a plain dict capped by *count*, this bounds total memory used by
    the cache (via max_total_bytes) and evicts least-recently-used entries,
    so a handful of large files can't starve out everything else or grow
    the cache unboundedly.
    """

    def __init__(self, max_entries: int = 128, max_total_bytes: int = 32 * 1024 * 1024):
        self.max_entries = max_entries
        self.max_total_bytes = max_total_bytes
        self._cache: "OrderedDict[str, bytes]" = OrderedDict()
        self._total_bytes = 0

    def compress(
        self, data: bytes, compresslevel: int = 6, cache_key: str = None
    ) -> bytes:
        if cache_key and cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            return self._cache[cache_key]

        compressed = gzip.compress(data, compresslevel=compresslevel)

        if cache_key and len(compressed) <= MAX_CACHEABLE_SIZE:
            self._cache[cache_key] = compressed
            self._total_bytes += len(compressed)
            self._cache.move_to_end(cache_key)
            self._evict_if_needed()

        return compressed

    def _evict_if_needed(self) -> None:
        while self._cache and (
            len(self._cache) > self.max_entries
            or self._total_bytes > self.max_total_bytes
        ):
            _, evicted = self._cache.popitem(last=False)
            self._total_bytes -= len(evicted)


# Global component instance expected by ThreadedHandlerWithSockets
COMPRESSION_CACHE = SimpleCachedCompressor(
    max_entries=128, max_total_bytes=32 * 1024 * 1024
)
