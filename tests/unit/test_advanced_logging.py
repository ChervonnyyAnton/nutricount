"""
Unit tests for advanced_logging.py
"""

import pytest
from unittest.mock import patch, Mock, MagicMock, mock_open
import tempfile
import os
from pathlib import Path
from datetime import datetime
from src.advanced_logging import (
    StructuredLogger,
    LogAnalyzer,
    LOGURU_AVAILABLE,
    ELASTICSEARCH_AVAILABLE
)


class TestStructuredLogger:
    """Test StructuredLogger class"""
    
    def test_init(self):
        """Test StructuredLogger initialization"""
        logger = StructuredLogger()
        assert logger.app_name == "nutrition-tracker"
        assert logger.log_level == "INFO"
        assert logger.es_client is None
        assert logger.log_dir == Path("logs")
    
    def test_init_with_custom_params(self):
        """Test StructuredLogger initialization with custom parameters"""
        logger = StructuredLogger(
            app_name="test-app",
            log_level="DEBUG",
            elasticsearch_url="http://localhost:9200"
        )
        assert logger.app_name == "test-app"
        assert logger.log_level == "DEBUG"
        assert logger.elasticsearch_url == "http://localhost:9200"
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', True)
    @patch('src.advanced_logging.loguru_logger')
    def test_setup_logging_with_loguru(self, mock_loguru):
        """Test logging setup with loguru available"""
        logger = StructuredLogger()
        # Verify loguru methods were called
        assert mock_loguru.remove.called
        assert mock_loguru.add.called
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', False)
    @patch('src.advanced_logging.logging.getLogger')
    def test_setup_logging_without_loguru(self, mock_get_logger):
        """Test logging setup without loguru"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        logger = StructuredLogger()
        
        mock_get_logger.assert_called_once_with("nutrition-tracker")
        mock_logger.addHandler.assert_called_once()
        mock_logger.setLevel.assert_called_once()
    
    @patch('src.advanced_logging.ELASTICSEARCH_AVAILABLE', True)
    @patch('src.advanced_logging.Elasticsearch')
    def test_setup_elasticsearch_success(self, mock_elasticsearch):
        """Test Elasticsearch setup success"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_elasticsearch.return_value = mock_client
        
        logger = StructuredLogger(elasticsearch_url="http://localhost:9200")
        
        assert logger.es_client == mock_client
        mock_client.ping.assert_called_once()
    
    @patch('src.advanced_logging.ELASTICSEARCH_AVAILABLE', True)
    @patch('src.advanced_logging.Elasticsearch')
    def test_setup_elasticsearch_failure(self, mock_elasticsearch):
        """Test Elasticsearch setup failure"""
        mock_client = Mock()
        mock_client.ping.return_value = False
        mock_elasticsearch.return_value = mock_client
        
        logger = StructuredLogger(elasticsearch_url="http://localhost:9200")
        
        assert logger.es_client is None
    
    @patch('src.advanced_logging.ELASTICSEARCH_AVAILABLE', False)
    def test_setup_elasticsearch_not_available(self):
        """Test Elasticsearch setup when not available"""
        logger = StructuredLogger(elasticsearch_url="http://localhost:9200")
        assert logger.es_client is None
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', True)
    @patch('src.advanced_logging.loguru_logger')
    def test_log_application_event_with_loguru(self, mock_loguru):
        """Test logging application event with loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_application_event("INFO", "Test message", user_id=123)
        
        logger.logger.bind.assert_called_once()
        logger.logger.bind.return_value.log.assert_called_once_with("INFO", "Test message")
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', False)
    def test_log_application_event_without_loguru(self):
        """Test logging application event without loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_application_event("INFO", "Test message", user_id=123)
        
        logger.logger.log.assert_called_once()
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', True)
    @patch('src.advanced_logging.loguru_logger')
    def test_log_access_event_with_loguru(self, mock_loguru):
        """Test logging access event with loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_access_event("GET", "/api/test", 200, 0.1, user_id=123, ip="127.0.0.1")
        
        logger.logger.bind.assert_called_once()
        logger.logger.bind.return_value.info.assert_called_once()
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', False)
    def test_log_access_event_without_loguru(self):
        """Test logging access event without loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_access_event("GET", "/api/test", 200, 0.1, user_id=123, ip="127.0.0.1")
        
        logger.logger.info.assert_called_once()
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', True)
    @patch('src.advanced_logging.loguru_logger')
    def test_log_security_event_with_loguru(self, mock_loguru):
        """Test logging security event with loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_security_event("login_failed", "Failed login attempt", user_id=123, ip="127.0.0.1")
        
        logger.logger.bind.assert_called_once()
        logger.logger.bind.return_value.warning.assert_called_once()
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', False)
    def test_log_security_event_without_loguru(self):
        """Test logging security event without loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_security_event("login_failed", "Failed login attempt", user_id=123, ip="127.0.0.1")
        
        logger.logger.warning.assert_called_once()
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', True)
    @patch('src.advanced_logging.loguru_logger')
    def test_log_performance_event_with_loguru(self, mock_loguru):
        """Test logging performance event with loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_performance_event("database_query", 0.5, {"table": "users"})
        
        logger.logger.bind.assert_called_once()
        logger.logger.bind.return_value.info.assert_called_once()
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', False)
    def test_log_performance_event_without_loguru(self):
        """Test logging performance event without loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_performance_event("database_query", 0.5, {"table": "users"})
        
        logger.logger.info.assert_called_once()
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', True)
    @patch('src.advanced_logging.loguru_logger')
    def test_log_business_event_with_loguru(self, mock_loguru):
        """Test logging business event with loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_business_event("user_registration", "New user registered", user_id=123)
        
        logger.logger.bind.assert_called_once()
        logger.logger.bind.return_value.info.assert_called_once()
    
    @patch('src.advanced_logging.LOGURU_AVAILABLE', False)
    def test_log_business_event_without_loguru(self):
        """Test logging business event without loguru"""
        logger = StructuredLogger()
        logger.logger = Mock()
        
        logger.log_business_event("user_registration", "New user registered", user_id=123)
        
        logger.logger.info.assert_called_once()
    
    def test_send_to_elasticsearch_no_client(self):
        """Test sending to Elasticsearch when no client"""
        logger = StructuredLogger()
        logger.es_client = None
        
        # Should not raise exception
        logger._send_to_elasticsearch("test", "INFO", "test message", {})
    
    def test_send_to_elasticsearch_with_client(self):
        """Test sending to Elasticsearch with client"""
        logger = StructuredLogger()
        mock_client = Mock()
        logger.es_client = mock_client
        
        logger._send_to_elasticsearch("test", "INFO", "test message", {"key": "value"})
        
        mock_client.index.assert_called_once()
    
    def test_send_to_elasticsearch_exception(self):
        """Test sending to Elasticsearch with exception"""
        logger = StructuredLogger()
        mock_client = Mock()
        mock_client.index.side_effect = Exception("Connection failed")
        logger.es_client = mock_client
        
        # Should not raise exception
        logger._send_to_elasticsearch("test", "INFO", "test message", {})
    
    def test_get_log_stats(self):
        """Test getting log statistics"""
        logger = StructuredLogger()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.log_dir = Path(temp_dir)
            
            # Create a test log file
            test_log = logger.log_dir / "test.log"
            test_log.write_text("test content")
            
            stats = logger.get_log_stats()
            
            assert stats["loguru_available"] == LOGURU_AVAILABLE
            assert stats["elasticsearch_available"] == ELASTICSEARCH_AVAILABLE
            assert stats["elasticsearch_connected"] is False
            assert stats["log_level"] == "INFO"
            assert "log_files" in stats


class TestLogAnalyzer:
    """Test LogAnalyzer class"""
    
    def test_init(self):
        """Test LogAnalyzer initialization"""
        analyzer = LogAnalyzer()
        assert analyzer.log_dir == Path("logs")
    
    def test_init_with_custom_dir(self):
        """Test LogAnalyzer initialization with custom directory"""
        analyzer = LogAnalyzer("custom_logs")
        assert analyzer.log_dir == Path("custom_logs")
    
    def test_analyze_error_patterns_no_log(self):
        """Test error pattern analysis when log doesn't exist"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            result = analyzer.analyze_error_patterns()
            
            assert "error" in result
            assert result["error"] == "Error log not found"
    
    def test_analyze_error_patterns_with_log(self):
        """Test error pattern analysis with log file"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            
            # Create error log with test content
            error_log = analyzer.log_dir / "error.log"
            error_log.write_text("""
