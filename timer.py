import keyboard
import threading
import time
import os
import sys
import json
import random
import socket
import window_utils
import i18n
import ota
from i18n import t  # Translation function

# System Tray modules
try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# Windows-specific module (only available on Windows)
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False
    print(t('warning_winsound'))

try:
    import pygetwindow as gw
    import pyautogui
    WINDOW_AUTOMATION_AVAILABLE = True
except ImportError:
    WINDOW_AUTOMATION_AVAILABLE = False
    print(t('warning_automation'))

import ctypes

def hide_console():
    """Hide the console window."""
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)

def show_console():
    """Show the console window."""
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 5)

def create_tray_icon(on_exit_callback, restart_callback, stop_callback):
    """Create a system tray icon."""
    if not TRAY_AVAILABLE:
        return None

    # Generate a simple icon (green circle or similar)
    image = Image.new('RGB', (64, 64), color='black')
    dc = ImageDraw.Draw(image)
    dc.ellipse([8, 8, 56, 56], fill='green', outline='white')

    def toggle_console(icon, item):
        global console_visible
        if console_visible:
            hide_console()
            console_visible = False
        else:
            show_console()
            console_visible = True

    menu = pystray.Menu(
        item(lambda text: t('tray_show') if not console_visible else t('tray_hide'), toggle_console),
        item(t('tray_start'), lambda icon, item: restart_callback()),
        item(t('tray_stop'), lambda icon, item: stop_callback()),
        item(t('tray_exit'), lambda icon, item: on_exit_callback())
    )

    icon = pystray.Icon("ringer", image, "ringer", menu)
    return icon

def tray_thread_func(icon):
    icon.run()

# --- Default settings ---
DEFAULT_TRIGGER_KEY = 'page up'
DEFAULT_STOP_KEY = 'page down'
DEFAULT_COUNTDOWN_SECONDS = 130
DEFAULT_RANDOM_OFFSET_SECONDS = 0
DEFAULT_AUTO_CLICK_WINDOWS = False
DEFAULT_AUTO_SWITCH_WINDOWS = False
DEFAULT_WAIT_FOR_TRIGGER = False
DEFAULT_SWITCH_INTERVAL = 1.5
DEFAULT_MOUSE_SPEED_LEVEL = 2
CONFIG_FILE = 'timer_config.json'
# -----------------------

current_timer = None
actual_countdown = 0  # Stores the actual countdown time with random offset applied
timer_start_time = None  # Timestamp when timer started
progress_thread = None  # Thread for displaying progress bar
stop_progress = False  # Flag to stop progress thread
config = {}
cycle_count = 0
dynamic_base_offset = 0
tray_icon = None
console_visible = True
# Store last trigger times for independent key schedules
last_extra_trigger_times = {} 
# Web shared state
web_logs = []
current_human_state_display = "Idle"

