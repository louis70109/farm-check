import keyboard
import threading
import time
import os
import sys
import winsound
import json

# --- Default settings ---
DEFAULT_TRIGGER_KEY = 'page up'
DEFAULT_STOP_KEY = 'page down'
DEFAULT_COUNTDOWN_SECONDS = 130
CONFIG_FILE = 'timer_config.json'
# -----------------------

current_timer = None
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

    return {
        'trigger_key': trigger_key_name,
        'stop_key': stop_key_name,
        'countdown_seconds': countdown_seconds
    }

def play_sound():
    """Play system default sound."""
    print(f"\nTime's up! Playing sound...")
    # MB_ICONEXCLAMATION produces a standard system alert sound
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

def on_timeout():
    play_sound()

def start_timer():
    global current_timer
    if current_timer is not None:
        current_timer.cancel()

    print(f"\n[RESET] Timer started: {config['countdown_seconds']} seconds...")
    current_timer = threading.Timer(config['countdown_seconds'], on_timeout)
    current_timer.start()

def stop_timer():
    global current_timer
    if current_timer is not None:
        current_timer.cancel()
        current_timer = None

    print("\n[STOP] Timer cancelled.")

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
        print("\nDo you want to reconfigure? (y/N): ", end='', flush=True)

        choice = input().strip().lower()

        if choice == 'y':
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
                'countdown_seconds': DEFAULT_COUNTDOWN_SECONDS
            }

    print(f"\n=== Program started ===")
    print(f"Press [{config['trigger_key']}] to START/RESET")
    print(f"Press [{config['stop_key']}] to STOP")
    print(f"Countdown: {config['countdown_seconds']} seconds\n")

    keyboard.add_hotkey(config['trigger_key'], start_timer)
    keyboard.add_hotkey(config['stop_key'], stop_timer)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProgram terminated.")

if __name__ == "__main__":
    main()