2025-01-01 10:00:00 | ERROR | Database connection failed
2025-01-01 10:01:00 | ERROR | Authentication failed for user 123
2025-01-01 10:02:00 | ERROR | Rate limit exceeded
2025-01-01 10:03:00 | ERROR | Unknown error occurred
""")
            
            result = analyzer.analyze_error_patterns()
            
            assert result["total_errors"] == 4
            assert "error_types" in result
            assert result["analysis_period_days"] == 7
    
    def test_analyze_performance_trends_no_log(self):
        """Test performance trend analysis when log doesn't exist"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            result = analyzer.analyze_performance_trends()
            
            assert "error" in result
            assert result["error"] == "Application log not found"
    
    def test_analyze_performance_trends_with_log(self):
        """Test performance trend analysis with log file"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            
            # Create app log with performance data
            app_log = analyzer.log_dir / "app.log"
            app_log.write_text("""
2025-01-01 10:00:00 | INFO | Performance: database_query took 0.5s
2025-01-01 10:01:00 | INFO | Performance: api_call took 0.2s
2025-01-01 10:02:00 | INFO | Performance: cache_lookup took 0.1s
""")
            
            result = analyzer.analyze_performance_trends()
            
            assert result["total_operations"] == 3
            assert "average_duration" in result
            assert "max_duration" in result
            assert "min_duration" in result
            assert result["analysis_period_days"] == 7
    
    def test_analyze_performance_trends_no_data(self):
        """Test performance trend analysis with no performance data"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            
            # Create app log without performance data
            app_log = analyzer.log_dir / "app.log"
            app_log.write_text("""
2025-01-01 10:00:00 | INFO | Regular log message
2025-01-01 10:01:00 | INFO | Another regular message
""")
            
            result = analyzer.analyze_performance_trends()
            
            assert "error" in result
            assert result["error"] == "No performance data found"
    
    def test_get_security_alerts_no_log(self):
        """Test security alerts when log doesn't exist"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            result = analyzer.get_security_alerts()
            
            assert "error" in result
            assert result["error"] == "Audit log not found"
    
    def test_get_security_alerts_with_log(self):
        """Test security alerts with log file"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            
            # Create audit log with security events
            audit_log = analyzer.log_dir / "audit.log"
            audit_log.write_text("""
2025-01-01 10:00:00 | INFO | FAILED login attempt for user 123
2025-01-01 10:01:00 | INFO | rate_limit hit for IP 127.0.0.1
2025-01-01 10:02:00 | INFO | admin action performed by user 456
2025-01-01 10:03:00 | INFO | token usage logged for user 789
""")
            
            result = analyzer.get_security_alerts()
            
            assert "security_events" in result
            assert result["analysis_period_days"] == 7
            assert result["security_events"]["failed_logins"] == 1
            assert result["security_events"]["rate_limit_hits"] == 1
            assert result["security_events"]["admin_actions"] == 1
            assert result["security_events"]["token_usage"] == 1


