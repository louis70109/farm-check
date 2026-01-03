import keyboard
import threading
import time
import os
import sys
import winsound
import json
import random

try:
    import pygetwindow as gw
    import pyautogui
    WINDOW_AUTOMATION_AVAILABLE = True
except ImportError:
    WINDOW_AUTOMATION_AVAILABLE = False
    print("Warning: pygetwindow or pyautogui not installed. Window automation disabled.")

# --- Default settings ---
DEFAULT_TRIGGER_KEY = 'page up'
DEFAULT_STOP_KEY = 'page down'
DEFAULT_COUNTDOWN_SECONDS = 130
DEFAULT_RANDOM_OFFSET_SECONDS = 0
DEFAULT_AUTO_CLICK_WINDOWS = False
CONFIG_FILE = 'timer_config.json'
# -----------------------

current_timer = None
actual_countdown = 0  # Stores the actual countdown time with random offset applied
timer_start_time = None  # Timestamp when timer started
progress_thread = None  # Thread for displaying progress bar
stop_progress = False  # Flag to stop progress thread
config = {}

def get_config_path():
    """Get the config file path in user's home directory or current directory."""
    if getattr(sys, 'frozen', False):
        # If running as exe, store config in same directory as exe
        return os.path.join(os.path.dirname(sys.executable), CONFIG_FILE)
    else:
        # If running as script, store in current directory
        return CONFIG_FILE

def load_config():
    """Load configuration from file, or return defaults if not found."""
    config_path = get_config_path()

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
            return None
    return None

def save_config(config):
    """Save configuration to file."""
    config_path = get_config_path()

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"\nSettings saved to: {config_path}")
        return True
    except Exception as e:
        print(f"Failed to save config: {e}")
        return False

def select_windows():
    """Let user select which MapleRoyals windows to auto-click."""
    if not WINDOW_AUTOMATION_AVAILABLE:
        return None

    try:
        # Find all windows with 'MapleRoyals' in title
        all_windows = [w for w in gw.getAllWindows() if 'MapleRoyals' in w.title]

        if not all_windows:
            print("  No MapleRoyals windows currently running.")
            print("  Will auto-click all MapleRoyals windows when available.")
            return None

        # Filter valid windows
        valid_windows = []
        seen_handles = set()

        for w in all_windows:
            try:
                if w._hWnd not in seen_handles:
                    _ = w.size
                    _ = w.title
                    valid_windows.append(w)
                    seen_handles.add(w._hWnd)
            except:
                continue

        if not valid_windows:
            print("  No valid MapleRoyals windows found.")
            print("  Will auto-click all MapleRoyals windows when available.")
            return None

        print(f"\n  Found {len(valid_windows)} MapleRoyals window(s):")
        for i, w in enumerate(valid_windows, 1):
            print(f"    [{i}] {w.title}")

        print("\n  Select windows to auto-click:")
        print("    Type '/all' for all windows")
        print("    Or enter numbers separated by commas (e.g., '1,3' or '2')")
        print("    Press Enter to cancel: ", end='', flush=True)

        selection = input().strip().lower()

        if not selection:
            print("  Selection cancelled. Auto-click will be disabled.")
            return False

        if selection == '/all':
            print(f"  Selected: All {len(valid_windows)} windows")
            return None  # None means "all windows"

        # Parse selection
        try:
            indices = [int(x.strip()) for x in selection.split(',')]
            selected_titles = []

            for idx in indices:
                if 1 <= idx <= len(valid_windows):
                    selected_titles.append(valid_windows[idx - 1].title)
                else:
                    print(f"  Warning: Invalid index {idx}, skipping")

            if not selected_titles:
                print("  No valid windows selected. Auto-click will be disabled.")
                return False

            print(f"  Selected {len(selected_titles)} window(s):")
            for title in selected_titles:
                print(f"    - {title}")

            return selected_titles

        except ValueError:
            print("  Invalid input. Auto-click will be disabled.")
            return False

    except Exception as e:
        print(f"  Error during window selection: {e}")
        print("  Will auto-click all MapleRoyals windows.")
        return None

