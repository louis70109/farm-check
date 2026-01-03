# Research: Timer Application

**Feature**: Timer Application  
**Date**: 2026-01-03  
**Status**: Complete

## Research Summary

This document consolidates research findings for the Timer Application project. Since this is a **reverse-engineered specification from existing code**, most technical decisions have already been made and implemented. This research documents those decisions and their rationale.

---

## 1. Technology Stack Decisions

### Python as Primary Language

**Decision**: Python 3.8+  
**Rationale**:
- Rapid development for desktop utilities
- Excellent library ecosystem for system interaction (`keyboard`, `winsound`)
- PyInstaller provides straightforward single-file executable packaging
- Cross-platform potential (though currently Windows-only)

**Alternatives Considered**:
- **C#/.NET**: Better Windows integration, but higher complexity for simple utility
- **Go**: Fast compilation and small binaries, but weaker GUI/system libraries
- **JavaScript/Electron**: Cross-platform, but much larger executable size

**Status**: ✅ Implemented

---

### Hotkey Library: `keyboard`

**Decision**: Use `keyboard==0.13.5`  
**Rationale**:
- Global hotkey registration (works when app not focused)
- Cross-platform support (Windows, macOS, Linux)
- Simple API: `keyboard.add_hotkey()`, `keyboard.read_event()`
- Active maintenance and good documentation

**Alternatives Considered**:
- **pynput**: Similar capabilities, but less intuitive API for hotkey registration
- **pyHook**: Windows-only, outdated, Python 2 legacy
- **Custom ctypes/Win32 API**: More control, but significantly more complex

**Status**: ✅ Implemented

---

### Window Automation: `pygetwindow` + `pyautogui`

**Decision**: Use as **optional dependencies** for auto-click feature  
**Rationale**:
- `pygetwindow`: Enumerate and interact with OS windows
- `pyautogui`: Mouse/keyboard automation
- Made optional to allow core timer functionality without these heavy dependencies
- Graceful degradation if not installed

**Alternatives Considered**:
- **win32gui (pywin32)**: More powerful but Windows-only and complex API
- **UIAutomation**: Professional automation framework, overkill for this use case
- **No automation**: Auto-click is enhancement, not core requirement

**Status**: ✅ Implemented (optional)

---

### Configuration Storage: JSON

**Decision**: Plain JSON file (`timer_config.json`)  
**Rationale**:
- Human-readable and editable
- Native Python support via `json` module
- Simple schema suitable for this use case
- No encryption needed (no sensitive data)

**Alternatives Considered**:
- **INI file**: Less flexible for nested structures (window selections)
- **YAML**: Additional dependency, overkill for simple config
- **SQLite**: Overhead for simple key-value storage
- **Registry (Windows)**: Platform-specific, harder to debug

**Status**: ✅ Implemented

---

### Sound Alert: `winsound`

**Decision**: Use Windows system beep (`winsound.MessageBeep`)  
**Rationale**:
- No external audio files required
- Works immediately on all Windows systems
- Standard library module (no additional dependencies)
- Lightweight and reliable

**Alternatives Considered**:
- **Custom audio files + pygame/playsound**: More flexible but requires audio file management
- **System bell (\a)**: Less reliable, often disabled on modern systems
- **External audio player (subprocess)**: Fragile and platform-dependent

**Status**: ✅ Implemented

---

## 2. Architecture Decisions

### Threading Model

**Decision**: Multi-threaded design with three threads:
1. **Main thread**: Hotkey listener (blocking `keyboard.wait()`)
2. **Timer thread**: `threading.Timer` for countdown
3. **Progress thread**: Real-time display updates
4. **Command listener thread**: Background input monitoring for `/setup`

**Rationale**:
- Hotkey listener must block without interfering with timer
- Progress bar needs periodic updates without blocking execution
- Command listener enables runtime reconfiguration

**Considerations**:
- Thread-safe access to global state (`current_timer`, `config`, `stop_progress`)
- Daemon threads for automatic cleanup on exit
- No complex synchronization primitives needed (simple flag-based coordination)

**Status**: ✅ Implemented

---

### Global State Management

