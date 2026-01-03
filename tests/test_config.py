"""
Configuration Management Tests

Tests for configuration loading, saving, and validation functions.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import sys

# Add parent directory to path to import timer module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import timer


class TestConfigPath:
    """Test configuration path resolution"""
    
    def test_get_config_path_script_mode(self):
        """Test config path when running as script"""
        with patch.object(sys, 'frozen', False, create=True):
            path = timer.get_config_path()
            assert path == 'timer_config.json'
    
    def test_get_config_path_executable_mode(self):
        """Test config path when running as executable"""
        with patch.object(sys, 'frozen', True, create=True):
            with patch.object(sys, 'executable', '/path/to/timer.exe'):
                path = timer.get_config_path()
                assert path == os.path.join('/path/to', 'timer_config.json')


class TestLoadConfig:
    """Test configuration loading"""
    
    def test_load_config_file_exists(self, tmp_path):
        """Test loading valid configuration file"""
        config_file = tmp_path / "timer_config.json"
        test_config = {
            "trigger_key": "f1",
            "stop_key": "f2",
            "countdown_seconds": 120,
            "random_offset_seconds": 5,
            "auto_click_windows": True,
            "selected_window_titles": ["Test Window"]
        }
        config_file.write_text(json.dumps(test_config))
        
        with patch('timer.get_config_path', return_value=str(config_file)):
            result = timer.load_config()
            assert result == test_config
    
    def test_load_config_file_missing(self, tmp_path):
        """Test loading when config file doesn't exist"""
        config_file = tmp_path / "nonexistent.json"
        
        with patch('timer.get_config_path', return_value=str(config_file)):
            result = timer.load_config()
            assert result is None
    
    def test_load_config_invalid_json(self, tmp_path, capsys):
        """Test loading corrupted JSON file"""
        config_file = tmp_path / "timer_config.json"
        config_file.write_text("{ invalid json }")
        
        with patch('timer.get_config_path', return_value=str(config_file)):
            result = timer.load_config()
            assert result is None
            
            # Check that error was printed
            captured = capsys.readouterr()
            assert "Failed to load config" in captured.out
    
    def test_load_config_with_missing_fields(self, tmp_path):
        """Test loading config with partial data"""
        config_file = tmp_path / "timer_config.json"
        partial_config = {
            "trigger_key": "f1",
            "stop_key": "f2"
            # Missing other fields
        }
        config_file.write_text(json.dumps(partial_config))
        
        with patch('timer.get_config_path', return_value=str(config_file)):
            result = timer.load_config()
            assert result == partial_config
            # Application should handle missing fields with defaults


class TestSaveConfig:
    """Test configuration saving"""
    
    def test_save_config_success(self, tmp_path, capsys):
        """Test successfully saving configuration"""
        config_file = tmp_path / "timer_config.json"
        test_config = {
            "trigger_key": "f1",
            "stop_key": "f2",
            "countdown_seconds": 120,
            "random_offset_seconds": 5,
            "auto_click_windows": False,
            "selected_window_titles": None
        }
        
        with patch('timer.get_config_path', return_value=str(config_file)):
            result = timer.save_config(test_config)
            assert result is True
            
            # Verify file was created
            assert config_file.exists()
            
            # Verify content is correct
            saved_data = json.loads(config_file.read_text())
            assert saved_data == test_config
            
            # Check confirmation message
            captured = capsys.readouterr()
            assert "Settings saved" in captured.out
    
    def test_save_config_write_error(self, tmp_path, capsys):
        """Test handling of write permission errors"""
        config_file = tmp_path / "readonly" / "timer_config.json"
        test_config = {"trigger_key": "f1"}
        
        with patch('timer.get_config_path', return_value=str(config_file)):
            result = timer.save_config(test_config)
            assert result is False
            
            # Check error message
            captured = capsys.readouterr()
            assert "Failed to save config" in captured.out
    
    def test_save_config_unicode_support(self, tmp_path):
        """Test saving configuration with Unicode characters"""
        config_file = tmp_path / "timer_config.json"
        test_config = {
            "trigger_key": "f1",
            "stop_key": "f2",
            "countdown_seconds": 130,
            "random_offset_seconds": 0,
            "auto_click_windows": True,
            "selected_window_titles": ["メイプルロワイヤル - キャラ1"]
        }
        
        with patch('timer.get_config_path', return_value=str(config_file)):
            result = timer.save_config(test_config)
            assert result is True
            
            # Verify Unicode preserved
            saved_data = json.loads(config_file.read_text(encoding='utf-8'))
            assert saved_data == test_config