def setup_config():
    """Interactive setup for configuration."""
    print("\n=== Key Configuration ===")
    print("Please press the key you want to use (press ESC to cancel)\n")

    print("Press the key for START/RESET timer:")
    trigger_key = keyboard.read_event(suppress=True)
    while trigger_key.event_type != 'down':
        trigger_key = keyboard.read_event(suppress=True)

    if trigger_key.name == 'esc':
        print("Setup cancelled.")
        return None

    trigger_key_name = trigger_key.name
    print(f"  -> Selected: [{trigger_key_name}]\n")

    print("Press the key for STOP timer:")
    stop_key = keyboard.read_event(suppress=True)
    while stop_key.event_type != 'down':
        stop_key = keyboard.read_event(suppress=True)

    if stop_key.name == 'esc':
        print("Setup cancelled.")
        return None

    stop_key_name = stop_key.name
    print(f"  -> Selected: [{stop_key_name}]\n")

    if trigger_key_name == stop_key_name:
        print("Error: START and STOP keys cannot be the same!")
        return None

    print(f"Countdown seconds (press Enter for default {DEFAULT_COUNTDOWN_SECONDS}): ", end='', flush=True)
    countdown_input = input().strip()

    if countdown_input:
        try:
            countdown_seconds = int(countdown_input)
            if countdown_seconds <= 0:
                print("Error: Countdown must be positive!")
                return None
        except ValueError:
            print("Error: Invalid number!")
            return None
    else:
        countdown_seconds = DEFAULT_COUNTDOWN_SECONDS

    print(f"\nRandom time offset in seconds (±N seconds to avoid detection)")
    print(f"  Example: 5 means timer will vary between {countdown_seconds-5}~{countdown_seconds+5} seconds")
    print(f"  Press Enter for default {DEFAULT_RANDOM_OFFSET_SECONDS}: ", end='', flush=True)
    offset_input = input().strip()

    if offset_input:
        try:
            random_offset = int(offset_input)
            if random_offset < 0:
                print("Error: Offset must be non-negative!")
                return None
            if random_offset >= countdown_seconds:
                print(f"Error: Offset must be less than countdown time ({countdown_seconds}s)!")
                return None
        except ValueError:
            print("Error: Invalid number!")
            return None
    else:
        random_offset = DEFAULT_RANDOM_OFFSET_SECONDS

    # Ask about auto-click feature
    auto_click = False
    selected_windows = None

    if WINDOW_AUTOMATION_AVAILABLE:
        print("\nAuto-click MapleRoyals windows when timer ends?")
        print("  Type '/enable' to enable, or press Enter to disable: ", end='', flush=True)
        auto_click_input = input().strip().lower()
        auto_click = (auto_click_input == '/enable')

        if auto_click:
            selected_windows = select_windows()
            # If user cancelled selection, disable auto-click
            if selected_windows is False:
                auto_click = False
                selected_windows = None
    else:
        print("\nNote: Auto-click feature unavailable (missing dependencies)")

    return {
        'trigger_key': trigger_key_name,
        'stop_key': stop_key_name,
        'countdown_seconds': countdown_seconds,
        'random_offset_seconds': random_offset,
        'auto_click_windows': auto_click,
        'selected_window_titles': selected_windows
    }

