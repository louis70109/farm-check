"""Internationalization (i18n) module for timer program."""

LANGUAGES = {
    'en': {
        # Language selection
        'select_language': 'Select Language / 選擇語言',
        'language_options': '  [1] English\n  [2] 繁體中文',
        'language_prompt': 'Enter your choice (1-2)',
        'invalid_language': 'Invalid choice. Using English.',

        # Program header
        'program_title': '=== Timer Program ===',
        'program_started': '=== Program started ===',

        # Configuration
        'key_configuration': '=== Key Configuration ===',
        'press_key_instruction': 'Please press the key you want to use (press ESC to cancel)',
        'press_start_key': 'Press the key for START/RESET timer:',
        'press_stop_key': 'Press the key for STOP timer:',
        'selected': '  -> Selected: [{}]',
        'setup_cancelled': 'Setup cancelled.',
        'same_key_error': 'Error: START and STOP keys cannot be the same!',

        # Countdown settings
        'countdown_prompt': 'Countdown seconds (press Enter for default {})',
        'countdown_error_positive': 'Error: Countdown must be positive!',
        'countdown_error_invalid': 'Error: Invalid number!',

        # Random offset
        'random_offset_title': 'Random time offset in seconds (±N seconds to avoid detection)',
        'random_offset_example': '  Example: 5 means timer will vary between {}~{} seconds',
        'random_offset_prompt': '  Press Enter for default {}',
        'offset_error_negative': 'Error: Offset must be non-negative!',
        'offset_error_range': 'Error: Offset must be less than countdown time ({})!',

        # Auto-click
        'auto_click_prompt': 'Auto-click MapleRoyals windows when timer ends?',
        'auto_click_enable': "  Type '/enable' to enable, or press Enter to disable",
        'auto_click_unavailable': 'Note: Auto-click feature unavailable (missing dependencies)',

        # Window selection
        'no_windows_running': '  No MapleRoyals windows currently running.',
        'will_click_all': '  Will auto-click all MapleRoyals windows when available.',
        'found_windows': '  Found {} MapleRoyals window(s):',
        'window_info': '    [{}] {} {} (HWND: {})',
        'window_position': 'at ({}, {})',
        'commands_title': '  Commands:',
        'command_preview': "    Type number (e.g., '1') to PREVIEW a window (it will flash)",
        'command_all': "    Type '/all' to select all windows",
        'command_select': "    Type numbers separated by commas (e.g., '1,3') to SELECT",
        'command_cancel': '    Press Enter to cancel',
        'enter_command': '  Enter command',
        'selection_cancelled': '  Selection cancelled. Auto-click will be disabled.',
        'selected_all': '  Selected: All {} windows',
        'flashing_window': '  Flashing window [{}]: {}...',
        'window_flashed': '  -> Window flashed! Did you see it?',
        'window_flash_failed': '  -> Warning: Could not flash window (may be minimized)',
        'invalid_index': '  Invalid index: {}',
        'selected_count': '  Selected {} window(s):',
        'window_hwnd': '    - {} (HWND: {})',
        'no_valid_selection': '  No valid windows selected. Try again.',
        'invalid_input': '  Invalid input. Use numbers separated by commas.',
        'unknown_command': '  Unknown command. Try again.',
        'selection_error': '  Error during window selection: {}',

        # Settings saved
        'settings_saved': 'Settings saved to: {}',
        'save_error': 'Failed to save config: {}',

        # Existing configuration
        'found_config': 'Found existing configuration:',
        'config_start_reset': '  START/RESET: [{}]',
        'config_stop': '  STOP: [{}]',
        'config_countdown': '  Countdown: {} seconds',
        'config_auto_click': '  Auto-click MapleRoyals: {}',
        'enabled': 'ENABLED',
        'disabled': 'DISABLED',
        'selected_windows': '  Selected windows: {} window(s) (all valid)',
        'old_config_detected': '  ⚠️  Old configuration format detected (title-based)',
        'reselect_prompt': '  Please re-select windows using new HWND-based system',
        'all_windows_closed': '  ⚠️  All selected windows are closed',
        'some_windows_closed': '  ⚠️  {} of {} selected window(s) are closed',
        'may_want_reselect': '  You may want to re-select windows',
        'needs_reconfiguration': 'Auto-click needs reconfiguration. Type \'/setup\' or press Enter to skip',
        'want_reconfigure': 'Do you want to reconfigure? (Type \'/setup\' or press Enter to skip)',
        'no_config_found': 'No configuration found. Please set up your keys.',
        'setup_failed': 'Setup failed. Using defaults.',
        'using_existing': 'Using existing configuration...',
        'config_updated': 'Configuration updated successfully!',

        # Timer operations
        'press_to_start': 'Press [{}] to START/RESET',
        'press_to_stop': 'Press [{}] to STOP',
        'countdown_display': 'Countdown: {} seconds',
        'auto_click_status': 'Auto-click MapleRoyals: {}',
        'selected_specific': '  Selected {} specific window(s)',
        'mode_all_windows': '  Mode: Click all windows',
        'type_setup': "Type '/setup' to reconfigure",

        # Timer messages
        'timer_started': '[RESET] Timer started: {:.2f}s (base: {:.2f}s, offset: {:+.2f}s)',
        'timer_started_simple': '[RESET] Timer started: {} seconds...',
        'timer_cancelled': '[STOP] Timer cancelled.',
        'times_up': "Time's up! Playing sound...",
        'auto_click_enabled': 'Auto-click is enabled. Clicking MapleRoyals windows...',

        # Auto-restart
        'will_auto_restart': 'Timer will auto-restart in 5 seconds...',
        'press_esc_configure': 'Press ESC to configure settings, or wait to auto-restart',
        'auto_restarting_in': 'Auto-restarting in {:.1f}s... (Press ESC to cancel)',
        'esc_pressed': 'ESC pressed! Configuration menu:',
        'config_menu_1': '1. Type a number to adjust countdown seconds',
        'config_menu_2': "2. Type '/setup' to reconfigure all settings",
        'config_menu_3': '3. Press Enter to restart timer with current settings',
        'your_choice': 'Your choice',
        'countdown_updated': 'Countdown updated to {} seconds.',
        'invalid_time': 'Invalid time. Press trigger key to restart.',
        'auto_restarting_now': 'Auto-restarting timer...',

        # Window clicking
        'no_windows_found': 'No MapleRoyals windows found',
        'none_selected_running': 'None of the selected windows are currently running.',
        'selected_hwnds': 'Selected HWNDs: {}',
        'available_hwnds': 'Available HWNDs: {}',
        'please_reselect': "Please run '/setup' to re-select windows.",
        'warning_missing': 'Warning: {} selected window(s) not running',
        'found_selected': 'Found {} of {} selected window(s)',
        'starting_sequence': 'Starting auto-click sequence...',
        'window_unavailable': '  [{}] Window HWND {} no longer available',
        'warning_activate': '  [{}] Warning: Could not activate HWND {}',
        'clicked': '  [{}] Clicked: {} (HWND: {})',
        'error_with_hwnd': '  [{}] Error with HWND {}: {}...',
        'sequence_completed': 'Auto-click sequence completed',
        'error_in_click': 'Error in click_maple_windows: {}',
        'window_automation_unavailable': 'Window automation not available',

        # Command listener
        'entering_setup': 'Entering setup mode...',
        'setup_cancelled_keeping': 'Setup cancelled. Keeping current configuration.',
        'program_resumed': '=== Program resumed ===',

        # Program termination
        'program_terminated': 'Program terminated.',

        # Language switching
        'language_changed': 'Language changed to English.',
        'language_command_help': "Type '/language' or '/lang' to change language",

        # OTA
        'checking_updates': 'Checking for updates (current: {})...',
        'new_version_found': 'New version found: {}!',
        'already_latest': 'You are already running the latest version.',
        'update_check_failed': 'Failed to check for updates: {}',
        'starting_patch': 'Starting OTA patch...',
        'patch_applied_success': 'Patch applied successfully!',
        'patch_failed': 'Patch failed: {}',
        'update_prompt': 'A newer version is available. Would you like to update?',
        'update_choice_prompt': 'Update now? [Y/n]: ',
        'restarting_program': 'Restarting program to apply updates...',
        'warning_automation': 'Warning: pygetwindow or pyautogui not installed. Window automation disabled.',
        'load_config_error': 'Failed to load config: {}',
        'invalid_warning': 'Warning: Invalid index {}, skipping',

        # Auto Switch (Alt+Esc)
        'auto_switch_prompt': 'Auto window-switch (Alt+Esc) when timer ends?',
        'auto_switch_enable': "  Type '/enable' to restore, or press Enter to skip",
        'starting_switch_sequence': 'Starting Alt+Esc sequence for {} window(s)...',
        'switch_sequence_completed': 'Alt+Esc sequence completed.',
        'config_auto_switch': '  Auto window-switch: {}',
        'auto_switch_status': 'Auto window-switch: {}',

        # Mouse Speed
        'mouse_speed_prompt': 'Mouse moving speed (1: Slow, 2: Normal, 3: Fast, 4: Instant) [Default: 2]',
        'mouse_speed_updated': 'Mouse speed set to: {}',

        # Switch Interval
        'switch_interval_prompt': 'Base interval between Alt+Esc switches (seconds) [Default: 1.5]',
        'switch_interval_updated': 'Switch interval base set to: {}s',

        # Attack Key
        'attack_key_prompt': 'Attack key to press after switching (press Enter to skip)',
        'attack_key_updated': 'Attack key set to: [{}]',
        'pressing_attack_key': '  -> Pressing attack key: [{}]',

        # Manual Trigger Configuration
        'wait_for_trigger_prompt': 'Wait for manual trigger after completing all window switches?',
        'wait_for_trigger_enable': "  Type '/enable' to wait, or press Enter for auto-restart",
        'config_wait_for_trigger': '  Manual trigger after cycle: {}',
        'waiting_for_next_trigger': 'Cycle completed. Waiting for manual key press to restart timer.',

        # Beautiful Logs
        'log_window_header': '[Window {}/{}] --------------------------',
        'log_alt_esc': '  -> Alt + Esc: Press ({:.0f}ms) | Release ({:.0f}ms)',
        'log_focus_delay': '  -> Reaction delay: {:.0f}ms',
        'log_attack': '  -> Attack action: [{}] ({:.0f}ms)',
        'log_next_delay': '  -> Next switch delay: {:.2f}s',

        # Fatigue Simulator
        'log_human_state': '✨ Human State: {} (Fatigue factor: x{:.2f})',
        'state_focused': 'Focused',
        'state_normal': 'Normal',
        'state_tired': 'Tired',
        'state_drowsy': 'Drowsy',
        'state_energized': 'Energized',

        # Anti-Detection
        'log_anti_detect_pause': '🛡️ Simulating human thought... ({:.1f}s)',
        'log_long_break': '🛌 Forced human break for physical recovery ({:.1f} mins)',
        'log_dynamic_shift': '🔄 Pattern shifting: {:+.2f}s',

        # System Tray
        'tray_show': 'Show Console',
        'tray_hide': 'Hide Console',
        'tray_start': 'Start/Reset Timer',
        'tray_stop': 'Stop Timer',
        'tray_exit': 'Exit Program',
        'tray_status_running': 'Running (Left: {})',
        'tray_status_idle': 'Idle',
        'console_hidden': 'Console hidden. You can open it from the system tray.',

        # Easter Eggs
        'easter_egg_coffee': '☕ Maru is grinding virtual beans for you... (Focused state chance increased!)',
        'ota_success_banner': '🎊 OTA Update successful! Applied codename: {}',

        # Extra Keys
        'extra_keys_prompt': 'Add high-level custom keys (e.g. key:cooldown)?',
        'extra_keys_instruction': '  Format: key1:seconds1,key2:seconds2 (e.g. x:30,v:15)',
        'extra_keys_skip': '  Press Enter to skip',
        'config_extra_keys': '  Extra Keys: {}',
        'pressing_extra_key': '  -> Pressing extra scheduled key: [{}]',
    },
    'zh_TW': {
        # Language selection
        'select_language': 'Select Language / 選擇語言',
        'language_options': '  [1] English\n  [2] 繁體中文',
        'language_prompt': '請輸入選項 (1-2)',
        'invalid_language': '無效的選擇。使用繁體中文。',

        # Program header
        'program_title': '=== 計時器程式 ===',
        'program_started': '=== 程式已啟動 ===',

        # Configuration
        'key_configuration': '=== 按鍵設定 ===',
        'press_key_instruction': '請按下您想使用的按鍵（按 ESC 取消）',
        'press_start_key': '請按下「開始/重置」計時器的按鍵：',
        'press_stop_key': '請按下「停止」計時器的按鍵：',
        'selected': '  -> 已選擇：[{}]',
        'setup_cancelled': '設定已取消。',
        'same_key_error': '錯誤：開始鍵和停止鍵不能相同！',

        # Countdown settings
        'countdown_prompt': '倒數秒數（按 Enter 使用預設值 {}）',
        'countdown_error_positive': '錯誤：倒數時間必須為正數！',
        'countdown_error_invalid': '錯誤：無效的數字！',

        # Random offset
        'random_offset_title': '隨機時間偏移秒數（±N 秒以避免被偵測）',
        'random_offset_example': '  範例：5 表示計時器會在 {}~{} 秒之間變化',
        'random_offset_prompt': '  按 Enter 使用預設值 {}',
        'offset_error_negative': '錯誤：偏移值必須為非負數！',
        'offset_error_range': '錯誤：偏移值必須小於倒數時間（{}）！',

        # Auto-click
        'auto_click_prompt': '計時結束時自動點擊 MapleRoyals 視窗？',
        'auto_click_enable': "  輸入 '/enable' 啟用，或按 Enter 停用",
        'auto_click_unavailable': '注意：自動點擊功能無法使用（缺少相依套件）',

        # Window selection
        'no_windows_running': '  目前沒有執行中的 MapleRoyals 視窗。',
        'will_click_all': '  將會自動點擊所有可用的 MapleRoyals 視窗。',
        'found_windows': '  找到 {} 個 MapleRoyals 視窗：',
        'window_info': '    [{}] {} {} (HWND: {})',
        'window_position': '位於 ({}, {})',
        'commands_title': '  指令：',
        'command_preview': "    輸入數字（例如 '1'）來預覽視窗（將會閃爍）",
        'command_all': "    輸入 '/all' 選擇所有視窗",
        'command_select': "    輸入逗號分隔的數字（例如 '1,3'）來選擇",
        'command_cancel': '    按 Enter 取消',
        'enter_command': '  請輸入指令',
        'selection_cancelled': '  已取消選擇。自動點擊將被停用。',
        'selected_all': '  已選擇：全部 {} 個視窗',
        'flashing_window': '  正在閃爍視窗 [{}]：{}...',
        'window_flashed': '  -> 視窗已閃爍！您看到了嗎？',
        'window_flash_failed': '  -> 警告：無法閃爍視窗（可能已最小化）',
        'invalid_index': '  無效的索引：{}',
        'selected_count': '  已選擇 {} 個視窗：',
        'window_hwnd': '    - {} (HWND: {})',
        'no_valid_selection': '  沒有選擇有效的視窗。請重試。',
        'invalid_input': '  無效的輸入。請使用逗號分隔的數字。',
        'unknown_command': '  未知的指令。請重試。',
        'selection_error': '  視窗選擇時發生錯誤：{}',

        # Settings saved
        'settings_saved': '設定已儲存至：{}',
        'save_error': '儲存設定失敗：{}',

        # Existing configuration
        'found_config': '找到現有設定：',
        'config_start_reset': '  開始/重置：[{}]',
        'config_stop': '  停止：[{}]',
        'config_countdown': '  倒數：{} 秒',
        'config_auto_click': '  自動點擊 MapleRoyals：{}',
        'enabled': '已啟用',
        'disabled': '已停用',
        'selected_windows': '  已選擇視窗：{} 個視窗（全部有效）',
        'old_config_detected': '  ⚠️  偵測到舊的設定格式（基於標題）',
        'reselect_prompt': '  請使用新的 HWND 系統重新選擇視窗',
        'all_windows_closed': '  ⚠️  所有已選擇的視窗都已關閉',
        'some_windows_closed': '  ⚠️  {} 個（共 {}）已選擇的視窗已關閉',
        'may_want_reselect': '  您可能需要重新選擇視窗',
        'needs_reconfiguration': '自動點擊需要重新設定。輸入 \'/setup\' 或按 Enter 跳過',
        'want_reconfigure': '是否要重新設定？（輸入 \'/setup\' 或按 Enter 跳過）',
        'no_config_found': '找不到設定檔。請設定您的按鍵。',
        'setup_failed': '設定失敗。使用預設值。',
        'using_existing': '使用現有設定...',
        'config_updated': '設定更新成功！',

        # Timer operations
        'press_to_start': '按 [{}] 開始/重置',
        'press_to_stop': '按 [{}] 停止',
        'countdown_display': '倒數：{} 秒',
        'auto_click_status': '自動點擊 MapleRoyals：{}',
        'selected_specific': '  已選擇 {} 個特定視窗',
        'mode_all_windows': '  模式：點擊所有視窗',
        'type_setup': "輸入 '/setup' 重新設定",

        # Timer messages
        'timer_started': '[重置] 計時器已啟動：{:.2f}秒（基礎：{:.2f}秒，偏移：{:+.2f}秒）',
        'timer_started_simple': '[重置] 計時器已啟動：{} 秒...',
        'timer_cancelled': '[停止] 計時器已取消。',
        'times_up': '時間到！播放音效...',
        'auto_click_enabled': '自動點擊已啟用。正在點擊 MapleRoyals 視窗...',

        # Auto-restart
        'will_auto_restart': '計時器將在 5 秒後自動重啟...',
        'press_esc_configure': '按 ESC 進行設定，或等待自動重啟',
        'auto_restarting_in': '{:.1f}秒後自動重啟...（按 ESC 取消）',
        'esc_pressed': '已按下 ESC！設定選單：',
        'config_menu_1': '1. 輸入數字調整倒數秒數',
        'config_menu_2': "2. 輸入 '/setup' 重新設定所有選項",
        'config_menu_3': '3. 按 Enter 使用目前設定重啟計時器',
        'your_choice': '您的選擇',
        'countdown_updated': '倒數時間已更新為 {} 秒。',
        'invalid_time': '無效的時間。按觸發鍵重新啟動。',
        'auto_restarting_now': '正在自動重啟計時器...',

        # Window clicking
        'no_windows_found': '找不到 MapleRoyals 視窗',
        'none_selected_running': '所選擇的視窗目前都沒有執行中。',
        'selected_hwnds': '已選擇的 HWNDs：{}',
        'available_hwnds': '可用的 HWNDs：{}',
        'please_reselect': "請執行 '/setup' 重新選擇視窗。",
        'warning_missing': '警告：{} 個已選擇的視窗未執行中',
        'found_selected': '找到 {} 個（共 {}）已選擇的視窗',
        'starting_sequence': '開始自動點擊序列...',
        'window_unavailable': '  [{}/{}] 視窗 HWND {} 已無法使用',
        'warning_activate': '  [{}/{}] 警告：無法啟動 HWND {}',
        'clicked': '  [{}/{}] 已點擊：{} (HWND: {})',
        'error_with_hwnd': '  [{}/{}] HWND {} 發生錯誤：{}...',
        'sequence_completed': '自動點擊序列已完成',
        'error_in_click': 'click_maple_windows 發生錯誤：{}',
        'window_automation_unavailable': '視窗自動化功能無法使用',

        # Command listener
        'entering_setup': '進入設定模式...',
        'setup_cancelled_keeping': '設定已取消。保留目前設定。',
        'program_resumed': '=== 程式已恢復 ===',

        # Program termination
        'program_terminated': '程式已終止。',

        # Language switching
        'language_changed': '語言已切換為繁體中文。',
        'language_command_help': "輸入 '/language' 或 '/lang' 切換語言",

        # OTA
        'checking_updates': '正在檢查更新 (目前版本: {})...',
        'new_version_found': '發現新版本: {}!',
        'already_latest': '目前的預設腳本已是最新版本。',
        'update_check_failed': '更新檢查失敗: {}',
        'starting_patch': '正在執行 OTA 線上更新 (Patch)...',
        'patch_applied_success': '更新成功！檔案已完成覆蓋。',
        'patch_failed': '更新失敗: {}',
        'update_prompt': '發現較新的程式版本，建議立即更新以獲取最新功能。',
        'update_choice_prompt': '是否立即執行更新？ [Y/n]: ',
        'restarting_program': '正在重啟程式以套用更新...',
        'warning_automation': '警告：pygetwindow 或 pyautogui 未安裝。視窗自動化已停用。',
        'load_config_error': '載入設定失敗：{}',
        'invalid_warning': '警告：無效的索引 {}，跳過',

        # Auto Switch (Alt+Esc)
        'auto_switch_prompt': '計時結束時自動切換視窗 (Alt+Esc)？',
        'auto_switch_enable': "  輸入 '/enable' 恢復，或按 Enter 跳過",
        'starting_switch_sequence': '開始執行 {} 個視窗的 Alt+Esc 切換序列...',
        'switch_sequence_completed': 'Alt+Esc 切換序列執行完畢。',
        'config_auto_switch': '  自動視窗切換 (Alt+Esc)：{}',
        'auto_switch_status': '自動視窗切換：{}',

        # Mouse Speed
        'mouse_speed_prompt': '滑鼠移動速度 (1: 慢, 2: 正常, 3: 快, 4: 極快) [預設: 2]',
        'mouse_speed_updated': '滑鼠移動速度已設為: {}',

        # Switch Interval
        'switch_interval_prompt': 'Alt+Esc 切換基礎間隔秒數 [預設: 1.5]',
        'switch_interval_updated': '切換間隔基礎值已設為: {}秒',

        # Attack Key
        'attack_key_prompt': '切換視窗後的攻擊按鍵（直接按 Enter 跳過）',
        'attack_key_updated': '攻擊按鍵已設為：[{}]',
        'pressing_attack_key': '  -> 正在按下攻擊按鍵：[{}]',

        # Manual Trigger Configuration
        'wait_for_trigger_prompt': '在完成所有視窗切換後等待手動再次觸發？',
        'wait_for_trigger_enable': "  輸入 '/enable' 啟用手動等待，或按 Enter 自動重啟",
        'config_wait_for_trigger': '  完成後手動觸發: {}',
        'waiting_for_next_trigger': '輪詢結束。請手動按下按鍵重新啟動計時器。',

        # Beautiful Logs
        'log_window_header': '[視窗 {}/{}] --------------------------',
        'log_alt_esc': '  -> Alt + Esc: 按下 ({:.0f}ms) | 放開 ({:.0f}ms)',
        'log_focus_delay': '  -> 擬人反應等待: {:.0f}ms',
        'log_attack': '  -> 執行攻擊行動: [{}] ({:.0f}ms)',
        'log_next_delay': '  -> 下次同步延遲: {:.2f}秒',

        # Fatigue Simulator
        'log_human_state': '✨ 當前狀態: {} (疲勞係數: x{:.2f})',
        'state_focused': '非常專注',
        'state_normal': '一般狀態',
        'state_tired': '有點疲累',
        'state_drowsy': '精神恍惚',
        'state_energized': '精神煥發 (神速)',

        # Anti-Detection
        'log_anti_detect_pause': '🛡️ 模擬人類思考中... ({:.1f}秒)',
        'log_long_break': '🛌 人類體力不支，正在進行中途休息 ({:.1f}分鐘)',
        'log_dynamic_shift': '🔄 偵測到節奏模式，實施動態相位偏移: {:+.2f}秒',

        # System Tray
        'tray_show': '顯示控制台',
        'tray_hide': '隱藏控制台',
        'tray_start': '開始/重置計時',
        'tray_stop': '停止計時',
        'tray_exit': '結束程式',
        'tray_status_running': '計時中 (剩餘: {})',
        'tray_status_idle': '閒置中',
        'console_hidden': '控制台已隱藏。您可以透過右下角系統匣開啟。',

        # Easter Eggs
        'easter_egg_coffee': '☕ Maru 正在為您研磨擬人化咖啡豆...（進入專注狀態機率提高！）',
        'ota_success_banner': '🎊 OTA 線上更新成功！本次更新代號：{}',

        # Extra Keys
        'extra_keys_prompt': '是否增加額外的自定義排程按鍵？',
        'extra_keys_instruction': '  格式：按鍵1:秒數1,按鍵2:秒數2（範例：x:30,v:15）',
        'extra_keys_skip': '  按 Enter 跳過',
        'config_extra_keys': '  額外按鍵排程: {}',
        'pressing_extra_key': '  -> 正在按下排程按鍵：[{}]',
    }
}

