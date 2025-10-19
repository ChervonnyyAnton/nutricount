"""
Monitoring Module
Handles metrics collection with Prometheus
"""

import logging
import time
from typing import Dict, Any, Optional
from functools import wraps

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = Gauge = Summary = CollectorRegistry = generate_latest = None

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects application metrics for Prometheus"""
    
    def __init__(self):
        self.registry = CollectorRegistry() if PROMETHEUS_AVAILABLE else None
        self.metrics = {}
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus not available, metrics collection disabled")
            return
        
        # HTTP metrics
        self.metrics['http_requests_total'] = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.metrics['http_request_duration_seconds'] = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Database metrics
        self.metrics['database_operations_total'] = Counter(
            'database_operations_total',
            'Total database operations',
            ['operation', 'table'],
            registry=self.registry
        )
        
        self.metrics['database_query_duration_seconds'] = Histogram(
            'database_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table'],
            registry=self.registry
        )
        
        # Cache metrics
        self.metrics['cache_operations_total'] = Counter(
            'cache_operations_total',
            'Total cache operations',
            ['operation', 'result'],
            registry=self.registry
        )
        
        self.metrics['cache_hit_rate'] = Gauge(
            'cache_hit_rate',
            'Cache hit rate percentage',
            registry=self.registry
        )
        
        # Application metrics
        self.metrics['active_users'] = Gauge(
            'active_users',
            'Number of active users',
            registry=self.registry
        )
        
        self.metrics['products_count'] = Gauge(
            'products_count',
            'Total number of products',
            registry=self.registry
        )
        
        self.metrics['dishes_count'] = Gauge(
            'dishes_count',
            'Total number of dishes',
            registry=self.registry
        )
        
        self.metrics['log_entries_count'] = Gauge(
            'log_entries_count',
            'Total number of log entries',
            registry=self.registry
        )
        
        # Fasting metrics
        self.metrics['fasting_sessions_total'] = Counter(
            'fasting_sessions_total',
            'Total fasting sessions',
            ['status', 'type'],
            registry=self.registry
        )
        
        self.metrics['fasting_duration_seconds'] = Histogram(
            'fasting_duration_seconds',
            'Fasting session duration in seconds',
            ['type'],
            registry=self.registry
        )
        
        # System metrics
        self.metrics['memory_usage_bytes'] = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )
        
        self.metrics['cpu_usage_percent'] = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        # Task metrics
        self.metrics['background_tasks_total'] = Counter(
            'background_tasks_total',
            'Total background tasks',
            ['task_type', 'status'],
            registry=self.registry
        )
        
        self.metrics['task_duration_seconds'] = Histogram(
            'task_duration_seconds',
            'Background task duration in seconds',
            ['task_type'],
            registry=self.registry
        )
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        if PROMETHEUS_AVAILABLE and 'http_requests_total' in self.metrics:
            self.metrics['http_requests_total'].labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code)
            ).inc()
            
            self.metrics['http_request_duration_seconds'].labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    def record_database_operation(self, operation: str, table: str, duration: float):
        """Record database operation metrics"""
        if PROMETHEUS_AVAILABLE and 'database_operations_total' in self.metrics:
            self.metrics['database_operations_total'].labels(
                operation=operation,
                table=table
            ).inc()
            
            self.metrics['database_query_duration_seconds'].labels(
                operation=operation,
                table=table
            ).observe(duration)
    
    def record_cache_operation(self, operation: str, hit: bool):
        """Record cache operation metrics"""
        if PROMETHEUS_AVAILABLE and 'cache_operations_total' in self.metrics:
            result = 'hit' if hit else 'miss'
            self.metrics['cache_operations_total'].labels(
                operation=operation,
                result=result
            ).inc()
    
    def update_cache_hit_rate(self, hit_rate: float):
        """Update cache hit rate"""
        if PROMETHEUS_AVAILABLE and 'cache_hit_rate' in self.metrics:
            self.metrics['cache_hit_rate'].set(hit_rate)
    
    def update_active_users(self, count: int):
        """Update active users count"""
        if PROMETHEUS_AVAILABLE and 'active_users' in self.metrics:
            self.metrics['active_users'].set(count)
    
    def update_counts(self, products: int, dishes: int, log_entries: int):
        """Update entity counts"""
        if PROMETHEUS_AVAILABLE:
            if 'products_count' in self.metrics:
                self.metrics['products_count'].set(products)
            if 'dishes_count' in self.metrics:
                self.metrics['dishes_count'].set(dishes)
            if 'log_entries_count' in self.metrics:
                self.metrics['log_entries_count'].set(log_entries)
    
    def record_fasting_session(self, status: str, fasting_type: str, duration: float = None):
        """Record fasting session metrics"""
        if PROMETHEUS_AVAILABLE and 'fasting_sessions_total' in self.metrics:
            self.metrics['fasting_sessions_total'].labels(
                status=status,
                type=fasting_type
            ).inc()
            
            if duration is not None and 'fasting_duration_seconds' in self.metrics:
                self.metrics['fasting_duration_seconds'].labels(
                    type=fasting_type
                ).observe(duration)
    
    def record_background_task(self, task_type: str, status: str, duration: float = None):
        """Record background task metrics"""
        if PROMETHEUS_AVAILABLE and 'background_tasks_total' in self.metrics:
            self.metrics['background_tasks_total'].labels(
                task_type=task_type,
                status=status
            ).inc()
            
            if duration is not None and 'task_duration_seconds' in self.metrics:
                self.metrics['task_duration_seconds'].labels(
                    task_type=task_type
                ).observe(duration)
    
    def update_system_metrics(self, memory_bytes: int, cpu_percent: float):
        """Update system metrics"""
        if PROMETHEUS_AVAILABLE:
            if 'memory_usage_bytes' in self.metrics:
                self.metrics['memory_usage_bytes'].set(memory_bytes)
            if 'cpu_usage_percent' in self.metrics:
                self.metrics['cpu_usage_percent'].set(cpu_percent)
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        if PROMETHEUS_AVAILABLE and self.registry:
            return generate_latest(self.registry).decode('utf-8')
        else:
            return "# Prometheus metrics not available\n"
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for API"""
        summary = {
            'prometheus_available': PROMETHEUS_AVAILABLE,
            'metrics_count': len(self.metrics) if self.metrics else 0,
            'registry_available': self.registry is not None
        }
        
        if PROMETHEUS_AVAILABLE and self.metrics:
            # Get some sample metrics
            summary['sample_metrics'] = {}
            for name, metric in self.metrics.items():
                if hasattr(metric, '_value'):
                    summary['sample_metrics'][name] = metric._value.get()
                elif hasattr(metric, '_sum'):
                    summary['sample_metrics'][name] = {
                        'count': metric._count.get(),
                        'sum': metric._sum.get()
                    }
        
        return summary

