# Implementation Plan: Timer Application

**Feature**: timer-application | **Date**: 2026-01-03  
**Status**: Reverse-Engineered (Existing Implementation)  
**Spec**: [spec.md](spec.md)

---

## Summary

The Timer Application is a Windows desktop utility that provides customizable countdown timers with global hotkey control, persistent configuration, random timing offsets for anti-detection, and optional automation features for MapleRoyals game windows. The application has been **fully implemented** and is in active use. This plan documents the existing implementation for maintenance and future enhancement purposes.

**Primary Requirement**: Provide a reliable, user-friendly timer with flexible configuration and automation capabilities.

**Technical Approach**: Python-based console application using threading for concurrent operations, packaged as a single-file Windows executable via PyInstaller. Configuration persists to JSON file, and global hotkeys enable hands-free operation.

---

## Technical Context

**Language/Version**: Python 3.8+  
**Primary Dependencies**: 
- `keyboard==0.13.5` (global hotkey registration)
- `winsound` (standard library, system sound)
- `threading` (standard library, timer and progress display)

**Optional Dependencies**:
- `pygetwindow==0.0.9` (window enumeration for auto-click)
- `pyautogui==0.9.54` (mouse/keyboard automation for auto-click)

**Storage**: Local JSON file (`timer_config.json`) in application directory  
**Testing**: Manual testing (no automated test suite currently)  
**Target Platform**: Windows 10/11 (64-bit)  
**Project Type**: Single-file console application  

**Performance Goals**: 
- Hotkey response < 100ms
- Progress bar updates at 2 Hz
- Memory footprint < 50MB

**Constraints**:
- Windows-only (due to `winsound` module)
- Requires keyboard access for hotkey registration
- May need administrator privileges for global hotkey registration

**Scale/Scope**: 
- Single-user desktop utility
- ~700 lines of Python code
- 7 global state variables
- 3 API contracts (Configuration, Timer Control, Window Automation)

---

## Constitution Check

*Since this project does not have a formal constitution file, standard software engineering principles are applied:*

### Code Quality ✅
- **Single Responsibility**: Functions have clear, focused purposes
- **Error Handling**: Graceful degradation for missing dependencies and invalid input
- **Resource Management**: Proper thread lifecycle management

### User Experience ✅
- **Sensible Defaults**: Page Up/Down keys, 130s countdown
- **Clear Feedback**: Progress bar, status messages
- **Reconfiguration**: Can adjust settings without restarting

### Maintainability ✅
- **Documentation**: Comprehensive inline comments
- **Clear Structure**: Function-based organization
- **State Management**: Explicit global variables with clear purpose

### Deployment ✅
- **Packaging**: Single-file executable via PyInstaller
- **Configuration**: Portable JSON file alongside executable
- **CI/CD**: GitHub Actions for automated releases

**No constitutional violations detected.** Project follows best practices for scope and complexity.

---

## Project Structure

### Documentation (this feature)

```text
.specify/features/timer-application/
├── spec.md              # Complete feature specification
├── plan.md              # This file (implementation plan)
├── research.md          # Technology decisions and rationale
├── data-model.md        # Configuration schema and runtime state
├── quickstart.md        # User and developer quick start guide
└── contracts/           # Function contracts (API specifications)
    ├── configuration-api.md        # Config management interface
    ├── timer-control-api.md        # Timer operation interface
    └── window-automation-api.md    # Window automation interface
```

### Source Code (repository root)

```text
farm-check-rms/
├── timer.py                    # Main application (~700 lines)
├── requirements.txt            # Python dependencies
├── timer_config.json          # User configuration (auto-generated, gitignored)
├── README.md                  # End-user documentation
├── CLAUDE.md                  # Development history and notes
├── .gitignore                 # Git exclusions
├── .github/
│   └── workflows/
│       └── build.yml         # CI/CD: Auto-build on tag push
└── .specify/                  # Specification framework
    ├── memory/
    │   └── constitution.md    # Project principles (template)
    ├── templates/             # Document templates
    ├── scripts/               # Automation scripts
    └── features/              # Feature specifications
        └── timer-application/ # This feature
```

**Structure Decision**: Single-file application structure chosen for maximum simplicity. All functionality is contained in `timer.py` with clear function boundaries. No need for multi-module architecture given the limited scope (~700 LOC).

---

## Complexity Tracking

**No constitutional violations to justify.** The project intentionally avoids over-engineering:

- ✅ No unnecessary abstraction layers
- ✅ No complex design patterns (no OOP, no dependency injection)
- ✅ Direct use of standard library where possible
- ✅ Optional dependencies gracefully degrade