class TestSetupConfig:
    """Test interactive configuration setup"""
    
    @patch('timer.keyboard.read_event')
    @patch('timer.select_windows')
    @patch('builtins.input')
    def test_setup_config_basic_flow(self, mock_input, mock_select_windows, mock_read_event):
        """Test basic configuration flow with default values"""
        # Mock keyboard events for hotkey selection
        trigger_event = MagicMock()
        trigger_event.event_type = 'down'
        trigger_event.name = 'f1'
        
        stop_event = MagicMock()
        stop_event.event_type = 'down'
        stop_event.name = 'f2'
        
        mock_read_event.side_effect = [trigger_event, stop_event]
        
        # Mock input for countdown, offset, and auto-click
        mock_input.side_effect = ['', '', '']  # Use all defaults
        
        # Mock window selection to disable
        mock_select_windows.return_value = False
        
        result = timer.setup_config()
        
        assert result is not None
        assert result['trigger_key'] == 'f1'
        assert result['stop_key'] == 'f2'
        assert result['countdown_seconds'] == timer.DEFAULT_COUNTDOWN_SECONDS
        assert result['random_offset_seconds'] == timer.DEFAULT_RANDOM_OFFSET_SECONDS
        assert result['auto_click_windows'] is False
    
    @patch('timer.keyboard.read_event')
    def test_setup_config_duplicate_keys_rejected(self, mock_read_event, capsys):
        """Test that duplicate hotkeys are rejected"""
        # Both keys return same value
        same_event = MagicMock()
        same_event.event_type = 'down'
        same_event.name = 'f1'
        
        mock_read_event.side_effect = [same_event, same_event]
        
        result = timer.setup_config()
        
        assert result is None
        captured = capsys.readouterr()
        assert "cannot be the same" in captured.out
    
    @patch('timer.keyboard.read_event')
    @patch('builtins.input')
    def test_setup_config_custom_countdown(self, mock_input, mock_read_event):
        """Test setting custom countdown value"""
        trigger_event = MagicMock()
        trigger_event.event_type = 'down'
        trigger_event.name = 'f1'
        
        stop_event = MagicMock()
        stop_event.event_type = 'down'
        stop_event.name = 'f2'
        
        mock_read_event.side_effect = [trigger_event, stop_event]
        mock_input.side_effect = ['90', '10', '']  # Custom countdown and offset
        
        result = timer.setup_config()
        
        assert result is not None
        assert result['countdown_seconds'] == 90
        assert result['random_offset_seconds'] == 10
    
    @patch('timer.keyboard.read_event')
    @patch('builtins.input')
    def test_setup_config_invalid_countdown(self, mock_input, mock_read_event, capsys):
        """Test validation rejects invalid countdown values"""
        trigger_event = MagicMock()
        trigger_event.event_type = 'down'
        trigger_event.name = 'f1'
        
        stop_event = MagicMock()
        stop_event.event_type = 'down'
        stop_event.name = 'f2'
        
        mock_read_event.side_effect = [trigger_event, stop_event]
        mock_input.side_effect = ['-5']  # Negative countdown
        
        result = timer.setup_config()
        
        assert result is None
        captured = capsys.readouterr()
        assert "must be positive" in captured.out
    
    @patch('timer.keyboard.read_event')
    @patch('builtins.input')
    def test_setup_config_offset_validation(self, mock_input, mock_read_event, capsys):
        """Test offset validation (must be < countdown)"""
        trigger_event = MagicMock()
        trigger_event.event_type = 'down'
        trigger_event.name = 'f1'
        
        stop_event = MagicMock()
        stop_event.event_type = 'down'
        stop_event.name = 'f2'
        
        mock_read_event.side_effect = [trigger_event, stop_event]
        mock_input.side_effect = ['100', '150']  # Offset > countdown
        
        result = timer.setup_config()
        
        assert result is None
        captured = capsys.readouterr()
        assert "less than countdown" in captured.out
    
    @patch('timer.keyboard.read_event')
    def test_setup_config_esc_cancellation(self, mock_read_event, capsys):
        """Test ESC key cancels setup"""
        esc_event = MagicMock()
        esc_event.event_type = 'down'
        esc_event.name = 'esc'
        
        mock_read_event.return_value = esc_event
        
        result = timer.setup_config()
        
        assert result is None
        captured = capsys.readouterr()
        assert "cancelled" in captured.out