def get_local_ip():
    """Find the local IP address for LAN access display."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def log_to_web(message):
    """Add a line to the web-viewable logs."""
    global web_logs
    web_logs.append(f"[{time.strftime('%H:%M:%S')}] {message}")
    # Keep only last 100 lines
    if len(web_logs) > 100:
        web_logs.pop(0)

class HumanStateFactory:
    """Factory for human state simulation (Fatigue removed)."""
    
    STATES = {
        'normal':  {'factor': 1.0, 'jitter': 0.0, 'weight': 100}
    }

    @classmethod
    def get_random_state(cls):
        return 'normal', cls.STATES['normal']

    @classmethod
    def apply_fatigue(cls, base_delay, state_info):
        """No fatigue applied."""
        return base_delay

    @classmethod
    def should_take_long_break(cls):
        """Disabled."""
        return False

def release_all_keys():
    """Safety function to release managed keys."""
    # List of keys that might get stuck
    managed_keys = ['alt', 'esc', 'shift', 'ctrl', 'win']
    
    # Add config-specific keys
    if config:
        if config.get('trigger_key'): managed_keys.append(config['trigger_key'])
        if config.get('stop_key'): managed_keys.append(config['stop_key'])
        if config.get('attack_key'): managed_keys.append(config['attack_key'])
    
    for k in set(managed_keys):
        try:
            if keyboard.is_pressed(k):
                keyboard.release(k)
        except:
            pass

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
            print(t('load_config_error', e))
            return None
    return None

def save_config(config):
    """Save configuration to file."""
    config_path = get_config_path()

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"\n{t('settings_saved', config_path)}")
        return True
    except Exception as e:
        print(t('save_error', e))
        return False

def select_windows():
    """
    Let user select which MapleRoyals windows to auto-click with preview.
    Returns list of HWNDs (integers) or None for all windows.
    """
    if not WINDOW_AUTOMATION_AVAILABLE:
        return None

    try:
        # Get all MapleRoyals windows with HWNDs
        windows = window_utils.get_maple_windows()

        if not windows:
            print(t('no_windows_running'))
            print(t('will_click_all'))
            return None

        print(f"\n{t('found_windows', len(windows))}")
        for i, (hwnd, title, pos) in enumerate(windows, 1):
            position_str = t('window_position', pos['left'], pos['top'])
            print(t('window_info', i, title, position_str, hwnd))

        print(f"\n{t('commands_title')}")
        print(t('command_preview'))
        print(t('command_all'))
        print(t('command_select'))
        print(t('command_cancel'))

        selected_hwnds = []

        while True:
            print(f"\n{t('enter_command')}: ", end='', flush=True)
            selection = input().strip().lower()

            if not selection:
                print(t('selection_cancelled'))
                return False

            if selection == '/all':
                all_hwnds = [hwnd for hwnd, _, _ in windows]
                print(t('selected_all', len(all_hwnds)))
                return all_hwnds

            # Check if it's a single number (preview mode)
            if selection.isdigit():
                idx = int(selection)
                if 1 <= idx <= len(windows):
                    hwnd, title, pos = windows[idx - 1]
                    print(t('flashing_window', idx, title))
                    if window_utils.flash_window(hwnd, count=5):
                        print(t('window_flashed'))
                    else:
                        print(t('window_flash_failed'))
                    continue
                else:
                    print(t('invalid_index', idx))
                    continue

            # Check if it's a comma-separated selection
            if ',' in selection or selection.isdigit():
                try:
                    indices = [int(x.strip()) for x in selection.split(',')]
                    selected_hwnds = []

                    for idx in indices:
                        if 1 <= idx <= len(windows):
                            hwnd, title, _ = windows[idx - 1]
                            selected_hwnds.append(hwnd)
                        else:
                            print(t('invalid_warning', idx))

                    if not selected_hwnds:
                        print(t('no_valid_selection'))
                        continue

                    print(t('selected_count', len(selected_hwnds)))
                    for hwnd in selected_hwnds:
                        # Find matching window for display
                        for h, title, pos in windows:
                            if h == hwnd:
                                print(t('window_hwnd', title, hwnd))
                                break

                    return selected_hwnds

                except ValueError:
                    print(t('invalid_input'))
                    continue

            print(t('unknown_command'))

    except Exception as e:
        print(t('selection_error', e))
        print(t('will_click_all'))
        return None

def setup_config():
    """Interactive setup for configuration."""
    print(f"\n{t('key_configuration')}")
    print(f"{t('press_key_instruction')}\n")

    print(f"{t('press_start_key')}")
    trigger_key = keyboard.read_event(suppress=True)
    while trigger_key.event_type != 'down':
        trigger_key = keyboard.read_event(suppress=True)

    if trigger_key.name == 'esc':
        print(t('setup_cancelled'))
        return None

    trigger_key_name = trigger_key.name
    print(t('selected', trigger_key_name) + "\n")

    print(f"{t('press_stop_key')}")
    stop_key = keyboard.read_event(suppress=True)
    while stop_key.event_type != 'down':
        stop_key = keyboard.read_event(suppress=True)

    if stop_key.name == 'esc':
        print(t('setup_cancelled'))
        return None

    stop_key_name = stop_key.name
    print(t('selected', stop_key_name) + "\n")

    if trigger_key_name == stop_key_name:
        print(t('same_key_error'))
        return None

    print(f"{t('countdown_prompt', DEFAULT_COUNTDOWN_SECONDS)}: ", end='', flush=True)
    countdown_input = input().strip()

    if countdown_input:
        try:
            countdown_seconds = float(countdown_input)
            if countdown_seconds <= 0:
                print(t('countdown_error_positive'))
                return None
        except ValueError:
            print(t('countdown_error_invalid'))
            return None
    else:
        countdown_seconds = DEFAULT_COUNTDOWN_SECONDS

    print(f"\n{t('random_offset_title')}")
    print(t('random_offset_example', countdown_seconds-0.5, countdown_seconds+0.5))
    print(f"{t('random_offset_prompt', DEFAULT_RANDOM_OFFSET_SECONDS)}: ", end='', flush=True)
    offset_input = input().strip()

    if offset_input:
        try:
            random_offset = float(offset_input)
            if random_offset < 0:
                print(t('offset_error_negative'))
                return None
            if random_offset >= countdown_seconds:
                print(t('offset_error_range', f"{countdown_seconds}s"))
                return None
        except ValueError:
            print(t('countdown_error_invalid'))
            return None
    else:
        random_offset = DEFAULT_RANDOM_OFFSET_SECONDS

    # --- Mode Selection (Separated Paths) ---
    print(f"\n{'='*20} MODE SELECTION {'='*20}")
    print("1. Traditional Timer Only (Sound Alert only)")
    print("2. Auto Switch Mode (Alt+Esc macro)")
    print("3. Auto Click Mode (Mouse Click macro)")
    print("Select Path (1-3): ", end='', flush=True)
    
    mode_selection = input().strip()
    auto_click = False
    auto_switch = False
    selected_windows = None
    switch_interval = DEFAULT_SWITCH_INTERVAL
    attack_key = None

    if mode_selection == '2':
        auto_switch = True
        # Ask about auto-switch details
        print(f"\n{t('switch_interval_prompt')}: ", end='', flush=True)
        si_input = input().strip()
        try:
            switch_interval = float(si_input) if si_input else DEFAULT_SWITCH_INTERVAL
            if switch_interval < 0.1: switch_interval = 0.1
        except ValueError:
            switch_interval = DEFAULT_SWITCH_INTERVAL

        print(f"\n{t('attack_key_prompt')}: ", end='', flush=True)
        attack_key_event = keyboard.read_event(suppress=True)
        while attack_key_event.event_type != 'down':
            attack_key_event = keyboard.read_event(suppress=True)
        attack_key = None if attack_key_event.name == 'enter' else attack_key_event.name
        if attack_key: print(t('selected', attack_key))

    elif mode_selection == '3':
        auto_click = True
        if WINDOW_AUTOMATION_AVAILABLE:
            selected_windows = select_windows()
            if selected_windows is False:
                auto_click = False
                selected_windows = None
        else:
            print(f"\n{t('auto_click_unavailable')}")

    # Ask about manual trigger after cycle
    print(f"\n{t('wait_for_trigger_prompt')}")
    print(f"{t('wait_for_trigger_enable')}: ", end='', flush=True)
    wait_for_trigger_input = input().strip().lower()
    wait_for_trigger = (wait_for_trigger_input == '/enable')

    return {
        'trigger_key': trigger_key_name,
        'stop_key': stop_key_name,
        'countdown_seconds': countdown_seconds,
        'random_offset_seconds': random_offset,
        'auto_click_windows': auto_click,
        'auto_switch_windows': auto_switch,
        'selected_window_hwnds': selected_windows,
        'switch_interval_base': switch_interval,
        'attack_key': attack_key,
        'wait_for_trigger': wait_for_trigger,
        'language': i18n.get_current_language()
    }

def switch_maple_windows():
    """Cycle through MapleRoyals windows using Alt+Esc with random jitter and human fatigue simulation."""
    windows = window_utils.get_maple_windows()
    if not windows:
        print(t('no_windows_found'))
        return

    # Filter by selected HWNDs if applicable
    selected_hwnds = config.get('selected_window_hwnds')
    if selected_hwnds:
        valid_hwnds = [h for h, _, _ in windows if h in selected_hwnds]
    else:
        valid_hwnds = [h for h, _, _ in windows]

    num_cycles = len(valid_hwnds)
    if num_cycles == 0:
        return

    base_interval = config.get('switch_interval_base', DEFAULT_SWITCH_INTERVAL)
    attack_key = config.get('attack_key')
    extra_keys_config = config.get('extra_keys', {})

    # Get a single state for this entire cycle to simulate consistency
    state_key, state_info = HumanStateFactory.get_random_state()
    state_msg = t('log_human_state', t('state_' + state_key), state_info['factor'])
    print(f"\n{state_msg}")
    
    global current_human_state_display
    current_human_state_display = state_msg
    log_to_web(state_msg)
    
    # Shuffle the windows to click this time to avoid predictable patterns
    windows_to_process = list(range(num_cycles))
    random.shuffle(windows_to_process)
    
    # Simulating a "thinking/hesitation" delay before starting the macro sequence
    pre_macro_pause = random.uniform(0.5, 2.5) * state_info['factor']
    pause_msg = t('log_anti_detect_pause', pre_macro_pause)
    print(pause_msg)
    log_to_web(pause_msg)
    time.sleep(pre_macro_pause)

    print(f"{t('starting_switch_sequence', num_cycles)} (Shuffled)")
    log_to_web(f"Starting shuffled cycle for {num_cycles} windows")

    current_time = time.time()

    for idx, window_idx in enumerate(windows_to_process):
        win_header = t('log_window_header', window_idx + 1, num_cycles)
        print(f"\n{win_header} (Step {idx+1}/{num_cycles})")
        log_to_web(f"{win_header} (Step {idx+1})")
        
        try:
            # All atomic delays are influenced by the current human state
            p_d1 = HumanStateFactory.apply_fatigue(random.uniform(0.04, 0.08), state_info)
            p_d2 = HumanStateFactory.apply_fatigue(random.uniform(0.05, 0.12), state_info)
            r_d1 = HumanStateFactory.apply_fatigue(random.uniform(0.03, 0.07), state_info)
            
            # Alt DOWN
            keyboard.press('alt')
            time.sleep(p_d1)
            # Esc DOWN
            keyboard.press('esc')
            time.sleep(p_d2)
            # Esc UP
            keyboard.release('esc')
            time.sleep(r_d1)
            # Alt UP
            keyboard.release('alt')
        finally:
            # Safety cleanup
            release_all_keys()
        
        print(t('log_alt_esc', p_d2 * 1000, r_d1 * 1000))
        
        # Delay after switch to "focus" before attack, influenced by fatigue
        focus_delay = HumanStateFactory.apply_fatigue(random.uniform(0.18, 0.40), state_info)
        print(t('log_focus_delay', focus_delay * 1000))
        time.sleep(focus_delay)
        
        # --- Handle Key Scheduling Logic ---
        keys_to_press = []
        
        # 1. Check original attack key
        if attack_key:
            keys_to_press.append(attack_key)
            
        # 2. Check extra scheduled keys (each with its own timeline)
        for key_name, interval_secs in extra_keys_config.items():
            last_time = last_extra_trigger_times.get(key_name, 0)
            if last_time == 0 or (current_time - last_time) >= interval_secs:
                keys_to_press.append(key_name)
                last_extra_trigger_times[key_name] = current_time

        # Shuffle for human-like randomness when pressing multiple keys
        random.shuffle(keys_to_press)
        
        for k in keys_to_press:
            try:
                key_press_dur = HumanStateFactory.apply_fatigue(random.uniform(0.06, 0.14), state_info)
                if k == attack_key:
                    print(t('log_attack', k, key_press_dur * 1000))
                else:
                    print(t('pressing_extra_key', k))
                
                keyboard.press(k)
                time.sleep(key_press_dur)
                keyboard.release(k)
            finally:
                release_all_keys()
            
            # Tiny gap between keys
            if len(keys_to_press) > 1:
                time.sleep(random.uniform(0.15, 0.35))
        
        # Human jitter between window cycles
        if idx < num_cycles - 1:
            # The base interval is already randomized, but we also apply fatigue factor
            state_jitter = state_info['factor'] * random.uniform(0.7, 1.3)
            jitter_delay = base_interval * state_jitter
            print(t('log_next_delay', jitter_delay))
            time.sleep(jitter_delay)
            
    print(f"\n{t('switch_sequence_completed')}")

def click_maple_windows():
    """
    Find and click MapleRoyals windows using stored HWNDs.
    Validates HWNDs before clicking.
    """
    if not WINDOW_AUTOMATION_AVAILABLE:
        print(t('window_automation_unavailable'))
        return

    # Mouse speed level mapping (duration in seconds)
    speed_map = {
        1: 1.0,    # Slow
        2: 0.5,    # Normal
        3: 0.2,    # Fast
        4: 0.05    # Instant
    }
    
    speed_level = config.get('mouse_speed_level', DEFAULT_MOUSE_SPEED_LEVEL)
    base_duration = speed_map.get(speed_level, 0.5)

    # Get a single state for this cycle to ensure consistency across windows
    state_key, state_info = HumanStateFactory.get_random_state()
    print(f"\n{t('log_human_state', t('state_' + state_key), state_info['factor'])}")

    try:
        # Get all current MapleRoyals windows
        all_windows = window_utils.get_maple_windows()

        if not all_windows:
            print(t('no_windows_found'))
            return

        # Get selected HWNDs from config
        selected_hwnds = config.get('selected_window_hwnds')

        # Build hwnd -> window mapping
        hwnd_map = {hwnd: (title, pos) for hwnd, title, pos in all_windows}

        if selected_hwnds is not None:
            # Validate selected HWNDs are still valid
            valid_hwnds = [h for h in selected_hwnds if h in hwnd_map]

            if not valid_hwnds:
                print(t('none_selected_running'))
                print(t('selected_hwnds', selected_hwnds))
                print(t('available_hwnds', list(hwnd_map.keys())))
                print(f"\n{t('please_reselect')}")
                return

            # Check if some windows are missing
            missing_count = len(selected_hwnds) - len(valid_hwnds)
            if missing_count > 0:
                print(f"\n{t('warning_missing', missing_count)}")

            windows_to_click = valid_hwnds
            print(f"\n{t('found_selected', len(windows_to_click), len(selected_hwnds))}")
        else:
            # Click all windows
            windows_to_click = list(hwnd_map.keys())
            print(f"\n{t('found_windows', len(windows_to_click))}")

        print(t('starting_sequence'))

        # Shuffle for human-like behavior
        random.shuffle(windows_to_click)

        # Calculate random delays
        total_time = 5.0
        num_windows = len(windows_to_click)
        delays = []
        remaining_time = total_time

        for i in range(num_windows - 1):
            max_delay = min(2.5, remaining_time - (num_windows - i - 1) * 0.3)
            delay = random.uniform(0.5, max_delay)
            delays.append(delay)
            remaining_time -= delay

        delays.append(max(0.3, remaining_time))

        # Click each window by HWND
        import pygetwindow as gw

        for i, hwnd in enumerate(windows_to_click):
            try:
                # Get window by HWND
                matching_windows = [w for w in gw.getAllWindows() if w._hWnd == hwnd]

                if not matching_windows:
                    print(t('window_unavailable', i+1, num_windows, hwnd))
                    continue

                window = matching_windows[0]
                title, pos = hwnd_map[hwnd]

                # Activate and click window
                try:
                    window_left, window_top = window.left, window.top
                    window_width, window_height = window.width, window.height

                    # Offset affected by fatigue (larger variance when tired)
                    offset_factor = 0.3 * state_info['factor']
                    offset_x = int(random.uniform(-offset_factor, offset_factor) * window_width)
                    offset_y = int(random.uniform(-offset_factor, offset_factor) * window_height)

                    click_x = window_left + window_width // 2 + offset_x
                    click_y = window_top + window_height // 2 + offset_y

                    # Move duration affected by fatigue factory
                    move_duration = HumanStateFactory.apply_fatigue(base_duration, state_info)

                    import pyautogui
                    pyautogui.moveTo(click_x, click_y, duration=move_duration)
                    
                    # Click delay affected by fatigue
                    click_delay = HumanStateFactory.apply_fatigue(random.uniform(0.05, 0.15), state_info)
                    time.sleep(click_delay)
                    pyautogui.click()
                    time.sleep(0.2)

                except Exception:
                    try:
                        window.activate()
                        time.sleep(0.15)
                    except:
                        print(t('warning_activate', i+1, num_windows, hwnd))

                keyboard.press_and_release(config['trigger_key'])
                print(t('clicked', i+1, num_windows, title, hwnd))

                if i < len(delays):
                    time.sleep(delays[i])

            except Exception as e:
                print(t('error_with_hwnd', i+1, num_windows, hwnd, str(e)[:50]))
                continue

        print(t('sequence_completed'))

    except Exception as e:
        print(t('error_in_click', e))

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
    print(f"\n\n{t('times_up')}")
    if WINSOUND_AVAILABLE:
        # MB_ICONEXCLAMATION produces a standard system alert sound
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    else:
        # Fallback for non-Windows systems (just print, tests will mock this)
        print("\a")  # Terminal bell

def on_timeout():
    global config
    play_sound()

    # Execute Alt+Esc sequence if enabled
    if config.get('auto_switch_windows', False):
        switch_maple_windows()

    # Execute auto-click if enabled
    if config.get('auto_click_windows', False):
        print(f"\n{t('auto_click_enabled')}")
        click_maple_windows()

    # Check if we should wait for manual trigger instead of auto-restarting
    if config.get('wait_for_trigger', False):
        print(f"\n{t('waiting_for_next_trigger')}")
        # Stop everything and stay in IDLE until user hits trigger_key manually
        stop_timer()
        return

    # Auto-restart countdown with ESC to cancel
    # For very short timers, skip or shorten the restart wait to avoid timeout issues
    wait_duration = 2.0 if config['countdown_seconds'] < 5 else 5.0
    
    print("\n" + "="*50)
    print(t('will_auto_restart'))
    print(t('press_esc_configure'))
    print("="*50)

    # Check for ESC key
    esc_pressed = False
    start_wait = time.time()

    while time.time() - start_wait < wait_duration:
        remaining = wait_duration - (time.time() - start_wait)
        print(f"\r{t('auto_restarting_in', remaining)}", end='', flush=True)

        # Check if ESC is pressed
        if keyboard.is_pressed('esc'):
            esc_pressed = True
            print(f"\n\n{t('esc_pressed')}")
            break

        time.sleep(0.1)

    if esc_pressed:
        # User wants to configure
        print(f"\n{t('config_menu_1')}")
        print(t('config_menu_2'))
        print(t('config_menu_3'))
        print(f"\n{t('your_choice')}: ", end='', flush=True)

        choice = input().strip()

        if choice == '/setup':
            # Unregister hotkeys before setup
            unregister_hotkeys()
            new_config = setup_config()
            if new_config:
                config = new_config
                save_config(config)
                print(f"\n{t('config_updated')}")
            else:
                print(f"\n{t('setup_cancelled_keeping')}")
            # Re-register hotkeys
            register_hotkeys()
            print(f"\n{t('press_to_start', config['trigger_key'])}")

        elif choice.isdigit():
            new_countdown = int(choice)
            if new_countdown > 0:
                config['countdown_seconds'] = new_countdown
                save_config(config)
                print(t('countdown_updated', new_countdown))
                start_timer()
            else:
                print(t('invalid_time'))
        else:
            # Just restart with current settings
            start_timer()
    else:
        # Auto-restart
        print(f"\n\n{t('auto_restarting_now')}")
        start_timer()

def start_timer():
    global current_timer, actual_countdown, timer_start_time, progress_thread, stop_progress, cycle_count, dynamic_base_offset
    if current_timer is not None:
        current_timer.cancel()

    # Increment cycle count
    cycle_count += 1
    
    # Long Break Simulation (Anti-detection)
    if cycle_count > 1 and HumanStateFactory.should_take_long_break():
        break_mins = random.uniform(5.5, 12.5)
        print(f"\n\n{t('log_long_break', break_mins)}")
        time.sleep(break_mins * 60)
        print(f"\n{t('program_resumed')}")

    # Dynamic Base Offset (shifting the macro rhythm every 5 cycles)
    if cycle_count % 5 == 0:
        dynamic_base_offset = random.randint(-12, 12)
        print(f"\n{t('log_dynamic_shift', dynamic_base_offset)}")

    # Stop existing progress thread if any
    if progress_thread is not None:
        stop_progress = True
        progress_thread.join(timeout=1.0)

    # Calculate actual countdown with random offset AND dynamic base offset
    base_time = config['countdown_seconds'] + dynamic_base_offset
    offset = float(config.get('random_offset_seconds', 0))

    if offset > 0:
        # Random offset between -offset and +offset (supports float/ms)
        random_offset = random.uniform(-offset, offset)
        actual_countdown = max(0.1, base_time + random_offset)
        print(f"\n{t('timer_started', actual_countdown, base_time, random_offset)}")
    else:
        actual_countdown = max(0.1, base_time)
        print(f"\n{t('timer_started_simple', actual_countdown)}")

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

    # Safety: release all managed keys
    release_all_keys()

    # Stop progress bar
    stop_progress = True
    timer_start_time = None

    print(f"\n{t('timer_cancelled')}")

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
                print(t('entering_setup'))
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
                    print(f"\n{t('config_updated')}")
                else:
                    print(f"\n{t('setup_cancelled_keeping')}")

                # Re-register hotkeys with new or existing config
                register_hotkeys()

                print(f"\n{t('program_resumed')}")
                print(t('press_to_start', config['trigger_key']))
                print(t('press_to_stop', config['stop_key']))
                print(t('countdown_display', config['countdown_seconds']))
                print(f"{t('type_setup')}\n")

            elif cmd == '/coffee':
                print(f"\n{t('easter_egg_coffee')}")
                # Secretly boost energized/focused weight
                HumanStateFactory.STATES['energized']['weight'] = 40
                HumanStateFactory.STATES['focused']['weight'] = 40
                HumanStateFactory.STATES['normal']['weight'] = 10
                HumanStateFactory.STATES['tired']['weight'] = 5
                HumanStateFactory.STATES['drowsy']['weight'] = 5
                print("✨ [Maru Mode] Current system status is now highly alert!")

            elif cmd in ['/language', '/lang']:
                print("\n" + "="*50)
                i18n.select_language()
                config['language'] = i18n.get_current_language()
                save_config(config)
                print(t('language_changed'))
                print("="*50 + "\n")

        except EOFError:
            # Handle Ctrl+D or EOF
            break
        except Exception as e:
            # Silently ignore errors to keep the listener running
            pass

def main():
    global config, tray_icon, console_visible

    # OTA check
    ota.run_ota_flow()

    # Start system tray icon if available
    if TRAY_AVAILABLE:
        def on_tray_exit():
            global tray_icon
            if tray_icon:
                tray_icon.stop()
            os._exit(0)

        tray_icon = create_tray_icon(
            on_exit_callback=on_tray_exit,
            restart_callback=start_timer,
            stop_callback=stop_timer
        )
        
        t_thread = threading.Thread(target=tray_thread_func, args=(tray_icon,), daemon=True)
        t_thread.start()

    # Language selection (only on first run or if not in config)
    saved_config = load_config()
    if saved_config and 'language' in saved_config:
        i18n.set_language(saved_config['language'])
    else:
        i18n.select_language()

    print(f"\n{t('program_title')}\n")

    # Load existing config
    existing_config = load_config()

    if existing_config:
        print(t('found_config'))
        print(t('config_start_reset', existing_config['trigger_key']))
        print(t('config_stop', existing_config['stop_key']))
        print(t('config_countdown', existing_config['countdown_seconds']))
        
        auto_click_status = t('enabled') if existing_config.get('auto_click_windows', False) else t('disabled')
        print(t('config_auto_click', auto_click_status))

        auto_switch_status = t('enabled') if existing_config.get('auto_switch_windows', False) else t('disabled')
        print(t('config_auto_switch', auto_switch_status))

        wait_for_trigger_status = t('enabled') if existing_config.get('wait_for_trigger', False) else t('disabled')
        print(t('config_wait_for_trigger', wait_for_trigger_status))

        # Validate HWNDs if auto-click is enabled
        need_reselect = False
        if existing_config.get('auto_click_windows', False):
            selected_hwnds = existing_config.get('selected_window_hwnds')

            # Migration: convert old format to new format
            if selected_hwnds is None and 'selected_window_titles' in existing_config:
                print(f"\n{t('old_config_detected')}")
                print(t('reselect_prompt'))
                need_reselect = True
            elif selected_hwnds:
                # Validate HWNDs
                valid_hwnds = [h for h in selected_hwnds if window_utils.is_window_valid(h)]

                if len(valid_hwnds) == 0:
                    print(f"\n{t('all_windows_closed')}")
                    print(t('reselect_prompt'))
                    need_reselect = True
                elif len(valid_hwnds) < len(selected_hwnds):
                    missing = len(selected_hwnds) - len(valid_hwnds)
                    print(f"\n{t('some_windows_closed', missing, len(selected_hwnds))}")
                    print(t('may_want_reselect'))
                else:
                    print(t('selected_windows', len(selected_hwnds)))

        if need_reselect:
            print(f"\n{t('needs_reconfiguration')}: ", end='', flush=True)
        else:
            print(f"\n{t('want_reconfigure')}: ", end='', flush=True)

        choice = input().strip().lower()

        if choice == '/setup':
            new_config = setup_config()
            if new_config:
                config = new_config
                save_config(config)
            else:
                print(f"{t('using_existing')}")
                config = existing_config
        else:
            config = existing_config
    else:
        print(f"{t('no_config_found')}\n")
        new_config = setup_config()

        if new_config:
            config = new_config
            save_config(config)
        else:
            print(t('setup_failed'))
            config = {
                'trigger_key': DEFAULT_TRIGGER_KEY,
                'stop_key': DEFAULT_STOP_KEY,
                'countdown_seconds': DEFAULT_COUNTDOWN_SECONDS,
                'auto_click_windows': DEFAULT_AUTO_CLICK_WINDOWS,
                'selected_window_hwnds': None
            }

    # Ensure focus on auto_click and selected_window_hwnds
    if 'auto_click_windows' not in config:
        config['auto_click_windows'] = DEFAULT_AUTO_CLICK_WINDOWS
    if 'selected_window_hwnds' not in config:
        if 'selected_window_titles' in config:
            del config['selected_window_titles']
        config['selected_window_hwnds'] = None
    
    # Ensure wait_for_trigger exists in config
    if 'wait_for_trigger' not in config:
        config['wait_for_trigger'] = DEFAULT_WAIT_FOR_TRIGGER

    # Ensure switch_interval_base exists in config
    if 'switch_interval_base' not in config:
        config['switch_interval_base'] = DEFAULT_SWITCH_INTERVAL
    
    # Ensure attack_key exists in config
    if 'attack_key' not in config:
        config['attack_key'] = None

    print(f"\n{t('program_started')}")
    print(t('press_to_start', config['trigger_key']))
    print(t('press_to_stop', config['stop_key']))
    print(t('countdown_display', config['countdown_seconds']))
    
    if config.get('auto_click_windows', False):
        print(t('auto_click_status', t('enabled')))
        selected_hwnds = config.get('selected_window_hwnds')
        if selected_hwnds:
            print(t('selected_specific', len(selected_hwnds)))
        else:
            print(t('mode_all_windows'))
    else:
        print(t('auto_click_status', t('disabled')))

    if config.get('auto_switch_windows', False):
        print(t('auto_switch_status', t('enabled')))
    else:
        print(t('auto_switch_status', t('disabled')))
        
    print(f"{t('type_setup')}\n")

    register_hotkeys()

    # Start command listener in a daemon thread
    listener_thread = threading.Thread(target=command_listener, daemon=True)
    listener_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{t('program_terminated')}")

if __name__ == "__main__":
    main()
