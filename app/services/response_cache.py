"""
Response Caching System for AI Language Tutor App

This module implements intelligent response caching to reduce API costs by:
- Caching common conversation patterns
- Storing frequently requested translations
- Implementing smart cache key generation
- Managing cache expiration and storage limits
- Providing cache hit/miss analytics
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Types of cacheable content"""

    CONVERSATION = "conversation"
    TRANSLATION = "translation"
    EXPLANATION = "explanation"
    SIMPLE_QA = "simple_qa"


@dataclass
class CacheEntry:
    """Cached response entry"""

    content: str
    provider: str
    language: str
    cache_type: CacheType
    created_at: datetime
    hit_count: int = 0
    last_accessed: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def is_stale(self, max_age_hours: int = 24) -> bool:
        """Check if cache entry is stale"""
        age = datetime.now() - self.created_at
        return age > timedelta(hours=max_age_hours)


class ResponseCache:
    """Intelligent response caching system"""

    def __init__(self, max_entries: int = 1000, default_ttl_hours: int = 24):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_entries = max_entries
        self.default_ttl_hours = default_ttl_hours
        self.stats = {"hits": 0, "misses": 0, "evictions": 0, "total_requests": 0}

        # Define cacheable patterns
        self.cacheable_patterns = {
            CacheType.CONVERSATION: [
                "hello",
                "hi",
                "how are you",
                "goodbye",
                "bye",
                "thanks",
                "thank you",
                "good morning",
                "good evening",
                "nice to meet you",
                "see you later",
            ],
            CacheType.TRANSLATION: [
                "translate",
                "what does",
                "mean in",
                "how do you say",
            ],
            CacheType.EXPLANATION: [
                "what is",
                "explain",
                "define",
                "meaning of",
                "tell me about",
            ],
            CacheType.SIMPLE_QA: [
                "help me",
                "can you",
                "how to",
                "why",
                "when",
                "where",
            ],
        }

    def _generate_cache_key(
        self,
        messages: List[Dict[str, str]],
        language: str,
        provider: Optional[str] = None,
    ) -> str:
        """Generate a unique cache key for the request"""

        # Extract the last user message (most relevant for caching)
        last_message = ""
        if messages:
            last_message = messages[-1].get("content", "").lower().strip()

        # Create a normalized key
        key_data = {
            "message": last_message[:200],  # Limit length
            "language": language,
            "message_count": len(messages),
        }

        # Generate hash
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _determine_cache_type(self, message: str) -> Optional[CacheType]:
        """Determine if and how a message should be cached"""

        message_lower = message.lower().strip()

        for cache_type, patterns in self.cacheable_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return cache_type

        return None

    def _should_cache(
        self, messages: List[Dict[str, str]], language: str, response_content: str
    ) -> bool:
        """Determine if a response should be cached"""

        if not messages or not response_content:
            return False

        # Don't cache very long responses (likely unique)
        if len(response_content) > 1000:
            return False

        # Don't cache very short responses (likely errors)
        if len(response_content) < 20:
            return False

        # Check if message matches cacheable patterns
        last_message = messages[-1].get("content", "")
        cache_type = self._determine_cache_type(last_message)

        return cache_type is not None

    def get(
        self,
        messages: List[Dict[str, str]],
        language: str,
        provider: Optional[str] = None,
    ) -> Optional[CacheEntry]:
        """Retrieve cached response if available"""

        self.stats["total_requests"] += 1

        cache_key = self._generate_cache_key(messages, language, provider)

        if cache_key not in self.cache:
            self.stats["misses"] += 1
            return None

        entry = self.cache[cache_key]

        # Check if entry is expired or stale
        if entry.is_expired() or entry.is_stale():
            del self.cache[cache_key]
            self.stats["misses"] += 1
            return None

        # Update access stats
        entry.hit_count += 1
        entry.last_accessed = datetime.now()
        self.stats["hits"] += 1

        logger.info(f"Cache HIT for key: {cache_key[:10]}... (hit #{entry.hit_count})")
        return entry

    def set(
        self,
        messages: List[Dict[str, str]],
        language: str,
        response_content: str,
        provider: str,
        ttl_hours: Optional[int] = None,
    ) -> bool:
        """Cache a response if appropriate"""

        if not self._should_cache(messages, language, response_content):
            return False

        cache_key = self._generate_cache_key(messages, language, provider)

        # Determine cache type
        last_message = messages[-1].get("content", "")
        cache_type = self._determine_cache_type(last_message)
        if cache_type is None:
            return False

        # Calculate expiration
        ttl = ttl_hours or self.default_ttl_hours
        expires_at = datetime.now() + timedelta(hours=ttl)

        # Create cache entry
        entry = CacheEntry(
            content=response_content,
            provider=provider,
            language=language,
            cache_type=cache_type,
            created_at=datetime.now(),
            expires_at=expires_at,
        )

        # Evict old entries if cache is full
        if len(self.cache) >= self.max_entries:
            self._evict_lru()

        self.cache[cache_key] = entry
        logger.info(
            f"Cache SET for key: {cache_key[:10]}... (type: {cache_type.value})"
        )
        return True

    def _evict_lru(self):
        """Evict least recently used cache entry"""

        if not self.cache:
            return

        # Find LRU entry
        lru_key = None
        lru_time = datetime.now()

        for key, entry in self.cache.items():
            access_time = entry.last_accessed or entry.created_at
            if access_time < lru_time:
                lru_time = access_time
                lru_key = key

        if lru_key:  # pragma: no branch
            del self.cache[lru_key]
            self.stats["evictions"] += 1
            logger.info(f"Cache EVICT LRU: {lru_key[:10]}...")

    def clear_expired(self):
        """Remove all expired cache entries"""

        expired_keys = []
        for key, entry in self.cache.items():
            if entry.is_expired() or entry.is_stale():
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info(f"Cache cleanup: removed {len(expired_keys)} expired entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""

        total_requests = self.stats["total_requests"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        # Calculate cache size and types
        type_distribution = {}
        total_size = 0

        for entry in self.cache.values():
            cache_type = entry.cache_type.value
            type_distribution[cache_type] = type_distribution.get(cache_type, 0) + 1
            total_size += len(entry.content)

        return {
            "entries": len(self.cache),
            "max_entries": self.max_entries,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "total_size_bytes": total_size,
            "type_distribution": type_distribution,
            "avg_entry_size": round(total_size / len(self.cache)) if self.cache else 0,
        }

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")


# Global cache instance
response_cache = ResponseCache(max_entries=1000, default_ttl_hours=24)