**Decision**: Use module-level global variables for shared state  
**Rationale**:
- Simple mental model for small application
- All state is centralized and easy to track
- No need for class-based state management at this scale

**Global Variables**:
```python
current_timer: threading.Timer | None
actual_countdown: int
timer_start_time: float | None
progress_thread: threading.Thread | None
stop_progress: bool
config: dict
```

**Trade-offs**:
- ❌ Less testable (globals complicate unit testing)
- ❌ Potential for race conditions if not careful
- ✅ Simple and direct for single-instance application
- ✅ No over-engineering for current scope

**Status**: ✅ Implemented

---

### Configuration Path Resolution

**Decision**: Context-dependent configuration location:
- **Script mode** (`.py`): Current working directory
- **Executable mode** (`.exe`): Same directory as executable

**Rationale**:
- Users expect config next to executable
- Avoids polluting user home directory
- Portable (can move exe + config together)

**Implementation**:
```python
if getattr(sys, 'frozen', False):
    # Running as exe
    return os.path.join(os.path.dirname(sys.executable), CONFIG_FILE)
else:
    # Running as script
    return CONFIG_FILE  # Current directory
```

**Status**: ✅ Implemented

---

## 3. Feature Implementation Research

### Random Time Offset (Anti-Detection)

**Decision**: Apply random offset at timer start, not statically  
**Rationale**:
- Each timer cycle gets fresh randomization
- Prevents predictable patterns across multiple cycles
- Simple implementation: `actual = base + random.randint(-offset, +offset)`

**Validation**:
- Offset must be non-negative (0 allowed to disable)
- Offset must be less than base countdown (prevent negative total time)

**Display Strategy**:
- Show actual countdown time with offset breakdown
- Example: `Timer started: 127s (base: 130s, offset: -3s)`
- Provides transparency while maintaining randomness

**Status**: ✅ Implemented

---

### Progress Bar Display

**Decision**: In-place console update using `\r` (carriage return)  
**Rationale**:
- No external GUI library required
- Works in standard Windows console
- Updates smoothly at 2 Hz (0.5s interval)

**Visual Design**:
```
[████████████████░░░░░░░░░░░░░░]  53.2% | 01:01 remaining
```

**Components**:
- **Bar**: 30 characters (█ filled, ░ empty)
- **Percentage**: 1 decimal place precision
- **Time**: MM:SS format

**Status**: ✅ Implemented

---

### Auto-Click Sequence Design

**Decision**: Randomized, human-like click pattern with animated mouse movement  
**Rationale**:
- Shuffle window order (unpredictable sequence)
- **Animated mouse movement** (0.3-0.8 seconds glide to each window)
- Random click positions (±30% offset from center)
- Natural reaction time pause after movement (0.05-0.15 seconds)
- Variable inter-click delays (0.5-2.5 seconds)
- Total sequence ~5-8 seconds (mimics human speed)

**Human-like Mouse Behavior**:
- Use `pyautogui.moveTo(x, y, duration=...)` for smooth animation
- Random movement duration (0.3-0.8 seconds) to simulate different mouse speeds
- Pause after reaching target (human reaction time before clicking)
- Avoids instant teleportation that looks robotic

**Safety Measures**:
- Validate window handles before interaction
- Skip invalid/closed windows gracefully
- Filter by user selection (if configured)

**Fallback Strategy**:
1. Try `pyautogui.moveTo()` then `click()` to activate window (most human-like)
2. Fall back to `window.activate()` (API call)
3. Press trigger key regardless of activation success

**Status**: ✅ Implemented

---

### Window Selection UX

**Decision**: Three selection modes:
1. **All windows** (type `/all` or leave `selected_window_titles: null`)
2. **Specific windows** (enter indices like `1,3`)
3. **Disabled** (cancel selection)

**Rationale**:
- Flexibility for users with multiple game clients
- Balance between convenience (all) and control (specific)
- Clear prompts and validation

**Persistence**:
- Store window titles (not indices) in config
- Handles window closes/reopens gracefully
- Reports missing windows without failing

**Status**: ✅ Implemented

---

### Runtime Reconfiguration

**Decision**: `/setup` command via background input listener  
**Rationale**:
- Users need to adapt to hotkey conflicts without restarting
- Countdown adjustments common during use