# Global metrics collector instance
metrics_collector = MetricsCollector()

def monitor_http_request(func):
    """Decorator to monitor HTTP requests"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            status_code = 200
            return result
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            
            # Extract method and endpoint from Flask request context
            try:
                from flask import request
                method = request.method
                endpoint = request.endpoint or 'unknown'
            except:
                method = 'unknown'
                endpoint = func.__name__
            
            metrics_collector.record_http_request(method, endpoint, status_code, duration)
    
    return wrapper

def monitor_database_operation(operation: str, table: str = 'unknown'):
    """Decorator to monitor database operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metrics_collector.record_database_operation(operation, table, duration)
        
        return wrapper
    return decorator

def monitor_cache_operation(operation: str):
    """Decorator to monitor cache operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                hit = result is not None
                metrics_collector.record_cache_operation(operation, hit)
                return result
            except Exception as e:
                metrics_collector.record_cache_operation(operation, False)
                raise
        
        return wrapper
    return decorator

def monitor_background_task(task_type: str):
    """Decorator to monitor background tasks"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                metrics_collector.record_background_task(task_type, 'success', time.time() - start_time)
                return result
            except Exception as e:
                metrics_collector.record_background_task(task_type, 'failure', time.time() - start_time)
                raise
        
        return wrapper
    return decorator

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.last_update = 0
        self.update_interval = 60  # Update every 60 seconds
    
    def update_metrics(self):
        """Update system metrics"""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        
        try:
            import psutil
            
            # Get memory usage
            memory_info = psutil.virtual_memory()
            memory_bytes = memory_info.used
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Update metrics
            metrics_collector.update_system_metrics(memory_bytes, cpu_percent)
            
            self.last_update = current_time
            
        except ImportError:
            logger.warning("psutil not available for system monitoring")
        except Exception as e:
            logger.error(f"System monitoring error: {e}")

# Global system monitor instance
system_monitor = SystemMonitor()
