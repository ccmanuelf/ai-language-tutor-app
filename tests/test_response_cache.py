"""
Comprehensive tests for response_cache.py module

Tests cover:
- CacheType enum
- CacheEntry dataclass (is_expired, is_stale)
- ResponseCache class (all methods)
- Cache operations (get, set, eviction)
- Statistics and analytics
- Global cache instance
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.services.response_cache import (
    CacheEntry,
    CacheType,
    ResponseCache,
    response_cache,
)

# ============================================================================
# Test Class 1: CacheType Enum
# ============================================================================


class TestCacheTypeEnum:
    """Test CacheType enum values"""

    def test_cache_type_conversation_value(self):
        """Test CONVERSATION cache type"""
        assert CacheType.CONVERSATION.value == "conversation"

    def test_cache_type_translation_value(self):
        """Test TRANSLATION cache type"""
        assert CacheType.TRANSLATION.value == "translation"

    def test_cache_type_explanation_value(self):
        """Test EXPLANATION cache type"""
        assert CacheType.EXPLANATION.value == "explanation"

    def test_cache_type_simple_qa_value(self):
        """Test SIMPLE_QA cache type"""
        assert CacheType.SIMPLE_QA.value == "simple_qa"

    def test_cache_type_enum_members(self):
        """Test all enum members exist"""
        assert len(CacheType) == 4
        members = [ct.value for ct in CacheType]
        assert "conversation" in members
        assert "translation" in members
        assert "explanation" in members
        assert "simple_qa" in members


# ============================================================================
# Test Class 2: CacheEntry Dataclass
# ============================================================================


class TestCacheEntryDataclass:
    """Test CacheEntry dataclass and methods"""

    def test_cache_entry_creation_minimal(self):
        """Test creating CacheEntry with required fields"""
        entry = CacheEntry(
            content="Hello",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=datetime.now(),
        )
        assert entry.content == "Hello"
        assert entry.provider == "claude"
        assert entry.language == "en"
        assert entry.cache_type == CacheType.CONVERSATION
        assert entry.hit_count == 0
        assert entry.last_accessed is None
        assert entry.expires_at is None

    def test_cache_entry_creation_with_all_fields(self):
        """Test creating CacheEntry with all fields"""
        now = datetime.now()
        expires = now + timedelta(hours=24)
        entry = CacheEntry(
            content="Hello",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=now,
            hit_count=5,
            last_accessed=now,
            expires_at=expires,
        )
        assert entry.hit_count == 5
        assert entry.last_accessed == now
        assert entry.expires_at == expires

    def test_is_expired_when_expires_at_is_none(self):
        """Test is_expired returns False when expires_at is None"""
        entry = CacheEntry(
            content="Test",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=datetime.now(),
            expires_at=None,
        )
        assert entry.is_expired() is False

    def test_is_expired_when_not_expired(self):
        """Test is_expired returns False when entry is fresh"""
        future_time = datetime.now() + timedelta(hours=1)
        entry = CacheEntry(
            content="Test",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=datetime.now(),
            expires_at=future_time,
        )
        assert entry.is_expired() is False

    def test_is_expired_when_expired(self):
        """Test is_expired returns True when entry is expired"""
        past_time = datetime.now() - timedelta(hours=1)
        entry = CacheEntry(
            content="Test",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=datetime.now() - timedelta(hours=25),
            expires_at=past_time,
        )
        assert entry.is_expired() is True

    def test_is_stale_when_fresh(self):
        """Test is_stale returns False for fresh entries"""
        entry = CacheEntry(
            content="Test",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=datetime.now(),
        )
        assert entry.is_stale(max_age_hours=24) is False

    def test_is_stale_when_stale(self):
        """Test is_stale returns True for old entries"""
        old_time = datetime.now() - timedelta(hours=25)
        entry = CacheEntry(
            content="Test",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=old_time,
        )
        assert entry.is_stale(max_age_hours=24) is True

    def test_is_stale_custom_max_age(self):
        """Test is_stale with custom max_age_hours"""
        old_time = datetime.now() - timedelta(hours=50)
        entry = CacheEntry(
            content="Test",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=old_time,
        )
        # Stale with 24h max age
        assert entry.is_stale(max_age_hours=24) is True
        # Fresh with 72h max age
        assert entry.is_stale(max_age_hours=72) is False

    def test_cache_entry_different_cache_types(self):
        """Test CacheEntry with all cache types"""
        for cache_type in CacheType:
            entry = CacheEntry(
                content="Test",
                provider="claude",
                language="en",
                cache_type=cache_type,
                created_at=datetime.now(),
            )
            assert entry.cache_type == cache_type

    def test_cache_entry_different_providers(self):
        """Test CacheEntry with different providers"""
        providers = ["claude", "mistral", "qwen", "deepseek", "ollama"]
        for provider in providers:
            entry = CacheEntry(
                content="Test",
                provider=provider,
                language="en",
                cache_type=CacheType.CONVERSATION,
                created_at=datetime.now(),
            )
            assert entry.provider == provider

    def test_cache_entry_different_languages(self):
        """Test CacheEntry with different languages"""
        languages = ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"]
        for language in languages:
            entry = CacheEntry(
                content="Test",
                provider="claude",
                language=language,
                cache_type=CacheType.CONVERSATION,
                created_at=datetime.now(),
            )
            assert entry.language == language


# ============================================================================
# Test Class 3: ResponseCache Initialization
# ============================================================================


class TestResponseCacheInitialization:
    """Test ResponseCache initialization"""

    def test_response_cache_default_initialization(self):
        """Test ResponseCache with default parameters"""
        cache = ResponseCache()
        assert cache.max_entries == 1000
        assert cache.default_ttl_hours == 24
        assert len(cache.cache) == 0
        assert cache.stats == {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0,
        }

    def test_response_cache_custom_max_entries(self):
        """Test ResponseCache with custom max_entries"""
        cache = ResponseCache(max_entries=500)
        assert cache.max_entries == 500
        assert cache.default_ttl_hours == 24

    def test_response_cache_custom_ttl(self):
        """Test ResponseCache with custom default_ttl_hours"""
        cache = ResponseCache(default_ttl_hours=12)
        assert cache.max_entries == 1000
        assert cache.default_ttl_hours == 12

    def test_response_cache_custom_both_parameters(self):
        """Test ResponseCache with both custom parameters"""
        cache = ResponseCache(max_entries=2000, default_ttl_hours=48)
        assert cache.max_entries == 2000
        assert cache.default_ttl_hours == 48

    def test_cacheable_patterns_initialized(self):
        """Test cacheable patterns are properly initialized"""
        cache = ResponseCache()
        assert CacheType.CONVERSATION in cache.cacheable_patterns
        assert CacheType.TRANSLATION in cache.cacheable_patterns
        assert CacheType.EXPLANATION in cache.cacheable_patterns
        assert CacheType.SIMPLE_QA in cache.cacheable_patterns
        # Check some patterns
        assert "hello" in cache.cacheable_patterns[CacheType.CONVERSATION]
        assert "translate" in cache.cacheable_patterns[CacheType.TRANSLATION]
        assert "what is" in cache.cacheable_patterns[CacheType.EXPLANATION]
        assert "help me" in cache.cacheable_patterns[CacheType.SIMPLE_QA]


# ============================================================================
# Test Class 4: Cache Key Generation
# ============================================================================


class TestCacheKeyGeneration:
    """Test _generate_cache_key method"""

    def test_generate_cache_key_simple_message(self):
        """Test cache key generation with simple message"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "Hello"}]
        key = cache._generate_cache_key(messages, "en", "claude")
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

    def test_generate_cache_key_same_inputs_same_key(self):
        """Test same inputs produce same cache key"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "Hello"}]
        key1 = cache._generate_cache_key(messages, "en", "claude")
        key2 = cache._generate_cache_key(messages, "en", "claude")
        assert key1 == key2

    def test_generate_cache_key_different_message_different_key(self):
        """Test different messages produce different keys"""
        cache = ResponseCache()
        messages1 = [{"role": "user", "content": "Hello"}]
        messages2 = [{"role": "user", "content": "Goodbye"}]
        key1 = cache._generate_cache_key(messages1, "en", "claude")
        key2 = cache._generate_cache_key(messages2, "en", "claude")
        assert key1 != key2

    def test_generate_cache_key_different_language_different_key(self):
        """Test different languages produce different keys"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "Hello"}]
        key1 = cache._generate_cache_key(messages, "en", "claude")
        key2 = cache._generate_cache_key(messages, "es", "claude")
        assert key1 != key2

    def test_generate_cache_key_case_insensitive(self):
        """Test cache key is case-insensitive"""
        cache = ResponseCache()
        messages1 = [{"role": "user", "content": "Hello"}]
        messages2 = [{"role": "user", "content": "HELLO"}]
        key1 = cache._generate_cache_key(messages1, "en", "claude")
        key2 = cache._generate_cache_key(messages2, "en", "claude")
        assert key1 == key2

    def test_generate_cache_key_strips_whitespace(self):
        """Test cache key strips leading/trailing whitespace"""
        cache = ResponseCache()
        messages1 = [{"role": "user", "content": "Hello"}]
        messages2 = [{"role": "user", "content": "  Hello  "}]
        key1 = cache._generate_cache_key(messages1, "en", "claude")
        key2 = cache._generate_cache_key(messages2, "en", "claude")
        assert key1 == key2

    def test_generate_cache_key_empty_messages(self):
        """Test cache key generation with empty messages"""
        cache = ResponseCache()
        messages = []
        key = cache._generate_cache_key(messages, "en", "claude")
        assert isinstance(key, str)
        assert len(key) == 32

    def test_generate_cache_key_multiple_messages(self):
        """Test cache key includes message count (different lengths = different keys)"""
        cache = ResponseCache()
        messages1 = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Hello"},
        ]
        messages2 = [{"role": "user", "content": "Hello"}]
        key1 = cache._generate_cache_key(messages1, "en", "claude")
        key2 = cache._generate_cache_key(messages2, "en", "claude")
        # Different message counts = different keys (includes message_count in key_data)
        assert key1 != key2

    def test_generate_cache_key_long_message_truncated(self):
        """Test cache key truncates long messages to 200 chars"""
        cache = ResponseCache()
        long_message = "x" * 500
        messages = [{"role": "user", "content": long_message}]
        key = cache._generate_cache_key(messages, "en", "claude")
        assert isinstance(key, str)
        assert len(key) == 32  # Still valid MD5 hash


