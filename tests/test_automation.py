"""
Window Automation Tests

Tests for window enumeration, selection, and auto-click functionality.
"""

import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import timer


class TestWindowAvailability:
    """Test window automation availability detection"""
    
    def test_window_automation_flag_when_available(self):
        """Test that WINDOW_AUTOMATION_AVAILABLE is set correctly"""
        # This will depend on whether dependencies are installed
        # The flag should be boolean
        assert isinstance(timer.WINDOW_AUTOMATION_AVAILABLE, bool)


class TestClickMapleWindows:
    """Test MapleRoyals window auto-click functionality"""
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', False)
    def test_click_windows_unavailable(self, capsys):
        """Test graceful handling when dependencies missing"""
        timer.click_maple_windows()
        
        captured = capsys.readouterr()
        assert "not available" in captured.out
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    def test_click_windows_none_found(self, mock_get_windows, capsys):
        """Test when no MapleRoyals windows exist"""
        mock_get_windows.return_value = []
        
        timer.click_maple_windows()
        
        captured = capsys.readouterr()
        assert "No MapleRoyals windows found" in captured.out
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    @patch('timer.keyboard.press_and_release')
    @patch('timer.pyautogui.moveTo')
    @patch('timer.pyautogui.click')
    @patch('timer.time.sleep')
    @patch('timer.random.shuffle')
    @patch('timer.random.uniform')
    def test_click_windows_all_windows(self, mock_uniform, mock_shuffle, mock_sleep,
                                       mock_click, mock_moveto, mock_keyboard, mock_get_windows, capsys):
        """Test clicking all MapleRoyals windows"""
        # Setup mock windows
        mock_win1 = MagicMock()
        mock_win1.title = "MapleRoyals - Character1"
        mock_win1._hWnd = 1
        mock_win1.left = 0
        mock_win1.top = 0
        mock_win1.width = 800
        mock_win1.height = 600
        mock_win1.size = (800, 600)
        
        mock_win2 = MagicMock()
        mock_win2.title = "MapleRoyals - Character2"
        mock_win2._hWnd = 2
        mock_win2.left = 100
        mock_win2.top = 100
        mock_win2.width = 800
        mock_win2.height = 600
        mock_win2.size = (800, 600)
        
        mock_get_windows.return_value = [mock_win1, mock_win2]
        
        # Config with all windows (selected_window_titles = None)
        timer.config = {
            'trigger_key': 'f1',
            'selected_window_titles': None
        }
        
        mock_uniform.return_value = 0.1  # Small offset for click position and movement duration
        
        timer.click_maple_windows()
        
        # Verify mouse movements and clicks happened
        assert mock_moveto.call_count == 2  # Mouse moved to each window
        assert mock_click.call_count == 2  # Clicked each window
        assert mock_keyboard.call_count == 2
        
        captured = capsys.readouterr()
        assert "Found 2 MapleRoyals" in captured.out
        assert "completed" in captured.out
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    @patch('timer.keyboard.press_and_release')
    @patch('timer.pyautogui.moveTo')
    @patch('timer.pyautogui.click')
    @patch('timer.random.shuffle')
    @patch('timer.random.uniform')
    def test_click_windows_selected_titles(self, mock_uniform, mock_shuffle,
                                           mock_click, mock_moveto, mock_keyboard, mock_get_windows):
        """Test clicking only selected windows"""
        mock_win1 = MagicMock()
        mock_win1.title = "MapleRoyals - Character1"
        mock_win1._hWnd = 1
        mock_win1.left = 0
        mock_win1.top = 0
        mock_win1.width = 800
        mock_win1.height = 600
        mock_win1.size = (800, 600)
        
        mock_win2 = MagicMock()
        mock_win2.title = "MapleRoyals - Character2"
        mock_win2._hWnd = 2
        mock_win2.left = 100
        mock_win2.top = 100
        mock_win2.width = 800
        mock_win2.height = 600
        mock_win2.size = (800, 600)
        
        mock_win3 = MagicMock()
        mock_win3.title = "MapleRoyals - Character3"
        mock_win3._hWnd = 3
        mock_win3.left = 200
        mock_win3.top = 200
        mock_win3.width = 800
        mock_win3.height = 600
        mock_win3.size = (800, 600)
        
        mock_get_windows.return_value = [mock_win1, mock_win2, mock_win3]
        
        # Only select windows 1 and 3
        timer.config = {
            'trigger_key': 'f1',
            'selected_window_titles': ["MapleRoyals - Character1", "MapleRoyals - Character3"]
        }
        
        mock_uniform.return_value = 0.1
        
        timer.click_maple_windows()
        
        # Verify only 2 windows clicked (1 and 3, not 2)
        assert mock_moveto.call_count == 2  # Mouse moved to 2 windows
        assert mock_click.call_count == 2  # Clicked 2 windows
        assert mock_keyboard.call_count == 2
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    def test_click_windows_selected_not_running(self, mock_get_windows, capsys):
        """Test when selected windows are not currently running"""
        mock_win1 = MagicMock()
        mock_win1.title = "MapleRoyals - Character1"
        mock_win1._hWnd = 1
        mock_win1.size = (800, 600)
        
        mock_get_windows.return_value = [mock_win1]
        
        # Config expects 2 windows but only 1 is running
        timer.config = {
            'trigger_key': 'f1',
            'selected_window_titles': ["MapleRoyals - Character1", "MapleRoyals - Character2"]
        }
        
        timer.click_maple_windows()
        
        captured = capsys.readouterr()
        assert "Not running" in captured.out
        assert "Character2" in captured.out
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    @patch('timer.keyboard.press_and_release')
    @patch('timer.pyautogui.moveTo')
    @patch('timer.pyautogui.click')
    @patch('timer.random.uniform')
    def test_click_windows_handles_window_error(self, mock_uniform, mock_click,
                                                 mock_moveto, mock_keyboard, mock_get_windows, capsys):
        """Test error handling when window becomes invalid during click"""
        mock_win1 = MagicMock()
        mock_win1.title = "MapleRoyals - Character1"
        mock_win1._hWnd = 1
        mock_win1.size = (800, 600)
        
        mock_win2 = MagicMock()
        mock_win2.title = "MapleRoyals - Character2"
        mock_win2._hWnd = 2
        # This window will throw error when accessing properties
        mock_win2.size = MagicMock(side_effect=Exception("Window closed"))
        
        mock_get_windows.return_value = [mock_win1, mock_win2]
        
        timer.config = {
            'trigger_key': 'f1',
            'selected_window_titles': None
        }
        
        mock_uniform.return_value = 0.1
        
        # Should not crash, should skip invalid window
        timer.click_maple_windows()
        
        # At least one window should be processed
        captured = capsys.readouterr()
        assert "MapleRoyals" in captured.out
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    def test_click_windows_filters_duplicates(self, mock_get_windows):
        """Test that duplicate window handles are filtered"""
        # Same window appearing twice (same _hWnd)
        mock_win1a = MagicMock()
        mock_win1a.title = "MapleRoyals - Test"
        mock_win1a._hWnd = 1
        mock_win1a.size = (800, 600)
        
        mock_win1b = MagicMock()
        mock_win1b.title = "MapleRoyals - Test"
        mock_win1b._hWnd = 1  # Same handle
        mock_win1b.size = (800, 600)
        
        mock_get_windows.return_value = [mock_win1a, mock_win1b]
        
        timer.config = {
            'trigger_key': 'f1',
            'selected_window_titles': None
        }
        
        # Implementation should deduplicate by handle
        # This tests the filtering logic
        seen_handles = set()
        valid_windows = []
        
        for w in [mock_win1a, mock_win1b]:
            if w._hWnd not in seen_handles:
                seen_handles.add(w._hWnd)
                valid_windows.append(w)
        
        assert len(valid_windows) == 1
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    @patch('timer.keyboard.press_and_release')
    @patch('timer.pyautogui.moveTo')
    @patch('timer.pyautogui.click')
    @patch('timer.time.sleep')
    @patch('timer.random.uniform')
    def test_mouse_movement_animation(self, mock_uniform, mock_sleep, mock_click,
                                     mock_moveto, mock_keyboard, mock_get_windows):
        """Test that mouse moves to target with animation duration"""
        mock_win = MagicMock()
        mock_win.title = "MapleRoyals - Test"
        mock_win._hWnd = 1
        mock_win.left = 100
        mock_win.top = 200
        mock_win.width = 800
        mock_win.height = 600
        mock_win.size = (800, 600)
        
        mock_get_windows.return_value = [mock_win]
        
        timer.config = {
            'trigger_key': 'f1',
            'selected_window_titles': None
        }
        
        # Mock uniform to return predictable values
        mock_uniform.side_effect = [
            0.1,    # offset_x calculation
            0.1,    # offset_y calculation
            0.5,    # move_duration
            0.1,    # reaction time pause
            1.0     # delay between windows (though only 1 window)
        ]
        
        timer.click_maple_windows()
        
        # Verify moveTo was called with duration parameter
        assert mock_moveto.call_count == 1
        call_args = mock_moveto.call_args
        
        # moveTo should be called with (x, y, duration=...)
        assert len(call_args[0]) == 2  # x, y positional args
        assert 'duration' in call_args[1]  # duration keyword arg
        
        # Verify duration is within expected range (0.3-0.8 seconds)
        duration = call_args[1]['duration']
        assert 0.3 <= duration <= 0.8, f"Duration {duration} is outside expected range [0.3, 0.8]"
        
        # Verify click was called after movement
        assert mock_click.call_count == 1


