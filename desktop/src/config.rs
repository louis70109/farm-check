//! Settings persistence, compatible with the Python app's `timer_config.json`.
//!
//! Keys this app owns are read and written. Any other keys in the file
//! (for example `selected_window_hwnds` written by the Python version) are
//! kept untouched so both programs can share the same file.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};

use serde_json::{Map, Number, Value};

pub const CONFIG_FILE: &str = "timer_config.json";
pub const DEFAULT_TRIGGER_KEY: &str = "page up";
pub const DEFAULT_STOP_KEY: &str = "page down";
pub const DEFAULT_COUNTDOWN_SECONDS: f64 = 130.0;
pub const DEFAULT_RANDOM_OFFSET_SECONDS: f64 = 0.0;
pub const DEFAULT_LANGUAGE: &str = "zh_TW";

#[derive(Debug, Clone, PartialEq)]
pub struct Settings {
    pub trigger_key: String,
    pub stop_key: String,
    pub countdown_seconds: f64,
    pub random_offset_seconds: f64,
    /// `"zh_TW"` or `"en"`.
    pub language: String,
    /// Keys owned by other programs; preserved on save.
    extra: Map<String, Value>,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            trigger_key: DEFAULT_TRIGGER_KEY.into(),
            stop_key: DEFAULT_STOP_KEY.into(),
            countdown_seconds: DEFAULT_COUNTDOWN_SECONDS,
            random_offset_seconds: DEFAULT_RANDOM_OFFSET_SECONDS,
            language: DEFAULT_LANGUAGE.into(),
            extra: Map::new(),
        }
    }
}

impl Settings {
    /// Parse settings from JSON text, falling back to defaults for anything
    /// missing or invalid. Never fails.
    pub fn parse(text: &str) -> Settings {
        let mut settings = Settings::default();
        let Ok(Value::Object(mut map)) = serde_json::from_str::<Value>(text) else {
            return settings;
        };

        if let Some(key) = take_nonempty_string(&mut map, "trigger_key") {
            settings.trigger_key = key;
        }
        if let Some(key) = take_nonempty_string(&mut map, "stop_key") {
            settings.stop_key = key;
        }
        if let Some(seconds) = map
            .remove("countdown_seconds")
            .and_then(|v| v.as_f64())
            .filter(|s| s.is_finite() && *s > 0.0)
        {
            settings.countdown_seconds = seconds;
        }
        if let Some(offset) = map
            .remove("random_offset_seconds")
            .and_then(|v| v.as_f64())
            .filter(|s| s.is_finite() && *s >= 0.0 && *s < settings.countdown_seconds)
        {
            settings.random_offset_seconds = offset;
        }
        if let Some(lang) = take_nonempty_string(&mut map, "language") {
            if lang == "en" || lang == "zh_TW" {
                settings.language = lang;
            }
        }

        settings.extra = map;
        settings
    }

    /// Serialize to JSON text, merging in the preserved foreign keys.
    pub fn serialize(&self) -> String {
        let mut map = self.extra.clone();
        map.insert(
            "trigger_key".into(),
            Value::String(self.trigger_key.clone()),
        );
        map.insert("stop_key".into(), Value::String(self.stop_key.clone()));
        map.insert(
            "countdown_seconds".into(),
            number_value(self.countdown_seconds),
        );
        map.insert(
            "random_offset_seconds".into(),
            number_value(self.random_offset_seconds),
        );
        map.insert("language".into(), Value::String(self.language.clone()));
        serde_json::to_string_pretty(&Value::Object(map))
            .expect("serializing a JSON object cannot fail")
    }
}

fn take_nonempty_string(map: &mut Map<String, Value>, key: &str) -> Option<String> {
    map.remove(key)
        .and_then(|v| v.as_str().map(str::to_owned))
        .filter(|s| !s.trim().is_empty())
}

