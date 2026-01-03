# Timer Application - Specification

## Overview

A Windows desktop timer application with customizable hotkeys, configuration persistence, system sound alerts, and optional automation features for MapleRoyals game windows. The application is designed to provide flexible countdown timing with anti-detection randomization features.

**Target Platform**: Windows (requires `winsound` and `keyboard` modules)  
**Programming Language**: Python 3.8+  
**Deployment**: Standalone executable (PyInstaller)

---

## Context

This application was developed to address the need for a customizable timer with the following key characteristics:

1. **User-configurable hotkeys** - Users should be able to define their own keyboard shortcuts
2. **Persistent configuration** - Settings should be remembered across sessions
3. **Anti-detection measures** - Random timing offsets to simulate human behavior
4. **Optional automation** - Ability to auto-click game windows when timer expires
5. **Ease of use** - Simple configuration flow with sensible defaults

The application is primarily used for timing periodic tasks in the MapleRoyals game, where regular actions need to be performed at intervals.

---

## Functional Requirements

### FR-1: Timer Control

**FR-1.1**: User can start/reset a countdown timer using a configurable hotkey  
**FR-1.2**: User can stop/cancel an active timer using a different configurable hotkey  
**FR-1.3**: Timer automatically fires callback when countdown reaches zero  
**FR-1.4**: System plays audible alert (Windows system beep) when timer expires

### FR-2: Configuration Management

**FR-2.1**: On first launch, user must configure:
- Start/reset hotkey (by pressing the desired key)
- Stop hotkey (by pressing the desired key)
- Countdown duration in seconds (default: 130s)
- Random time offset range (±N seconds, default: 0)
- Auto-click MapleRoyals windows option (enable/disable)
- Specific window selection (if auto-click enabled)

**FR-2.2**: Configuration must be persisted to local JSON file (`timer_config.json`)  
**FR-2.3**: Configuration file location must follow these rules:
- When running as `.py` script: current working directory
- When running as `.exe`: same directory as executable

**FR-2.4**: On subsequent launches, user must be shown existing configuration  
**FR-2.5**: User can reconfigure by typing `/setup` at any time during execution

### FR-3: Random Time Offset (Anti-Detection)

**FR-3.1**: User can configure a random offset range (±N seconds) during setup  
**FR-3.2**: Each time timer starts, actual countdown duration = base_time ± random(0, N)  
**FR-3.3**: Application must display the actual countdown time including offset  
**FR-3.4**: Each timer restart must recalculate a new random offset

**Example**: Base time = 130s, offset = 5s → actual time varies between 125s-135s

### FR-4: Progress Display

**FR-4.1**: While timer is running, display real-time progress bar  
**FR-4.2**: Progress display must include:
- Visual bar representation (█ filled, ░ empty)
- Percentage complete (e.g., 53.2%)
- Remaining time in MM:SS format

**FR-4.3**: Progress must update at least twice per second (0.5s intervals)  
**FR-4.4**: Progress display must update in-place (same line, no scrolling)

### FR-5: Timer Expiration Behavior

**FR-5.1**: When timer expires:
1. Play system alert sound
2. Execute auto-click sequence (if enabled)
3. Display auto-restart countdown (5 seconds)
4. Automatically restart timer unless user presses ESC

**FR-5.2**: If user presses ESC during auto-restart countdown:
- Show configuration menu with three options:
  - Enter number to adjust countdown seconds
  - Type `/setup` to reconfigure all settings
  - Press Enter to restart with current settings

**FR-5.3**: Auto-restart countdown must be cancellable within 5-second window

### FR-6: Auto-Click MapleRoyals Windows

**FR-6.1**: User can enable/disable auto-click during configuration  
**FR-6.2**: When auto-click is enabled, user can select:
- All MapleRoyals windows (type `/all`)
- Specific windows by index (e.g., `1,3`)
- Or cancel to disable auto-click

**FR-6.3**: When timer expires and auto-click is enabled:
1. Find all MapleRoyals windows (title contains "MapleRoyals")
2. Filter by user's window selection (if specified)
3. Shuffle window order for randomness
4. For each window:
   - Calculate random click position (±30% offset from center)
   - Click to activate window
   - Press the configured trigger key
   - Wait random delay (0.5-2.5 seconds) before next window

