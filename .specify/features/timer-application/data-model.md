# Data Model: Timer Application

**Feature**: Timer Application  
**Date**: 2026-01-03  
**Source**: Reverse-engineered from `timer.py`

## Overview

The Timer Application uses a simple data model with minimal persistence. The primary data structure is the configuration object, stored as JSON. Runtime state is managed through module-level global variables.

---

## 1. Persistent Data (Configuration)

### Configuration Schema

**File**: `timer_config.json`  
**Location**: Same directory as executable (`.exe`) or current working directory (`.py`)  
**Format**: JSON

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

### Field Definitions

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `trigger_key` | string | Yes | `"page up"` | Valid keyboard key name | Hotkey to start/reset timer |
| `stop_key` | string | Yes | `"page down"` | Valid keyboard key name, must differ from `trigger_key` | Hotkey to stop timer |
| `countdown_seconds` | integer | Yes | `130` | `> 0` | Base countdown duration in seconds |
| `random_offset_seconds` | integer | Yes | `0` | `>= 0`, `< countdown_seconds` | Random time variation (±N seconds) |
| `auto_click_windows` | boolean | Yes | `false` | `true` or `false` | Enable auto-click feature |
| `selected_window_titles` | array\|null | Yes | `null` | Array of strings or `null` | Window titles to auto-click (`null` = all windows) |

### Validation Rules

#### Hotkey Constraints
- **Unique**: `trigger_key` ≠ `stop_key`
- **Valid**: Must be recognized by `keyboard` library
- **Examples**: `"page up"`, `"f1"`, `"ctrl+shift+t"`

#### Countdown Constraints
- **Positive**: `countdown_seconds > 0`
- **Offset Range**: `0 <= random_offset_seconds < countdown_seconds`
- **Reason**: Prevents negative actual countdown times

#### Window Selection Constraints
- **Null** → Click all MapleRoyals windows
- **Empty Array** → Invalid (treated as disabled)
- **String Array** → Click only specified window titles
- **Window Title Format**: Exact match required (e.g., `"MapleRoyals - Character1"`)

### Configuration Lifecycle

```
┌─────────────────────────────────────────────────────┐
│ Application Startup                                 │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ File exists? │
        └──────┬───────┘
               │
       ┌───────┴────────┐
       │                │
      Yes              No
       │                │
       ▼                ▼
   ┌────────┐      ┌────────────┐
   │ Load   │      │ Run setup  │
   │ config │      │ wizard     │
   └───┬────┘      └─────┬──────┘
       │                 │
       ▼                 ▼
   ┌────────┐      ┌────────────┐
   │ Parse  │      │ Create new │
   │ JSON   │      │ config     │
   └───┬────┘      └─────┬──────┘
       │                 │
       ├─────────────────┘
       │
       ▼
   ┌────────────┐
   │ Validate   │
   │ schema     │
   └─────┬──────┘
         │
    ┌────┴────┐
    │         │
  Valid    Invalid
    │         │
    ▼         ▼
┌───────┐  ┌──────────┐
│ Use   │  │ Delete & │
│ config│  │ recreate │
└───────┘  └──────────┘
```

### Error Handling

| Error Condition | Behavior |
|-----------------|----------|
| File not found | Run first-time setup wizard |
| Invalid JSON syntax | Log error, delete file, run setup |
| Missing required field | Use default value, save config |
| Invalid field value | Reject during setup, prompt re-entry |
| File write failure | Log error, continue with in-memory config |

---

## 2. Runtime State (Global Variables)

### Timer State

```python
current_timer: threading.Timer | None = None
```

**Purpose**: Active countdown timer thread  
**Lifecycle**:
- `None` → No timer running
- `threading.Timer` instance → Timer active
- Replaced on each start/reset
- Cancelled on stop or application exit

**Operations**:
- `start_timer()` → Creates and starts new `Timer` instance
- `stop_timer()` → Calls `.cancel()` and sets to `None`
- `on_timeout()` → Called when timer reaches zero

---

### Actual Countdown

```python
actual_countdown: int = 0
```

**Purpose**: Stores the calculated countdown duration (base + random offset)  
**Calculation**: `base_time ± random.randint(0, offset)`  
**Example**: Base=130s, Offset=5s → Actual could be 125-135s

**Used By**:
- `show_progress()` → Calculate percentage and remaining time
- Display logic → Show user the actual time being counted

---

### Timer Start Time

```python
timer_start_time: float | None = None
```

**Purpose**: Unix timestamp when timer started  
**Type**: `float` from `time.time()`  
**Used By**:
- `show_progress()` → Calculate elapsed time
- Progress bar → Compute remaining time

**Lifecycle**:
- `None` → Timer not running
- `float` → Timer active (timestamp in seconds since epoch)

---

### Progress Thread Management

```python
progress_thread: threading.Thread | None = None
stop_progress: bool = False
```

**Purpose**: Control progress bar display thread  
**Pattern**: Flag-based thread termination

**Lifecycle**:
```
Start Timer:
  stop_progress = False
  progress_thread = Thread(target=show_progress)
  progress_thread.start()

Stop Timer:
  stop_progress = True
  progress_thread.join(timeout=1.0)
  progress_thread = None
```

**Thread-Safety**: Single writer (main thread), single reader (progress thread)

---

### Configuration Object

```python
config: dict = {}
```

**Purpose**: In-memory configuration loaded from JSON  
**Structure**: Matches JSON schema (see Section 1)  
**Mutability**: Modified during setup or quick-adjust