/// Write whole numbers as integers (`130`, not `130.0`) like the Python app.
fn number_value(v: f64) -> Value {
    if v.fract() == 0.0 && v.abs() < i64::MAX as f64 {
        Value::Number(Number::from(v as i64))
    } else {
        Value::Number(Number::from_f64(v).unwrap_or_else(|| Number::from(0)))
    }
}

/// Config location: next to the executable (like the frozen Python build),
/// falling back to the current directory.
pub fn config_path() -> PathBuf {
    std::env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(|dir| dir.join(CONFIG_FILE)))
        .unwrap_or_else(|| PathBuf::from(CONFIG_FILE))
}

/// Load settings; a missing or unreadable file yields defaults.
pub fn load(path: &Path) -> Settings {
    match fs::read_to_string(path) {
        Ok(text) => Settings::parse(&text),
        Err(_) => Settings::default(),
    }
}

pub fn save(path: &Path, settings: &Settings) -> io::Result<()> {
    fs::write(path, settings.serialize())
}

/// Map a keyboard-library style key name (as stored in the config, e.g.
/// `"page up"`) to the key string GPUI reports (e.g. `"pageup"`).
pub fn key_to_config_name(gpui_key: &str) -> String {
    match gpui_key {
        "pageup" => "page up".into(),
        "pagedown" => "page down".into(),
        "escape" => "esc".into(),
        other => other.to_string(),
    }
}

/// Inverse of [`key_to_config_name`].
pub fn config_name_to_key(name: &str) -> String {
    match name {
        "page up" => "pageup".into(),
        "page down" => "pagedown".into(),
        "esc" => "escape".into(),
        other => other.to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn defaults_when_empty() {
        assert_eq!(Settings::parse("{}"), Settings::default());
        assert_eq!(Settings::parse("not json"), Settings::default());
    }

    #[test]
    fn reads_python_written_file() {
        let text = r#"{
            "trigger_key": "f1",
            "stop_key": "f2",
            "countdown_seconds": 90,
            "random_offset_seconds": 5,
            "auto_click_windows": true,
            "selected_window_hwnds": [262148, 393218],
            "language": "en"
        }"#;
        let s = Settings::parse(text);
        assert_eq!(s.trigger_key, "f1");
        assert_eq!(s.stop_key, "f2");
        assert_eq!(s.countdown_seconds, 90.0);
        assert_eq!(s.random_offset_seconds, 5.0);
        assert_eq!(s.language, "en");
    }

    #[test]
    fn invalid_values_fall_back_to_defaults() {
        let s = Settings::parse(
            r#"{"countdown_seconds": -3, "random_offset_seconds": 500, "language": "fr", "trigger_key": "  "}"#,
        );
        assert_eq!(s.countdown_seconds, DEFAULT_COUNTDOWN_SECONDS);
        assert_eq!(s.random_offset_seconds, 0.0);
        assert_eq!(s.language, DEFAULT_LANGUAGE);
        assert_eq!(s.trigger_key, DEFAULT_TRIGGER_KEY);
    }

    #[test]
    fn save_preserves_foreign_keys_and_writes_integers() {
        let mut s =
            Settings::parse(r#"{"selected_window_hwnds": [1, 2], "auto_click_windows": true}"#);
        s.countdown_seconds = 130.0;
        s.random_offset_seconds = 2.5;
        let out: Value = serde_json::from_str(&s.serialize()).unwrap();
        assert_eq!(out["selected_window_hwnds"], serde_json::json!([1, 2]));
        assert_eq!(out["auto_click_windows"], Value::Bool(true));
        assert_eq!(out["countdown_seconds"], serde_json::json!(130));
        assert_eq!(out["random_offset_seconds"], serde_json::json!(2.5));
        assert_eq!(Settings::parse(&s.serialize()), s);
    }

    #[test]
    fn key_name_mapping_round_trips() {
        for name in ["page up", "page down", "esc", "f1", "a"] {
            assert_eq!(key_to_config_name(&config_name_to_key(name)), name);
        }
        assert_eq!(config_name_to_key("page up"), "pageup");
        assert_eq!(key_to_config_name("escape"), "esc");
    }
}