**FR-6.4**: Total auto-click sequence should take approximately 5 seconds  
**FR-6.5**: Display progress/status messages during auto-click sequence

### FR-7: Runtime Command Interface

**FR-7.1**: User can type `/setup` at any time to enter configuration mode  
**FR-7.2**: When `/setup` is invoked:
1. Unregister current hotkeys
2. Stop active timer (if any)
3. Execute full configuration flow
4. Re-register hotkeys with new settings
5. Resume normal operation

**FR-7.3**: Command listener must run in background thread without blocking main program

---

## Non-Functional Requirements

### NFR-1: Performance

**NFR-1.1**: Hotkey response time must be < 100ms  
**NFR-1.2**: Progress bar updates must not consume > 5% CPU  
**NFR-1.3**: Application memory footprint must be < 50MB during normal operation

### NFR-2: Reliability

**NFR-2.1**: Configuration file corruption must not crash the application  
**NFR-2.2**: Invalid window handles must be gracefully skipped (no crashes)  
**NFR-2.3**: Hotkey conflicts must be detected and reported to user  
**NFR-2.4**: Missing dependencies (pygetwindow, pyautogui) must degrade gracefully

### NFR-3: Usability

**NFR-3.1**: Configuration flow must be self-explanatory without external documentation  
**NFR-3.2**: Default values must be provided for all configurable parameters  
**NFR-3.3**: Error messages must be clear and actionable  
**NFR-3.4**: User must be able to cancel setup at any point by pressing ESC

### NFR-4: Maintainability

**NFR-4.1**: Code must follow single-responsibility principle for functions  
**NFR-4.2**: Configuration schema must be versioned for future migrations  
**NFR-4.3**: Global state must be minimized and clearly documented

### NFR-5: Portability

**NFR-5.1**: Application must package as single-file executable (PyInstaller `--onefile`)  
**NFR-5.2**: Executable must run on Windows 10/11 without additional installation  
**NFR-5.3**: Configuration file must be portable (relative paths only)

### NFR-6: Security

**NFR-6.1**: Application must request only necessary system permissions  
**NFR-6.2**: No sensitive data (passwords, tokens) should be stored  
**NFR-6.3**: Auto-click feature must validate window titles before interaction

---

## User Stories

### US-1: First-Time Setup
**As a** new user  
**I want to** configure my preferred hotkeys on first launch  
**So that** the timer controls match my keyboard layout and preferences

**Acceptance Criteria**:
- Application detects absence of `timer_config.json`
- Setup wizard guides through all configuration steps
- User presses actual keys to define hotkeys (not typing key names)
- Configuration is saved automatically after completion
- Application is immediately ready to use after setup

---

### US-2: Daily Use
**As a** regular user  
**I want to** quickly start the timer without reconfiguring  
**So that** I can minimize interruption to my workflow

**Acceptance Criteria**:
- Application loads existing configuration on startup
- Displays current settings clearly
- Pressing configured hotkey immediately starts timer
- Progress bar provides visual feedback
- Timer auto-restarts after expiration

---

### US-3: Avoid Game Detection
**As a** game player  
**I want** the timer to vary slightly each cycle  
**So that** automated systems cannot detect fixed timing patterns

**Acceptance Criteria**:
- User can configure random offset range (e.g., ±5 seconds)
- Each timer start uses a different random offset
- Application displays actual countdown time with offset
- Offset range is validated (must be less than base time)
- Offset can be disabled by setting to 0

---

### US-4: Multi-Window Automation
**As a** user with multiple game clients  
**I want to** selectively auto-click specific windows  
**So that** only relevant game instances are automated

**Acceptance Criteria**:
- Application lists all MapleRoyals windows with indices
- User can select specific windows by number (e.g., `1,3`)
- User can select all windows with `/all` command
- Auto-click sequence randomizes window order
- Auto-click uses human-like timing and click positions

---

### US-5: Quick Adjustment
**As a** user whose timing needs change  
**I want to** quickly adjust countdown duration without full reconfiguration  
**So that** I can adapt to different game scenarios

**Acceptance Criteria**:
- When timer expires, ESC key opens quick menu
- User can type a number to change countdown seconds
- New duration is saved to configuration
- Timer can immediately restart with new duration
- User can also access full `/setup` from this menu