class TestElasticsearchIntegration:
    """Test Elasticsearch integration to increase coverage"""
    
    def test_log_application_event_with_elasticsearch(self):
        """Test log_application_event with Elasticsearch client"""
        logger = StructuredLogger("test_app")
        logger.es_client = MagicMock()
        
        with patch.object(logger, '_send_to_elasticsearch') as mock_send:
            logger.log_application_event("INFO", "Test message", extra="data")
            
            # Should call _send_to_elasticsearch
            mock_send.assert_called_once()
    
    def test_log_access_event_with_elasticsearch(self):
        """Test log_access_event with Elasticsearch client"""
        logger = StructuredLogger("test_app")
        logger.es_client = MagicMock()
        
        with patch.object(logger, '_send_to_elasticsearch') as mock_send:
            logger.log_access_event("GET", "/test", 200, 0.1, user_id=1, ip="127.0.0.1")
            
            # Should call _send_to_elasticsearch
            mock_send.assert_called_once()
    
    def test_log_security_event_with_elasticsearch(self):
        """Test log_security_event with Elasticsearch client"""
        logger = StructuredLogger("test_app")
        logger.es_client = MagicMock()
        
        with patch.object(logger, '_send_to_elasticsearch') as mock_send:
            logger.log_security_event("login", "User logged in", user_id=1, ip="127.0.0.1")
            
            # Should call _send_to_elasticsearch
            mock_send.assert_called_once()
    
    def test_log_performance_event_with_elasticsearch(self):
        """Test log_performance_event with Elasticsearch client"""
        logger = StructuredLogger("test_app")
        logger.es_client = MagicMock()
        
        with patch.object(logger, '_send_to_elasticsearch') as mock_send:
            logger.log_performance_event("database_query", 0.5, {"table": "users"})
            
            # Should call _send_to_elasticsearch
            mock_send.assert_called_once()
    
    def test_log_business_event_with_elasticsearch(self):
        """Test log_business_event with Elasticsearch client"""
        logger = StructuredLogger("test_app")
        logger.es_client = MagicMock()
        
        with patch.object(logger, '_send_to_elasticsearch') as mock_send:
            logger.log_business_event("purchase", "User made a purchase", user_id=1, amount=100)
            
            # Should call _send_to_elasticsearch
            mock_send.assert_called_once()