# ============================================================================
# Test Class 5: Cache Type Determination
# ============================================================================


class TestCacheTypeDetermination:
    """Test _determine_cache_type method"""

    def test_determine_cache_type_conversation_hello(self):
        """Test CONVERSATION type for 'hello'"""
        cache = ResponseCache()
        cache_type = cache._determine_cache_type("hello")
        assert cache_type == CacheType.CONVERSATION

    def test_determine_cache_type_conversation_goodbye(self):
        """Test CONVERSATION type for 'goodbye'"""
        cache = ResponseCache()
        cache_type = cache._determine_cache_type("goodbye, see you later")
        assert cache_type == CacheType.CONVERSATION

    def test_determine_cache_type_translation(self):
        """Test TRANSLATION type"""
        cache = ResponseCache()
        # Note: "translate" is first TRANSLATION pattern that doesn't match CONVERSATION
        cache_type = cache._determine_cache_type("translate bonjour to English")
        assert cache_type == CacheType.TRANSLATION

    def test_determine_cache_type_explanation(self):
        """Test EXPLANATION type"""
        cache = ResponseCache()
        # "what is" pattern matches EXPLANATION
        cache_type = cache._determine_cache_type("what is the definition of grammar")
        assert cache_type == CacheType.EXPLANATION

    def test_determine_cache_type_simple_qa(self):
        """Test SIMPLE_QA type"""
        cache = ResponseCache()
        cache_type = cache._determine_cache_type("help me with grammar")
        assert cache_type == CacheType.SIMPLE_QA

    def test_determine_cache_type_no_match(self):
        """Test None returned when no pattern matches"""
        cache = ResponseCache()
        # Must avoid all patterns: hello, goodbye, thanks, translate, what, help, etc.
        cache_type = cache._determine_cache_type("xyz unique message 12345 no patterns")
        assert cache_type is None

    def test_determine_cache_type_case_insensitive(self):
        """Test cache type determination is case-insensitive"""
        cache = ResponseCache()
        cache_type1 = cache._determine_cache_type("HELLO")
        cache_type2 = cache._determine_cache_type("hello")
        assert cache_type1 == cache_type2 == CacheType.CONVERSATION

    def test_determine_cache_type_with_extra_text(self):
        """Test cache type with pattern in middle of text"""
        cache = ResponseCache()
        cache_type = cache._determine_cache_type("I want to say hello to my friend")
        assert cache_type == CacheType.CONVERSATION

    def test_determine_cache_type_empty_message(self):
        """Test cache type with empty message"""
        cache = ResponseCache()
        cache_type = cache._determine_cache_type("")
        assert cache_type is None

    def test_determine_cache_type_whitespace_only(self):
        """Test cache type with whitespace-only message"""
        cache = ResponseCache()
        cache_type = cache._determine_cache_type("   ")
        assert cache_type is None