def click_maple_windows():
    """
    Find and click MapleRoyals windows with human-like timing.
    Respects user's window selection from config.
    """
    if not WINDOW_AUTOMATION_AVAILABLE:
        print("Window automation not available")
        return

    try:
        # Find all windows with 'MapleRoyals' in title
        all_windows = [w for w in gw.getAllWindows() if 'MapleRoyals' in w.title]

        if not all_windows:
            print("No MapleRoyals windows found")
            return

        # Filter out invalid windows and duplicates
        valid_windows = []
        seen_handles = set()

        for w in all_windows:
            try:
                # Check if window is valid and accessible
                if w._hWnd not in seen_handles:
                    # Try to get window rect to verify it's accessible
                    _ = w.size
                    _ = w.title  # Verify we can read title
                    valid_windows.append(w)
                    seen_handles.add(w._hWnd)
            except:
                continue

        if not valid_windows:
            print("No valid MapleRoyals windows found")
            return

        # Filter by user selection if configured
        selected_titles = config.get('selected_window_titles')
        print(f"\nDebug: selected_window_titles from config: {selected_titles}")
        print(f"Debug: Type of selected_window_titles: {type(selected_titles)}")

        if selected_titles is not None:
            # User has selected specific windows
            print(f"Debug: Filtering {len(valid_windows)} windows by {len(selected_titles)} selected titles")
            windows = [w for w in valid_windows if w.title in selected_titles]

            if not windows:
                print(f"None of the selected windows are currently running.")
                print(f"Selected windows: {', '.join(selected_titles)}")
                return

            print(f"\nFound {len(windows)} of {len(selected_titles)} selected window(s)")
            not_found = set(selected_titles) - {w.title for w in windows}
            if not_found:
                print(f"Not running: {', '.join(not_found)}")
        else:
            # Click all windows
            print(f"Debug: No window selection, clicking all windows")
            windows = valid_windows
            print(f"\nFound {len(valid_windows)} MapleRoyals window(s)")

        print("Starting auto-click sequence...")

        # Shuffle windows to make it more human-like
        random.shuffle(windows)

        # Calculate random delays that sum to approximately 5 seconds
        total_time = 5.0
        num_windows = len(windows)

        # Generate random delays with variation
        delays = []
        remaining_time = total_time

        for i in range(num_windows - 1):
            # Random delay between 0.5 to 2.5 seconds, but ensure we don't exceed total time
            max_delay = min(2.5, remaining_time - (num_windows - i - 1) * 0.3)
            delay = random.uniform(0.5, max_delay)
            delays.append(delay)
            remaining_time -= delay

        # Last delay uses remaining time (with a minimum of 0.3s)
        delays.append(max(0.3, remaining_time))

        # Click each window
        for i, window in enumerate(windows):
            try:
                # Use mouse to activate window (more human-like and bypasses API restrictions)
                try:
                    # Get window position and size
                    window_left, window_top, window_width, window_height = window.left, window.top, window.width, window.height

                    # Add random offset to click position (±30% from center)
                    # This makes it look more human-like
                    offset_x = int(random.uniform(-0.3, 0.3) * window_width)
                    offset_y = int(random.uniform(-0.3, 0.3) * window_height)

                    click_x = window_left + window_width // 2 + offset_x
                    click_y = window_top + window_height // 2 + offset_y

                    # Move mouse to target position with human-like animation
                    # Random duration between 0.3 to 0.8 seconds for more natural movement
                    move_duration = random.uniform(0.3, 0.8)
                    pyautogui.moveTo(click_x, click_y, duration=move_duration)
                    
                    # Small pause after movement (human reaction time)
                    time.sleep(random.uniform(0.05, 0.15))
                    
                    # Click on the position (mouse is already there)
                    pyautogui.click()
                    time.sleep(0.2)  # Wait for window to become active

                except Exception:
                    # If mouse click fails, try API activate as fallback
                    try:
                        window.activate()
                        time.sleep(0.15)
                    except:
                        print(f"  [{i+1}/{num_windows}] Warning: Could not activate '{window.title}', sending keypress anyway")

                # Press the trigger key
                keyboard.press_and_release(config['trigger_key'])

                print(f"  [{i+1}/{num_windows}] Clicked: {window.title}")

                # Wait before next window (except for the last one)
                if i < len(delays):
                    time.sleep(delays[i])

            except Exception as e:
                print(f"  [{i+1}/{num_windows}] Error with '{window.title}': {str(e)[:50]}... (skipped)")
                continue

        print("Auto-click sequence completed")

    except Exception as e:
        print(f"Error in click_maple_windows: {e}")

def show_progress():
    """Display progress bar while timer is running."""
    global stop_progress, timer_start_time, actual_countdown

    while not stop_progress:
        if timer_start_time is None:
            time.sleep(0.1)
            continue

        elapsed = time.time() - timer_start_time
        remaining = max(0, actual_countdown - elapsed)
        progress = min(1.0, elapsed / actual_countdown) if actual_countdown > 0 else 1.0

        # Progress bar configuration
        bar_length = 30
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        # Format time
        mins, secs = divmod(int(remaining), 60)
        time_str = f"{mins:02d}:{secs:02d}"

        # Display progress bar
        print(f"\r[{bar}] {progress*100:5.1f}% | {time_str} remaining", end='', flush=True)

        time.sleep(0.5)  # Update twice per second

