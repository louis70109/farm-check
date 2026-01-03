# Timer Control API Contract

**Version**: 1.0  
**Module**: Timer Control & Execution  
**Date**: 2026-01-03

## Overview

This contract defines the interface for timer control operations in the Timer Application. These are internal function contracts for the core timer functionality.

---

## 1. Start Timer

### Function Signature

```python
def start_timer() -> None
```

### Description

Starts or resets the countdown timer. If a timer is already running, cancels it and starts a new one. Applies random offset to countdown duration.

### Parameters

None (uses global `config` object)

### Required Global State

| Variable | Type | Purpose |
|----------|------|---------|
| `config` | `dict` | Configuration object with countdown settings |
| `current_timer` | `threading.Timer \| None` | Previous timer to cancel |
| `actual_countdown` | `int` | Output: calculated countdown duration |
| `timer_start_time` | `float` | Output: timestamp when started |
| `progress_thread` | `threading.Thread \| None` | Progress display thread |
| `stop_progress` | `bool` | Flag to stop progress thread |

### Behavior

```python
1. Cancel existing timer (if any)
2. Stop existing progress thread (if any)
3. Read config['countdown_seconds'] and config['random_offset_seconds']
4. Calculate: actual_countdown = base ± random.randint(-offset, +offset)
5. Set timer_start_time = time.time()
6. Print: "[RESET] Timer started: {actual}s (base: {base}s, offset: {offset:+d}s)"
7. Start progress_thread (runs show_progress())
8. Create threading.Timer(actual_countdown, on_timeout)
9. Start the timer
```

### Side Effects

- Modifies global variables: `current_timer`, `actual_countdown`, `timer_start_time`, `progress_thread`, `stop_progress`
- Prints status message to stdout
- Spawns two threads: timer thread and progress thread

### Thread Safety

- Called from main thread or hotkey callback
- Cancels previous threads before starting new ones
- No explicit locking required (sequential execution guaranteed by keyboard library)

### Example Output

```
[RESET] Timer started: 133s (base: 130s, offset: +3s)
[████████░░░░░░░░░░░░░░░░░░░░░░]  26.3% | 01:38 remaining
```

---

## 2. Stop Timer

### Function Signature

```python
def stop_timer() -> None
```

### Description

Cancels the active timer and stops the progress display.

### Parameters

None

### Required Global State

| Variable | Type | Purpose |
|----------|------|---------|
| `current_timer` | `threading.Timer \| None` | Timer to cancel |
| `stop_progress` | `bool` | Flag to terminate progress thread |
| `timer_start_time` | `float \| None` | Reset to None |

### Behavior

```python
1. If current_timer is not None:
   - Call current_timer.cancel()
   - Set current_timer = None
2. Set stop_progress = True (terminates progress thread)
3. Set timer_start_time = None
4. Print: "[STOP] Timer cancelled."
```

### Side Effects

- Modifies global variables: `current_timer`, `stop_progress`, `timer_start_time`
- Prints status message to stdout
- Terminates progress thread

### Example Output

```
[STOP] Timer cancelled.
```

---

## 3. On Timeout (Timer Expiration)

### Function Signature

```python
def on_timeout() -> None
```

### Description

Callback function executed when timer reaches zero. Plays sound, executes auto-click (if enabled), and handles auto-restart logic.

### Parameters

None (callback, invoked by `threading.Timer`)

### Required Global State

| Variable | Type | Purpose |
|----------|------|---------|
| `config` | `dict` | Configuration for auto-click and countdown settings |

### Behavior

```python
1. Call play_sound()
2. If config['auto_click_windows'] is True:
   - Call click_maple_windows()
3. Display auto-restart message
4. Wait 5 seconds with ESC detection
5. If ESC pressed:
   - Show configuration menu:
     - Type number → adjust countdown
     - Type '/setup' → full reconfiguration
     - Press Enter → restart with current settings
6. Else (no ESC):
   - Automatically call start_timer()
```

### Auto-Restart Countdown

During 5-second wait:
- Display: `Auto-restarting in X.Xs... (Press ESC to cancel)`
- Check for ESC key press every 0.1 seconds
- If ESC detected, break loop and show menu

### Menu Options

| Input | Action |
|-------|--------|
| `<number>` | Update `config['countdown_seconds']`, save, restart timer |
| `/setup` | Unregister hotkeys, run `setup_config()`, re-register hotkeys |
| `<Enter>` | Restart timer with current settings |

### Side Effects

- Plays system sound
- May click game windows (if auto-click enabled)
- Blocks execution for ~5 seconds (auto-restart countdown)
- May trigger configuration flow
- Starts new timer automatically (unless cancelled)

### Thread Safety

- Called from timer thread (not main thread)
- Blocks timer thread during auto-restart wait
- Hotkeys remain active during wait

---

## 4. Play Sound

### Function Signature

```python
def play_sound() -> None
```

### Description

Plays Windows system alert sound.

### Parameters

None

### Platform Requirements

- **Windows**: Uses `winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)`
- **macOS/Linux**: Not supported (function would need platform-specific implementation)

### Behavior

```python
1. Print: "Time's up! Playing sound..."
2. Call: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
```

### Side Effects

- Prints message to stdout
- Plays system sound (audible)
- Non-blocking (sound plays asynchronously)

### Error Handling

No explicit error handling. If `winsound` is not available, application will fail at import time.

---

## 5. Show Progress

### Function Signature

```python
def show_progress() -> None
```

### Description

Displays real-time progress bar in console. Runs in separate thread until `stop_progress` flag is set.

### Parameters

None (daemon thread function)

### Required Global State

