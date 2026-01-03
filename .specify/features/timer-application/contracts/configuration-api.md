# Configuration API Contract

**Version**: 1.0  
**Module**: Configuration Management  
**Date**: 2026-01-03

## Overview

This contract defines the interface for configuration management in the Timer Application. Since this is a standalone Python script (not a web API), these are **function contracts** rather than HTTP endpoints.

---

## 1. Load Configuration

### Function Signature

```python
def load_config() -> dict | None
```

### Description

Loads configuration from the JSON file stored in the application directory.

### Parameters

None

### Returns

| Type | Description |
|------|-------------|
| `dict` | Successfully loaded and parsed configuration object |
| `None` | File does not exist or parsing failed |

### Configuration Schema

```python
{
    "trigger_key": str,              # Hotkey to start/reset timer
    "stop_key": str,                 # Hotkey to stop timer
    "countdown_seconds": int,        # Base countdown duration
    "random_offset_seconds": int,    # Random time variation (±N seconds)
    "auto_click_windows": bool,      # Enable auto-click feature
    "selected_window_titles": list[str] | None  # Window titles to click (null = all)
}
```

### Error Handling

| Condition | Behavior |
|-----------|----------|
| File not found | Return `None` |
| Invalid JSON | Print error message, return `None` |
| Missing fields | Return partial dict (caller handles defaults) |
| File read permission error | Print error message, return `None` |

### Side Effects

- Reads from filesystem
- Prints error messages to stdout

### Example Usage

```python
config = load_config()
if config:
    print("Configuration loaded successfully")
else:
    print("No configuration found, running setup...")
    config = setup_config()
```

---

## 2. Save Configuration

### Function Signature

```python
def save_config(config: dict) -> bool
```

### Description

Saves configuration to JSON file in the application directory.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `config` | `dict` | Yes | Configuration object matching schema |

### Returns

| Type | Description |
|------|-------------|
| `bool` | `True` if save succeeded, `False` if failed |

### Required Fields

All fields must be present in the `config` dictionary:

```python
{
    "trigger_key": str,
    "stop_key": str,
    "countdown_seconds": int,
    "random_offset_seconds": int,
    "auto_click_windows": bool,
    "selected_window_titles": list[str] | None
}
```

### Error Handling

| Condition | Behavior |
|-----------|----------|
| File write permission error | Print error message, return `False` |
| Directory does not exist | Attempt to create, return `False` if fails |
| Invalid config format | No validation (caller responsible) |

### Side Effects

- Writes to filesystem
- Prints confirmation or error message to stdout

### Example Usage

```python
config = {
    "trigger_key": "f1",
    "stop_key": "f2",
    "countdown_seconds": 120,
    "random_offset_seconds": 5,
    "auto_click_windows": True,
    "selected_window_titles": ["MapleRoyals - Main"]
}

if save_config(config):
    print("Configuration saved")
else:
    print("Failed to save configuration")
```

---

## 3. Setup Configuration (Interactive)

### Function Signature

```python
def setup_config() -> dict | None
```

### Description

Interactive wizard that guides user through configuration setup. Captures keyboard input for hotkeys and validates all settings.

### Parameters

None (interactive function)

### Returns

| Type | Description |
|------|-------------|
| `dict` | Complete configuration object if setup succeeded |
| `None` | Setup was cancelled (user pressed ESC) |

### User Interaction Flow

```
1. Prompt: "Press the key for START/RESET timer"
   → User presses key
   → Display selected key

2. Prompt: "Press the key for STOP timer"
   → User presses key
   → Validate: must differ from trigger key
   → Display selected key

3. Prompt: "Countdown seconds (default 130)"
   → User types number or presses Enter
   → Validate: must be positive integer
   → Display selected value

4. Prompt: "Random offset ±N seconds (default 0)"
   → User types number or presses Enter
   → Validate: non-negative, less than countdown
   → Display selected value

5. Prompt: "Enable auto-click? (type '/enable' or Enter)"
   → If enabled:
      → Call select_windows()
      → Display selected windows

6. Return complete configuration dictionary
```

### Validation Rules

| Field | Validation | Error Message |
|-------|------------|---------------|
| `trigger_key` | Must be valid key | (captured from keyboard) |
| `stop_key` | Must differ from `trigger_key` | "START and STOP keys cannot be the same!" |
| `countdown_seconds` | `> 0` | "Countdown must be positive!" |
| `random_offset_seconds` | `>= 0`, `< countdown_seconds` | "Offset must be less than countdown time!" |

### Cancellation

User can press **ESC** at any prompt to cancel setup. Function returns `None`.

### Side Effects

- Reads from stdin
- Writes to stdout
- Blocks execution until complete
- May call `select_windows()` if auto-click enabled

### Example Usage