def play_sound():
    """Play system default sound."""
    print(f"\n\nTime's up! Playing sound...")
    # MB_ICONEXCLAMATION produces a standard system alert sound
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

def on_timeout():
    global config
    play_sound()

    # Execute auto-click if enabled
    if config.get('auto_click_windows', False):
        print("\nAuto-click is enabled. Clicking MapleRoyals windows...")
        click_maple_windows()

    # Auto-restart countdown with ESC to cancel
    print("\n" + "="*50)
    print("Timer will auto-restart in 5 seconds...")
    print("Press ESC to configure settings, or wait to auto-restart")
    print("="*50)

    # Check for ESC key for 5 seconds
    esc_pressed = False
    start_wait = time.time()
    wait_duration = 5.0

    while time.time() - start_wait < wait_duration:
        remaining = wait_duration - (time.time() - start_wait)
        print(f"\rAuto-restarting in {remaining:.1f}s... (Press ESC to cancel)", end='', flush=True)

        # Check if ESC is pressed
        if keyboard.is_pressed('esc'):
            esc_pressed = True
            print("\n\nESC pressed! Configuration menu:")
            break

        time.sleep(0.1)

    if esc_pressed:
        # User wants to configure
        print("\n1. Type a number to adjust countdown seconds")
        print("2. Type '/setup' to reconfigure all settings")
        print("3. Press Enter to restart timer with current settings")
        print("\nYour choice: ", end='', flush=True)

        choice = input().strip()

        if choice == '/setup':
            # Unregister hotkeys before setup
            unregister_hotkeys()
            new_config = setup_config()
            if new_config:
                config = new_config
                save_config(config)
                print("\nConfiguration updated successfully!")
            else:
                print("\nSetup cancelled. Keeping current configuration.")
            # Re-register hotkeys
            register_hotkeys()
            print(f"\nPress [{config['trigger_key']}] to start timer")

        elif choice.isdigit():
            new_countdown = int(choice)
            if new_countdown > 0:
                config['countdown_seconds'] = new_countdown
                save_config(config)
                print(f"Countdown updated to {new_countdown} seconds.")
                start_timer()
            else:
                print("Invalid time. Press trigger key to restart.")
        else:
            # Just restart with current settings
            start_timer()
    else:
        # Auto-restart
        print("\n\nAuto-restarting timer...")
        start_timer()

def start_timer():
    global current_timer, actual_countdown, timer_start_time, progress_thread, stop_progress
    if current_timer is not None:
        current_timer.cancel()

    # Stop existing progress thread if any
    if progress_thread is not None:
        stop_progress = True
        progress_thread.join(timeout=1.0)

    # Calculate actual countdown with random offset
    base_time = config['countdown_seconds']
    offset = config.get('random_offset_seconds', 0)

    if offset > 0:
        # Random offset between -offset and +offset
        random_offset = random.randint(-offset, offset)
        actual_countdown = base_time + random_offset
        print(f"\n[RESET] Timer started: {actual_countdown}s (base: {base_time}s, offset: {random_offset:+d}s)")
    else:
        actual_countdown = base_time
        print(f"\n[RESET] Timer started: {actual_countdown} seconds...")

    # Start timer and progress bar
    timer_start_time = time.time()
    stop_progress = False
    progress_thread = threading.Thread(target=show_progress, daemon=True)
    progress_thread.start()

    current_timer = threading.Timer(actual_countdown, on_timeout)
    current_timer.start()

def stop_timer():
    global current_timer, stop_progress, timer_start_time
    if current_timer is not None:
        current_timer.cancel()
        current_timer = None

    # Stop progress bar
    stop_progress = True
    timer_start_time = None

    print("\n[STOP] Timer cancelled.")

def register_hotkeys():
    """Register all hotkeys."""
    keyboard.add_hotkey(config['trigger_key'], start_timer)
    keyboard.add_hotkey(config['stop_key'], stop_timer)