---

### US-6: Runtime Reconfiguration
**As a** user who wants to change hotkeys mid-session  
**I want to** type `/setup` to reconfigure without restarting the application  
**So that** I can adapt to keyboard conflicts or changing preferences

**Acceptance Criteria**:
- `/setup` command is recognized at any time
- Current timer stops safely
- Full configuration flow is executed
- Hotkeys are updated immediately
- Application resumes with new settings

---

## Edge Cases

### EC-1: Duplicate Hotkey Assignment
**Scenario**: User assigns same key for start and stop  
**Expected Behavior**: Configuration rejects the duplicate and prompts user to select different keys

### EC-2: Configuration File Corruption
**Scenario**: `timer_config.json` is malformed or contains invalid JSON  
**Expected Behavior**: Application logs error, deletes corrupt file, and launches first-time setup

### EC-3: No MapleRoyals Windows Found
**Scenario**: Auto-click is enabled but no MapleRoyals windows are running  
**Expected Behavior**: Application logs "No MapleRoyals windows found" and continues (timer still restarts)

### EC-4: Window Becomes Invalid During Auto-Click
**Scenario**: A MapleRoyals window closes while auto-click sequence is executing  
**Expected Behavior**: Application catches exception, logs error for that window, continues to next window

### EC-5: Invalid Selected Window Titles
**Scenario**: Configuration references window titles that no longer exist  
**Expected Behavior**: Application reports which selected windows are not running, clicks only available windows

### EC-6: User Holds ESC Key During Auto-Restart
**Scenario**: ESC key is held down for extended period  
**Expected Behavior**: Application detects ESC once, cancels auto-restart, shows menu (no repeated triggers)

### EC-7: Extremely Large Offset Value
**Scenario**: User enters offset value >= countdown seconds  
**Expected Behavior**: Configuration validates and rejects with error: "Offset must be less than countdown time"

### EC-8: Negative Countdown Value
**Scenario**: User enters countdown seconds as 0 or negative number  
**Expected Behavior**: Configuration rejects with error: "Countdown must be positive!"

### EC-9: Hotkey Already Registered by Another Application
**Scenario**: Selected hotkey conflicts with system or another application  
**Expected Behavior**: Application attempts to register, reports if registration fails (keyboard library limitation)

### EC-10: PyGetWindow/PyAutoGUI Not Installed
**Scenario**: User environment lacks optional window automation dependencies  
**Expected Behavior**: Application sets `WINDOW_AUTOMATION_AVAILABLE = False`, disables auto-click feature gracefully, shows warning

### EC-11: Timer Restarted During Active Countdown
**Scenario**: User presses start hotkey while timer is already running  
**Expected Behavior**: Current timer is cancelled, new timer starts immediately with fresh random offset

### EC-12: Multiple Rapid Hotkey Presses
**Scenario**: User rapidly presses start hotkey multiple times  
**Expected Behavior**: Each press cancels previous timer and starts new one (last press wins)

### EC-13: Command Input During Configuration
**Scenario**: User types `/setup` command while already in setup mode  
**Expected Behavior**: Command listener gracefully ignores input or silently fails (setup flow controls input)

---

## Technical Constraints

### TC-1: Platform-Specific Dependencies
- **Constraint**: Application uses `winsound` module (Windows-only)
- **Impact**: No macOS/Linux support without significant refactoring

### TC-2: Global Hotkey Registration
- **Constraint**: `keyboard` library requires appropriate OS permissions
- **Impact**: May require administrator privileges on some Windows configurations

### TC-3: Window Automation Limitations
- **Constraint**: `pygetwindow` and `pyautogui` are optional dependencies
- **Impact**: Auto-click feature gracefully degrades if not installed

### TC-4: Thread Safety
- **Constraint**: Multiple threads access global state (`config`, `current_timer`, `stop_progress`)
- **Impact**: Must carefully manage thread lifecycle to prevent race conditions

### TC-5: JSON Configuration Format
- **Constraint**: Configuration persisted as plain text JSON
- **Impact**: No encryption; users should not store sensitive data

---

## Dependencies

