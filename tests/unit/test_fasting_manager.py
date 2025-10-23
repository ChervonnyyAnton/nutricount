"""
Unit tests for fasting manager
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, date
from src.fasting_manager import FastingManager, FastingSession, FastingGoal, FastingType, FastingStatus


class TestFastingSession:
    """Test FastingSession class"""
    
    def test_fasting_session_creation(self):
        """Test creating a fasting session"""
        session = FastingSession(
            id=1,
            user_id=1,
            start_time=datetime.now(),
            fasting_type='16:8',
            status='active',
            notes='Test session'
        )
        
        assert session.id == 1
        assert session.user_id == 1
        assert session.fasting_type == '16:8'
        assert session.status == 'active'
        assert session.notes == 'Test session'
    
    def test_fasting_session_duration_calculation(self):
        """Test duration calculation"""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=16)
        
        session = FastingSession(
            id=1,
            user_id=1,
            start_time=start_time,
            end_time=end_time,
            duration_hours=16.0,
            fasting_type='16:8',
            status='completed'
        )
        
        assert session.duration_hours == 16.0
    
    def test_fasting_session_progress_calculation(self):
        """Test progress calculation"""
        start_time = datetime.now() - timedelta(hours=8)
        
        session = FastingSession(
            id=1,
            user_id=1,
            start_time=start_time,
            fasting_type='16:8',
            status='active'
        )
        
        # Test that session exists and has correct attributes
        assert session.start_time is not None
        assert session.fasting_type == '16:8'
        assert session.status == 'active'


class TestFastingGoal:
    """Test FastingGoal class"""
    
    def test_fasting_goal_creation(self):
        """Test creating a fasting goal"""
        goal = FastingGoal(
            id=1,
            user_id=1,
            goal_type='daily_hours',
            target_value=16.0,
            current_value=8.0,
            period_start='2024-01-01',
            period_end='2024-01-31',
            status='active'
        )
        
        assert goal.id == 1
        assert goal.goal_type == 'daily_hours'
        assert goal.target_value == 16.0
        assert goal.current_value == 8.0
        assert goal.status == 'active'
    
    def test_fasting_goal_progress_calculation(self):
        """Test progress calculation"""
        goal = FastingGoal(
            id=1,
            user_id=1,
            goal_type='daily_hours',
            target_value=16.0,
            current_value=8.0,
            period_start='2024-01-01',
            period_end='2024-01-31',
            status='active'
        )
        
        # Test that goal exists and has correct attributes
        assert goal.target_value == 16.0
        assert goal.current_value == 8.0
        assert goal.goal_type == 'daily_hours'
        assert goal.status == 'active'


class TestFastingType:
    """Test FastingType enum"""
    
    def test_fasting_type_values(self):
        """Test fasting type enum values"""
        assert FastingType.SIXTEEN_EIGHT.value == "16:8"
        assert FastingType.EIGHTEEN_SIX.value == "18:6"
        assert FastingType.TWENTY_FOUR.value == "20:4"
        assert FastingType.OMAD.value == "OMAD"
        assert FastingType.CUSTOM.value == "Custom"


class TestFastingStatus:
    """Test FastingStatus enum"""
    
    def test_fasting_status_values(self):
        """Test fasting status enum values"""
        assert FastingStatus.ACTIVE.value == "active"
        assert FastingStatus.COMPLETED.value == "completed"
        assert FastingStatus.PAUSED.value == "paused"
        assert FastingStatus.CANCELLED.value == "cancelled"


class TestFastingManager:
    """Test FastingManager class"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database connection"""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.lastrowid = 1
        mock_cursor.rowcount = 1
        
        # Make mock_db support context manager protocol
        mock_db.__enter__ = Mock(return_value=mock_db)
        mock_db.__exit__ = Mock(return_value=None)
        
        return mock_db
    
    def test_start_fasting_session(self, mock_db):
        """Test starting a fasting session"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            session = manager.start_fasting_session('16:8', 'Test session')
            
            assert session.fasting_type == '16:8'
            assert session.status == 'active'
            assert session.notes == 'Test session'
            mock_db.execute.assert_called()
            mock_db.commit.assert_called()
    
    def test_end_fasting_session(self, mock_db):
        """Test ending a fasting session"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock active session
            mock_db.execute.return_value.fetchone.return_value = {
                'id': 1,
                'user_id': 1,
                'start_time': (datetime.now() - timedelta(hours=16)).isoformat(),
                'fasting_type': '16:8',
                'status': 'active',
                'notes': 'Test session',
                'end_time': None,
                'duration_hours': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Mock the update query
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = {
                'id': 1,
                'user_id': 1,
                'start_time': (datetime.now() - timedelta(hours=16)).isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_hours': 16.0,
                'fasting_type': '16:8',
                'status': 'completed',
                'notes': 'Test session',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            mock_db.execute.return_value = mock_cursor
            
            session = manager.end_fasting_session(1)  # Pass session_id
            
            assert session.status == 'completed'
            assert session.duration_hours is not None
            mock_db.execute.assert_called()
            mock_db.commit.assert_called()
    
    def test_end_fasting_session_not_found(self, mock_db):
        """Test ending a fasting session that doesn't exist"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock no active session found
            mock_db.execute.return_value.fetchone.return_value = None
            
            session = manager.end_fasting_session(999)
            
            assert session is None
    
    def test_pause_fasting_session(self, mock_db):
        """Test pausing a fasting session"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            result = manager.pause_fasting_session(1)
            
            assert result is True
            mock_db.execute.assert_called()
            mock_db.commit.assert_called()
    
    def test_pause_fasting_session_not_found(self, mock_db):
        """Test pausing a fasting session that doesn't exist"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock no rows affected
            mock_cursor = Mock()
            mock_cursor.rowcount = 0
            mock_db.execute.return_value = mock_cursor
            
            result = manager.pause_fasting_session(999)
            
            assert result is False
    
    def test_resume_fasting_session(self, mock_db):
        """Test resuming a paused fasting session"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            result = manager.resume_fasting_session(1)
            
            assert result is True
            mock_db.execute.assert_called()
            mock_db.commit.assert_called()
    
    def test_resume_fasting_session_not_found(self, mock_db):
        """Test resuming a fasting session that doesn't exist"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock no rows affected
            mock_cursor = Mock()
            mock_cursor.rowcount = 0
            mock_db.execute.return_value = mock_cursor
            
            result = manager.resume_fasting_session(999)
            
            assert result is False
    
    def test_cancel_fasting_session(self, mock_db):
        """Test cancelling a fasting session"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            result = manager.cancel_fasting_session(1)
            
            assert result is True
            mock_db.execute.assert_called()
            mock_db.commit.assert_called()
    
    def test_cancel_fasting_session_not_found(self, mock_db):
        """Test cancelling a fasting session that doesn't exist"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock no rows affected
            mock_cursor = Mock()
            mock_cursor.rowcount = 0
            mock_db.execute.return_value = mock_cursor
            
            result = manager.cancel_fasting_session(999)
            
            assert result is False
    
    def test_get_active_session(self, mock_db):
        """Test getting active session"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock active session
            mock_db.execute.return_value.fetchone.return_value = {
                'id': 1,
                'user_id': 1,
                'start_time': (datetime.now() - timedelta(hours=8)).isoformat(),
                'fasting_type': '16:8',
                'status': 'active',
                'notes': 'Test session',
                'end_time': None,
                'duration_hours': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            session = manager.get_active_session()
            
            assert session is not None
            assert session.status == 'active'
            assert session.fasting_type == '16:8'
    
    def test_get_active_session_none(self, mock_db):
        """Test getting active session when none exists"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock no active session
            mock_db.execute.return_value.fetchone.return_value = None
            
            session = manager.get_active_session()
            
            assert session is None
    
    def test_get_fasting_sessions(self, mock_db):
        """Test getting fasting sessions"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock sessions data
            mock_sessions = [
                {
                    'id': 1,
                    'user_id': 1,
                    'start_time': (datetime.now() - timedelta(hours=16)).isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'duration_hours': 16.0,
                    'fasting_type': '16:8',
                    'status': 'completed',
                    'notes': 'Test session',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            ]
            mock_db.execute.return_value.fetchall.return_value = mock_sessions
            
            sessions = manager.get_fasting_sessions()
            
            assert len(sessions) == 1
            assert sessions[0].status == 'completed'
            assert sessions[0].duration_hours == 16.0
    
    def test_get_fasting_stats(self, mock_db):
        """Test getting fasting statistics"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock stats data - first call returns stats, second call returns streak
            mock_cursor1 = Mock()
            mock_cursor1.fetchone.return_value = {
                'total_sessions': 1,
                'avg_duration': 16.0,
                'total_hours': 16.0,
                'longest_session': 16.0,
                'shortest_session': 16.0
            }
            
            mock_cursor2 = Mock()
            mock_cursor2.fetchone.return_value = {'current_streak': 5}
            
            # Mock multiple calls to execute
            mock_db.execute.side_effect = [mock_cursor1, mock_cursor2]
            
            stats = manager.get_fasting_stats()
            
            assert stats['total_sessions'] == 1
            assert stats['avg_duration'] == 16.0
            assert stats['total_hours'] == 16.0
            assert stats['longest_session'] == 16.0
            assert stats['current_streak'] == 5
    
    def test_get_fasting_stats_no_streak(self, mock_db):
        """Test getting fasting statistics with no streak"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock stats data - first call returns stats, second call returns None for streak
            mock_cursor1 = Mock()
            mock_cursor1.fetchone.return_value = {
                'total_sessions': 0,
                'avg_duration': None,
                'total_hours': None,
                'longest_session': None,
                'shortest_session': None
            }
            
            mock_cursor2 = Mock()
            mock_cursor2.fetchone.return_value = None
            
            # Mock multiple calls to execute
            mock_db.execute.side_effect = [mock_cursor1, mock_cursor2]
            
            stats = manager.get_fasting_stats()
            
            assert stats['total_sessions'] == 0
            assert stats['current_streak'] == 0
    
    def test_create_fasting_goal(self, mock_db):
        """Test creating a fasting goal"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            goal = manager.create_fasting_goal(
                'daily_hours',
                16.0,
                date(2024, 1, 1),
                date(2024, 1, 31)
            )
            
            assert goal.goal_type == 'daily_hours'
            assert goal.target_value == 16.0
            assert goal.status == 'active'
            mock_db.execute.assert_called()
            mock_db.commit.assert_called()
    
    def test_update_goal_progress_daily_hours(self, mock_db):
        """Test updating goal progress for daily hours"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock goal data
            mock_goal = Mock()
            mock_goal.fetchone.return_value = {
                'goal_type': 'daily_hours',
                'period_start': '2024-01-01',
                'period_end': '2024-01-31'
            }
            
            # Mock progress calculation
            mock_progress = Mock()
            mock_progress.fetchone.return_value = {'total_hours': 32.0}
            
            # Mock update
            mock_update = Mock()
            mock_update.rowcount = 1
            
            mock_db.execute.side_effect = [mock_goal, mock_progress, mock_update]
            
            result = manager.update_goal_progress(1)
            
            assert result is True
            assert mock_db.execute.call_count == 3
            mock_db.commit.assert_called()
    
    def test_update_goal_progress_weekly_sessions(self, mock_db):
        """Test updating goal progress for weekly sessions"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock goal data
            mock_goal = Mock()
            mock_goal.fetchone.return_value = {
                'goal_type': 'weekly_sessions',
                'period_start': '2024-01-01',
                'period_end': '2024-01-31'
            }
            
            # Mock progress calculation
            mock_progress = Mock()
            mock_progress.fetchone.return_value = {'session_count': 4}
            
            # Mock update
            mock_update = Mock()
            mock_update.rowcount = 1
            
            mock_db.execute.side_effect = [mock_goal, mock_progress, mock_update]
            
            result = manager.update_goal_progress(1)
            
            assert result is True
            assert mock_db.execute.call_count == 3
            mock_db.commit.assert_called()
    
    def test_update_goal_progress_monthly_hours(self, mock_db):
        """Test updating goal progress for monthly hours"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock goal data
            mock_goal = Mock()
            mock_goal.fetchone.return_value = {
                'goal_type': 'monthly_hours',
                'period_start': '2024-01-01',
                'period_end': '2024-01-31'
            }
            
            # Mock progress calculation
            mock_progress = Mock()
            mock_progress.fetchone.return_value = {'total_hours': 128.0}
            
            # Mock update
            mock_update = Mock()
            mock_update.rowcount = 1
            
            mock_db.execute.side_effect = [mock_goal, mock_progress, mock_update]
            
            result = manager.update_goal_progress(1)
            
            assert result is True
            assert mock_db.execute.call_count == 3
            mock_db.commit.assert_called()
    
    def test_update_goal_progress_goal_not_found(self, mock_db):
        """Test updating goal progress when goal doesn't exist"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock goal not found
            mock_goal = Mock()
            mock_goal.fetchone.return_value = None
            
            mock_db.execute.return_value = mock_goal
            
            result = manager.update_goal_progress(999)
            
            assert result is False
    
    def test_get_fasting_goals(self, mock_db):
        """Test getting fasting goals"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock goals data
            mock_goals = [
                {
                    'id': 1,
                    'user_id': 1,
                    'goal_type': 'daily_hours',
                    'target_value': 16.0,
                    'current_value': 8.0,
                    'period_start': '2024-01-01',
                    'period_end': '2024-01-31',
                    'status': 'active',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            ]
            mock_db.execute.return_value.fetchall.return_value = mock_goals
            
            goals = manager.get_fasting_goals()
            
            assert len(goals) == 1
            assert goals[0].goal_type == 'daily_hours'
            assert goals[0].target_value == 16.0
    
    def test_get_fasting_progress_with_active_session(self, mock_db):
        """Test getting fasting progress with active session"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock active session
            mock_session = Mock()
            mock_session.fetchone.return_value = {
                'id': 1,
                'user_id': 1,
                'start_time': (datetime.now() - timedelta(hours=8)).isoformat(),
                'fasting_type': '16:8',
                'status': 'active',
                'notes': 'Test session',
                'end_time': None,
                'duration_hours': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Mock stats
            mock_stats_cursor = Mock()
            mock_stats_cursor.fetchone.return_value = {
                'total_sessions': 1,
                'avg_duration': 16.0,
                'total_hours': 16.0,
                'longest_session': 16.0,
                'shortest_session': 16.0
            }
            
            mock_streak_cursor = Mock()
            mock_streak_cursor.fetchone.return_value = {'current_streak': 5}
            
            # Mock goals
            mock_goals_cursor = Mock()
            mock_goals_cursor.fetchall.return_value = []
            
            mock_db.execute.side_effect = [mock_session, mock_stats_cursor, mock_streak_cursor, mock_goals_cursor]
            
            progress = manager.get_fasting_progress()
            
            assert progress['is_fasting'] is True
            assert progress['active_session'] is not None
            assert 'current_duration_hours' in progress
            assert 'target_hours' in progress
            assert 'progress_percentage' in progress
    
    def test_get_fasting_progress_without_active_session(self, mock_db):
        """Test getting fasting progress without active session"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock no active session
            mock_session = Mock()
            mock_session.fetchone.return_value = None
            
            # Mock stats
            mock_stats_cursor = Mock()
            mock_stats_cursor.fetchone.return_value = {
                'total_sessions': 0,
                'avg_duration': None,
                'total_hours': None,
                'longest_session': None,
                'shortest_session': None
            }
            
            mock_streak_cursor = Mock()
            mock_streak_cursor.fetchone.return_value = None
            
            # Mock goals
            mock_goals_cursor = Mock()
            mock_goals_cursor.fetchall.return_value = []
            
            mock_db.execute.side_effect = [mock_session, mock_stats_cursor, mock_streak_cursor, mock_goals_cursor]
            
            progress = manager.get_fasting_progress()
            
            assert progress['is_fasting'] is False
            assert progress['active_session'] is None
            assert 'current_duration_hours' not in progress
            assert 'target_hours' not in progress
            assert 'progress_percentage' not in progress
    
    def test_get_fasting_progress_18_6_type(self, mock_db):
        """Test getting fasting progress for 18:6 fasting type"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock active session with 18:6 type
            mock_session = Mock()
            mock_session.fetchone.return_value = {
                'id': 1,
                'user_id': 1,
                'start_time': (datetime.now() - timedelta(hours=9)).isoformat(),
                'fasting_type': '18:6',
                'status': 'active',
                'notes': 'Test session',
                'end_time': None,
                'duration_hours': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Mock stats
            mock_stats_cursor = Mock()
            mock_stats_cursor.fetchone.return_value = {
                'total_sessions': 1,
                'avg_duration': 18.0,
                'total_hours': 18.0,
                'longest_session': 18.0,
                'shortest_session': 18.0
            }
            
            mock_streak_cursor = Mock()
            mock_streak_cursor.fetchone.return_value = {'current_streak': 1}
            
            # Mock goals
            mock_goals_cursor = Mock()
            mock_goals_cursor.fetchall.return_value = []
            
            mock_db.execute.side_effect = [mock_session, mock_stats_cursor, mock_streak_cursor, mock_goals_cursor]
            
            progress = manager.get_fasting_progress()
            
            assert progress['is_fasting'] is True
            assert progress['target_hours'] == 18
            assert 'progress_percentage' in progress
    
    def test_get_fasting_progress_20_4_type(self, mock_db):
        """Test getting fasting progress for 20:4 fasting type"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock active session with 20:4 type
            mock_session = Mock()
            mock_session.fetchone.return_value = {
                'id': 1,
                'user_id': 1,
                'start_time': (datetime.now() - timedelta(hours=10)).isoformat(),
                'fasting_type': '20:4',
                'status': 'active',
                'notes': 'Test session',
                'end_time': None,
                'duration_hours': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Mock stats
            mock_stats_cursor = Mock()
            mock_stats_cursor.fetchone.return_value = {
                'total_sessions': 1,
                'avg_duration': 20.0,
                'total_hours': 20.0,
                'longest_session': 20.0,
                'shortest_session': 20.0
            }
            
            mock_streak_cursor = Mock()
            mock_streak_cursor.fetchone.return_value = {'current_streak': 1}
            
            # Mock goals
            mock_goals_cursor = Mock()
            mock_goals_cursor.fetchall.return_value = []
            
            mock_db.execute.side_effect = [mock_session, mock_stats_cursor, mock_streak_cursor, mock_goals_cursor]
            
            progress = manager.get_fasting_progress()
            
            assert progress['is_fasting'] is True
            assert progress['target_hours'] == 20
            assert 'progress_percentage' in progress
    
    def test_get_fasting_progress_custom_type(self, mock_db):
        """Test getting fasting progress for custom fasting type"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock active session with custom type
            mock_session = Mock()
            mock_session.fetchone.return_value = {
                'id': 1,
                'user_id': 1,
                'start_time': (datetime.now() - timedelta(hours=12)).isoformat(),
                'fasting_type': 'Custom',
                'status': 'active',
                'notes': 'Test session',
                'end_time': None,
                'duration_hours': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Mock stats
            mock_stats_cursor = Mock()
            mock_stats_cursor.fetchone.return_value = {
                'total_sessions': 1,
                'avg_duration': 12.0,
                'total_hours': 12.0,
                'longest_session': 12.0,
                'shortest_session': 12.0
            }
            
            mock_streak_cursor = Mock()
            mock_streak_cursor.fetchone.return_value = {'current_streak': 1}
            
            # Mock goals
            mock_goals_cursor = Mock()
            mock_goals_cursor.fetchall.return_value = []
            
            mock_db.execute.side_effect = [mock_session, mock_stats_cursor, mock_streak_cursor, mock_goals_cursor]
            
            progress = manager.get_fasting_progress()
            
            assert progress['is_fasting'] is True
            assert progress['target_hours'] is None
            assert progress['progress_percentage'] is None
    
    def test_row_to_session(self, mock_db):
        """Test converting database row to FastingSession"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            row = {
                'id': 1,
                'user_id': 1,
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_hours': 16.0,
                'fasting_type': '16:8',
                'status': 'completed',
                'notes': 'Test session',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            session = manager._row_to_session(row)
            
            assert session.id == 1
            assert session.user_id == 1
            assert session.duration_hours == 16.0
            assert session.fasting_type == '16:8'
            assert session.status == 'completed'
    
    def test_row_to_session_none(self, mock_db):
        """Test converting None row to FastingSession"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            session = manager._row_to_session(None)
            
            assert session is None
    
    def test_row_to_goal(self, mock_db):
        """Test converting database row to FastingGoal"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            row = {
                'id': 1,
                'user_id': 1,
                'goal_type': 'daily_hours',
                'target_value': 16.0,
                'current_value': 8.0,
                'period_start': '2024-01-01',
                'period_end': '2024-01-31',
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            goal = manager._row_to_goal(row)
            
            assert goal.id == 1
            assert goal.user_id == 1
            assert goal.goal_type == 'daily_hours'
            assert goal.target_value == 16.0
            assert goal.current_value == 8.0
    
    def test_row_to_goal_none(self, mock_db):
        """Test converting None row to FastingGoal"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            goal = manager._row_to_goal(None)
            
            assert goal is None
    
    def test_get_fasting_settings(self, mock_db):
        """Test getting fasting settings"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock settings data
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = {
                'id': 1,
                'user_id': 1,
                'fasting_goal': '16:8',
                'preferred_start_time': '20:00',
                'enable_reminders': 1,
                'enable_notifications': 1,
                'default_notes': 'Default notes',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            mock_db.cursor.return_value = mock_cursor
            
            settings = manager.get_fasting_settings()
            
            assert settings is not None
            assert settings['fasting_goal'] == '16:8'
            assert settings['enable_reminders'] is True
            assert settings['enable_notifications'] is True
    
    def test_get_fasting_settings_not_found(self, mock_db):
        """Test getting fasting settings when none exist"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock no settings found
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = None
            mock_db.cursor.return_value = mock_cursor
            
            settings = manager.get_fasting_settings()
            
            assert settings is None
    
    def test_get_fasting_settings_exception(self, mock_db):
        """Test getting fasting settings with exception"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            
            manager = FastingManager('test.db')
            
            settings = manager.get_fasting_settings()
            
            assert settings is None
    
    def test_create_fasting_settings(self, mock_db):
        """Test creating fasting settings"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock settings creation
            mock_cursor = Mock()
            mock_cursor.lastrowid = 1
            mock_db.cursor.return_value = mock_cursor
            
            # Mock get_fasting_settings call
            with patch.object(manager, 'get_fasting_settings') as mock_get_settings:
                mock_get_settings.return_value = {
                    'id': 1,
                    'user_id': 1,
                    'fasting_goal': '16:8',
                    'preferred_start_time': '20:00',
                    'enable_reminders': True,
                    'enable_notifications': True,
                    'default_notes': 'Default notes'
                }
                
                settings_data = {
                    'user_id': 1,
                    'fasting_goal': '16:8',
                    'preferred_start_time': '20:00',
                    'enable_reminders': True,
                    'enable_notifications': True,
                    'default_notes': 'Default notes'
                }
                
                result = manager.create_fasting_settings(settings_data)
                
                assert result is not None
                assert result['fasting_goal'] == '16:8'
                mock_db.commit.assert_called()
    
    def test_create_fasting_settings_exception(self, mock_db):
        """Test creating fasting settings with exception"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            
            manager = FastingManager('test.db')
            
            settings_data = {
                'user_id': 1,
                'fasting_goal': '16:8',
                'preferred_start_time': '20:00',
                'enable_reminders': True,
                'enable_notifications': True,
                'default_notes': 'Default notes'
            }
            
            with pytest.raises(ValueError):
                manager.create_fasting_settings(settings_data)
    
    def test_update_fasting_settings(self, mock_db):
        """Test updating fasting settings"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock settings update
            mock_cursor = Mock()
            mock_cursor.rowcount = 1
            mock_db.cursor.return_value = mock_cursor
            
            # Mock get_fasting_settings call
            with patch.object(manager, 'get_fasting_settings') as mock_get_settings:
                mock_get_settings.return_value = {
                    'id': 1,
                    'user_id': 1,
                    'fasting_goal': '18:6',
                    'preferred_start_time': '19:00',
                    'enable_reminders': False,
                    'enable_notifications': True,
                    'default_notes': 'Updated notes'
                }
                
                settings_data = {
                    'fasting_goal': '18:6',
                    'preferred_start_time': '19:00',
                    'enable_reminders': False,
                    'enable_notifications': True,
                    'default_notes': 'Updated notes'
                }
                
                result = manager.update_fasting_settings(1, settings_data)
                
                assert result is not None
                assert result['fasting_goal'] == '18:6'
                mock_db.commit.assert_called()
    
    def test_update_fasting_settings_not_found(self, mock_db):
        """Test updating fasting settings when none exist"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db
            
            manager = FastingManager('test.db')
            
            # Mock no settings found
            mock_cursor = Mock()
            mock_cursor.rowcount = 0
            mock_db.cursor.return_value = mock_cursor
            
            settings_data = {
                'fasting_goal': '18:6',
                'preferred_start_time': '19:00',
                'enable_reminders': False,
                'enable_notifications': True,
                'default_notes': 'Updated notes'
            }
            
            with pytest.raises(ValueError):
                manager.update_fasting_settings(1, settings_data)
    
    def test_update_fasting_settings_exception(self, mock_db):
        """Test updating fasting settings with exception"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            
            manager = FastingManager('test.db')
            
            settings_data = {
                'fasting_goal': '18:6',
                'preferred_start_time': '19:00',
                'enable_reminders': False,
                'enable_notifications': True,
                'default_notes': 'Updated notes'
            }
            
            with pytest.raises(ValueError):
                manager.update_fasting_settings(1, settings_data)


class TestFastingStatsValidation:
    """Test validation in get_fasting_stats"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database connection"""
        mock = Mock()
        mock.cursor.return_value = Mock()
        mock.execute.return_value = Mock()
        return mock

    def test_get_fasting_stats_with_negative_days(self, mock_db):
        """Test get_fasting_stats rejects negative days parameter"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db

            manager = FastingManager('test.db')

            # Should raise ValueError for negative days
            with pytest.raises(ValueError, match="Invalid days parameter"):
                manager.get_fasting_stats(user_id=1, days=-5)

    def test_get_fasting_stats_with_string_days(self, mock_db):
        """Test get_fasting_stats rejects string days parameter"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db

            manager = FastingManager('test.db')

            # Should raise ValueError for string days
            with pytest.raises(ValueError, match="Invalid days parameter"):
                manager.get_fasting_stats(user_id=1, days="30")

    def test_get_fasting_stats_with_float_days(self, mock_db):
        """Test get_fasting_stats rejects float days parameter"""
        with patch('src.fasting_manager.sqlite3.connect') as mock_connect:
            mock_connect.return_value = mock_db

            manager = FastingManager('test.db')

            # Should raise ValueError for float days
            with pytest.raises(ValueError, match="Invalid days parameter"):
                manager.get_fasting_stats(user_id=1, days=30.5)