class TestLogAnalyzerExtended:
    """Test LogAnalyzer extended functionality to increase coverage"""
    
    def test_analyze_error_patterns_exception(self):
        """Test analyze_error_patterns with exception"""
        analyzer = LogAnalyzer()
        
        with patch.object(analyzer, 'log_dir', Path("/nonexistent/path")):
            result = analyzer.analyze_error_patterns()
            
            assert "error" in result
    
    def test_analyze_performance_trends_exception(self):
        """Test analyze_performance_trends with exception"""
        analyzer = LogAnalyzer()
        
        with patch.object(analyzer, 'log_dir', Path("/nonexistent/path")):
            result = analyzer.analyze_performance_trends()
            
            assert "error" in result
    
    def test_analyze_performance_trends_no_data(self):
        """Test analyze_performance_trends with no performance data"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            
            # Create empty app.log
            app_log = analyzer.log_dir / "app.log"
            app_log.write_text("")
            
            result = analyzer.analyze_performance_trends()
            
            assert result["error"] == "No performance data found"
    
    def test_get_security_alerts_exception(self):
        """Test get_security_alerts with exception"""
        analyzer = LogAnalyzer()
        
        with patch.object(analyzer, 'log_dir', Path("/nonexistent/path")):
            result = analyzer.get_security_alerts()
            
            assert "error" in result
    
    def test_get_security_alerts_high_failed_logins(self):
        """Test get_security_alerts with high failed logins"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            
            # Create audit.log with high failed logins
            audit_log = analyzer.log_dir / "audit.log"
            audit_content = "\n".join(["FAILED login attempt" for _ in range(15)])
            audit_log.write_text(audit_content)
            
            result = analyzer.get_security_alerts()
            
            assert "alerts" in result
            assert len(result["alerts"]) > 0
            assert any(alert["type"] == "high_failed_logins" for alert in result["alerts"])
    
    def test_get_security_alerts_rate_limit_exceeded(self):
        """Test get_security_alerts with rate limit exceeded"""
        analyzer = LogAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer.log_dir = Path(temp_dir)
            
            # Create audit.log with rate limit hits
            audit_log = analyzer.log_dir / "audit.log"
            audit_content = "\n".join(["rate_limit hit" for _ in range(10)])
            audit_log.write_text(audit_content)
            
            result = analyzer.get_security_alerts()
            
            assert "alerts" in result
            assert len(result["alerts"]) > 0
            assert any(alert["type"] == "rate_limit_exceeded" for alert in result["alerts"])


class TestElasticsearchErrorTracking:
    """Test Elasticsearch error tracking improvements"""

    def test_es_error_count_initialization(self, tmp_path):
        """Test error counter is initialized to 0"""
        logger = StructuredLogger(app_name="test-app")
        assert logger.es_error_count == 0

    def test_es_error_count_increments_on_failure(self, tmp_path):
        """Test error counter increments on Elasticsearch failures"""
        with patch('src.advanced_logging.ELASTICSEARCH_AVAILABLE', True):
            with patch('src.advanced_logging.Elasticsearch') as mock_es_class:
                # Create a mock Elasticsearch client that raises errors
                mock_es = Mock()
                mock_es.index.side_effect = Exception("Connection error")
                mock_es_class.return_value = mock_es

                logger = StructuredLogger(
                    app_name="test-app",
                    elasticsearch_url="http://localhost:9200"
                )

                # Trigger Elasticsearch logging which should fail
                logger._send_to_elasticsearch("test", "INFO", "test message", {})

                # Error counter should increment
                assert logger.es_error_count == 1

                # Send another log
                logger._send_to_elasticsearch("test", "INFO", "test message 2", {})
                assert logger.es_error_count == 2

    def test_es_error_count_in_stats(self, tmp_path):
        """Test error count is included in log stats"""
        logger = StructuredLogger(app_name="test-app")
        logger.es_error_count = 5  # Simulate errors

        stats = logger.get_log_stats()

        assert "elasticsearch_error_count" in stats
        assert stats["elasticsearch_error_count"] == 5