# Current language (default)
current_lang = 'zh_TW'

def set_language(lang_code):
    """Set the current language."""
    global current_lang
    if lang_code in LANGUAGES:
        current_lang = lang_code
        return True
    return False

def t(key, *args):
    """
    Translate a key to the current language.

    Args:
        key: The translation key
        *args: Optional format arguments

    Returns:
        Translated and formatted string
    """
    text = LANGUAGES.get(current_lang, LANGUAGES['en']).get(key, key)
    if args:
        try:
            return text.format(*args)
        except (IndexError, KeyError):
            return text
    return text

def get_current_language():
    """Get the current language code."""
    return current_lang

def select_language():
    """
    Interactive language selection at program startup.

    Returns:
        Selected language code ('en' or 'zh_TW')
    """
    print("\n" + t('select_language'))
    print(t('language_options'))
    print(f"\n{t('language_prompt')}: ", end='', flush=True)

    try:
        choice = input().strip()
        if choice == '1':
            set_language('en')
            return 'en'
        elif choice == '2':
            set_language('zh_TW')
            return 'zh_TW'
        else:
            # Default to Traditional Chinese
            print(t('invalid_language'))
            set_language('zh_TW')
            return 'zh_TW'
    except (EOFError, KeyboardInterrupt):
        set_language('zh_TW')
        return 'zh_TW'