```python
print("No configuration found. Starting setup wizard...")
config = setup_config()

if config:
    save_config(config)
    print("Setup complete!")
else:
    print("Setup cancelled. Using defaults.")
```

---

## 4. Get Configuration Path

### Function Signature

```python
def get_config_path() -> str
```

### Description

Returns the absolute path to the configuration file, accounting for whether the application is running as a script or packaged executable.

### Parameters

None

### Returns

| Type | Description |
|------|-------------|
| `str` | Absolute path to `timer_config.json` |

### Path Resolution Logic

```python
if getattr(sys, 'frozen', False):
    # Running as .exe
    return os.path.join(os.path.dirname(sys.executable), "timer_config.json")
else:
    # Running as .py script
    return "timer_config.json"  # Current directory
```

### Example Usage

```python
config_path = get_config_path()
print(f"Configuration file: {config_path}")

# Expected outputs:
# Script mode: "timer_config.json"
# Executable mode: "C:\Users\Name\Desktop\timer_config.json"
```

---

## 5. Select Windows (Auto-Click)

### Function Signature

```python
def select_windows() -> list[str] | None | bool
```

### Description

Interactive window selection for auto-click feature. Enumerates MapleRoyals windows and lets user choose which to automate.

### Parameters

None (interactive function)

### Returns

| Type | Description |
|------|-------------|
| `None` | Click all MapleRoyals windows (user typed `/all`) |
| `list[str]` | List of specific window titles to click |
| `False` | Auto-click disabled (user cancelled selection) |

### User Interaction Flow

```
1. Find all windows with "MapleRoyals" in title
   → If none found: Return None (will click all when available)

2. Display numbered list of windows:
   [1] MapleRoyals - Character1
   [2] MapleRoyals - Character2
   [3] MapleRoyals - Character3

3. Prompt: "Type '/all' for all, or enter numbers (e.g., '1,3')"
   → User types selection
   → Parse and validate indices
   → Return list of window titles

4. Handle special inputs:
   → "/all" → Return None
   → "" (empty) → Return False
   → "1,3" → Return ["MapleRoyals - Character1", "MapleRoyals - Character3"]
```

### Window Validation

- Filters out duplicate window handles
- Verifies window is accessible (can read `.size` and `.title`)
- Skips invalid or crashed windows

### Error Handling

| Condition | Behavior |
|-----------|----------|
| No MapleRoyals windows | Print warning, return `None` |
| Invalid index (e.g., "10" when only 3 windows) | Skip invalid index, use valid ones |
| No valid indices | Print message, return `False` |
| pygetwindow not installed | Return `None` (caller handles gracefully) |

### Example Usage

```python
if WINDOW_AUTOMATION_AVAILABLE:
    selected = select_windows()
    
    if selected is None:
        print("Will click all MapleRoyals windows")
    elif selected is False:
        print("Auto-click disabled")
    else:
        print(f"Will click {len(selected)} specific windows")
```

---

## Contract Versioning

**Version**: 1.0  
**Status**: Stable  
**Breaking Changes**: None

### Future Compatibility

If configuration schema changes in future versions:

1. Add `"config_version": 1` field to JSON
2. Implement migration function: `migrate_config(old_dict, from_version, to_version) -> dict`
3. Call migration in `load_config()` when version mismatch detected

---

## Testing Contract

### Unit Test Requirements

| Function | Test Cases |
|----------|------------|
| `load_config()` | File exists, file missing, invalid JSON, partial config |
| `save_config()` | Valid config, write permission error, directory creation |
| `get_config_path()` | Script mode, executable mode |

### Integration Test Requirements

| Scenario | Expected Behavior |
|----------|-------------------|
| First-time setup | `load_config()` → `None`, `setup_config()` → dict, `save_config()` → `True` |
| Subsequent runs | `load_config()` → dict with all fields |
| Configuration change | Modify dict, `save_config()`, restart, `load_config()` → updated dict |

---

## Security Considerations

1. **No Sensitive Data**: Configuration should not contain passwords or API keys
2. **File Permissions**: Config file is plain text (no encryption)
3. **Input Validation**: All user inputs validated before saving
4. **Path Traversal**: Config path is fixed (no user-provided paths)

---

## Performance Characteristics

| Operation | Expected Time | Complexity |
|-----------|---------------|------------|
| `load_config()` | < 10ms | O(1) - single file read |
| `save_config()` | < 50ms | O(1) - single file write |
| `setup_config()` | User-dependent | Blocking (interactive) |
| `select_windows()` | < 500ms | O(n) where n = open windows |

---

## Dependencies

- `json` (standard library)
- `os` (standard library)
- `sys` (standard library)
- `keyboard` (external, for setup_config)
- `pygetwindow` (optional, for select_windows)

---

## Conclusion

This contract defines the complete configuration management interface for the Timer Application. All functions follow Python conventions and provide clear error handling and return values.
