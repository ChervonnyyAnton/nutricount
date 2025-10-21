"""
Integration tests for metrics routes.
Tests for Prometheus metrics, metrics summary, and background tasks.
"""

from unittest.mock import patch


class TestMetricsRoutes:
    """Tests for metrics routes endpoints"""

    def test_prometheus_metrics_error(self, client, app):
        """Test GET /metrics with error (test lines 33-35)"""
        with patch("routes.metrics.system_monitor") as mock_monitor:
            # Make update_metrics raise an exception
            mock_monitor.update_metrics.side_effect = Exception("Test error")

            response = client.get("/metrics")

            # Should return 500 with error message
            assert response.status_code == 500
            assert b"Error getting metrics" in response.data

    def test_metrics_summary_error(self, client, app):
        """Test GET /api/metrics/summary with error (test lines 54-56)"""
        with patch("routes.metrics.metrics_collector") as mock_collector:
            # Make get_metrics_summary raise an exception
            mock_collector.get_metrics_summary.side_effect = Exception("Test error")

            response = client.get("/api/metrics/summary")

            # Should return 500 with error message
            assert response.status_code == 500
            data = response.json
            assert data["status"] == "error"

    def test_create_background_task_backup_success(self, client, app):
        """Test POST /api/tasks with backup task (test lines 88-90)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            mock_manager.backup_database.return_value = "test-task-id"

            task_data = {"task_type": "backup", "backup_path": "/tmp/test_backup.db"}

            response = client.post("/api/tasks", json=task_data)

            assert response.status_code == 201
            data = response.json
            assert data["status"] == "success"
            assert "task_id" in data["data"]
            assert data["data"]["task_type"] == "backup"
            mock_manager.backup_database.assert_called_once_with("/tmp/test_backup.db")

    def test_create_background_task_optimize_success(self, client, app):
        """Test POST /api/tasks with optimize task (test line 92)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            mock_manager.optimize_database.return_value = "test-task-id"

            task_data = {"task_type": "optimize"}

            response = client.post("/api/tasks", json=task_data)

            assert response.status_code == 201
            data = response.json
            assert data["status"] == "success"
            assert "task_id" in data["data"]
            assert data["data"]["task_type"] == "optimize"
            mock_manager.optimize_database.assert_called_once()

    def test_create_background_task_export_success(self, client, app):
        """Test POST /api/tasks with export task (test lines 94-95)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            mock_manager.export_data.return_value = "test-task-id"

            task_data = {"task_type": "export", "export_format": "csv"}

            response = client.post("/api/tasks", json=task_data)

            assert response.status_code == 201
            data = response.json
            assert data["status"] == "success"
            assert "task_id" in data["data"]
            assert data["data"]["task_type"] == "export"
            mock_manager.export_data.assert_called_once_with("csv")

    def test_create_background_task_export_default_format(self, client, app):
        """Test POST /api/tasks with export task and default format (test line 95)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            mock_manager.export_data.return_value = "test-task-id"

            task_data = {"task_type": "export"}  # No format specified

            response = client.post("/api/tasks", json=task_data)

            assert response.status_code == 201
            data = response.json
            assert data["status"] == "success"
            assert "task_id" in data["data"]
            mock_manager.export_data.assert_called_once_with("json")

    def test_create_background_task_cleanup_success(self, client, app):
        """Test POST /api/tasks with cleanup task (test lines 97-98)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            mock_manager.cleanup_old_logs.return_value = "test-task-id"

            task_data = {"task_type": "cleanup", "days": 60}

            response = client.post("/api/tasks", json=task_data)

            assert response.status_code == 201
            data = response.json
            assert data["status"] == "success"
            assert "task_id" in data["data"]
            assert data["data"]["task_type"] == "cleanup"
            mock_manager.cleanup_old_logs.assert_called_once_with(60)

    def test_create_background_task_cleanup_default_days(self, client, app):
        """Test POST /api/tasks with cleanup task and default days (test line 98)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            mock_manager.cleanup_old_logs.return_value = "test-task-id"

            task_data = {"task_type": "cleanup"}  # No days specified

            response = client.post("/api/tasks", json=task_data)

            assert response.status_code == 201
            data = response.json
            assert data["status"] == "success"
            assert "task_id" in data["data"]
            mock_manager.cleanup_old_logs.assert_called_once_with(30)

    def test_create_background_task_connection_error(self, client, app):
        """Test POST /api/tasks with connection error (test lines 133, 160)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            # Make task creation raise a Redis connection error
            mock_manager.backup_database.side_effect = Exception("redis connection refused")

            task_data = {"task_type": "backup"}
            response = client.post("/api/tasks", json=task_data)

            # Should return 500 with connection error message
            assert response.status_code == 500
            data = response.json
            assert data["status"] == "error"
            # Check for task service unavailable message
            assert "unavailable" in data["message"].lower() or "error" in data["message"].lower()

    def test_get_task_status_failure_with_not_found(self, client, app):
        """Test GET /api/tasks/<id> with FAILURE status (test line 153)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            # Mock task status with FAILURE and "not found" error
            mock_manager.get_task_status.return_value = {
                "status": "FAILURE",
                "error": "Task not found in backend",
            }

            response = client.get("/api/tasks/test-task-id")

            assert response.status_code == 404
            data = response.json
            assert data["status"] == "error"
            assert "not found" in data["message"].lower()

    def test_get_task_status_not_found_status(self, client, app):
        """Test GET /api/tasks/<id> with NOT_FOUND status (test line 160)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            # Mock task status with NOT_FOUND
            mock_manager.get_task_status.return_value = {"status": "NOT_FOUND"}

            response = client.get("/api/tasks/test-task-id")

            assert response.status_code == 404
            data = response.json
            assert data["status"] == "error"
            assert "not found" in data["message"].lower()

    def test_get_task_status_failure_status(self, client, app):
        """Test GET /api/tasks/<id> with FAILURE status (test lines 172-179)"""
        with patch("routes.metrics.task_manager") as mock_manager:
            # Mock task status with FAILURE (but without "not found" in error)
            mock_manager.get_task_status.return_value = {
                "status": "FAILURE",
                "error": "Some other error",
            }

            response = client.get("/api/tasks/test-task-id")

            # Should still return 404 as per the code logic
            assert response.status_code == 404
            data = response.json
            assert data["status"] == "error"

    def test_get_task_status_success(self, client, app):
        """Test GET /api/tasks/<id> with successful status"""
        with patch("routes.metrics.task_manager") as mock_manager:
            # Mock task status with SUCCESS
            mock_manager.get_task_status.return_value = {
                "status": "SUCCESS",
                "result": {"completed": True},
            }

            response = client.get("/api/tasks/test-task-id")

            assert response.status_code == 200
            data = response.json
            assert data["status"] == "success"
            assert data["data"]["status"] == "SUCCESS"

    def test_get_task_status_pending(self, client, app):
        """Test GET /api/tasks/<id> with PENDING status"""
        with patch("routes.metrics.task_manager") as mock_manager:
            # Mock task status with PENDING
            mock_manager.get_task_status.return_value = {"status": "PENDING"}

            response = client.get("/api/tasks/test-task-id")

            assert response.status_code == 200
            data = response.json
            assert data["status"] == "success"
            assert data["data"]["status"] == "PENDING"

    def test_get_task_status_exception(self, client, app):
        """Test GET /api/tasks/<id> with exception"""
        with patch("routes.metrics.task_manager") as mock_manager:
            # Make get_task_status raise an exception
            mock_manager.get_task_status.side_effect = Exception("Test error")

            response = client.get("/api/tasks/test-task-id")

            assert response.status_code == 500
            data = response.json
            assert data["status"] == "error"
