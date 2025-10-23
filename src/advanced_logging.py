"""
Advanced Logging Module
Handles structured logging with ELK Stack integration
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

try:
    from loguru import logger as loguru_logger

    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    loguru_logger = None

try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None

try:
    from elasticsearch import Elasticsearch

    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    Elasticsearch = None


class StructuredLogger:
    """Structured logging with multiple outputs"""

    def __init__(
        self,
        app_name: str = "nutrition-tracker",
        log_level: str = "INFO",
        elasticsearch_url: str = None,
    ):
        self.app_name = app_name
        self.log_level = log_level
        self.elasticsearch_url = elasticsearch_url
        self.es_client = None
        self.es_error_count = 0  # Track Elasticsearch errors

        # Create logs directory
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Setup logging
        self._setup_logging()
        self._setup_elasticsearch()

    def _setup_logging(self):
        """Setup structured logging"""
        if LOGURU_AVAILABLE:
            # Remove default handler
            loguru_logger.remove()

            # Console logging with colors
            loguru_logger.add(
                sys.stdout,
                level=self.log_level,
                format=(
                    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                    "<level>{message}</level>"
                ),
                colorize=True,
            )

            # File logging - application logs
            loguru_logger.add(
                self.log_dir / "app.log",
                level=self.log_level,
                format=(
                    "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                    "{name}:{function}:{line} - {message}"
                ),
                rotation="10 MB",
                retention="30 days",
                compression="zip",
            )

            # File logging - error logs
            loguru_logger.add(
                self.log_dir / "error.log",
                level="ERROR",
                format=(
                    "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                    "{name}:{function}:{line} - {message}"
                ),
                rotation="5 MB",
                retention="90 days",
                compression="zip",
            )

            # File logging - access logs
            loguru_logger.add(
                self.log_dir / "access.log",
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                rotation="10 MB",
                retention="30 days",
                compression="zip",
                filter=lambda record: record["extra"].get("log_type") == "access",
            )

            # File logging - audit logs
            loguru_logger.add(
                self.log_dir / "audit.log",
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                rotation="5 MB",
                retention="365 days",
                compression="zip",
                filter=lambda record: record["extra"].get("log_type") == "audit",
            )

            self.logger = loguru_logger
        else:
            # Fallback to standard logging
            self.logger = logging.getLogger(self.app_name)
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, self.log_level))

    def _setup_elasticsearch(self):
        """Setup Elasticsearch connection"""
        if ELASTICSEARCH_AVAILABLE and self.elasticsearch_url:
            try:
                self.es_client = Elasticsearch([self.elasticsearch_url])
                # Test connection
                if self.es_client.ping():
                    self.logger.info("Elasticsearch connection established")
                else:
                    self.logger.warning("Elasticsearch connection failed")
                    self.es_client = None
            except Exception as e:
                self.logger.warning(f"Elasticsearch setup failed: {e}")
                self.es_client = None

    def log_application_event(self, level: str, message: str, **kwargs):
        """Log application event"""
        extra_data = {
            "log_type": "application",
            "app_name": self.app_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }

        if LOGURU_AVAILABLE:
            self.logger.bind(**extra_data).log(level, message)
        else:
            self.logger.log(getattr(logging, level), f"{message} | {json.dumps(extra_data)}")

        # Send to Elasticsearch if available
        if self.es_client:
            self._send_to_elasticsearch("application", level, message, extra_data)

    def log_access_event(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_id: int = None,
        ip: str = None,
    ):
        """Log HTTP access event"""
        extra_data = {
            "log_type": "access",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
            "user_id": user_id,
            "ip": ip,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        message = f"{method} {path} {status_code} {duration:.3f}s"

        if LOGURU_AVAILABLE:
            self.logger.bind(**extra_data).info(message)
        else:
            self.logger.info(f"{message} | {json.dumps(extra_data)}")

        # Send to Elasticsearch if available
        if self.es_client:
            self._send_to_elasticsearch("access", "INFO", message, extra_data)

    def log_security_event(
        self, event_type: str, message: str, user_id: int = None, ip: str = None, **kwargs
    ):
        """Log security event"""
        extra_data = {
            "log_type": "security",
            "event_type": event_type,
            "user_id": user_id,
            "ip": ip,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }

        if LOGURU_AVAILABLE:
            self.logger.bind(**extra_data).warning(message)
        else:
            self.logger.warning(f"{message} | {json.dumps(extra_data)}")

        # Send to Elasticsearch if available
        if self.es_client:
            self._send_to_elasticsearch("security", "WARNING", message, extra_data)

    def log_performance_event(
        self, operation: str, duration: float, details: Dict[str, Any] = None
    ):
        """Log performance event"""
        extra_data = {
            "log_type": "performance",
            "operation": operation,
            "duration": duration,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        message = f"Performance: {operation} took {duration:.3f}s"

        if LOGURU_AVAILABLE:
            self.logger.bind(**extra_data).info(message)
        else:
            self.logger.info(f"{message} | {json.dumps(extra_data)}")

        # Send to Elasticsearch if available
        if self.es_client:
            self._send_to_elasticsearch("performance", "INFO", message, extra_data)

    def log_business_event(self, event_type: str, message: str, user_id: int = None, **kwargs):
        """Log business event"""
        extra_data = {
            "log_type": "business",
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }

        if LOGURU_AVAILABLE:
            self.logger.bind(**extra_data).info(message)
        else:
            self.logger.info(f"{message} | {json.dumps(extra_data)}")

        # Send to Elasticsearch if available
        if self.es_client:
            self._send_to_elasticsearch("business", "INFO", message, extra_data)

    def _send_to_elasticsearch(self, log_type: str, level: str, message: str, data: Dict[str, Any]):
        """Send log to Elasticsearch"""
        if not self.es_client:
            return

        try:
            index_name = (
                f"{self.app_name}-{log_type}-{datetime.now(timezone.utc).strftime('%Y.%m.%d')}"
            )

            document = {
                "@timestamp": datetime.now(timezone.utc).isoformat(),
                "level": level,
                "message": message,
                "log_type": log_type,
                **data,
            }

            self.es_client.index(index=index_name, body=document)
        except Exception as e:
            # Increment error counter to track Elasticsearch issues
            self.es_error_count += 1
            # Write to stderr to avoid logging recursion but still capture the error
            if self.es_error_count <= 5:  # Only log first 5 errors to avoid spam
                print(f"Elasticsearch error ({self.es_error_count}): {e}", file=sys.stderr)

    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        stats = {
            "loguru_available": LOGURU_AVAILABLE,
            "elasticsearch_available": ELASTICSEARCH_AVAILABLE,
            "elasticsearch_connected": self.es_client is not None,
            "elasticsearch_error_count": self.es_error_count,
            "log_level": self.log_level,
            "log_directory": str(self.log_dir),
        }

        # Get log file sizes
        if self.log_dir.exists():
            stats["log_files"] = {}
            for log_file in self.log_dir.glob("*.log"):
                stats["log_files"][log_file.name] = {
                    "size_bytes": log_file.stat().st_size,
                    "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat(),
                }

        return stats


class LogAnalyzer:
    """Analyzes logs for patterns and anomalies"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)

    def analyze_error_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Analyze error patterns in logs"""
        error_patterns = {}

        try:
            error_log = self.log_dir / "error.log"
            if not error_log.exists():
                return {"error": "Error log not found"}

            # Simple pattern analysis
            with open(error_log, "r") as f:
                lines = f.readlines()

            # Count errors by type
            error_counts = {}
            for log_line in lines:
                if "ERROR" in log_line:
                    # Extract error type (simplified)
                    if "Database" in log_line:
                        error_counts["database"] = error_counts.get("database", 0) + 1
                    elif "Authentication" in log_line:
                        error_counts["authentication"] = error_counts.get("authentication", 0) + 1
                    elif "Rate limit" in log_line:
                        error_counts["rate_limit"] = error_counts.get("rate_limit", 0) + 1
                    else:
                        error_counts["other"] = error_counts.get("other", 0) + 1

            error_patterns = {
                "total_errors": len([log_line for log_line in lines if "ERROR" in log_line]),
                "error_types": error_counts,
                "analysis_period_days": days,
            }

        except Exception as e:
            error_patterns = {"error": str(e)}

        return error_patterns

    def analyze_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyze performance trends"""
        performance_data = {}

        try:
            app_log = self.log_dir / "app.log"
            if not app_log.exists():
                return {"error": "Application log not found"}

            # Simple performance analysis
            with open(app_log, "r") as f:
                lines = f.readlines()

            # Extract performance data
            durations = []
            for line in lines:
                if "Performance:" in line and "took" in line:
                    try:
                        # Extract duration (simplified)
                        duration_str = line.split("took ")[1].split("s")[0]
                        duration = float(duration_str)
                        durations.append(duration)
                    except (ValueError, IndexError):
                        continue

            if durations:
                performance_data = {
                    "total_operations": len(durations),
                    "average_duration": sum(durations) / len(durations),
                    "max_duration": max(durations),
                    "min_duration": min(durations),
                    "analysis_period_days": days,
                }
            else:
                performance_data = {"error": "No performance data found"}

        except Exception as e:
            performance_data = {"error": str(e)}

        return performance_data

    def get_security_alerts(self, days: int = 7) -> Dict[str, Any]:
        """Get security alerts from logs"""
        security_alerts = {}

        try:
            audit_log = self.log_dir / "audit.log"
            if not audit_log.exists():
                return {"error": "Audit log not found"}

            with open(audit_log, "r") as f:
                lines = f.readlines()

            # Count security events
            security_events = {
                "failed_logins": 0,
                "rate_limit_hits": 0,
                "admin_actions": 0,
                "token_usage": 0,
            }

            for line in lines:
                if "FAILED" in line and "login" in line.lower():
                    security_events["failed_logins"] += 1
                elif "rate_limit" in line.lower():
                    security_events["rate_limit_hits"] += 1
                elif "admin" in line.lower():
                    security_events["admin_actions"] += 1
                elif "token" in line.lower():
                    security_events["token_usage"] += 1

            security_alerts = {
                "security_events": security_events,
                "analysis_period_days": days,
                "alerts": [],
            }

            # Generate alerts
            if security_events["failed_logins"] > 10:
                security_alerts["alerts"].append(
                    {
                        "type": "high_failed_logins",
                        "message": (
                            f"High number of failed login attempts: "
                            f"{security_events['failed_logins']}"
                        ),
                        "severity": "warning",
                    }
                )

            if security_events["rate_limit_hits"] > 5:
                security_alerts["alerts"].append(
                    {
                        "type": "rate_limit_exceeded",
                        "message": (
                            f"Multiple rate limit hits: {security_events['rate_limit_hits']}"
                        ),
                        "severity": "info",
                    }
                )

        except Exception as e:
            security_alerts = {"error": str(e)}

        return security_alerts


# Global logger instance
structured_logger = StructuredLogger()

# Global log analyzer instance
log_analyzer = LogAnalyzer()