Complexity is justified only where it provides clear value:
- **Threading**: Required for non-blocking timer and progress display
- **Random Offset**: Addresses real user need (anti-detection)
- **Auto-Click**: Optional feature, disabled if dependencies missing

---

## Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Timer Application                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ Configuration │  │ Timer Control  │  │    Window      │ │
│  │  Management   │  │   & Display    │  │   Automation   │ │
│  └───────┬───────┘  └────────┬───────┘  └────────┬───────┘ │
│          │                   │                    │          │
│          │                   │                    │          │
│  ┌───────▼───────────────────▼────────────────────▼───────┐ │
│  │              Global State Variables                     │ │
│  │  - config (dict)                                        │ │
│  │  - current_timer (Timer)                                │ │
│  │  - actual_countdown (int)                               │ │
│  │  - timer_start_time (float)                             │ │
│  │  - progress_thread (Thread)                             │ │
│  │  - stop_progress (bool)                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘

External Interfaces:
- keyboard library (hotkey registration)
- winsound module (system sound)
- pygetwindow/pyautogui (optional window automation)
- JSON file system (configuration persistence)
```

### Component Responsibilities

#### 1. Configuration Management
**Purpose**: Persist and manage user preferences

**Key Functions**:
- `load_config()`: Read JSON configuration
- `save_config(dict)`: Write JSON configuration
- `setup_config()`: Interactive configuration wizard
- `select_windows()`: Interactive window selection
- `get_config_path()`: Resolve config file location

**Dependencies**: `json`, `os`, `sys`, `keyboard` (for key capture)

---

#### 2. Timer Control & Display
**Purpose**: Core countdown timer functionality

**Key Functions**:
- `start_timer()`: Initialize and start countdown
- `stop_timer()`: Cancel active countdown
- `on_timeout()`: Handle timer expiration
- `show_progress()`: Real-time progress bar (threaded)
- `play_sound()`: System alert on expiration

**Dependencies**: `threading`, `time`, `winsound`, `random`

**Threading Model**:
- Main thread: Hotkey listener (`keyboard.wait()`)
- Timer thread: Countdown execution (`threading.Timer`)
- Progress thread: Progress bar updates (daemon thread)
- Command listener thread: Monitor stdin for `/setup`

---

#### 3. Window Automation (Optional)
**Purpose**: Auto-click game windows when timer expires

**Key Functions**:
- `click_maple_windows()`: Enumerate and click windows
- Randomization: Click positions, window order, delays

**Dependencies**: `pygetwindow`, `pyautogui` (optional)

**Graceful Degradation**: If dependencies missing, feature is disabled but application continues to function.

---

#### 4. Hotkey Management
**Purpose**: Register and manage global keyboard shortcuts

**Key Functions**:
- `register_hotkeys()`: Bind hotkeys to callbacks
- `unregister_hotkeys()`: Remove hotkey bindings

**Dependencies**: `keyboard`

---

#### 5. Runtime Reconfiguration
**Purpose**: Allow settings changes without restart

**Key Function**:
- `command_listener()`: Background thread monitoring stdin for `/setup`

**Behavior**: When `/setup` detected, unregister hotkeys, stop timer, run config wizard, re-register hotkeys

---

## Data Flow

### Startup Flow

```
main()
  │
  ├─→ load_config()
  │     │
  │     ├─→ File exists? → Parse JSON → Return dict
  │     └─→ File missing? → Return None
  │
  ├─→ if config is None:
  │     └─→ setup_config()
  │           └─→ Interactive wizard → Return dict
  │
  ├─→ save_config(dict)
  │
  ├─→ register_hotkeys()
  │     ├─→ keyboard.add_hotkey(trigger_key, start_timer)
  │     └─→ keyboard.add_hotkey(stop_key, stop_timer)
  │
  ├─→ Start command_listener() thread
  │
  └─→ keyboard.wait()  # Block main thread
```

---

### Timer Start Flow

```
User presses trigger_key
  │
  ├─→ start_timer()
  │     │
  │     ├─→ Cancel existing timer (if any)
  │     ├─→ Stop existing progress thread (if any)
  │     │
  │     ├─→ Calculate actual_countdown:
  │     │     base = config['countdown_seconds']
  │     │     offset = random.randint(-N, +N)
  │     │     actual_countdown = base + offset
  │     │
  │     ├─→ Set timer_start_time = time.time()
  │     │
  │     ├─→ Print status with offset information
  │     │
  │     ├─→ Start progress_thread:
  │     │     stop_progress = False
  │     │     Thread(target=show_progress, daemon=True).start()
  │     │
  │     └─→ Create and start timer:
  │           current_timer = Timer(actual_countdown, on_timeout)
  │           current_timer.start()
  │
  └─→ show_progress() runs in parallel:
        while not stop_progress:
          Calculate elapsed, remaining, progress
          Display progress bar (in-place update)
          Sleep 0.5 seconds
