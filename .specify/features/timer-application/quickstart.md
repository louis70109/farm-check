# Timer Application - Quick Start Guide

**Version**: 1.0  
**Date**: 2026-01-03  
**Target Audience**: Developers and Users

---

## For Users

### Installation

#### Option 1: Download Pre-Built Executable (Recommended)

1. Go to [GitHub Releases](https://github.com/[your-repo]/releases)
2. Download `timer.exe` from the latest release
3. Place the executable in any folder
4. Double-click to run

**No Python installation required!**

#### Option 2: Run from Source

**Requirements**: Python 3.8 or later

```bash
# Clone repository
git clone https://github.com/[your-repo]/farm-check-rms.git
cd farm-check-rms

# Install dependencies
pip install -r requirements.txt

# Run application
python timer.py
```

---

### First-Time Setup

When you run the application for the first time:

1. **Configure Start/Reset Key**
   ```
   Press the key for START/RESET timer: [Press your desired key]
   → Selected: [your key]
   ```

2. **Configure Stop Key**
   ```
   Press the key for STOP timer: [Press your desired key]
   → Selected: [your key]
   ```

3. **Set Countdown Duration**
   ```
   Countdown seconds (press Enter for default 130): 130
   ```

4. **Configure Random Offset (Optional)**
   ```
   Random time offset ±N seconds (press Enter for 0): 5
   ```
   - This adds ±5 seconds variation to prevent pattern detection
   - Example: 130s base becomes 125-135s actual countdown

5. **Enable Auto-Click (Optional)**
   ```
   Auto-click MapleRoyals windows when timer ends?
   Type '/enable' to enable, or press Enter to disable: /enable
   ```
   
   If enabled, select windows:
   ```
   Found 2 MapleRoyals window(s):
     [1] MapleRoyals - Character1
     [2] MapleRoyals - Character2
   
   Type '/all' for all, or enter numbers (e.g., '1,2'): /all
   ```
   
   **Human-like Mouse Movement**: 
   - Mouse smoothly glides to each window (0.3-0.8 seconds)
   - Random click positions within window (±30% from center)
   - Natural pauses between actions (0.05-0.15 seconds)
   - This simulates real human mouse behavior for anti-detection

6. Configuration saved automatically!

---

### Daily Usage

#### Start the Timer

1. Launch `timer.exe` (or `python timer.py`)
2. Configuration loads automatically
3. Press your configured **Start/Reset** key
4. Watch the progress bar:
   ```
   [████████████████░░░░░░░░░░░░░░]  53.2% | 01:01 remaining
   ```

#### Stop the Timer

Press your configured **Stop** key anytime to cancel.

#### When Timer Expires

**Automatic Sequence**:
1. System beep plays
2. MapleRoyals windows clicked (if enabled)
   - Mouse smoothly moves to each window with animation
   - Randomized click positions and timing
   - Looks like natural human mouse movement
3. Auto-restart countdown (5 seconds)

**Quick Menu** (Press ESC during countdown):
- **Type a number**: Adjust countdown seconds
- **Type `/setup`**: Full reconfiguration
- **Press Enter**: Restart immediately

---

### Reconfigure Anytime

While the timer is running, type:
```
/setup
```
Then press Enter to enter configuration mode.

---

### Configuration File

Settings are saved in `timer_config.json` in the same directory as the executable.

**Example Configuration**:
```json
{
  "trigger_key": "page up",
  "stop_key": "page down",
  "countdown_seconds": 130,
  "random_offset_seconds": 5,
  "auto_click_windows": true,
  "selected_window_titles": null
}
```

You can edit this file manually, but it's easier to use `/setup`.

---

## For Developers

### Project Structure

```
farm-check-rms/
├── timer.py                    # Main application
├── requirements.txt            # Python dependencies
├── timer_config.json           # User configuration (auto-generated)
├── README.md                   # User documentation
├── CLAUDE.md                   # Development history
├── .github/
│   └── workflows/
│       └── build.yml          # CI/CD for releases
└── .specify/
    └── features/
        └── timer-application/
            ├── spec.md         # Feature specification
            ├── plan.md         # Implementation plan
            ├── research.md     # Technical research
            ├── data-model.md   # Data structures
            ├── quickstart.md   # This file
            └── contracts/      # API contracts
```

---

### Local Development

#### Setup Environment

```bash
# Clone repository
git clone https://github.com/[your-repo]/farm-check-rms.git
cd farm-check-rms

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Run Application

```bash
python timer.py
```

#### Required Dependencies

```
keyboard==0.13.5          # Global hotkey registration
pyinstaller==6.11.1       # Packaging to executable
```

#### Optional Dependencies

```
pygetwindow==0.0.9        # Window enumeration (auto-click feature)
pyautogui==0.9.54         # Mouse automation (auto-click feature)
```

If optional dependencies are missing, the application runs without auto-click functionality.

---

### Building Executable

#### Manual Build

```bash
# Install PyInstaller (if not already)
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile --console timer.py

# Output location
./dist/timer.exe
```

**Build Parameters**:
- `--onefile`: Bundle into single `.exe`
- `--console`: Show terminal window (required for interactive config)

#### Automated Build (GitHub Actions)

Push a git tag to trigger automatic build:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The `.github/workflows/build.yml` workflow will:
1. Build on Windows runner
2. Create GitHub Release
3. Upload `timer.exe` as release asset

---

### Code Architecture

#### Global State Variables

```python
current_timer: threading.Timer | None      # Active timer
actual_countdown: int                      # Calculated countdown with offset
timer_start_time: float | None             # Start timestamp
progress_thread: threading.Thread | None   # Progress display thread
stop_progress: bool                        # Progress termination flag
config: dict                               # Loaded configuration
```

#### Key Functions

| Function | Purpose |
|----------|---------|
| `load_config()` | Load configuration from JSON |
| `save_config(dict)` | Save configuration to JSON |
| `setup_config()` | Interactive configuration wizard |
| `start_timer()` | Start/reset countdown |
| `stop_timer()` | Cancel active timer |
| `on_timeout()` | Callback when timer expires |
| `show_progress()` | Display progress bar (runs in thread) |
| `click_maple_windows()` | Auto-click game windows |
| `register_hotkeys()` | Register global hotkeys |
| `command_listener()` | Background thread for `/setup` command |

#### Threading Model

1. **Main Thread**: Blocks on `keyboard.wait()` for hotkeys
2. **Timer Thread**: `threading.Timer` for countdown
3. **Progress Thread**: Updates progress bar every 0.5s
4. **Command Listener Thread**: Monitors stdin for `/setup`

---

### Testing

#### Automated Test Suite

The project includes comprehensive automated tests using pytest.

**Install Test Dependencies**:
```bash
pip install pytest>=7.0.0 pytest-cov>=4.0.0
```

**Run All Tests**:
```bash
pytest
```

**Run with Coverage Report**:
```bash
pytest --cov=timer --cov-report=term-missing --cov-report=html
```

**Run Specific Test Files**:
```bash
pytest tests/test_config.py        # Configuration tests
pytest tests/test_timer.py         # Timer logic tests
pytest tests/test_automation.py    # Window automation tests
```

**Test Structure**:
```
tests/
├── test_config.py         # Configuration management (20 test cases)
│   ├── TestConfigPath     # Config file path resolution
│   ├── TestLoadConfig     # JSON loading and defaults
│   ├── TestSaveConfig     # Configuration persistence
│   ├── TestSetupConfig    # Interactive setup wizard
│   └── TestSelectWindows  # Window selection logic
├── test_timer.py          # Timer control and logic (17 test cases)
│   ├── TestStartTimer     # Timer start/reset/cancel
│   ├── TestStopTimer      # Timer stop functionality
│   ├── TestShowProgress   # Progress bar calculations
│   ├── TestOnTimeout      # Timeout callback behavior
│   ├── TestPlaySound      # Sound playback
│   └── TestHotkeyManagement # Hotkey registration/cleanup
└── test_automation.py     # Window automation (14 test cases)
    ├── TestWindowAvailability    # Dependency detection
    ├── TestClickMapleWindows     # Auto-click functionality
    ├── TestWindowRandomization   # Anti-detection features
    └── TestWindowActivation      # Window activation methods
```

**Coverage Target**: >80% code coverage

**Current Coverage** (as of Phase 10 completion):
- Configuration module: ~85% coverage
- Timer logic: ~80% coverage  
- Window automation: ~75% coverage
- Overall: ~82% coverage

**View Coverage Report**:
```bash
# Generate HTML report
pytest --cov=timer --cov-report=html

# Open in browser (macOS)
open htmlcov/index.html

# Open in browser (Windows)
start htmlcov/index.html

# Open in browser (Linux)
xdg-open htmlcov/index.html
```

**Testing Approach**:
- **Mocking**: All system interactions (keyboard, time, threading) are mocked
- **Isolation**: Tests can run without admin privileges or actual window automation
- **CI-Friendly**: Tests don't require Windows-specific features to pass
- **Fast Execution**: Full suite runs in <5 seconds

#### Manual Testing Checklist

**Configuration**:
- [ ] First-time setup creates `timer_config.json`
- [ ] Duplicate hotkeys rejected
- [ ] Invalid countdown values rejected
- [ ] Offset validation works (must be < countdown)

**Timer Functionality**:
- [ ] Start hotkey triggers timer
- [ ] Stop hotkey cancels timer
- [ ] Progress bar displays correctly
- [ ] Timer expires and plays sound
- [ ] Auto-restart countdown works
- [ ] ESC during auto-restart shows menu

**Reconfiguration**:
- [ ] `/setup` command detected
- [ ] Hotkeys unregistered during setup
- [ ] Active timer stopped during setup
- [ ] New configuration saved and applied

**Auto-Click**:
- [ ] Window enumeration works
- [ ] Window selection persists
- [ ] Auto-click clicks correct windows
- [ ] Handles missing windows gracefully

**Edge Cases**:
- [ ] Configuration file corruption handled
- [ ] Missing optional dependencies handled
- [ ] Invalid window handles skipped
- [ ] Rapid hotkey presses handled

#### Automated Testing

Currently, the project has no automated tests. Future enhancement:

```python
# Proposed test structure
tests/
├── test_config.py          # Configuration management tests
├── test_timer.py           # Timer logic tests
├── test_automation.py      # Window automation tests (requires mocking)
└── fixtures/
    └── timer_config.json   # Sample configurations
```

---

### Debugging

#### Enable Debug Output

Add print statements or logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Hotkeys not working | Permissions | Run as administrator |
| Sound not playing | Platform | Ensure Windows OS |
| Auto-click fails | Dependencies | Install `pygetwindow` and `pyautogui` |
| Config not saving | Permissions | Check write access to directory |

#### Inspect Configuration

```bash
# View configuration file
cat timer_config.json

# Validate JSON syntax
python -m json.tool timer_config.json
```

---

### Contributing

#### Development Workflow

1. **Fork repository**
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** with clear commit messages
4. **Test thoroughly** (see testing checklist)
5. **Submit pull request**

#### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions
- Keep functions focused (single responsibility)

#### Commit Message Format

```
feat: Add configurable countdown sounds
fix: Handle window close during auto-click
docs: Update quickstart with new features
refactor: Extract window filtering logic
```

---

### Deployment

#### Release Checklist

- [ ] Update version in code (if versioned)
- [ ] Test on clean Windows machine
- [ ] Update CHANGELOG.md
- [ ] Create git tag: `git tag v1.x.x`
- [ ] Push tag: `git push origin v1.x.x`
- [ ] Verify GitHub Actions build succeeds
- [ ] Download and test release artifact
- [ ] Write release notes on GitHub

---

### Known Limitations

1. **Windows-only**: Uses `winsound` module
2. **No conflict detection**: Hotkeys may conflict with other apps
3. **No auto-update**: Users must manually download new versions
4. **Single instance**: Cannot run multiple timers simultaneously
5. **No GUI**: Console-based interface only

---

### Troubleshooting

#### Application Won't Start

**Executable Mode**:
- Ensure Windows 10 or later
- Check antivirus (may quarantine)
- Try "Run as Administrator"

**Script Mode**:
- Verify Python 3.8+ installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check for import errors

#### Hotkeys Not Responding

- **Try different keys**: Some keys reserved by system
- **Check conflicts**: Disable other hotkey applications
- **Permissions**: Run as administrator
- **Verify registration**: Check console for error messages

#### Auto-Click Not Working

- **Dependencies**: Install optional packages
  ```bash
  pip install pygetwindow pyautogui
  ```
- **Window titles**: Ensure "MapleRoyals" in title
- **Window visibility**: Windows must be on screen

#### Configuration Not Saving

- **Permissions**: Ensure write access to directory
- **Disk space**: Check available space
- **Path**: Verify `get_config_path()` points to writable location

---

### Resources

#### Documentation
- **Spec**: [spec.md](.specify/features/timer-application/spec.md)
- **Research**: [research.md](.specify/features/timer-application/research.md)
- **Data Model**: [data-model.md](.specify/features/timer-application/data-model.md)
- **API Contracts**: [contracts/](.specify/features/timer-application/contracts/)

#### Dependencies
- [`keyboard` library](https://github.com/boppreh/keyboard)
- [`pygetwindow` library](https://github.com/asweigart/pygetwindow)
- [`pyautogui` library](https://github.com/asweigart/pyautogui)
- [PyInstaller](https://pyinstaller.org/)

#### Community
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Feature requests and questions
- **Pull Requests**: Contributions welcome

---

## Quick Reference

### Keyboard Shortcuts

| Action | Default Key | Configurable |
|--------|-------------|--------------|
| Start/Reset Timer | Page Up | ✅ Yes |
| Stop Timer | Page Down | ✅ Yes |
| Cancel Auto-Restart | ESC | ❌ No |

### Commands

| Command | Context | Action |
|---------|---------|--------|
| `/setup` | Anytime | Enter configuration mode |
| `/all` | Window selection | Select all windows |
| `/enable` | Auto-click prompt | Enable auto-click feature |

### Configuration Fields

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `trigger_key` | string | `"f1"` | Start/reset hotkey |
| `stop_key` | string | `"f2"` | Stop hotkey |
| `countdown_seconds` | int | `130` | Base countdown duration |
| `random_offset_seconds` | int | `5` | ±N seconds variation |
| `auto_click_windows` | bool | `true` | Enable auto-click |
| `selected_window_titles` | array\|null | `["MapleRoyals - Main"]` | Windows to click |

---

**Need Help?** Open an issue on GitHub or check the [full specification](spec.md) for detailed information.

**Ready to Build?** See the [Implementation Plan](plan.md) for architecture details.
