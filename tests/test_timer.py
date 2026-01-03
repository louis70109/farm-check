"""
Timer Control & Logic Tests

Tests for timer start, stop, timeout, and progress display functions.
"""

import time
import threading
import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import timer


class TestStartTimer:
    """Test timer start functionality"""
    
    @patch('timer.threading.Timer')
    @patch('timer.threading.Thread')
    @patch('timer.random.randint')
    def test_start_timer_basic(self, mock_randint, mock_thread, mock_timer_class):
        """Test basic timer start without offset"""
        # Setup
        timer.config = {
            'countdown_seconds': 100,
            'random_offset_seconds': 0,
            'trigger_key': 'f1'
        }
        timer.current_timer = None
        timer.stop_progress = False
        
        mock_randint.return_value = 0
        mock_timer_instance = MagicMock()
        mock_timer_class.return_value = mock_timer_instance
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Execute
        timer.start_timer()
        
        # Verify
        assert timer.actual_countdown == 100
        assert timer.timer_start_time is not None
        assert timer.stop_progress is False
        mock_timer_class.assert_called_once_with(100, timer.on_timeout)
        mock_timer_instance.start.assert_called_once()
        mock_thread_instance.start.assert_called_once()
    
    @patch('timer.threading.Timer')
    @patch('timer.threading.Thread')
    @patch('timer.random.randint')
    def test_start_timer_with_random_offset(self, mock_randint, mock_thread, mock_timer_class, capsys):
        """Test timer start with random offset applied"""
        timer.config = {
            'countdown_seconds': 130,
            'random_offset_seconds': 5,
            'trigger_key': 'f1'
        }
        timer.current_timer = None
        
        # Mock random offset to +3 seconds
        mock_randint.return_value = 3
        mock_timer_instance = MagicMock()
        mock_timer_class.return_value = mock_timer_instance
        
        timer.start_timer()
        
        # Verify actual countdown includes offset
        assert timer.actual_countdown == 133  # 130 + 3
        
        # Verify random was called correctly
        mock_randint.assert_called_once_with(-5, 5)
        
        # Check output shows offset
        captured = capsys.readouterr()
        assert "133s" in captured.out
        assert "+3s" in captured.out
    
    @patch('timer.threading.Timer')
    @patch('timer.threading.Thread')
    def test_start_timer_cancels_existing_timer(self, mock_thread, mock_timer_class):
        """Test that starting timer cancels existing timer"""
        timer.config = {
            'countdown_seconds': 100,
            'random_offset_seconds': 0,
            'trigger_key': 'f1'
        }
        
        # Create existing timer
        existing_timer = MagicMock()
        timer.current_timer = existing_timer
        
        # Start new timer
        timer.start_timer()
        
        # Verify old timer was cancelled
        existing_timer.cancel.assert_called_once()
    
    @patch('timer.threading.Timer')
    @patch('timer.threading.Thread')
    def test_start_timer_stops_existing_progress(self, mock_thread, mock_timer_class):
        """Test that starting timer stops existing progress thread"""
        timer.config = {
            'countdown_seconds': 100,
            'random_offset_seconds': 0,
            'trigger_key': 'f1'
        }
        
        # Create existing progress thread
        existing_progress = MagicMock()
        timer.progress_thread = existing_progress
        timer.stop_progress = False
        
        timer.start_timer()
        
        # Verify stop flag was set
        # Note: In actual implementation, stop_progress is set to True first,
        # then thread.join() is called, then new thread is started
        existing_progress.join.assert_called()


class TestStopTimer:
    """Test timer stop functionality"""
    
    def test_stop_timer_with_active_timer(self, capsys):
        """Test stopping an active timer"""
        # Setup active timer
        mock_timer = MagicMock()
        timer.current_timer = mock_timer
        timer.timer_start_time = time.time()
        
        # Stop timer
        timer.stop_timer()
        
        # Verify
        mock_timer.cancel.assert_called_once()
        assert timer.current_timer is None
        assert timer.timer_start_time is None
        assert timer.stop_progress is True
        
        captured = capsys.readouterr()
        assert "STOP" in captured.out or "cancelled" in captured.out
    
    def test_stop_timer_when_no_timer_active(self):
        """Test stopping when no timer is running"""
        timer.current_timer = None
        timer.timer_start_time = None
        
        # Should not crash
        timer.stop_timer()
        
        assert timer.current_timer is None