```

---

### Timer Expiration Flow

```
threading.Timer expires
  │
  ├─→ on_timeout()
  │     │
  │     ├─→ play_sound()
  │     │     └─→ winsound.MessageBeep(MB_ICONEXCLAMATION)
  │     │
  │     ├─→ if config['auto_click_windows']:
  │     │     └─→ click_maple_windows()
  │     │           ├─→ Find MapleRoyals windows
  │     │           ├─→ Filter by selected_window_titles
  │     │           ├─→ Shuffle window order
  │     │           └─→ For each window:
  │     │                 ├─→ Click random position
  │     │                 ├─→ Press trigger_key
  │     │                 └─→ Wait random delay
  │     │
  │     ├─→ Display auto-restart message (5 seconds)
  │     │     │
  │     │     ├─→ if ESC pressed:
  │     │     │     └─→ Show menu:
  │     │     │           ├─→ Type number → adjust countdown
  │     │     │           ├─→ Type '/setup' → full reconfig
  │     │     │           └─→ Press Enter → restart immediately
  │     │     │
  │     │     └─→ else (no ESC):
  │     │           └─→ Auto-restart: start_timer()
  │     │
  │     └─→ Return to IDLE state
```

---

## Implementation Status

### ✅ Fully Implemented Features

1. **Configuration Management**
   - JSON persistence
   - Interactive setup wizard
   - Path resolution (script vs. executable)
   - Field validation
   - Backwards compatibility

2. **Timer Functionality**
   - Start/stop/reset operations
   - Random time offset
   - Threading-based countdown
   - System sound alert
   - Global hotkey control

3. **Progress Display**
   - Real-time progress bar
   - Percentage and time remaining
   - In-place console updates
   - Daemon thread lifecycle

4. **Window Automation**
   - MapleRoyals window enumeration
   - User-selectable window targeting
   - Human-like click randomization
   - Graceful error handling

5. **Runtime Reconfiguration**
   - `/setup` command detection
   - Hotkey re-registration
   - Timer cancellation during setup
   - Quick-adjust menu (ESC during auto-restart)

6. **Packaging & Deployment**
   - PyInstaller single-file build
   - GitHub Actions CI/CD
   - Automated release creation
   - Version tagging workflow

---

### ❌ Not Implemented (By Design)

1. **Automated Testing**: Manual testing deemed sufficient for current scope
2. **GUI Interface**: Console application intentionally simple
3. **Cross-Platform Support**: Windows-only due to `winsound`
4. **Multi-Timer Support**: Single timer instance sufficient
5. **Configuration Versioning**: Schema stable, no migration needed yet

---

## Dependencies & Build

### Runtime Dependencies

**Required** (`requirements.txt`):
```
keyboard==0.13.5
```

**Optional** (for auto-click feature):
```
pygetwindow==0.0.9
pyautogui==0.9.54
```

**Standard Library** (no installation needed):
- `threading` - Timer and background threads
- `winsound` - Windows system sounds
- `json` - Configuration persistence
- `os`, `sys` - Path resolution
- `time` - Timestamps and delays
- `random` - Offset randomization

### Build Dependencies

**Packaging** (`requirements.txt`):
```
pyinstaller==6.11.1
```

### Build Commands

**Local Build**:
```bash
# Install dependencies
pip install -r requirements.txt

# Build single-file executable
pyinstaller --onefile --console timer.py

# Output: dist/timer.exe
```

**CI/CD Build** (GitHub Actions):
```yaml
# Triggered by: git push origin v1.0.0
runs-on: windows-latest
steps:
  - Install Python 3.11
  - Install dependencies
  - Build with PyInstaller
  - Upload to GitHub Releases