### Required Python Packages
```
keyboard==0.13.5          # Hotkey detection and registration
pyinstaller==6.11.1       # Packaging to standalone executable
```

### Optional Python Packages
```
pygetwindow==0.0.9        # Window enumeration (for auto-click)
pyautogui==0.9.54         # Mouse automation (for auto-click)
```

### Standard Library Modules
- `threading` - Timer and background command listener
- `winsound` - Windows system sound playback
- `json` - Configuration persistence
- `os`, `sys` - File path resolution
- `time` - Timing and delays
- `random` - Random offset calculation

---

## Data Model

### Configuration Schema (`timer_config.json`)

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

**Field Descriptions**:
- `trigger_key` (string): Keyboard key name for start/reset action
- `stop_key` (string): Keyboard key name for stop action
- `countdown_seconds` (integer): Base countdown duration in seconds
- `random_offset_seconds` (integer): ±N seconds random variation
- `auto_click_windows` (boolean): Whether to enable auto-click feature
- `selected_window_titles` (array|null): 
  - `null` = click all MapleRoyals windows
  - `[]` or `false` = auto-click disabled
  - `["title1", "title2"]` = click only specified windows

### Global State Variables

```python
current_timer: threading.Timer | None      # Active countdown timer
actual_countdown: int                      # Calculated time with offset
timer_start_time: float | None             # Unix timestamp of start
progress_thread: threading.Thread | None   # Progress bar display thread
stop_progress: bool                        # Flag to terminate progress thread
config: dict                               # Loaded configuration object
```

---

## Success Criteria

### Baseline Success
- ✅ Application launches and prompts for configuration on first run
- ✅ Hotkeys successfully start/stop timer
- ✅ Timer expires and plays sound
- ✅ Configuration persists across restarts

### Full Feature Success
- ✅ Random offset varies timer duration each cycle
- ✅ Progress bar displays accurate countdown
- ✅ Auto-click successfully triggers MapleRoyals windows
- ✅ User can reconfigure via `/setup` command
- ✅ ESC quick-menu allows rapid countdown adjustment

### Quality Success
- ✅ No crashes during 1-hour continuous operation
- ✅ Hotkey response feels instant (< 100ms perceived)
- ✅ Executable size < 20MB (single-file package)
- ✅ First-time user completes setup without documentation

---

## Out of Scope

The following features are explicitly **not** included in this specification:

1. **Cross-platform support** - macOS/Linux compatibility
2. **Custom sound files** - User-provided audio files (only system beep)
3. **Multiple timer profiles** - Work/rest/gaming presets
4. **Timer history logging** - Persistent record of past countdowns
5. **System tray icon** - Minimize to tray functionality
6. **Timer pause/resume** - Only start/stop/reset supported
7. **Network synchronization** - Multi-device timer coordination
8. **GUI interface** - Pure console-based application
9. **Scheduled timers** - Future/calendar-based timing
10. **Scripting/plugin system** - Extensibility for custom actions

---

## Assumptions

1. **Windows Environment**: Users are running Windows 10 or later
2. **Keyboard Access**: Users have functional keyboard with configurable keys
3. **Admin Privileges**: Users can grant necessary permissions for global hotkeys
4. **English Locale**: Error messages and UI text are in English
5. **Single User**: No multi-user or concurrent-session requirements
6. **Local Storage**: Users have write permissions in application directory
7. **MapleRoyals Game**: Window titles contain exact string "MapleRoyals"
8. **Display Availability**: Console output is visible (not headless)

---

## Glossary

- **Hotkey**: A keyboard shortcut that triggers an action globally (even when application is not focused)
- **Auto-click**: Automated mouse click and keyboard press on game window
- **Random Offset**: Time variation applied to base countdown duration
- **Progress Bar**: Visual ASCII representation of timer completion percentage
- **Configuration Persistence**: Storing user settings to disk for future sessions
- **Window Handle**: OS-level identifier for a graphical window (HWND on Windows)
- **Daemon Thread**: Background thread that automatically terminates when main program exits
- **PyInstaller**: Tool for packaging Python applications as standalone executables
- **System Beep**: Native OS sound alert (not requiring external audio files)

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-03  
**Author**: Reverse-engineered from existing implementation (`timer.py`)