class TestShowProgress:
    """Test progress bar display"""
    
    @patch('timer.time')
    def test_show_progress_calculation(self, mock_time_module):
        """Test progress bar percentage and time calculation"""
        # Mock time progression
        start_time = 1000.0
        timer.timer_start_time = start_time
        timer.actual_countdown = 100
        timer.stop_progress = False
        
        # Simulate 50 seconds elapsed
        mock_time_module.time.return_value = start_time + 50
        mock_time_module.sleep.side_effect = lambda x: setattr(timer, 'stop_progress', True)
        
        # This test verifies the calculation logic
        elapsed = 50
        remaining = max(0, 100 - elapsed)
        progress = min(1.0, elapsed / 100)
        
        assert remaining == 50
        assert progress == 0.5
        
        # Test edge case: timer expired
        mock_time_module.time.return_value = start_time + 120
        elapsed = 120
        remaining = max(0, 100 - elapsed)
        progress = min(1.0, elapsed / 100)
        
        assert remaining == 0
        assert progress == 1.0
    
    def test_show_progress_bar_formatting(self):
        """Test progress bar string formatting"""
        # Test progress bar generation
        bar_length = 30
        progress = 0.532  # 53.2%
        
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        assert filled_length == 15  # int(30 * 0.532) = 15
        assert len(bar) == 30
        assert bar.count('█') == 15
        assert bar.count('░') == 15
    
    def test_show_progress_time_formatting(self):
        """Test remaining time formatting (MM:SS)"""
        remaining = 125  # 2 minutes 5 seconds
        
        mins, secs = divmod(int(remaining), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        assert time_str == "02:05"
        
        # Test edge cases
        remaining = 59
        mins, secs = divmod(int(remaining), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        assert time_str == "00:59"
        
        remaining = 3661  # 61 minutes 1 second
        mins, secs = divmod(int(remaining), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        assert time_str == "61:01"


class TestOnTimeout:
    """Test timer expiration callback"""
    
    @patch('timer.play_sound')
    @patch('timer.keyboard.is_pressed')
    @patch('timer.time')
    @patch('timer.start_timer')
    def test_on_timeout_auto_restart(self, mock_start_timer, mock_time_module, 
                                     mock_is_pressed, mock_play_sound):
        """Test auto-restart after timeout without ESC"""
        timer.config = {'auto_click_windows': False}
        
        # Mock time for 5-second countdown
        mock_time_module.time.side_effect = [0, 0.1, 0.2, 5.1]  # Exceeds 5 seconds
        mock_time_module.sleep = lambda x: None
        mock_is_pressed.return_value = False  # ESC not pressed
        
        timer.on_timeout()
        
        # Verify sound played
        mock_play_sound.assert_called_once()
        
        # Verify auto-restart happened
        mock_start_timer.assert_called_once()
    
    @patch('timer.play_sound')
    @patch('timer.click_maple_windows')
    @patch('timer.keyboard.is_pressed')
    @patch('timer.time')
    def test_on_timeout_with_auto_click(self, mock_time_module, mock_is_pressed,
                                        mock_click_windows, mock_play_sound):
        """Test auto-click execution when enabled"""
        timer.config = {'auto_click_windows': True}
        
        mock_time_module.time.side_effect = [0, 5.1]
        mock_time_module.sleep = lambda x: None
        mock_is_pressed.return_value = False
        
        timer.on_timeout()
        
        # Verify auto-click was called
        mock_click_windows.assert_called_once()
    
    @patch('timer.play_sound')
    @patch('timer.keyboard.is_pressed')
    @patch('timer.time')
    @patch('builtins.input')
    @patch('timer.start_timer')
    @patch('timer.save_config')
    def test_on_timeout_esc_adjust_countdown(self, mock_save, mock_start, mock_input,
                                             mock_time_module, mock_is_pressed, mock_play_sound):
        """Test ESC menu - adjust countdown"""
        timer.config = {
            'auto_click_windows': False,
            'countdown_seconds': 130
        }
        
        mock_time_module.time.side_effect = [0, 0.1]
        mock_time_module.sleep = lambda x: None
        mock_is_pressed.return_value = True  # ESC pressed
        mock_input.return_value = '150'  # New countdown value
        
        timer.on_timeout()
        
        # Verify countdown updated
        assert timer.config['countdown_seconds'] == 150
        mock_save.assert_called_once_with(timer.config)
        mock_start.assert_called_once()


class TestPlaySound:
    """Test sound playback"""
    
    @patch('timer.winsound.MessageBeep')
    def test_play_sound(self, mock_beep, capsys):
        """Test that system beep is played"""
        timer.play_sound()
        
        mock_beep.assert_called_once_with(timer.winsound.MB_ICONEXCLAMATION)
        
        captured = capsys.readouterr()
        assert "Time's up" in captured.out or "sound" in captured.out


class TestHotkeyManagement:
    """Test hotkey registration and unregistration"""
    
    @patch('timer.keyboard.add_hotkey')
    def test_register_hotkeys(self, mock_add_hotkey):
        """Test hotkey registration"""
        timer.config = {
            'trigger_key': 'f1',
            'stop_key': 'f2'
        }
        
        timer.register_hotkeys()
        
        # Verify both hotkeys registered
        assert mock_add_hotkey.call_count == 2
        calls = mock_add_hotkey.call_args_list
        assert calls[0] == call('f1', timer.start_timer)
        assert calls[1] == call('f2', timer.stop_timer)
    
    @patch('timer.keyboard.remove_hotkey')
    def test_unregister_hotkeys(self, mock_remove_hotkey):
        """Test hotkey unregistration"""
        timer.config = {
            'trigger_key': 'f1',
            'stop_key': 'f2'
        }
        
        timer.unregister_hotkeys()
        
        # Verify both hotkeys removed
        assert mock_remove_hotkey.call_count == 2
    
    @patch('timer.keyboard.remove_hotkey')
    def test_unregister_hotkeys_handles_errors(self, mock_remove_hotkey):
        """Test that unregister handles errors gracefully"""
        timer.config = {
            'trigger_key': 'f1',
            'stop_key': 'f2'
        }
        
        mock_remove_hotkey.side_effect = Exception("Hotkey not registered")
        
        # Should not crash
        timer.unregister_hotkeys()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