| Variable | Type | Purpose |
|----------|------|---------|
| `stop_progress` | `bool` | Termination flag |
| `timer_start_time` | `float \| None` | Calculate elapsed time |
| `actual_countdown` | `int` | Total duration for percentage calculation |

### Behavior

```python
while not stop_progress:
    if timer_start_time is None:
        sleep(0.1)
        continue
    
    elapsed = time.time() - timer_start_time
    remaining = max(0, actual_countdown - elapsed)
    progress = min(1.0, elapsed / actual_countdown)
    
    # Build progress bar
    filled = int(30 * progress)
    bar = '█' * filled + '░' * (30 - filled)
    
    # Format remaining time
    mins, secs = divmod(int(remaining), 60)
    time_str = f"{mins:02d}:{secs:02d}"
    
    # Display (in-place update using \r)
    print(f"\r[{bar}] {progress*100:5.1f}% | {time_str} remaining", end='', flush=True)
    
    sleep(0.5)  # Update twice per second
```

### Progress Bar Format

```
[████████████████░░░░░░░░░░░░░░]  53.2% | 01:01 remaining
```

**Components**:
- **Bar**: 30 characters (█ = filled, ░ = empty)
- **Percentage**: Float with 1 decimal place
- **Time**: MM:SS format

### Thread Lifecycle

- **Start**: Spawned by `start_timer()`
- **Stop**: `stop_progress = True`, thread checks flag and exits
- **Type**: Daemon thread (automatically terminated if main thread exits)

### Performance

- **Update Frequency**: 2 Hz (every 0.5 seconds)
- **CPU Usage**: Minimal (< 1%)
- **Blocking**: No (runs in separate thread)

---

## 6. Register Hotkeys

### Function Signature

```python
def register_hotkeys() -> None
```

### Description

Registers global hotkeys for start and stop actions using keys from configuration.

### Parameters

None (uses global `config` object)

### Required Global State

| Variable | Type | Purpose |
|----------|------|---------|
| `config` | `dict` | Contains `trigger_key` and `stop_key` |

### Behavior

```python
keyboard.add_hotkey(config['trigger_key'], start_timer)
keyboard.add_hotkey(config['stop_key'], stop_timer)
```

### Side Effects

- Registers global hotkeys (OS-level)
- May require elevated privileges on some systems
- Hotkeys remain active even when application not focused

### Error Handling

No explicit error handling. If hotkey registration fails:
- `keyboard` library may print warning
- Hotkey silently fails to register
- Application continues running

**Known Issue**: No feedback if hotkey already registered by another application.

---

## 7. Unregister Hotkeys

### Function Signature

```python
def unregister_hotkeys() -> None
```

### Description

Removes global hotkey registrations. Called before entering configuration mode.

### Parameters

None (uses global `config` object)

### Required Global State

| Variable | Type | Purpose |
|----------|------|---------|
| `config` | `dict` | Contains `trigger_key` and `stop_key` |

### Behavior

```python
try:
    keyboard.remove_hotkey(config['trigger_key'])
    keyboard.remove_hotkey(config['stop_key'])
except:
    pass  # Silently ignore if hotkeys not registered
```

### Error Handling

Uses try-except to handle cases where:
- Hotkeys were never registered
- Hotkeys already unregistered
- `keyboard` library encounters error

### Side Effects

- Removes global hotkeys (OS-level)
- Suppresses all exceptions

---

## Contract Versioning

**Version**: 1.0  
**Status**: Stable  
**Breaking Changes**: None

---

## Thread Safety Analysis

| Function | Thread Context | Locking Required | Notes |
|----------|----------------|------------------|-------|
| `start_timer()` | Main / Hotkey callback | No | Sequential execution guaranteed |
| `stop_timer()` | Main / Hotkey callback | No | Sequential execution guaranteed |
| `on_timeout()` | Timer thread | No | Blocks timer thread only |
| `play_sound()` | Timer thread | No | System call, thread-safe |
| `show_progress()` | Progress thread | No | Read-only access to globals |
| `register_hotkeys()` | Main thread | No | Configuration stable during registration |
| `unregister_hotkeys()` | Main thread | No | Configuration stable during unregistration |

**Reasoning**: Global state is only modified when timer is stopped (during configuration). Runtime operations are read-only or use simple flag-based coordination (`stop_progress`).

---

## Performance Characteristics

| Operation | Expected Time | Blocking |
|-----------|---------------|----------|
| `start_timer()` | < 5ms | No (spawns threads) |
| `stop_timer()` | < 10ms | Briefly (joins progress thread with 1s timeout) |
| `on_timeout()` | 5+ seconds | Yes (auto-restart countdown) |
| `play_sound()` | < 50ms | No (async system call) |
| `show_progress()` | Continuous | No (separate thread) |
| `register_hotkeys()` | < 10ms | No |
| `unregister_hotkeys()` | < 10ms | No |

---

## Error Handling Strategy

1. **Timer Cancellation**: Always safe (no-op if already cancelled)
2. **Thread Termination**: Flag-based (no forced termination)
3. **Sound Playback**: No error handling (assumes `winsound` available)
4. **Hotkey Registration**: Silent failure (limitation of `keyboard` library)
5. **Progress Display**: Checks for `None` values before calculation

---

## Dependencies

- `threading` (standard library)
- `time` (standard library)
- `winsound` (standard library, Windows-only)
- `keyboard` (external)
- `random` (standard library, for offset calculation)

---

## Conclusion

This contract defines the core timer control interface for the Timer Application. The design emphasizes simplicity, with thread-safe operations achieved through sequential execution guarantees rather than complex locking primitives.
