"""
Async Task Manager Module
Handles background tasks with Celery
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

try:
    from celery import Celery
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    Celery = None
    AsyncResult = None

from src.config import Config

logger = logging.getLogger(__name__)

# Initialize Celery if available
if CELERY_AVAILABLE:
    celery_app = Celery('nutrition_tracker')
    celery_app.config_from_object({
        'broker_url': 'redis://localhost:6379/1',
        'result_backend': 'redis://localhost:6379/1',
        'task_serializer': 'json',
        'accept_content': ['json'],
        'result_serializer': 'json',
        'timezone': 'UTC',
        'enable_utc': True,
        'task_track_started': True,
        'task_time_limit': 30 * 60,  # 30 minutes
        'task_soft_time_limit': 25 * 60,  # 25 minutes
        'worker_prefetch_multiplier': 1,
        'worker_max_tasks_per_child': 1000,
    })
else:
    celery_app = None

class TaskManager:
    """Manages background tasks"""
    
    def __init__(self):
        self.celery_available = CELERY_AVAILABLE and celery_app is not None
    
    def backup_database(self, backup_path: str = None) -> str:
        """Backup database task"""
        if self.celery_available:
            result = backup_database_task.delay(backup_path)
            return result.id
        else:
            # Fallback to synchronous execution
            return self._backup_database_sync(backup_path)
    
    def optimize_database(self) -> str:
        """Optimize database task"""
        if self.celery_available:
            result = optimize_database_task.delay()
            return result.id
        else:
            return self._optimize_database_sync()
    
    def calculate_nutrition_stats(self, date_range: Dict[str, str]) -> str:
        """Calculate nutrition statistics task"""
        if self.celery_available:
            result = calculate_nutrition_stats_task.delay(date_range)
            return result.id
        else:
            return self._calculate_nutrition_stats_sync(date_range)
    
    def export_data(self, export_format: str = 'json') -> str:
        """Export data task"""
        if self.celery_available:
            result = export_data_task.delay(export_format)
            return result.id
        else:
            return self._export_data_sync(export_format)
    
    def cleanup_old_logs(self, days: int = 30) -> str:
        """Cleanup old logs task"""
        if self.celery_available:
            result = cleanup_old_logs_task.delay(days)
            return result.id
        else:
            return self._cleanup_old_logs_sync(days)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        if self.celery_available:
            try:
                result = AsyncResult(task_id, app=celery_app)
                status = result.status
                
                # Check if task exists (PENDING status with no result usually means task doesn't exist)
                if status == 'PENDING' and not result.info:
                    return {
                        'id': task_id,
                        'status': 'NOT_FOUND',
                        'error': 'Task not found'
                    }
                
                return {
                    'id': task_id,
                    'status': status,
                    'result': result.result if result.ready() else None,
                    'error': str(result.traceback) if result.failed() else None,
                    'progress': result.info.get('progress', 0) if result.info else 0
                }
            except Exception as e:
                return {
                    'id': task_id,
                    'status': 'FAILURE',
                    'error': str(e)
                }
        else:
            # In fallback mode, we can't check task status, so return NOT_FOUND for any task_id
            return {
                'id': task_id,
                'status': 'NOT_FOUND',
                'error': 'Task not found (Celery unavailable)'
            }
    
    def _backup_database_sync(self, backup_path: str = None) -> str:
        """Synchronous database backup"""
        try:
            import sqlite3
            import shutil
            from datetime import datetime
            
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"backups/nutrition_{timestamp}.db"
            
            shutil.copy2(Config.DATABASE, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return f"sync_backup_{datetime.now().timestamp()}"
        except Exception as e:
            logger.error(f"Backup error: {e}")
            raise
    
    def _optimize_database_sync(self) -> str:
        """Synchronous database optimization"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(Config.DATABASE)
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
            conn.close()
            logger.info("Database optimized")
            return f"sync_optimize_{datetime.now().timestamp()}"
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            raise
    
    def _calculate_nutrition_stats_sync(self, date_range: Dict[str, str]) -> str:
        """Synchronous nutrition stats calculation"""
        try:
            # This would contain the actual stats calculation logic
            logger.info(f"Calculating nutrition stats for {date_range}")
            return f"sync_stats_{datetime.now().timestamp()}"
        except Exception as e:
            logger.error(f"Stats calculation error: {e}")
            raise
    
    def _export_data_sync(self, export_format: str) -> str:
        """Synchronous data export"""
        try:
            logger.info(f"Exporting data in {export_format} format")
            return f"sync_export_{datetime.now().timestamp()}"
        except Exception as e:
            logger.error(f"Export error: {e}")
            raise
    
    def _cleanup_old_logs_sync(self, days: int) -> str:
        """Synchronous log cleanup"""
        try:
            logger.info(f"Cleaning up logs older than {days} days")
            return f"sync_cleanup_{datetime.now().timestamp()}"
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            raise