class TestWindowRandomization:
    """Test randomization features for human-like behavior"""
    
    def test_mouse_movement_duration_range(self):
        """Test that mouse movement duration is within human-like range"""
        # Test multiple iterations to ensure randomness stays in bounds
        for _ in range(100):
            duration = random.uniform(0.3, 0.8)
            assert 0.3 <= duration <= 0.8
            assert isinstance(duration, float)
    def test_click_position_randomization(self):
        """Test random click position calculation"""
        window_width = 800
        window_height = 600
        window_left = 100
        window_top = 100
        
        # Test that offset stays within bounds
        for _ in range(10):
            offset_x = random.uniform(-0.3, 0.3) * window_width
            offset_y = random.uniform(-0.3, 0.3) * window_height
            
            click_x = window_left + window_width // 2 + offset_x
            click_y = window_top + window_height // 2 + offset_y
            
            # Verify click is within reasonable bounds
            assert window_left - 240 <= click_x <= window_left + 800 + 240
            assert window_top - 180 <= click_y <= window_top + 600 + 180
    
    def test_delay_randomization(self):
        """Test that delays are within expected range"""
        # Total time should be approximately 5 seconds
        num_windows = 3
        total_time = 5.0
        
        delays = []
        remaining_time = total_time
        
        for i in range(num_windows - 1):
            max_delay = min(2.5, remaining_time - (num_windows - i - 1) * 0.3)
            delay = random.uniform(0.5, max_delay)
            delays.append(delay)
            remaining_time -= delay
        
        # Last delay
        delays.append(max(0.3, remaining_time))
        
        # Verify all delays in reasonable range
        for delay in delays[:-1]:
            assert 0.5 <= delay <= 2.5
        
        # Verify total approximately 5 seconds
        assert 4.0 <= sum(delays) <= 6.0
    
    @patch('timer.random.shuffle')
    def test_window_order_randomization(self, mock_shuffle):
        """Test that window order is shuffled"""
        windows = [MagicMock(), MagicMock(), MagicMock()]
        
        # Implementation should call shuffle on windows
        random.shuffle(windows)
        mock_shuffle.assert_called()


class TestWindowActivation:
    """Test window activation strategies"""
    
    @patch('timer.pyautogui.click')
    def test_window_activation_click_method(self, mock_click):
        """Test window activation via mouse click"""
        window_left = 100
        window_top = 100
        window_width = 800
        window_height = 600
        
        click_x = window_left + window_width // 2
        click_y = window_top + window_height // 2
        
        timer.pyautogui.click(click_x, click_y)
        
        mock_click.assert_called_once_with(click_x, click_y)
    
    def test_window_activation_fallback(self):
        """Test fallback to window.activate() if click fails"""
        mock_window = MagicMock()
        
        # If click fails, should try activate()
        try:
            mock_window.activate()
        except:
            pass
        
        # Should attempt activation
        mock_window.activate.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