```

---

## Configuration Schema

### JSON File Structure

**Location**: `timer_config.json` (same directory as executable)

```json
{
  "trigger_key": "page up",
  "stop_key": "page down",
  "countdown_seconds": 130,
  "random_offset_seconds": 5,
  "auto_click_windows": true,
  "selected_window_titles": [
    "MapleRoyals - Character1",
    "MapleRoyals - Character2"
  ]
}
```

**Field Validation**:
- `trigger_key` ≠ `stop_key` (unique hotkeys)
- `countdown_seconds` > 0 (positive integer)
- `random_offset_seconds` >= 0 and < `countdown_seconds`
- `selected_window_titles`: `null` (all windows) or array of strings

**Backwards Compatibility**: Missing fields use default values. New fields ignored by older versions.

---

## Testing Strategy

### Manual Testing Checklist

**Configuration**:
- [x] First-time setup creates valid JSON
- [x] Existing config loads correctly
- [x] Invalid JSON triggers re-setup
- [x] Hotkey validation rejects duplicates
- [x] Countdown validation enforces positivity
- [x] Offset validation prevents negatives

**Timer Operations**:
- [x] Start hotkey triggers countdown
- [x] Stop hotkey cancels countdown
- [x] Reset during active timer works
- [x] Progress bar displays accurately
- [x] Timer expires and plays sound
- [x] Random offset varies each cycle

**Reconfiguration**:
- [x] `/setup` command detected
- [x] Hotkeys disabled during setup
- [x] Configuration saves and applies
- [x] ESC menu during auto-restart works
- [x] Quick countdown adjustment works

**Window Automation**:
- [x] Window enumeration finds MapleRoyals
- [x] Window selection persists
- [x] Auto-click clicks correct windows
- [x] Missing windows handled gracefully
- [x] Invalid handles skipped

**Edge Cases**:
- [x] Config file corruption handled
- [x] Missing optional dependencies detected
- [x] Rapid hotkey presses managed
- [x] Window close during auto-click handled

### Future Automated Testing

**Proposed Test Structure**:
```python
tests/
├── test_config.py              # Configuration CRUD
├── test_timer.py               # Timer logic (mocked time)
├── test_automation.py          # Window automation (mocked pygetwindow)
├── test_integration.py         # End-to-end flows
└── fixtures/
    ├── valid_config.json       # Test configuration samples
    └── invalid_config.json     # Malformed JSON samples
```

**Testing Framework**: `pytest` (to be added)

---

## Deployment Process

### Release Workflow

1. **Version Decision**: Determine next version (semantic versioning)
2. **Testing**: Run full manual test checklist
3. **Documentation**: Update README.md and CHANGELOG.md
4. **Tagging**: Create git tag
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
5. **CI/CD**: GitHub Actions automatically:
   - Builds on Windows runner
   - Creates GitHub Release
   - Uploads `timer.exe` artifact
6. **Verification**: Download and test release artifact
7. **Announcement**: Publish release notes

### Distribution

**Primary Method**: GitHub Releases (pre-built executables)  
**Alternative**: Source distribution via Git clone

**No external hosting** (npm, PyPI, etc.) - application is standalone executable.

---

## Maintenance & Support

### Common Issues

| Issue | Root Cause | Solution |
|-------|------------|----------|
| Hotkeys not responding | Conflicts with other apps | Try different keys or close conflicting software |
| Sound not playing | Non-Windows platform | Ensure Windows 10/11 |
| Auto-click fails | Missing dependencies | Install `pygetwindow` and `pyautogui` |
| Config not saving | File permissions | Run as administrator or move to writable directory |

### Monitoring

**No telemetry or analytics.** Issues reported via GitHub Issues.

### Backward Compatibility

**Configuration**: New fields added with defaults. Old configs remain valid.  
**API**: No public API. Internal changes do not affect users.

---

## Future Enhancements (Out of Scope)

### Potential Improvements

1. **Cross-Platform Support**: Refactor `winsound` usage
2. **Automated Testing**: Add pytest suite
3. **GUI Option**: Optional tkinter interface
4. **Configuration Profiles**: Multiple timer presets
5. **Timer History**: Log past countdowns
6. **Custom Sounds**: User-provided audio files
7. **System Tray Icon**: Minimize to tray
8. **Pause/Resume**: Mid-countdown pause
9. **Webhook Integration**: Trigger external services on expiration
10. **Plugin System**: Extensibility for custom actions

### Non-Goals

- ❌ Web-based interface
- ❌ Mobile applications
- ❌ Cloud synchronization
- ❌ Multi-user support
- ❌ Enterprise features

---

## Conclusion

The Timer Application is a **complete, production-ready** desktop utility that meets all functional and non-functional requirements outlined in the specification. The codebase is stable, well-documented, and actively maintained.

**Key Strengths**:
- ✅ Simple, focused design
- ✅ Reliable operation
- ✅ User-friendly configuration
- ✅ Comprehensive error handling
- ✅ Automated build and release

**Maintenance Priority**: Low. Application is stable and feature-complete for current needs.

---

**Document Status**: Complete  
**Next Steps**: None required (implementation finished)  
**For New Features**: Create new spec → plan → implement cycle

---

**Branch**: N/A (main branch, no feature branch workflow)  
**Artifacts**:
- [spec.md](spec.md) - Complete specification
- [research.md](research.md) - Technical decisions
- [data-model.md](data-model.md) - Data structures
- [quickstart.md](quickstart.md) - User/developer guide
- [contracts/](contracts/) - API contracts
- [plan.md](plan.md) - This document

**Implementation**: [timer.py](../../timer.py) (~700 lines)