**Access Pattern**:
- Read: Multiple threads (hotkey callbacks, timer, command listener)
- Write: Main thread during configuration only
- **No locking required**: Writes occur only when timer is stopped

---

## 3. Entities and Relationships

### Entity: Configuration

**Attributes**:
- `trigger_key`: string
- `stop_key`: string  
- `countdown_seconds`: int
- `random_offset_seconds`: int
- `auto_click_windows`: bool
- `selected_window_titles`: array|null

**Operations**:
- `load_config()`: File → dict
- `save_config(dict)`: dict → File
- `setup_config()`: Interactive → dict

**Validation**:
- Keys must be unique
- Countdown must be positive
- Offset must be less than countdown
- Window titles must be exact matches

---

### Entity: Timer Instance

**Attributes**:
- `actual_countdown`: int (calculated)
- `start_time`: float (timestamp)
- `base_time`: int (from config)
- `offset`: int (random value)

**Operations**:
- `start_timer()`: Create new instance
- `stop_timer()`: Cancel and destroy
- `on_timeout()`: Callback when complete

**Lifecycle**: Ephemeral (recreated on each start)

---

### Entity: Window Selection

**Attributes**:
- `title`: string (window title)
- `handle`: int (OS window handle)
- `position`: (x, y, width, height)

**Operations**:
- `gw.getAllWindows()`: Enumerate all windows
- Filter by title contains "MapleRoyals"
- Click at random position within bounds

**Validation**:
- Handle must be valid
- Window must be accessible
- Gracefully skip if closed

---

## 4. State Transitions

### Timer State Machine

```
┌─────────┐
│  IDLE   │◄──────────────┐
└────┬────┘               │
     │                    │
     │ start_timer()      │ stop_timer()
     │                    │
     ▼                    │
┌──────────┐              │
│ RUNNING  │──────────────┤
└────┬─────┘              │
     │                    │
     │ timeout            │
     │                    │
     ▼                    │
┌──────────┐              │
│ EXPIRED  │──────────────┘
└──────────┘
     │
     │ auto-restart (5s)
     │ or ESC → configure
     │
     └─────► back to IDLE or RUNNING
```

### Configuration State Machine

```
┌──────────────┐
│ NOT_LOADED   │
└──────┬───────┘
       │ load_config()
       │
       ▼
┌──────────────┐
│   LOADED     │◄──────────────┐
└──────┬───────┘               │
       │                       │
       │ /setup or ESC         │
       │                       │
       ▼                       │
┌──────────────┐               │
│ CONFIGURING  │               │
└──────┬───────┘               │
       │                       │
       │ save_config()         │
       │                       │
       └───────────────────────┘
```

---

## 5. Data Flow

### Start Timer Flow

```
User presses trigger_key
    ↓
keyboard.on_hotkey() detects
    ↓
start_timer() called
    ↓
Read config['countdown_seconds']
Read config['random_offset_seconds']
    ↓
Calculate: actual_countdown = base ± random(offset)
    ↓
Set timer_start_time = time.time()
    ↓
Create threading.Timer(actual_countdown, on_timeout)
    ↓
Start progress_thread
    ↓
Timer runs...
```

### Auto-Click Flow

```
Timer expires
    ↓
on_timeout() called
    ↓
Check config['auto_click_windows']
    ↓
If enabled:
    ↓
    gw.getAllWindows() → Filter "MapleRoyals"
    ↓
    Filter by config['selected_window_titles']
    ↓
    Shuffle window order
    ↓
    For each window:
        Click random position
        Press config['trigger_key']
        Wait random delay (0.5-2.5s)
```

---

## 6. Data Validation

### Input Validation

| Input | Validation | Error Handling |
|-------|------------|----------------|
| Hotkey (keyboard press) | Captured via `keyboard.read_event()` | ESC cancels |
| Countdown seconds (user input) | `int()`, `> 0` | Prompt re-entry |
| Offset seconds (user input) | `int()`, `>= 0`, `< countdown` | Prompt re-entry |
| Window selection (user input) | Parse comma-separated indices or `/all` | Invalid indices skipped |
| JSON file | `json.load()` | Delete file on parse error |

### Runtime Validation

| Operation | Validation | Fallback |
|-----------|------------|----------|
| Window handle access | Try `window.size`, `window.title` | Skip window |
| Hotkey registration | `keyboard.add_hotkey()` | No explicit check (library limitation) |
| Config file write | Try `open()`, `json.dump()` | Log error, continue |

---

## 7. Data Constraints Summary

### Hard Constraints (Enforced)
- ✅ Hotkeys must be unique
- ✅ Countdown must be positive integer
- ✅ Offset must be less than countdown
- ✅ Window titles must be strings

### Soft Constraints (Recommended)
- ⚠️ Hotkeys should not conflict with system shortcuts
- ⚠️ Countdown should be reasonable (e.g., 10-600 seconds)
- ⚠️ Offset should be meaningful (e.g., 1-10 seconds)

### Assumptions
- 🔹 User has write permissions in application directory
- 🔹 MapleRoyals window titles contain exact string "MapleRoyals"
- 🔹 Windows remain accessible during auto-click sequence
- 🔹 System allows global hotkey registration

---

## Conclusion

The Timer Application uses a minimal data model optimized for simplicity and reliability. Persistent configuration is limited to user preferences, while runtime state is managed through straightforward global variables. This design supports the application's scope without unnecessary complexity.

**Key Characteristics**:
- **Simple**: One JSON file, seven global variables
- **Robust**: Graceful error handling throughout
- **Transparent**: All state visible and understandable
- **Maintainable**: Clear lifecycle and validation rules
