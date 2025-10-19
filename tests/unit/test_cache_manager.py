"""
Unit tests for cache manager
"""
import pytest
from unittest.mock import Mock, patch
import time
import json
from src.cache_manager import CacheManager, cached, cache_invalidate, CacheMetrics, cache_metrics


class TestCacheManager:
    """Test CacheManager class"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection"""
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.delete.return_value = True
        mock_redis.ping.return_value = True
        mock_redis.keys.return_value = []
        mock_redis.exists.return_value = False
        mock_redis.flushdb.return_value = True
        mock_redis.info.return_value = {
            'connected_clients': 1,
            'used_memory_human': '1MB',
            'keyspace_hits': 10,
            'keyspace_misses': 5
        }
        return mock_redis
    
    def test_cache_manager_initialization(self, mock_redis):
        """Test cache manager initialization"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            
            assert cache_manager.redis_client is not None
            assert cache_manager.fallback_cache_size == 1000
    
    def test_cache_manager_initialization_no_redis(self):
        """Test cache manager initialization without Redis"""
        with patch('src.cache_manager.REDIS_AVAILABLE', False):
            cache_manager = CacheManager()
            
            assert cache_manager.redis_client is None
            assert cache_manager.use_redis is False
    
    def test_cache_manager_initialization_redis_error(self, mock_redis):
        """Test cache manager initialization with Redis connection error"""
        # Mock redis.from_url to raise exception during connection
        with patch('src.cache_manager.redis.from_url') as mock_from_url:
            mock_from_url.side_effect = Exception("Connection failed")
            
            cache_manager = CacheManager()
            
            assert cache_manager.redis_client is None
            assert cache_manager.use_redis is False
    
    def test_cache_get_miss(self, mock_redis):
        """Test cache get on miss"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            
            result = cache_manager.get('test-key')
            
            assert result is None
    
    def test_cache_get_hit(self, mock_redis):
        """Test cache get on hit"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            
            # Mock Redis connection to work
            mock_redis.ping.return_value = True
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            # Mock cache hit
            mock_redis.get.return_value = '{"test": "data"}'
            
            result = cache_manager.get('test-key')
            
            assert result == {'test': 'data'}
            mock_redis.get.assert_called_with('test-key')
    
    def test_cache_get_fallback_hit(self):
        """Test cache get with fallback cache hit"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        # Add item to fallback cache
        cache_manager.fallback_cache['test-key'] = {
            'value': {'test': 'data'},
            'expires': time.time() + 300
        }
        
        result = cache_manager.get('test-key')
        
        assert result == {'test': 'data'}
    
    def test_cache_get_fallback_expired(self):
        """Test cache get with expired fallback cache item"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        # Add expired item to fallback cache
        cache_manager.fallback_cache['test-key'] = {
            'value': {'test': 'data'},
            'expires': time.time() - 1  # Expired
        }
        
        result = cache_manager.get('test-key')
        
        assert result is None
        assert 'test-key' not in cache_manager.fallback_cache
    
    def test_cache_get_exception(self, mock_redis):
        """Test cache get with exception"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            mock_redis.get.side_effect = Exception("Redis error")
            
            result = cache_manager.get('test-key')
            
            assert result is None
    
    def test_cache_set(self, mock_redis):
        """Test cache set"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            
            result = cache_manager.set('test-key', {'test': 'data'}, 600)
            
            assert result is True
    
    def test_cache_set_fallback(self):
        """Test cache set with fallback cache"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        result = cache_manager.set('test-key', {'test': 'data'}, 600)
        
        assert result is True
        assert 'test-key' in cache_manager.fallback_cache
    
    def test_cache_set_fallback_full(self):
        """Test cache set with full fallback cache"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        cache_manager.fallback_cache_size = 2
        
        # Fill cache
        cache_manager.fallback_cache['key1'] = {
            'value': 'data1',
            'expires': time.time() + 100
        }
        cache_manager.fallback_cache['key2'] = {
            'value': 'data2',
            'expires': time.time() + 200
        }
        
        result = cache_manager.set('key3', 'data3', 600)
        
        assert result is True
        assert 'key3' in cache_manager.fallback_cache
        # Oldest key should be removed
        assert len(cache_manager.fallback_cache) == 2
    
    def test_cache_set_exception(self, mock_redis):
        """Test cache set with exception"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            mock_redis.setex.side_effect = Exception("Redis error")
            
            result = cache_manager.set('test-key', {'test': 'data'}, 600)
            
            assert result is False
    
    def test_cache_delete(self, mock_redis):
        """Test cache delete"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            
            result = cache_manager.delete('test-key')
            
            assert result is True
    
    def test_cache_delete_fallback(self):
        """Test cache delete with fallback cache"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        cache_manager.fallback_cache['test-key'] = {
            'value': 'data',
            'expires': time.time() + 300
        }
        
        result = cache_manager.delete('test-key')
        
        assert result is True
        assert 'test-key' not in cache_manager.fallback_cache
    
    def test_cache_delete_fallback_missing(self):
        """Test cache delete with missing key in fallback cache"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        result = cache_manager.delete('test-key')
        
        assert result is False
    
    def test_cache_delete_exception(self, mock_redis):
        """Test cache delete with exception"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            mock_redis.delete.side_effect = Exception("Redis error")
            
            result = cache_manager.delete('test-key')
            
            assert result is False
    
    def test_cache_clear(self, mock_redis):
        """Test cache clear"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            
            result = cache_manager.clear()
            
            assert result is True
    
    def test_cache_clear_fallback(self):
        """Test cache clear with fallback cache"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        cache_manager.fallback_cache['key1'] = {'value': 'data1', 'expires': time.time() + 300}
        cache_manager.fallback_cache['key2'] = {'value': 'data2', 'expires': time.time() + 300}
        
        result = cache_manager.clear()
        
        assert result is True
        assert len(cache_manager.fallback_cache) == 0
    
    def test_cache_clear_exception(self, mock_redis):
        """Test cache clear with exception"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            mock_redis.flushdb.side_effect = Exception("Redis error")
            
            result = cache_manager.clear()
            
            assert result is False
    
    def test_cache_exists(self, mock_redis):
        """Test cache exists"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            
            result = cache_manager.exists('test-key')
            
            assert result is False
    
    def test_cache_exists_fallback(self):
        """Test cache exists with fallback cache"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        cache_manager.fallback_cache['test-key'] = {
            'value': 'data',
            'expires': time.time() + 300
        }
        
        result = cache_manager.exists('test-key')
        
        assert result is True
    
    def test_cache_exists_fallback_expired(self):
        """Test cache exists with expired fallback cache item"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        cache_manager.fallback_cache['test-key'] = {
            'value': 'data',
            'expires': time.time() - 1  # Expired
        }
        
        result = cache_manager.exists('test-key')
        
        assert result is False
        assert 'test-key' not in cache_manager.fallback_cache
    
    def test_cache_exists_exception(self, mock_redis):
        """Test cache exists with exception"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            mock_redis.exists.side_effect = Exception("Redis error")
            
            result = cache_manager.exists('test-key')
            
            assert result is False
    
    def test_cache_get_stats_redis(self, mock_redis):
        """Test cache get stats with Redis"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            result = cache_manager.get_stats()
            
            assert result['type'] == 'redis'
            assert 'connected_clients' in result
            assert 'hit_rate' in result
    
    def test_cache_get_stats_fallback(self):
        """Test cache get stats with fallback cache"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        cache_manager.fallback_cache['key1'] = {'value': 'data1', 'expires': time.time() + 300}
        
        result = cache_manager.get_stats()
        
        assert result['type'] == 'fallback'
        assert result['cache_size'] == 1
        assert result['max_size'] == 1000
    
    def test_cache_get_stats_exception(self, mock_redis):
        """Test cache get stats with exception"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            mock_redis.info.side_effect = Exception("Redis error")
            
            result = cache_manager.get_stats()
            
            assert result['type'] == 'error'
            assert 'error' in result
    
    def test_cache_delete_pattern(self, mock_redis):
        """Test cache delete with pattern"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            
            # Mock Redis connection to work
            mock_redis.ping.return_value = True
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            # Mock keys matching pattern
            mock_redis.keys.return_value = ['products:test:1', 'products:test:2']
            mock_redis.delete.return_value = 2
            
            result = cache_manager.delete_pattern('products:*')
            
            assert result == 2
            mock_redis.keys.assert_called_with('products:*')
            mock_redis.delete.assert_called_with('products:test:1', 'products:test:2')
    
    def test_cache_delete_pattern_no_keys(self, mock_redis):
        """Test cache delete pattern with no matching keys"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            mock_redis.keys.return_value = []
            
            result = cache_manager.delete_pattern('products:*')
            
            assert result == 0
    
    def test_cache_delete_pattern_fallback(self):
        """Test cache delete pattern with fallback cache"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        result = cache_manager.delete_pattern('products:*')
        
        assert result == 0  # Fallback cache doesn't support pattern matching
    
    def test_cache_delete_pattern_exception(self, mock_redis):
        """Test cache delete pattern with exception"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            mock_redis.keys.side_effect = Exception("Redis error")
            
            result = cache_manager.delete_pattern('products:*')
            
            assert result == 0
    
    def test_cache_health_check(self, mock_redis):
        """Test cache health check"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            
            result = cache_manager.health_check()
            
            assert result is True
    
    def test_cache_health_check_fallback(self):
        """Test cache health check with fallback cache"""
        cache_manager = CacheManager()
        cache_manager.use_redis = False
        
        result = cache_manager.health_check()
        
        assert result is True  # Fallback cache is always "healthy"
    
    def test_cache_health_check_exception(self, mock_redis):
        """Test cache health check with exception"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            cache_manager = CacheManager()
            cache_manager.use_redis = True
            cache_manager.redis_client = mock_redis
            
            mock_redis.ping.side_effect = Exception("Redis error")
            
            result = cache_manager.health_check()
            
            assert result is False