def unregister_hotkeys():
    """Unregister all hotkeys."""
    try:
        keyboard.remove_hotkey(config['trigger_key'])
        keyboard.remove_hotkey(config['stop_key'])
    except:
        pass

def command_listener():
    """Listen for user commands in a separate thread."""
    global config

    while True:
        try:
            cmd = input().strip()

            if cmd == '/setup':
                print("\n" + "="*50)
                print("Entering setup mode...")
                print("="*50)

                # Temporarily unregister hotkeys
                unregister_hotkeys()

                # Stop current timer if running
                stop_timer()

                # Run setup
                new_config = setup_config()

                if new_config:
                    config = new_config
                    save_config(config)
                    print("\nConfiguration updated successfully!")
                else:
                    print("\nSetup cancelled. Keeping current configuration.")

                # Re-register hotkeys with new or existing config
                register_hotkeys()

                print(f"\n=== Program resumed ===")
                print(f"Press [{config['trigger_key']}] to START/RESET")
                print(f"Press [{config['stop_key']}] to STOP")
                print(f"Countdown: {config['countdown_seconds']} seconds")
                print("Type '/setup' to reconfigure\n")

        except EOFError:
            # Handle Ctrl+D or EOF
            break
        except Exception as e:
            # Silently ignore errors to keep the listener running
            pass

def main():
    global config

    print("=== Timer Program ===\n")

    # Load existing config
    existing_config = load_config()

    if existing_config:
        print("Found existing configuration:")
        print(f"  START/RESET: [{existing_config['trigger_key']}]")
        print(f"  STOP: [{existing_config['stop_key']}]")
        print(f"  Countdown: {existing_config['countdown_seconds']} seconds")
        auto_click_status = "ENABLED" if existing_config.get('auto_click_windows', False) else "DISABLED"
        print(f"  Auto-click MapleRoyals: {auto_click_status}")

        if existing_config.get('auto_click_windows', False):
            selected_titles = existing_config.get('selected_window_titles')
            if selected_titles:
                print(f"  Selected windows ({len(selected_titles)}):")
                for title in selected_titles:
                    print(f"    - {title}")
            else:
                print(f"  Mode: Click all windows")

        print("\nDo you want to reconfigure? (Type '/setup' or press Enter to skip): ", end='', flush=True)

        choice = input().strip().lower()

        if choice == '/setup':
            new_config = setup_config()
            if new_config:
                config = new_config
                save_config(config)
            else:
                print("Using existing configuration...")
                config = existing_config
        else:
            config = existing_config
    else:
        print("No configuration found. Please set up your keys.\n")
        new_config = setup_config()

        if new_config:
            config = new_config
            save_config(config)
        else:
            print("Setup failed. Using defaults.")
            config = {
                'trigger_key': DEFAULT_TRIGGER_KEY,
                'stop_key': DEFAULT_STOP_KEY,
                'countdown_seconds': DEFAULT_COUNTDOWN_SECONDS,
                'auto_click_windows': DEFAULT_AUTO_CLICK_WINDOWS,
                'selected_window_titles': None
            }

    # Ensure auto_click_windows exists in config (for backwards compatibility)
    if 'auto_click_windows' not in config:
        config['auto_click_windows'] = DEFAULT_AUTO_CLICK_WINDOWS

    # Ensure selected_window_titles exists in config (for backwards compatibility)
    if 'selected_window_titles' not in config:
        config['selected_window_titles'] = None

    print(f"\n=== Program started ===")
    print(f"Press [{config['trigger_key']}] to START/RESET")
    print(f"Press [{config['stop_key']}] to STOP")
    print(f"Countdown: {config['countdown_seconds']} seconds")
    if config.get('auto_click_windows', False):
        print("Auto-click MapleRoyals: ENABLED")
        selected_titles = config.get('selected_window_titles')
        if selected_titles:
            print(f"  Selected {len(selected_titles)} specific window(s)")
        else:
            print(f"  Mode: Click all windows")
    else:
        print("Auto-click MapleRoyals: DISABLED")
    print("Type '/setup' to reconfigure\n")

    register_hotkeys()

    # Start command listener in a daemon thread
    listener_thread = threading.Thread(target=command_listener, daemon=True)
    listener_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram terminated.")

if __name__ == "__main__":
    main()
