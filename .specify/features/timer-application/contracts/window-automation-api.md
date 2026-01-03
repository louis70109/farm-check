# Window Automation API Contract

**Version**: 1.0  
**Module**: Window Automation (Auto-Click)  
**Date**: 2026-01-03

## Overview

This contract defines the interface for window automation features in the Timer Application. This module is **optional** and requires `pygetwindow` and `pyautogui` dependencies.

---

## 1. Click MapleRoyals Windows

### Function Signature

```python
def click_maple_windows() -> None
```

### Description

Finds and interacts with MapleRoyals game windows using human-like timing and randomization. Respects user's window selection from configuration.

### Parameters

None (uses global `config` object)

### Required Global State

| Variable | Type | Purpose |
|----------|------|---------|
| `config` | `dict` | Contains `trigger_key`, `auto_click_windows`, `selected_window_titles` |
| `WINDOW_AUTOMATION_AVAILABLE` | `bool` | Flag indicating if dependencies are installed |

### Preconditions

- `WINDOW_AUTOMATION_AVAILABLE` must be `True`
- `config['auto_click_windows']` should be `True` (caller's responsibility to check)
- At least one MapleRoyals window should be running (gracefully handles absence)

### Behavior

```python
1. Find all windows with "MapleRoyals" in title using gw.getAllWindows()
2. Filter out invalid/duplicate windows (check handle, size, title accessibility)
3. If config['selected_window_titles'] is not None:
   - Filter windows by matching titles
   - Report which selected windows are not running
4. If no valid windows found:
   - Print message and return early
5. Shuffle windows list (randomize order)
6. For each window:
   a. Calculate random click position (±30% offset from center)
   b. Click on that position to activate window
   c. Wait 0.2 seconds for activation
   d. Press trigger key (config['trigger_key'])
   e. Print progress: "[X/Y] Clicked: {window_title}"
   f. Wait random delay (0.5-2.5 seconds)
7. Print: "Auto-click sequence completed"
```

### Window Selection Logic

| `selected_window_titles` | Behavior |
|--------------------------|----------|
| `None` | Click all MapleRoyals windows |
| `["Title1", "Title2"]` | Click only windows with exact title matches |
| `[]` or `False` | Caller should not invoke this function |

### Randomization Strategy

**Click Position**:
```python
window_center_x = window.left + window.width // 2
window_center_y = window.top + window.height // 2

offset_x = random.uniform(-0.3, 0.3) * window.width
offset_y = random.uniform(-0.3, 0.3) * window.height

click_x = window_center_x + offset_x
click_y = window_center_y + offset_y
```

**Inter-Click Delay**:
- Total sequence time: ~5 seconds
- Distribute delays across windows
- Each delay: 0.5-2.5 seconds (random)
- Last delay: Remaining time (minimum 0.3s)

### Window Validation

Each window must pass:
1. **Handle uniqueness**: `window._hWnd not in seen_handles`
2. **Accessibility**: Can read `window.size` without exception
3. **Title readable**: Can access `window.title` without exception

### Error Handling

| Condition | Behavior |
|-----------|----------|
| No MapleRoyals windows | Print message, return early |
| All windows invalid | Print message, return early |
| Selected windows not found | Print warning, click available ones only |
| Window closes during sequence | Catch exception, skip that window, continue |
| Window activation fails | Print warning, send keypress anyway |
| Dependencies not installed | Caller detects via `WINDOW_AUTOMATION_AVAILABLE` |

### Side Effects

- Moves mouse cursor
- Clicks on screen positions
- Sends keyboard input to windows
- Prints progress messages to stdout
- Takes 5+ seconds to execute (blocking)

### Performance

- **Execution Time**: ~5 seconds for any number of windows
- **Blocking**: Yes (runs synchronously)
- **Thread Context**: Called from timer thread (in `on_timeout()`)

### Example Output

```
Found 3 MapleRoyals window(s)
Starting auto-click sequence...
  [1/3] Clicked: MapleRoyals - Character1
  [2/3] Clicked: MapleRoyals - Character2
  [3/3] Clicked: MapleRoyals - Character3
Auto-click sequence completed
```

### Example Output (Window Not Running)

```
Found 1 of 2 selected window(s)
Not running: MapleRoyals - Character3
Starting auto-click sequence...
  [1/1] Clicked: MapleRoyals - Character1
Auto-click sequence completed
```

---

## 2. Select Windows (Interactive)

### Function Signature

```python
def select_windows() -> list[str] | None | bool
```

### Description

Interactive dialog for selecting which MapleRoyals windows to auto-click. Called during configuration setup.

### Parameters

None (interactive function)

### Preconditions

- `WINDOW_AUTOMATION_AVAILABLE` must be `True`

### Returns

| Return Value | Meaning |
|-------------|---------|
| `None` | User selected `/all` - click all MapleRoyals windows |
| `list[str]` | List of specific window titles (e.g., `["MapleRoyals - Character1"]`) |
| `False` | User cancelled - disable auto-click feature |

### Behavior

```python
1. Find all MapleRoyals windows using gw.getAllWindows()
2. If no windows found:
   - Print: "No MapleRoyals windows currently running"
   - Print: "Will auto-click all MapleRoyals windows when available"
   - Return None
3. Filter valid windows (deduplicate, verify accessibility)
4. Display numbered list:
   Found 3 MapleRoyals window(s):
     [1] MapleRoyals - Character1
     [2] MapleRoyals - Character2
     [3] MapleRoyals - Character3
5. Prompt user:
   "Type '/all' for all windows"
   "Or enter numbers separated by commas (e.g., '1,3' or '2')"
   "Press Enter to cancel: "
6. Parse input:
   - Empty string → Return False
   - "/all" → Return None
   - "1,3" → Parse indices, return list of titles
7. Validate indices (skip invalid, warn user)
8. Return list of selected titles
```

### User Input Examples

| Input | Result |
|-------|--------|
| `<Enter>` | Returns `False` (auto-click disabled) |
| `/all` | Returns `None` (click all windows) |
| `1` | Returns `["MapleRoyals - Character1"]` |
| `1,3` | Returns `["MapleRoyals - Character1", "MapleRoyals - Character3"]` |
| `1,5` | Returns `["MapleRoyals - Character1"]` (5 is invalid, skipped) |
| `10,20` | Returns `False` (all invalid → disable) |

### Error Handling

| Condition | Behavior |
|-----------|----------|
| No windows running | Print warning, return `None` |
| All indices invalid | Print message, return `False` |
| Some indices invalid | Print warning, use valid indices |
| ValueError in parsing | Print "Invalid input", return `False` |
| Window exception during enumeration | Skip window, continue |

### Side Effects

- Reads from stdin
- Writes to stdout
- Blocks execution until user responds
- Enumerates OS windows (may be slow)

### Example Interaction

```
Found 2 MapleRoyals window(s):
  [1] MapleRoyals - Main
  [2] MapleRoyals - Alt

Select windows to auto-click:
  Type '/all' for all windows
  Or enter numbers separated by commas (e.g., '1,3' or '2')
  Press Enter to cancel: 1,2

Selected 2 window(s):
  - MapleRoyals - Main
  - MapleRoyals - Alt
```

---

## 3. Window Automation Availability Check

### Global Flag

```python
WINDOW_AUTOMATION_AVAILABLE: bool
```

### Description

Module-level flag indicating whether window automation dependencies are installed and functional.

### Initialization

```python
try:
    import pygetwindow as gw
    import pyautogui
    WINDOW_AUTOMATION_AVAILABLE = True
except ImportError:
    WINDOW_AUTOMATION_AVAILABLE = False
    print("Warning: pygetwindow or pyautogui not installed. Window automation disabled.")
```

### Usage

```python
if WINDOW_AUTOMATION_AVAILABLE:
    # Offer auto-click option during setup
    selected = select_windows()
else:
    # Skip auto-click feature
    print("Auto-click feature unavailable")
    config['auto_click_windows'] = False
```

---

## Contract Versioning

**Version**: 1.0  
**Status**: Stable  
**Breaking Changes**: None

---

## Window Detection Details

### Window Enumeration

Uses `pygetwindow.getAllWindows()` which returns all top-level windows.

**Filter Criteria**:
1. Title contains "MapleRoyals" (case-sensitive substring match)
2. Window has valid handle (`window._hWnd`)
3. Window properties are accessible (`.size`, `.title` don't throw exceptions)

### Window Handle Deduplication

Multiple window objects may reference the same physical window. Use handle (`_hWnd`) tracking:

```python
seen_handles = set()
for window in all_windows:
    if window._hWnd not in seen_handles:
        seen_handles.add(window._hWnd)
        valid_windows.append(window)
```

### Window Activation Strategy

**Primary Method** (Human-like):
```python
# Click random position within window bounds
pyautogui.click(click_x, click_y)
time.sleep(0.2)  # Wait for activation
```

**Fallback Method** (API call):
```python
try:
    window.activate()
    time.sleep(0.15)
except:
    print("Warning: Could not activate window, sending keypress anyway")
```

---

## Security Considerations

1. **Window Title Matching**: Exact substring match prevents accidental clicks on unrelated windows
2. **Bounds Checking**: Click positions always within window boundaries
3. **User Confirmation**: User must explicitly enable auto-click during setup
4. **Validation**: Each window validated before interaction

---

## Platform Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Windows | ✅ Fully supported | Tested with Windows 10/11 |
| macOS | ⚠️ Partial | `pygetwindow` has limited macOS support |
| Linux | ⚠️ Partial | Depends on X11/Wayland environment |

**Recommendation**: Windows-only application (current scope).

---

## Performance Characteristics

| Operation | Time Complexity | Expected Duration |
|-----------|-----------------|-------------------|
| Window enumeration | O(n) where n = total windows | 50-200ms |
| Window validation | O(1) per window | 1-5ms per window |
| Click sequence | O(m) where m = selected windows | ~5 seconds total |
| Window activation | O(1) | 200ms per window |

---

## Dependencies

### Required
- `pygetwindow>=0.0.9` (window enumeration)
- `pyautogui>=0.9.54` (mouse/keyboard automation)

### Optional Fallback
If dependencies missing:
- Set `WINDOW_AUTOMATION_AVAILABLE = False`
- Disable auto-click feature
- Application continues to function (timer still works)

---

## Testing Considerations

### Unit Testing Challenges
- **Window Enumeration**: Requires actual windows to be running
- **Mouse Clicks**: May interfere with user's system during tests
- **Timing**: Human-like delays make tests slow

### Recommended Approach
- Mock `pygetwindow.getAllWindows()`
- Mock `pyautogui.click()`
- Test window filtering and selection logic
- Integration tests require dedicated test environment

---

## Known Limitations

1. **Title Matching**: Assumes window titles contain exact string "MapleRoyals"
2. **Z-Order**: Does not guarantee window remains activated (user/OS may switch focus)
3. **Multi-Monitor**: Click positions calculated in primary monitor coordinates
4. **Accessibility**: May not work with elevated privilege windows
5. **Timing**: 5-second sequence is approximate (actual time varies)

---

## Future Enhancements (Out of Scope)

- 🔮 Configurable click positions (specific coordinates per window)
- 🔮 Screenshot verification (confirm window content before click)
- 🔮 Advanced anti-detection (variable sequence patterns)
- 🔮 Remote window support (RDP, VNC sessions)
- 🔮 Multi-monitor awareness (explicit monitor targeting)

---

## Conclusion

This contract defines the window automation interface for the Timer Application. The design prioritizes human-like behavior and safety, with comprehensive error handling for real-world window management scenarios.