# ============================================================================
# Test Class 6: Should Cache Logic
# ============================================================================


class TestShouldCacheLogic:
    """Test _should_cache method"""

    def test_should_cache_valid_conversation(self):
        """Test should cache valid conversation message"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "Hello! How can I help you?"
        assert cache._should_cache(messages, "en", response) is True

    def test_should_cache_empty_messages(self):
        """Test should not cache when messages empty"""
        cache = ResponseCache()
        messages = []
        response = "Hello! How are you today?"
        assert cache._should_cache(messages, "en", response) is False

    def test_should_cache_empty_response(self):
        """Test should not cache when response empty"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = ""
        assert cache._should_cache(messages, "en", response) is False

    def test_should_cache_response_too_long(self):
        """Test should not cache very long responses"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "x" * 1001  # Over 1000 char limit
        assert cache._should_cache(messages, "en", response) is False

    def test_should_cache_response_too_short(self):
        """Test should not cache very short responses"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "Hi"  # Less than 20 chars
        assert cache._should_cache(messages, "en", response) is False

    def test_should_cache_no_matching_pattern(self):
        """Test should not cache when no pattern matches"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "unique message xyz123"}]
        response = "This is a valid length response"
        assert cache._should_cache(messages, "en", response) is False

    def test_should_cache_translation_pattern(self):
        """Test should cache translation requests"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "translate hello to Spanish"}]
        response = "The translation is: Hola"
        assert cache._should_cache(messages, "en", response) is True

    def test_should_cache_explanation_pattern(self):
        """Test should cache explanation requests"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "explain what grammar means"}]
        response = "Grammar is the set of rules that govern language structure."
        assert cache._should_cache(messages, "en", response) is True

    def test_should_cache_simple_qa_pattern(self):
        """Test should cache simple Q&A"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "help me understand this"}]
        response = "I'd be happy to help you understand this topic!"
        assert cache._should_cache(messages, "en", response) is True

    def test_should_cache_response_exactly_1000_chars(self):
        """Test should cache response at exactly 1000 chars"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "x" * 1000  # Exactly 1000 chars
        assert cache._should_cache(messages, "en", response) is True

    def test_should_cache_response_exactly_20_chars(self):
        """Test should cache response at exactly 20 chars"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "x" * 20  # Exactly 20 chars
        assert cache._should_cache(messages, "en", response) is True

    def test_should_cache_none_response(self):
        """Test should not cache None response"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = None
        assert cache._should_cache(messages, "en", response) is False


# ============================================================================
# Test Class 7: Get Operation
# ============================================================================


class TestGetOperation:
    """Test get method"""

    def test_get_cache_miss(self):
        """Test get returns None on cache miss"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        result = cache.get(messages, "en", "claude")
        assert result is None
        assert cache.stats["misses"] == 1
        assert cache.stats["hits"] == 0
        assert cache.stats["total_requests"] == 1

    def test_get_cache_hit(self):
        """Test get returns entry on cache hit"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "Hello! How can I help you today?"

        # First set the cache
        cache.set(messages, "en", response, "claude")

        # Then get it
        result = cache.get(messages, "en", "claude")
        assert result is not None
        assert result.content == response
        assert cache.stats["hits"] == 1
        assert cache.stats["misses"] == 0

    def test_get_increments_hit_count(self):
        """Test get increments hit_count on cache hit"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "Hello! How can I help you today?"

        cache.set(messages, "en", response, "claude")

        result1 = cache.get(messages, "en", "claude")
        assert result1.hit_count == 1

        result2 = cache.get(messages, "en", "claude")
        assert result2.hit_count == 2

    def test_get_updates_last_accessed(self):
        """Test get updates last_accessed timestamp"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "Hello! How can I help you today?"

        cache.set(messages, "en", response, "claude")

        result = cache.get(messages, "en", "claude")
        assert result.last_accessed is not None
        assert isinstance(result.last_accessed, datetime)

    def test_get_expired_entry_returns_none(self):
        """Test get returns None for expired entries"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]

        # Manually create expired entry (set expires_at in past)
        cache_key = cache._generate_cache_key(messages, "en", "claude")
        past_time = datetime.now() - timedelta(hours=1)
        cache.cache[cache_key] = CacheEntry(
            content="Hello! How can I help you today?",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=datetime.now() - timedelta(hours=25),
            expires_at=past_time,
        )

        # Try to get - should be expired
        result = cache.get(messages, "en", "claude")
        assert result is None
        assert cache.stats["misses"] == 1

    def test_get_stale_entry_returns_none(self):
        """Test get returns None for stale entries"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]

        # Manually create stale entry
        cache_key = cache._generate_cache_key(messages, "en", "claude")
        old_time = datetime.now() - timedelta(hours=25)
        cache.cache[cache_key] = CacheEntry(
            content="Old response",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=old_time,
        )

        # Try to get - should be stale
        result = cache.get(messages, "en", "claude")
        assert result is None
        assert cache_key not in cache.cache  # Should be deleted

    def test_get_increments_total_requests(self):
        """Test get always increments total_requests"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]

        # Miss
        cache.get(messages, "en", "claude")
        assert cache.stats["total_requests"] == 1

        # Hit
        cache.set(messages, "en", "Hello! How can I help?", "claude")
        cache.get(messages, "en", "claude")
        assert cache.stats["total_requests"] == 2

    def test_get_with_none_messages(self):
        """Test get with None messages raises TypeError"""
        cache = ResponseCache()
        # _generate_cache_key tries to call len(messages), which fails for None
        with pytest.raises(TypeError):
            cache.get(None, "en", "claude")

    def test_get_different_languages_different_cache(self):
        """Test get with different languages accesses different cache entries"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]

        cache.set(messages, "en", "Hello! How can I help you?", "claude")
        cache.set(messages, "es", "¡Hola! ¿Cómo puedo ayudarte?", "claude")

        result_en = cache.get(messages, "en", "claude")
        result_es = cache.get(messages, "es", "claude")

        assert result_en.content == "Hello! How can I help you?"
        assert result_es.content == "¡Hola! ¿Cómo puedo ayudarte?"

    def test_get_logging_on_hit(self, caplog):
        """Test get logs cache hit"""
        import logging

        caplog.set_level(logging.INFO)

        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help you today?", "claude")
        cache.get(messages, "en", "claude")

        assert "Cache HIT" in caplog.text


# ============================================================================
# Test Class 8: Set Operation
# ============================================================================


class TestSetOperation:
    """Test set method"""

    def test_set_valid_entry(self):
        """Test set adds valid entry to cache"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "Hello! How can I help you?"

        result = cache.set(messages, "en", response, "claude")
        assert result is True
        assert len(cache.cache) == 1

    def test_set_returns_false_when_should_not_cache(self):
        """Test set returns False when should not cache"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "unique xyz123"}]
        response = "Response"

        result = cache.set(messages, "en", response, "claude")
        assert result is False
        assert len(cache.cache) == 0

    def test_set_with_custom_ttl(self):
        """Test set with custom TTL"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        response = "Hello! How can I help you?"

        cache.set(messages, "en", response, "claude", ttl_hours=48)

        cache_key = cache._generate_cache_key(messages, "en", "claude")
        entry = cache.cache[cache_key]

        # Check TTL is approximately 48 hours from now
        time_until_expiry = entry.expires_at - datetime.now()
        assert 47 <= time_until_expiry.total_seconds() / 3600 <= 49

    def test_set_with_default_ttl(self):
        """Test set uses default TTL when not specified"""
        cache = ResponseCache(default_ttl_hours=36)
        messages = [{"role": "user", "content": "hello"}]
        response = "Hello! How can I help you?"

        cache.set(messages, "en", response, "claude")

        cache_key = cache._generate_cache_key(messages, "en", "claude")
        entry = cache.cache[cache_key]

        # Check TTL is approximately 36 hours from now
        time_until_expiry = entry.expires_at - datetime.now()
        assert 35 <= time_until_expiry.total_seconds() / 3600 <= 37

    def test_set_creates_correct_cache_type(self):
        """Test set creates entry with correct cache type"""
        cache = ResponseCache()

        # Conversation
        messages1 = [{"role": "user", "content": "hello"}]
        cache.set(messages1, "en", "Hello! How can I help you?", "claude")
        key1 = cache._generate_cache_key(messages1, "en", "claude")
        assert cache.cache[key1].cache_type == CacheType.CONVERSATION

        # Translation (use "translate bonjour" to avoid "hello" pattern)
        messages2 = [{"role": "user", "content": "translate bonjour"}]
        cache.set(messages2, "en", "Translation result: Bonjour", "claude")
        key2 = cache._generate_cache_key(messages2, "en", "claude")
        assert cache.cache[key2].cache_type == CacheType.TRANSLATION

    def test_set_evicts_when_cache_full(self):
        """Test set evicts LRU entry when cache is full"""
        cache = ResponseCache(max_entries=2)

        # Add 2 entries
        messages1 = [{"role": "user", "content": "hello"}]
        cache.set(messages1, "en", "Hello! How are you today?", "claude")

        messages2 = [{"role": "user", "content": "goodbye"}]
        cache.set(messages2, "en", "Goodbye! See you later!", "claude")

        assert len(cache.cache) == 2
        assert cache.stats["evictions"] == 0

        # Add 3rd entry - should evict first
        messages3 = [{"role": "user", "content": "thanks"}]
        cache.set(messages3, "en", "You're welcome! Happy to help!", "claude")

        assert len(cache.cache) == 2
        assert cache.stats["evictions"] == 1

    def test_set_returns_false_when_no_cache_type(self):
        """Test set returns False when cache type cannot be determined"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]

        # Mock _determine_cache_type to return None
        with patch.object(cache, "_determine_cache_type", return_value=None):
            result = cache.set(messages, "en", "Response that meets length", "claude")
            assert result is False

    def test_set_defensive_check_for_none_cache_type(self):
        """Test defensive code path when cache_type becomes None after should_cache passes"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]

        # Mock _should_cache to return True, but _determine_cache_type returns None
        # This simulates a race condition or edge case in defensive programming
        with patch.object(cache, "_should_cache", return_value=True):
            with patch.object(cache, "_determine_cache_type", return_value=None):
                result = cache.set(
                    messages, "en", "Valid response for caching", "claude"
                )
                assert result is False
                assert len(cache.cache) == 0

    def test_set_logging_on_success(self, caplog):
        """Test set logs on successful cache"""
        import logging

        caplog.set_level(logging.INFO)

        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help?", "claude")

        assert "Cache SET" in caplog.text

    def test_set_overrides_existing_entry(self):
        """Test set overrides existing cache entry"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]

        cache.set(messages, "en", "First response for testing", "claude")
        cache.set(messages, "en", "Second response for testing", "claude")

        result = cache.get(messages, "en", "claude")
        assert result.content == "Second response for testing"
        assert len(cache.cache) == 1


# ============================================================================
# Test Class 9: LRU Eviction
# ============================================================================


class TestLRUEviction:
    """Test _evict_lru method"""

    def test_evict_lru_empty_cache(self):
        """Test evict_lru does nothing when cache is empty"""
        cache = ResponseCache()
        cache._evict_lru()
        assert len(cache.cache) == 0
        assert cache.stats["evictions"] == 0

    def test_evict_lru_single_entry(self):
        """Test evict_lru removes the only entry"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help you today?", "claude")

        cache._evict_lru()
        assert len(cache.cache) == 0
        assert cache.stats["evictions"] == 1

    def test_evict_lru_removes_least_recently_used(self):
        """Test evict_lru removes entry with oldest last_accessed"""
        cache = ResponseCache()

        # Add first entry
        messages1 = [{"role": "user", "content": "hello"}]
        cache.set(messages1, "en", "Hello! How are you today?", "claude")
        key1 = cache._generate_cache_key(messages1, "en", "claude")

        # Add second entry
        messages2 = [{"role": "user", "content": "goodbye"}]
        cache.set(messages2, "en", "Goodbye! See you later!", "claude")
        key2 = cache._generate_cache_key(messages2, "en", "claude")

        # Access second entry (making first the LRU)
        cache.get(messages2, "en", "claude")

        # Evict LRU
        cache._evict_lru()

        # First entry should be gone
        assert key1 not in cache.cache
        assert key2 in cache.cache

    def test_evict_lru_uses_created_at_when_no_last_accessed(self):
        """Test evict_lru uses created_at when last_accessed is None"""
        cache = ResponseCache()

        # Add entries without accessing them
        messages1 = [{"role": "user", "content": "hello"}]
        cache.set(messages1, "en", "Hello! How are you today?", "claude")
        key1 = cache._generate_cache_key(messages1, "en", "claude")

        # Modify created_at to make it older
        cache.cache[key1].created_at = datetime.now() - timedelta(hours=2)

        messages2 = [{"role": "user", "content": "goodbye"}]
        cache.set(messages2, "en", "Goodbye! See you later!", "claude")
        key2 = cache._generate_cache_key(messages2, "en", "claude")

        # Evict LRU
        cache._evict_lru()

        # Older entry should be gone
        assert key1 not in cache.cache
        assert key2 in cache.cache

    def test_evict_lru_increments_evictions_stat(self):
        """Test evict_lru increments evictions counter"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help you today?", "claude")

        assert cache.stats["evictions"] == 0
        cache._evict_lru()
        assert cache.stats["evictions"] == 1

        # Add another and evict again
        cache.set(messages, "en", "Hello again! How are you?", "claude")
        cache._evict_lru()
        assert cache.stats["evictions"] == 2

    def test_evict_lru_logging(self, caplog):
        """Test evict_lru logs eviction"""
        import logging

        caplog.set_level(logging.INFO)

        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help you today?", "claude")
        cache._evict_lru()

        assert "Cache EVICT LRU" in caplog.text

    def test_evict_lru_automatic_on_set_when_full(self):
        """Test evict_lru is called automatically when cache is full"""
        cache = ResponseCache(max_entries=2)

        # Fill cache
        messages1 = [{"role": "user", "content": "hello"}]
        cache.set(messages1, "en", "Hello! How are you today?", "claude")

        messages2 = [{"role": "user", "content": "goodbye"}]
        cache.set(messages2, "en", "Goodbye! See you later!", "claude")

        assert cache.stats["evictions"] == 0

        # Add one more - should trigger eviction
        messages3 = [{"role": "user", "content": "thanks"}]
        cache.set(messages3, "en", "You're welcome! Happy to help!", "claude")

        assert cache.stats["evictions"] == 1
        assert len(cache.cache) == 2

    def test_evict_lru_multiple_entries(self):
        """Test evict_lru with multiple entries"""
        cache = ResponseCache()

        # Add multiple entries at different times
        for i in range(5):
            messages = [{"role": "user", "content": f"hello {i}"}]
            cache.set(messages, "en", f"Hello {i}! How are you?", "claude")

        # Access entries in specific order
        cache.get([{"role": "user", "content": "hello 2"}], "en", "claude")
        cache.get([{"role": "user", "content": "hello 4"}], "en", "claude")
        cache.get([{"role": "user", "content": "hello 1"}], "en", "claude")

        # Evict - should remove "hello 0" (never accessed) or "hello 3" (never accessed)
        initial_count = len(cache.cache)
        cache._evict_lru()
        assert len(cache.cache) == initial_count - 1

    def test_evict_lru_with_future_timestamps(self):
        """Test evict_lru handles edge case with future timestamps"""
        cache = ResponseCache()

        # Create entries: one past, one future
        past_time = datetime.now() - timedelta(hours=1)
        future_time = datetime.now() + timedelta(hours=1)

        # Past entry
        messages1 = [{"role": "user", "content": "hello past"}]
        cache_key1 = cache._generate_cache_key(messages1, "en", "claude")
        entry1 = CacheEntry(
            content="Hello! From the past here",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=past_time,
            last_accessed=None,
            expires_at=past_time + timedelta(hours=24),
        )
        cache.cache[cache_key1] = entry1

        # Future entry
        messages2 = [{"role": "user", "content": "hello future"}]
        cache_key2 = cache._generate_cache_key(messages2, "en", "claude")
        entry2 = CacheEntry(
            content="Hello! From the future!",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=future_time,
            last_accessed=None,
            expires_at=future_time + timedelta(hours=24),
        )
        cache.cache[cache_key2] = entry2

        assert len(cache.cache) == 2

        # Evict should remove the past entry (oldest)
        cache._evict_lru()

        assert len(cache.cache) == 1
        assert cache_key1 not in cache.cache  # Past entry removed
        assert cache_key2 in cache.cache  # Future entry remains

    def test_evict_lru_all_entries_same_timestamp(self):
        """Test evict_lru when all entries have identical timestamps"""
        cache = ResponseCache()

        # Create a fixed timestamp
        fixed_time = datetime.now() - timedelta(hours=1)

        # Manually create multiple entries with identical timestamps
        for i in range(3):
            messages = [{"role": "user", "content": f"test message {i}"}]
            cache_key = cache._generate_cache_key(messages, "en", "claude")

            entry = CacheEntry(
                content=f"Response for test {i} here",
                provider="claude",
                language="en",
                cache_type=CacheType.CONVERSATION,
                created_at=fixed_time,
                last_accessed=None,  # No access yet
                expires_at=fixed_time + timedelta(hours=24),
            )
            cache.cache[cache_key] = entry

        assert len(cache.cache) == 3

        # Evict one entry - should work even with identical timestamps
        cache._evict_lru()

        assert len(cache.cache) == 2
        assert cache.stats["evictions"] == 1


# ============================================================================
# Test Class 10: Clear Expired
# ============================================================================


class TestClearExpired:
    """Test clear_expired method"""

    def test_clear_expired_empty_cache(self):
        """Test clear_expired with empty cache"""
        cache = ResponseCache()
        cache.clear_expired()
        assert len(cache.cache) == 0

    def test_clear_expired_no_expired_entries(self):
        """Test clear_expired when no entries are expired"""
        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How are you today?", "claude", ttl_hours=24)

        cache.clear_expired()
        assert len(cache.cache) == 1

    def test_clear_expired_removes_expired_entries(self):
        """Test clear_expired removes expired entries"""
        cache = ResponseCache()

        # Manually add expired entry
        messages1 = [{"role": "user", "content": "hello"}]
        key1 = cache._generate_cache_key(messages1, "en", "claude")
        past_time = datetime.now() - timedelta(hours=1)
        cache.cache[key1] = CacheEntry(
            content="Hello! How are you today?",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=datetime.now() - timedelta(hours=25),
            expires_at=past_time,
        )

        # Add fresh entry
        messages2 = [{"role": "user", "content": "goodbye"}]
        cache.set(messages2, "en", "Goodbye! See you later!", "claude", ttl_hours=24)

        cache.clear_expired()

        # Only fresh entry should remain
        assert len(cache.cache) == 1
        key2 = cache._generate_cache_key(messages2, "en", "claude")
        assert key2 in cache.cache

    def test_clear_expired_removes_stale_entries(self):
        """Test clear_expired removes stale entries"""
        cache = ResponseCache()

        # Manually add stale entry
        messages = [{"role": "user", "content": "hello"}]
        cache_key = cache._generate_cache_key(messages, "en", "claude")
        old_time = datetime.now() - timedelta(hours=25)
        cache.cache[cache_key] = CacheEntry(
            content="Old response",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=old_time,
        )

        cache.clear_expired()
        assert len(cache.cache) == 0

    def test_clear_expired_logging_when_entries_removed(self, caplog):
        """Test clear_expired logs when entries are removed"""
        import logging

        caplog.set_level(logging.INFO, logger="app.services.response_cache")

        cache = ResponseCache()
        messages = [{"role": "user", "content": "hello"}]
        # Manually create expired entry
        cache_key = cache._generate_cache_key(messages, "en", "claude")
        past_time = datetime.now() - timedelta(hours=1)
        cache.cache[cache_key] = CacheEntry(
            content="Hello! How are you today?",
            provider="claude",
            language="en",
            cache_type=CacheType.CONVERSATION,
            created_at=datetime.now() - timedelta(hours=25),
            expires_at=past_time,
        )

        cache.clear_expired()

        assert "Cache cleanup" in caplog.text
        assert "removed 1 expired entries" in caplog.text

    def test_clear_expired_no_logging_when_no_entries_removed(self, caplog):
        """Test clear_expired doesn't log when no entries removed"""
        import logging

        caplog.set_level(logging.INFO)

        cache = ResponseCache()
        cache.clear_expired()

        assert "Cache cleanup" not in caplog.text

    def test_clear_expired_multiple_expired_entries(self):
        """Test clear_expired removes multiple expired entries"""
        cache = ResponseCache()

        # Manually add multiple expired entries
        past_time = datetime.now() - timedelta(hours=1)
        for i in range(3):
            messages = [{"role": "user", "content": f"hello {i}"}]
            cache_key = cache._generate_cache_key(messages, "en", "claude")
            cache.cache[cache_key] = CacheEntry(
                content=f"Hello {i}! How are you?",
                provider="claude",
                language="en",
                cache_type=CacheType.CONVERSATION,
                created_at=datetime.now() - timedelta(hours=25),
                expires_at=past_time,
            )

        # Add one fresh entry
        messages_fresh = [{"role": "user", "content": "goodbye"}]
        cache.set(
            messages_fresh, "en", "Goodbye! See you later!", "claude", ttl_hours=24
        )

        cache.clear_expired()

        # Only 1 entry should remain
        assert len(cache.cache) == 1