class TestCacheDecorators:
    """Test cache decorators"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection"""
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.keys.return_value = []
        mock_redis.delete.return_value = True
        mock_redis.flushdb.return_value = True
        return mock_redis
    
    def test_cached_decorator(self, mock_redis):
        """Test cached decorator"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            from src.cache_manager import cache_manager
            
            # Mock Redis connection to work
            mock_redis.ping.return_value = True
            cache_manager.use_redis = True
            
            @cached(timeout=600)
            def test_function():
                return {'result': 'test'}
            
            result = test_function()
            
            assert result == {'result': 'test'}
    
    def test_cached_decorator_with_args(self, mock_redis):
        """Test cached decorator with arguments"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            from src.cache_manager import cache_manager
            
            # Mock Redis connection to work
            mock_redis.ping.return_value = True
            cache_manager.use_redis = True
            
            @cached(timeout=600)
            def test_function(arg1, arg2):
                return {'result': f'{arg1}_{arg2}'}
            
            result = test_function('test1', 'test2')
            
            assert result == {'result': 'test1_test2'}
    
    def test_cached_decorator_with_key_prefix(self, mock_redis):
        """Test cached decorator with key prefix"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            from src.cache_manager import cache_manager
            
            # Mock Redis connection to work
            mock_redis.ping.return_value = True
            cache_manager.use_redis = True
            
            @cached(timeout=600, key_prefix="test")
            def test_function():
                return {'result': 'test'}
            
            result = test_function()
            
            assert result == {'result': 'test'}
    
    def test_cache_invalidate_decorator(self, mock_redis):
        """Test cache invalidate decorator"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            from src.cache_manager import cache_manager
            
            # Mock Redis connection to work
            mock_redis.ping.return_value = True
            cache_manager.use_redis = True
            
            @cache_invalidate('test:*')
            def test_function():
                return {'result': 'test'}
            
            result = test_function()
            
            assert result == {'result': 'test'}
    
    def test_cache_invalidate_with_pattern(self, mock_redis):
        """Test cache invalidate with custom pattern"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            from src.cache_manager import cache_manager
            
            # Mock Redis connection to work
            mock_redis.ping.return_value = True
            cache_manager.use_redis = True
            
            @cache_invalidate('custom:*')
            def test_function():
                return {'result': 'test'}
            
            result = test_function()
            
            assert result == {'result': 'test'}
    
    def test_cache_invalidate_no_pattern(self, mock_redis):
        """Test cache invalidate without pattern"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            from src.cache_manager import cache_manager
            
            # Mock Redis connection to work
            mock_redis.ping.return_value = True
            cache_manager.use_redis = True
            
            @cache_invalidate()
            def test_function():
                return {'result': 'test'}
            
            result = test_function()
            
            assert result == {'result': 'test'}
    
    def test_cache_invalidate_fallback(self):
        """Test cache invalidate with fallback cache"""
        from src.cache_manager import cache_manager
        
        cache_manager.use_redis = False
        cache_manager.fallback_cache['key1'] = {'value': 'data1', 'expires': time.time() + 300}
        
        @cache_invalidate()
        def test_function():
            return {'result': 'test'}
        
        result = test_function()
        
        assert result == {'result': 'test'}
        assert len(cache_manager.fallback_cache) == 0  # Should be cleared
    
    def test_cache_invalidate_exception(self, mock_redis):
        """Test cache invalidate with exception"""
        with patch('src.cache_manager.redis.Redis', return_value=mock_redis):
            from src.cache_manager import cache_manager
            
            # Mock Redis connection to work
            mock_redis.ping.return_value = True
            cache_manager.use_redis = True
            mock_redis.keys.side_effect = Exception("Redis error")
            
            @cache_invalidate('test:*')
            def test_function():
                return {'result': 'test'}
            
            result = test_function()
            
            assert result == {'result': 'test'}  # Function should still execute