class TestSelectWindows:
    """Test window selection for auto-click"""
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', False)
    def test_select_windows_dependencies_missing(self):
        """Test graceful handling when dependencies unavailable"""
        result = timer.select_windows()
        assert result is None
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    def test_select_windows_no_windows_found(self, mock_get_windows, capsys):
        """Test when no MapleRoyals windows are running"""
        mock_get_windows.return_value = []
        
        result = timer.select_windows()
        
        assert result is None
        captured = capsys.readouterr()
        assert "No MapleRoyals windows" in captured.out
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    @patch('builtins.input')
    def test_select_windows_all_windows(self, mock_input, mock_get_windows, capsys):
        """Test selecting all windows with /all command"""
        # Mock windows
        mock_win1 = MagicMock()
        mock_win1.title = "MapleRoyals - Character1"
        mock_win1._hWnd = 1
        mock_win1.size = (800, 600)
        
        mock_win2 = MagicMock()
        mock_win2.title = "MapleRoyals - Character2"
        mock_win2._hWnd = 2
        mock_win2.size = (800, 600)
        
        mock_get_windows.return_value = [mock_win1, mock_win2]
        mock_input.return_value = '/all'
        
        result = timer.select_windows()
        
        assert result is None  # None means "all windows"
        captured = capsys.readouterr()
        assert "All" in captured.out
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    @patch('builtins.input')
    def test_select_windows_specific_indices(self, mock_input, mock_get_windows):
        """Test selecting specific windows by index"""
        mock_win1 = MagicMock()
        mock_win1.title = "MapleRoyals - Character1"
        mock_win1._hWnd = 1
        mock_win1.size = (800, 600)
        
        mock_win2 = MagicMock()
        mock_win2.title = "MapleRoyals - Character2"
        mock_win2._hWnd = 2
        mock_win2.size = (800, 600)
        
        mock_win3 = MagicMock()
        mock_win3.title = "MapleRoyals - Character3"
        mock_win3._hWnd = 3
        mock_win3.size = (800, 600)
        
        mock_get_windows.return_value = [mock_win1, mock_win2, mock_win3]
        mock_input.return_value = '1,3'
        
        result = timer.select_windows()
        
        assert result == ["MapleRoyals - Character1", "MapleRoyals - Character3"]
    
    @patch('timer.WINDOW_AUTOMATION_AVAILABLE', True)
    @patch('timer.gw.getAllWindows')
    @patch('builtins.input')
    def test_select_windows_cancel_selection(self, mock_input, mock_get_windows, capsys):
        """Test cancelling window selection"""
        mock_win1 = MagicMock()
        mock_win1.title = "MapleRoyals - Test"
        mock_win1._hWnd = 1
        mock_win1.size = (800, 600)
        
        mock_get_windows.return_value = [mock_win1]
        mock_input.return_value = ''  # Empty string = cancel
        
        result = timer.select_windows()
        
        assert result is False
        captured = capsys.readouterr()
        assert "cancelled" in captured.out or "disabled" in captured.out


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