# ============================================================================
# Test Class 11: Statistics
# ============================================================================


class TestStatistics:
    """Test get_stats method"""

    def test_get_stats_empty_cache(self):
        """Test get_stats with empty cache"""
        cache = ResponseCache()
        stats = cache.get_stats()

        assert stats["entries"] == 0
        assert stats["max_entries"] == 1000
        assert stats["hit_rate"] == 0.0
        assert stats["total_requests"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["evictions"] == 0
        assert stats["total_size_bytes"] == 0
        assert stats["type_distribution"] == {}
        assert stats["avg_entry_size"] == 0

    def test_get_stats_with_cache_entries(self):
        """Test get_stats with cache entries"""
        cache = ResponseCache()

        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help?", "claude")

        stats = cache.get_stats()

        assert stats["entries"] == 1
        assert stats["total_size_bytes"] > 0
        assert "conversation" in stats["type_distribution"]
        assert stats["avg_entry_size"] > 0

    def test_get_stats_hit_rate_calculation(self):
        """Test get_stats calculates hit rate correctly"""
        cache = ResponseCache()

        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help?", "claude")

        # 1 hit, 0 misses
        cache.get(messages, "en", "claude")
        stats = cache.get_stats()
        assert stats["hit_rate"] == 100.0

        # 1 hit, 1 miss
        messages2 = [{"role": "user", "content": "goodbye"}]
        cache.get(messages2, "en", "claude")
        stats = cache.get_stats()
        assert stats["hit_rate"] == 50.0

    def test_get_stats_type_distribution(self):
        """Test get_stats type distribution"""
        cache = ResponseCache()

        # Add conversation
        messages1 = [{"role": "user", "content": "hello"}]
        cache.set(messages1, "en", "Hello! How are you today?", "claude")

        # Add translation (use "translate bonjour" to avoid "hello" pattern)
        messages2 = [{"role": "user", "content": "translate bonjour"}]
        cache.set(messages2, "en", "Translation: Bonjour means hello", "claude")

        stats = cache.get_stats()

        assert stats["type_distribution"]["conversation"] == 1
        assert stats["type_distribution"]["translation"] == 1

    def test_get_stats_total_size_calculation(self):
        """Test get_stats calculates total size correctly"""
        cache = ResponseCache()

        messages = [{"role": "user", "content": "hello"}]
        response = "Hello! How can I help?"
        cache.set(messages, "en", response, "claude")

        stats = cache.get_stats()

        assert stats["total_size_bytes"] == len(response)
        assert stats["avg_entry_size"] == len(response)

    def test_get_stats_avg_entry_size_multiple_entries(self):
        """Test get_stats calculates average entry size"""
        cache = ResponseCache()

        messages1 = [{"role": "user", "content": "hello"}]
        response1 = "Hello! How are you today?"
        cache.set(messages1, "en", response1, "claude")  # 26 bytes

        messages2 = [{"role": "user", "content": "goodbye"}]
        response2 = "Goodbye! See you later!"
        cache.set(messages2, "en", response2, "claude")  # 24 bytes

        stats = cache.get_stats()

        # Average: (25 + 23) / 2 = 24
        assert stats["avg_entry_size"] == 24

    def test_get_stats_max_entries(self):
        """Test get_stats reports max_entries correctly"""
        cache = ResponseCache(max_entries=500)
        stats = cache.get_stats()
        assert stats["max_entries"] == 500

    def test_get_stats_evictions_tracking(self):
        """Test get_stats tracks evictions"""
        cache = ResponseCache(max_entries=2)

        # Fill cache and trigger eviction
        messages1 = [{"role": "user", "content": "hello"}]
        cache.set(messages1, "en", "Hello! How are you today?", "claude")

        messages2 = [{"role": "user", "content": "goodbye"}]
        cache.set(messages2, "en", "Goodbye! See you later!", "claude")

        messages3 = [{"role": "user", "content": "thanks"}]
        cache.set(messages3, "en", "You're welcome! Happy to help!", "claude")

        stats = cache.get_stats()
        assert stats["evictions"] == 1

    def test_get_stats_hit_rate_rounds_to_two_decimals(self):
        """Test get_stats rounds hit rate to 2 decimals"""
        cache = ResponseCache()

        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help you today?", "claude")

        # 1 hit
        cache.get(messages, "en", "claude")

        # 2 misses
        cache.get([{"role": "user", "content": "goodbye"}], "en", "claude")
        cache.get([{"role": "user", "content": "thanks"}], "en", "claude")

        stats = cache.get_stats()
        # 1 hit out of 3 requests = 33.33...%
        assert stats["hit_rate"] == 33.33

    def test_get_stats_zero_division_guard(self):
        """Test get_stats handles zero total_requests"""
        cache = ResponseCache()
        stats = cache.get_stats()

        # Should not raise division by zero
        assert stats["hit_rate"] == 0.0


# ============================================================================
# Test Class 12: Clear Operation
# ============================================================================


class TestClearOperation:
    """Test clear method"""

    def test_clear_empty_cache(self):
        """Test clear on empty cache"""
        cache = ResponseCache()
        cache.clear()
        assert len(cache.cache) == 0

    def test_clear_removes_all_entries(self):
        """Test clear removes all cache entries"""
        cache = ResponseCache()

        # Add multiple entries
        for i in range(5):
            messages = [{"role": "user", "content": f"hello {i}"}]
            cache.set(messages, "en", f"Hello {i}! How are you?", "claude")

        assert len(cache.cache) == 5

        cache.clear()
        assert len(cache.cache) == 0

    def test_clear_does_not_reset_stats(self):
        """Test clear does not reset statistics"""
        cache = ResponseCache()

        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help you today?", "claude")
        cache.get(messages, "en", "claude")

        # Stats should have data
        assert cache.stats["hits"] == 1
        assert cache.stats["total_requests"] == 1

        cache.clear()

        # Stats should be preserved
        assert cache.stats["hits"] == 1
        assert cache.stats["total_requests"] == 1

    def test_clear_logging(self, caplog):
        """Test clear logs cache clear"""
        import logging

        caplog.set_level(logging.INFO)

        cache = ResponseCache()
        cache.clear()

        assert "Cache cleared" in caplog.text

    def test_clear_allows_new_entries_after_clear(self):
        """Test cache can accept new entries after clear"""
        cache = ResponseCache()

        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help you today?", "claude")

        cache.clear()

        # Add new entry
        messages2 = [{"role": "user", "content": "goodbye"}]
        cache.set(messages2, "en", "Goodbye! See you later!", "claude")

        assert len(cache.cache) == 1

    def test_clear_resets_to_empty_dict(self):
        """Test clear resets cache to empty dictionary"""
        cache = ResponseCache()

        messages = [{"role": "user", "content": "hello"}]
        cache.set(messages, "en", "Hello! How can I help you today?", "claude")

        cache.clear()

        assert isinstance(cache.cache, dict)
        assert len(cache.cache) == 0


# ============================================================================
# Test Class 13: Global Instance
# ============================================================================


class TestGlobalInstance:
    """Test global response_cache instance"""

    def test_global_instance_exists(self):
        """Test global response_cache instance exists"""
        from app.services.response_cache import response_cache

        assert response_cache is not None
        assert isinstance(response_cache, ResponseCache)

    def test_global_instance_default_configuration(self):
        """Test global instance has correct default configuration"""
        from app.services.response_cache import response_cache

        assert response_cache.max_entries == 1000
        assert response_cache.default_ttl_hours == 24

    def test_global_instance_is_singleton(self):
        """Test global instance is a singleton"""
        from app.services.response_cache import response_cache as cache1
        from app.services.response_cache import response_cache as cache2

        assert cache1 is cache2