class TestCacheMetrics:
    """Test CacheMetrics class"""
    
    def test_cache_metrics_initialization(self):
        """Test cache metrics initialization"""
        metrics = CacheMetrics()
        
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.sets == 0
        assert metrics.deletes == 0
    
    def test_cache_metrics_record_hit(self):
        """Test recording cache hit"""
        metrics = CacheMetrics()
        
        metrics.record_hit()
        
        assert metrics.hits == 1
    
    def test_cache_metrics_record_miss(self):
        """Test recording cache miss"""
        metrics = CacheMetrics()
        
        metrics.record_miss()
        
        assert metrics.misses == 1
    
    def test_cache_metrics_record_set(self):
        """Test recording cache set"""
        metrics = CacheMetrics()
        
        metrics.record_set()
        
        assert metrics.sets == 1
    
    def test_cache_metrics_record_delete(self):
        """Test recording cache delete"""
        metrics = CacheMetrics()
        
        metrics.record_delete()
        
        assert metrics.deletes == 1
    
    def test_cache_metrics_get_stats(self):
        """Test getting cache metrics stats"""
        metrics = CacheMetrics()
        
        metrics.record_hit()
        metrics.record_hit()
        metrics.record_miss()
        metrics.record_set()
        metrics.record_delete()
        
        stats = metrics.get_stats()
        
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['sets'] == 1
        assert stats['deletes'] == 1
        assert stats['total_requests'] == 3
        assert stats['hit_rate'] == (2 / 3) * 100
    
    def test_cache_metrics_get_stats_no_requests(self):
        """Test getting cache metrics stats with no requests"""
        metrics = CacheMetrics()
        
        stats = metrics.get_stats()
        
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['sets'] == 0
        assert stats['deletes'] == 0
        assert stats['total_requests'] == 0
        assert stats['hit_rate'] == 0