**Implementation**:
- Daemon thread with `input()` loop
- Unregister hotkeys during setup to prevent conflicts
- Stop active timer before reconfiguration
- Re-register hotkeys after completion

**Edge Cases Handled**:
- EOF (Ctrl+D) breaks listener loop
- Exceptions silently ignored (keeps listener alive)
- Setup cancellation (ESC) preserves existing config

**Status**: ✅ Implemented

---

### Auto-Restart Behavior

**Decision**: 5-second countdown with ESC interrupt  
**Rationale**:
- Reduces friction for continuous use
- Quick-adjust menu for common changes
- ESC is universal "cancel" key

**Menu Options on ESC**:
1. Enter number → adjust countdown only
2. Type `/setup` → full reconfiguration
3. Press Enter → restart with current settings

**Status**: ✅ Implemented

---

## 4. Packaging & Distribution

### PyInstaller Configuration

**Decision**: Single-file executable (`--onefile`)  
**Rationale**:
- Easier distribution (one file vs. directory)
- No manual dependency management for users
- Self-contained (no Python installation required)

**Parameters**:
```bash
pyinstaller --onefile --console timer.py
```

- `--onefile`: Bundle everything into single `.exe`
- `--console`: Show terminal window (required for configuration prompts)

**Limitations**:
- Larger file size (~10-15MB vs. ~2MB for `--onedir`)
- Slower startup (extracts to temp directory)
- Acceptable trade-off for convenience

**Status**: ✅ Implemented

---

### GitHub Actions Automation

**Decision**: Auto-build on git tags (e.g., `v1.0.0`)  
**Rationale**:
- Version tags trigger releases
- Consistent build environment
- Automated artifact upload to GitHub Releases

**Configuration** (`.github/workflows/build.yml`):
- Trigger: `push: tags: v*`
- Platform: `runs-on: windows-latest`
- Upload: `softprops/action-gh-release@v1`

**Permissions Fix**:
- Required `contents: write` permission for release creation
- Issue discovered and resolved during initial setup

**Status**: ✅ Implemented

---

## 5. Known Limitations & Future Research

### Cross-Platform Support

**Current Status**: Windows-only  
**Blocker**: `winsound` module

**Research for Future**:
- **macOS**: Use `afplay /System/Library/Sounds/Ping.aiff`
- **Linux**: Use `paplay` or `aplay` for system sounds
- **Abstraction**: Create sound adapter pattern

**Priority**: Low (current user base is Windows-only)

---

### Hotkey Conflict Detection

**Current Status**: No conflict detection  
**Issue**: If hotkey already registered, silently fails or unpredictable behavior

**Research for Future**:
- `keyboard` library provides no conflict detection API
- Possible workaround: Try-except on `add_hotkey()` and prompt user
- Alternative: Use more obscure default keys (e.g., `F13-F24`)

**Priority**: Medium (users can work around by choosing different keys)

---

### Configuration Migration

**Current Status**: No versioning or migration  
**Risk**: Future config schema changes break existing configs

**Research for Future**:
- Add `"config_version": 1` field to JSON
- Implement migration functions for schema updates
- Graceful handling of unknown fields

**Priority**: Low (current schema is stable)

---

## 6. Best Practices Applied

### Error Handling

**Implemented**:
- Configuration file corruption → delete and recreate
- Invalid window handles → skip gracefully
- Missing optional dependencies → feature degradation
- User input validation → clear error messages

---

### User Experience

**Implemented**:
- Clear prompts with examples
- Sensible defaults (130s, 0s offset, Page Up/Down)
- ESC cancellation everywhere
- Real-time feedback (progress bar, status messages)

---

### Code Organization

**Implemented**:
- Function-based organization (no over-engineering)
- Clear function names describing purpose
- Separation of concerns (config, timer, hotkeys, automation)
- Inline comments for complex logic

---

## Conclusion

All technical decisions for the Timer Application have been researched, implemented, and validated through actual use. This document serves as a record of those decisions for future maintenance and potential enhancements.

**No further research is required for current feature set.**

**Next Steps**: Proceed to Phase 1 (Data Model & Contracts)
