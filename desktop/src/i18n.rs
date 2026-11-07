//! Traditional Chinese (zh_TW) and English strings for the desktop UI.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Lang {
    ZhTw,
    En,
}

impl Lang {
    pub fn from_code(code: &str) -> Lang {
        match code {
            "en" => Lang::En,
            _ => Lang::ZhTw,
        }
    }

    pub fn code(self) -> &'static str {
        match self {
            Lang::ZhTw => "zh_TW",
            Lang::En => "en",
        }
    }

    pub fn other(self) -> Lang {
        match self {
            Lang::ZhTw => Lang::En,
            Lang::En => Lang::ZhTw,
        }
    }

    /// Name of this language, written in that language.
    pub fn native_name(self) -> &'static str {
        match self {
            Lang::ZhTw => "繁體中文",
            Lang::En => "English",
        }
    }
}

/// Translate `key`. Unknown keys are returned unchanged.
pub fn tr(lang: Lang, key: &'static str) -> &'static str {
    let (zh, en) = match key {
        "title" => ("計時器", "Timer"),
        "remaining" => ("剩餘時間", "Time remaining"),
        "countdown_total" => ("倒數時長", "Countdown"),
        "status_idle" => (
            "待機中，按下開始鍵啟動",
            "Idle — press the START key to begin",
        ),
        "status_running" => ("計時中…", "Running…"),
        "status_finished" => ("時間到！", "Time's up!"),
        "status_stopped" => ("已停止", "Stopped"),
        "start" => ("開始 / 重置", "Start / Reset"),
        "stop" => ("停止", "Stop"),
        "settings" => ("設定", "Settings"),
        "countdown_seconds" => ("倒數秒數", "Countdown (seconds)"),
        "random_offset" => ("隨機偏移 ±秒", "Random offset ±seconds"),
        "offset_hint" => (
            "例：5 表示每次倒數在設定值 ±5 秒之間隨機（避免固定節奏）",
            "e.g. 5 means each run varies randomly within ±5 seconds of the setting",
        ),
        "start_key" => ("開始 / 重置 熱鍵", "START / RESET key"),
        "stop_key" => ("停止 熱鍵", "STOP key"),
        "change" => ("變更", "Change"),
        "press_key" => (
            "請按下要使用的按鍵（Esc 取消）…",
            "Press a key (Esc to cancel)…",
        ),
        "same_key_error" => (
            "開始與停止不能是同一個按鍵",
            "START and STOP keys cannot be the same",
        ),
        "hotkey_scope" => (
            "熱鍵只在本視窗有焦點時有效（尚不支援全域熱鍵）",
            "Hotkeys work only while this window is focused (no global hotkeys yet)",
        ),
        "timer_started" => (
            "實際倒數 {}s（基準 {}s，偏移 {}s）",
            "Running {}s (base {}s, offset {}s)",
        ),
        "saved_to" => ("已儲存至 {}", "Saved to {}"),
        "save_error" => ("儲存設定失敗：{}", "Failed to save settings: {}"),
        _ => return key_fallback(key),
    };
    match lang {
        Lang::ZhTw => zh,
        Lang::En => en,
    }
}

/// Keys that are not in the table are returned as-is; this is only hit for
/// programmer error, and keeps the UI readable rather than panicking.
fn key_fallback(key: &'static str) -> &'static str {
    key
}

/// Replace each `{}` in `template`, in order, with the given arguments.
pub fn fmt(template: &str, args: &[String]) -> String {
    let mut out = String::with_capacity(template.len());
    let mut rest = template;
    let mut args = args.iter();
    while let Some(pos) = rest.find("{}") {
        out.push_str(&rest[..pos]);
        out.push_str(args.next().map(String::as_str).unwrap_or("{}"));
        rest = &rest[pos + 2..];
    }
    out.push_str(rest);
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn language_codes_round_trip() {
        assert_eq!(Lang::from_code("en"), Lang::En);
        assert_eq!(Lang::from_code("zh_TW"), Lang::ZhTw);
        assert_eq!(Lang::from_code("unknown"), Lang::ZhTw);
        assert_eq!(Lang::En.other(), Lang::ZhTw);
        assert_eq!(Lang::ZhTw.code(), "zh_TW");
    }

    #[test]
    fn every_key_is_translated_in_both_languages() {
        let keys = [
            "title",
            "remaining",
            "countdown_total",
            "status_idle",
            "status_running",
            "status_finished",
            "status_stopped",
            "start",
            "stop",
            "settings",
            "countdown_seconds",
            "random_offset",
            "offset_hint",
            "start_key",
            "stop_key",
            "change",
            "press_key",
            "same_key_error",
            "hotkey_scope",
            "timer_started",
            "saved_to",
            "save_error",
        ];
        for key in keys {
            assert_ne!(tr(Lang::ZhTw, key), key, "missing zh_TW for {key}");
            assert_ne!(tr(Lang::En, key), key, "missing en for {key}");
        }
    }

    #[test]
    fn fmt_fills_placeholders_in_order() {
        assert_eq!(
            fmt("實際 {}s（基準 {}s）", &["12.5".into(), "130".into()]),
            "實際 12.5s（基準 130s）"
        );
        assert_eq!(fmt("no args", &[]), "no args");
        assert_eq!(fmt("{} {}", &["a".into()]), "a {}");
    }
}
