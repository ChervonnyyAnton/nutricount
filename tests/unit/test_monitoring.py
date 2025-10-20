"""
Unit tests for monitoring.py
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import time
from src.monitoring import (
    MetricsCollector,
    monitor_http_request,
    monitor_database_operation,
    monitor_cache_operation,
    monitor_background_task,
    SystemMonitor
)


class TestMetricsCollector:
    """Test MetricsCollector class"""
    
    def test_init(self):
        """Test MetricsCollector initialization"""
        collector = MetricsCollector()
        assert collector.metrics != {}  # Metrics are initialized
        assert collector.registry is not None  # Registry is created even without Prometheus
    
    @patch('src.monitoring.PROMETHEUS_AVAILABLE', True)
    def test_init_with_prometheus(self):
        """Test MetricsCollector initialization with Prometheus"""
        collector = MetricsCollector()
        assert collector.metrics != {}
        assert collector.registry is not None
    
    def test_record_http_request(self):
        """Test recording HTTP request metrics"""
        collector = MetricsCollector()
        
        # Since Prometheus is not available, we test the fallback behavior
        collector.record_http_request('GET', '/api/test', 200, 0.5)
        # The method should not raise an error even without Prometheus
    
    def test_record_database_operation(self):
        """Test recording database operation metrics"""
        collector = MetricsCollector()
        
        collector.record_database_operation('SELECT', 'users', 0.1)
        # The method should not raise an error even without Prometheus
    
    def test_record_cache_operation(self):
        """Test recording cache operation metrics"""
        collector = MetricsCollector()
        
        collector.record_cache_operation('GET', 0.05)
        # The method should not raise an error even without Prometheus
    
    def test_record_fasting_session(self):
        """Test recording fasting session metrics"""
        collector = MetricsCollector()
        
        collector.record_fasting_session('started', 'intermittent', 3600)
        # The method should not raise an error even without Prometheus
    
    def test_record_background_task(self):
        """Test recording background task metrics"""
        collector = MetricsCollector()
        
        collector.record_background_task('email_sending', 'completed', 2.5)
        # The method should not raise an error even without Prometheus
    
    def test_get_metrics(self):
        """Test getting all metrics"""
        collector = MetricsCollector()
        
        metrics = collector.get_metrics()
        
        assert isinstance(metrics, str)
        assert "http_requests_total" in metrics  # Should contain Prometheus metrics
    
    def test_get_metrics_summary(self):
        """Test getting metrics summary"""
        collector = MetricsCollector()
        
        summary = collector.get_metrics_summary()
        
        assert isinstance(summary, dict)
        assert 'prometheus_available' in summary
        assert 'metrics_count' in summary
        assert 'registry_available' in summary
    
    def test_update_system_metrics(self):
        """Test updating system metrics"""
        collector = MetricsCollector()
        
        collector.update_system_metrics(1024, 25.5)
        # The method should not raise an error even without Prometheus
    
    def test_get_prometheus_metrics(self):
        """Test getting Prometheus metrics"""
        collector = MetricsCollector()
        
        prometheus_metrics = collector.get_metrics()  # This is the actual method name
        
        assert isinstance(prometheus_metrics, str)
        assert "http_requests_total" in prometheus_metrics
    
    def test_update_cache_hit_rate(self):
        """Test updating cache hit rate"""
        collector = MetricsCollector()
        
        # Test with rate value
        collector.update_cache_hit_rate(0.85)
        # Should not raise error even without Prometheus
    
    @patch('src.monitoring.PROMETHEUS_AVAILABLE', True)
    def test_update_cache_hit_rate_with_prometheus(self):
        """Test updating cache hit rate with Prometheus"""
        collector = MetricsCollector()
        
        # Mock the cache_hit_rate metric
        mock_metric = Mock()
        collector.metrics["cache_hit_rate"] = mock_metric
        
        collector.update_cache_hit_rate(0.75)
        
        # Should call set on the metric
        mock_metric.set.assert_called_once_with(0.75)
    
    def test_update_active_users(self):
        """Test updating active users count"""
        collector = MetricsCollector()
        
        # Test with user count
        collector.update_active_users(42)
        # Should not raise error even without Prometheus
    
    @patch('src.monitoring.PROMETHEUS_AVAILABLE', True)
    def test_update_active_users_with_prometheus(self):
        """Test updating active users with Prometheus"""
        collector = MetricsCollector()
        
        # Mock the active_users metric
        mock_metric = Mock()
        collector.metrics["active_users"] = mock_metric
        
        collector.update_active_users(100)
        
        # Should call set on the metric
        mock_metric.set.assert_called_once_with(100)
    
    def test_update_counts(self):
        """Test updating entity counts"""
        collector = MetricsCollector()
        
        # Test with various counts
        collector.update_counts(50, 30, 200)
        # Should not raise error even without Prometheus
    
    @patch('src.monitoring.PROMETHEUS_AVAILABLE', True)
    def test_update_counts_with_prometheus(self):
        """Test updating entity counts with Prometheus"""
        collector = MetricsCollector()
        
        # Mock the count metrics
        mock_products = Mock()
        mock_dishes = Mock()
        mock_logs = Mock()
        collector.metrics["products_count"] = mock_products
        collector.metrics["dishes_count"] = mock_dishes
        collector.metrics["log_entries_count"] = mock_logs
        
        collector.update_counts(75, 45, 300)
        
        # Should call set on all metrics
        mock_products.set.assert_called_once_with(75)
        mock_dishes.set.assert_called_once_with(45)
        mock_logs.set.assert_called_once_with(300)
    
    @patch('src.monitoring.PROMETHEUS_AVAILABLE', False)
    def test_get_metrics_without_prometheus(self):
        """Test get_metrics when Prometheus is not available"""
        collector = MetricsCollector()
        
        metrics = collector.get_metrics()
        
        assert isinstance(metrics, str)
        assert "Prometheus metrics not available" in metrics
    
    @patch('src.monitoring.PROMETHEUS_AVAILABLE', False)
    def test_init_metrics_without_prometheus(self):
        """Test _init_metrics when Prometheus is not available"""
        # This tests line 40-41 (the warning log)
        with patch('src.monitoring.logger') as mock_logger:
            collector = MetricsCollector()
            
            # Should log warning when Prometheus not available
            mock_logger.warning.assert_called_once()
            assert "Prometheus not available" in str(mock_logger.warning.call_args)


class TestMonitorHttpRequest:
    """Test monitor_http_request decorator"""
    
    def test_monitor_http_request_success(self):
        """Test monitoring successful HTTP request"""
        @monitor_http_request
        def test_endpoint():
            return {'status': 'success'}
        
        result = test_endpoint()
        
        assert result['status'] == 'success'
    
    def test_monitor_http_request_exception(self):
        """Test monitoring HTTP request with exception"""
        @monitor_http_request
        def test_endpoint():
            raise Exception("Test error")
        
        with pytest.raises(Exception):
            test_endpoint()


class TestMonitorDatabaseOperation:
    """Test monitor_database_operation decorator"""
    
    def test_monitor_database_operation_success(self):
        """Test monitoring successful database operation"""
        @monitor_database_operation('SELECT', 'users')
        def test_query():
            return {'data': 'test'}
        
        result = test_query()
        
        assert result['data'] == 'test'
    
    def test_monitor_database_operation_exception(self):
        """Test monitoring database operation with exception"""
        @monitor_database_operation('INSERT', 'users')
        def test_query():
            raise Exception("Database error")
        
        with pytest.raises(Exception):
            test_query()


class TestMonitorCacheOperation:
    """Test monitor_cache_operation decorator"""
    
    def test_monitor_cache_operation_success(self):
        """Test monitoring successful cache operation"""
        @monitor_cache_operation('GET')
        def test_cache_get():
            return 'cached_value'
        
        result = test_cache_get()
        
        assert result == 'cached_value'
    
    def test_monitor_cache_operation_exception(self):
        """Test monitoring cache operation with exception"""
        @monitor_cache_operation('SET')
        def test_cache_set():
            raise Exception("Cache error")
        
        with pytest.raises(Exception):
            test_cache_set()


class TestMonitorBackgroundTask:
    """Test monitor_background_task decorator"""
    
    def test_monitor_background_task_success(self):
        """Test monitoring successful background task"""
        @monitor_background_task('email_sending')
        def test_task():
            return {'status': 'completed'}
        
        result = test_task()
        
        assert result['status'] == 'completed'
    
    def test_monitor_background_task_exception(self):
        """Test monitoring background task with exception"""
        @monitor_background_task('data_processing')
        def test_task():
            raise Exception("Task error")
        
        with pytest.raises(Exception):
            test_task()


class TestSystemMonitor:
    """Test SystemMonitor class"""
    
    def test_init(self):
        """Test SystemMonitor initialization"""
        monitor = SystemMonitor()
        assert monitor.last_update == 0
        assert monitor.update_interval == 60
    
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    @patch('src.monitoring.metrics_collector')
    def test_update_metrics(self, mock_metrics_collector, mock_cpu_percent, mock_virtual_memory):
        """Test updating system metrics"""
        # Mock psutil values
        mock_virtual_memory.return_value = Mock(used=1024)
        mock_cpu_percent.return_value = 25.5
        
        monitor = SystemMonitor()
        monitor.update_metrics()
        
        mock_metrics_collector.update_system_metrics.assert_called_once_with(1024, 25.5)
        assert monitor.last_update > 0
    
    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_percent')
    @patch('src.monitoring.metrics_collector')
    def test_update_metrics_interval(self, mock_metrics_collector, mock_cpu_percent, mock_virtual_memory):
        """Test that metrics are not updated too frequently"""
        monitor = SystemMonitor()
        monitor.last_update = time.time()  # Set to current time
        
        monitor.update_metrics()
        
        # Should not call update_system_metrics due to interval
        mock_metrics_collector.update_system_metrics.assert_not_called()
    
    @patch('src.monitoring.metrics_collector')
    def test_update_metrics_import_error(self, mock_metrics_collector):
        """Test handling of psutil import error"""
        with patch('psutil.virtual_memory', side_effect=ImportError("psutil not available")):
            monitor = SystemMonitor()
            monitor.update_metrics()
        
        # Should not call update_system_metrics due to import error
        mock_metrics_collector.update_system_metrics.assert_not_called()
    
    @patch('psutil.virtual_memory')
    @patch('src.monitoring.metrics_collector')
    def test_update_metrics_exception(self, mock_metrics_collector, mock_virtual_memory):
        """Test handling of general exception"""
        mock_virtual_memory.side_effect = Exception("System error")
        
        monitor = SystemMonitor()
        monitor.update_metrics()
        
        # Should not call update_system_metrics due to exception
        mock_metrics_collector.update_system_metrics.assert_not_called()