# Global task manager instance
task_manager = TaskManager()

# Celery tasks (only if Celery is available)
if CELERY_AVAILABLE and celery_app:

    @celery_app.task(bind=True)
    def backup_database_task(self, backup_path: str = None):
        """Celery task for database backup"""
        try:
            self.update_state(state='PROGRESS', meta={'progress': 10})
            
            import sqlite3
            import shutil
            from datetime import datetime
            
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"backups/nutrition_{timestamp}.db"
            
            self.update_state(state='PROGRESS', meta={'progress': 50})
            
            shutil.copy2(Config.DATABASE, backup_path)
            
            self.update_state(state='PROGRESS', meta={'progress': 100})
            logger.info(f"Database backed up to {backup_path}")
            
            return {'status': 'success', 'backup_path': backup_path}
        except Exception as e:
            logger.error(f"Backup task error: {e}")
            self.update_state(state='FAILURE', meta={'error': str(e)})
            raise

    @celery_app.task(bind=True)
    def optimize_database_task(self):
        """Celery task for database optimization"""
        try:
            self.update_state(state='PROGRESS', meta={'progress': 10})
            
            import sqlite3
            
            self.update_state(state='PROGRESS', meta={'progress': 50})
            
            conn = sqlite3.connect(Config.DATABASE)
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
            conn.close()
            
            self.update_state(state='PROGRESS', meta={'progress': 100})
            logger.info("Database optimized")
            
            return {'status': 'success', 'message': 'Database optimized'}
        except Exception as e:
            logger.error(f"Optimization task error: {e}")
            self.update_state(state='FAILURE', meta={'error': str(e)})
            raise

    @celery_app.task(bind=True)
    def calculate_nutrition_stats_task(self, date_range: Dict[str, str]):
        """Celery task for nutrition stats calculation"""
        try:
            self.update_state(state='PROGRESS', meta={'progress': 10})
            
            # Simulate stats calculation
            import time
            time.sleep(2)  # Simulate work
            
            self.update_state(state='PROGRESS', meta={'progress': 50})
            
            # Actual stats calculation would go here
            stats = {
                'total_calories': 2000,
                'avg_protein': 150,
                'avg_carbs': 200,
                'avg_fat': 80
            }
            
            self.update_state(state='PROGRESS', meta={'progress': 100})
            logger.info(f"Nutrition stats calculated for {date_range}")
            
            return {'status': 'success', 'stats': stats}
        except Exception as e:
            logger.error(f"Stats calculation task error: {e}")
            self.update_state(state='FAILURE', meta={'error': str(e)})
            raise

    @celery_app.task(bind=True)
    def export_data_task(self, export_format: str = 'json'):
        """Celery task for data export"""
        try:
            self.update_state(state='PROGRESS', meta={'progress': 10})
            
            # Simulate export process
            import time
            time.sleep(3)  # Simulate work
            
            self.update_state(state='PROGRESS', meta={'progress': 50})
            
            # Actual export logic would go here
            export_path = f"exports/nutrition_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            
            self.update_state(state='PROGRESS', meta={'progress': 100})
            logger.info(f"Data exported in {export_format} format")
            
            return {'status': 'success', 'export_path': export_path}
        except Exception as e:
            logger.error(f"Export task error: {e}")
            self.update_state(state='FAILURE', meta={'error': str(e)})
            raise

    @celery_app.task(bind=True)
    def cleanup_old_logs_task(self, days: int = 30):
        """Celery task for log cleanup"""
        try:
            self.update_state(state='PROGRESS', meta={'progress': 10})
            
            # Simulate cleanup process
            import time
            time.sleep(1)  # Simulate work
            
            self.update_state(state='PROGRESS', meta={'progress': 50})
            
            # Actual cleanup logic would go here
            cleaned_files = 5  # Simulated
            
            self.update_state(state='PROGRESS', meta={'progress': 100})
            logger.info(f"Cleaned up logs older than {days} days")
            
            return {'status': 'success', 'cleaned_files': cleaned_files}
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
            self.update_state(state='FAILURE', meta={'error': str(e)})
            raise

    @celery_app.task(bind=True)
    def send_notification_task(self, user_id: int, message: str, notification_type: str = 'info'):
        """Celery task for sending notifications"""
        try:
            self.update_state(state='PROGRESS', meta={'progress': 10})
            
            # Simulate notification sending
            import time
            time.sleep(0.5)  # Simulate work
            
            self.update_state(state='PROGRESS', meta={'progress': 100})
            logger.info(f"Notification sent to user {user_id}: {message}")
            
            return {'status': 'success', 'message': 'Notification sent'}
        except Exception as e:
            logger.error(f"Notification task error: {e}")
            self.update_state(state='FAILURE', meta={'error': str(e)})
            raise
