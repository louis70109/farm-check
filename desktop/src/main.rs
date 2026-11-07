//! Desktop countdown timer built with GPUI (the Rust UI framework from Zed).
//!
//! A GUI port of the Python `timer.py` countdown: adjustable countdown and
//! random offset, START/RESET and STOP hotkeys, progress bar, zh_TW / en UI,
//! and settings shared with the Python version through `timer_config.json`.

mod config;
mod i18n;
mod timer;

use std::path::PathBuf;
use std::time::{Duration, Instant};

use gpui::{
    div, prelude::*, px, relative, rgb, size, App, Application, Bounds, ClickEvent, Context, Div,
    FocusHandle, FontWeight, KeyDownEvent, SharedString, Stateful, TitlebarOptions, Window,
    WindowBounds, WindowOptions,
};

use config::Settings;
use i18n::{fmt, tr, Lang};
use timer::{format_mmss, Countdown, Phase, Plan};

const BG: u32 = 0x1e1e2e;
const PANEL: u32 = 0x27273a;
const TEXT: u32 = 0xf5f5f5;
const MUTED: u32 = 0x9ca3af;
const ACCENT: u32 = 0x2563eb;
const DANGER: u32 = 0xdc2626;
const BUTTON: u32 = 0x3f3f56;
const BAR_TRACK: u32 = 0x3f3f56;
const BAR_FILL: u32 = 0x22c55e;
const WARN: u32 = 0xf59e0b;

/// Which hotkey is being re-bound.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Slot {
    Start,
    Stop,
}

/// Modifier-only key names; pressing these alone never binds a hotkey.
const MODIFIER_KEYS: &[&str] = &[
    "shift", "control", "alt", "platform", "function", "capslock",
];

struct TimerApp {
    focus: FocusHandle,
    settings: Settings,
    settings_path: PathBuf,
    countdown: Countdown,
    last_plan: Option<Plan>,
    recording: Option<Slot>,
    notice: Option<String>,
}

impl TimerApp {
    fn new(settings: Settings, settings_path: PathBuf, cx: &mut Context<Self>) -> Self {
        // Drive the progress bar and detect time-up. The loop ends when the
        // view is dropped (`update` returns an error).
        cx.spawn(async move |this, cx| loop {
            cx.background_executor()
                .timer(Duration::from_millis(100))
                .await;
            if this.update(cx, |app, cx| app.tick(cx)).is_err() {
                break;
            }
        })
        .detach();

        Self {
            focus: cx.focus_handle(),
            settings,
            settings_path,
            countdown: Countdown::default(),
            last_plan: None,
            recording: None,
            notice: None,
        }
    }

    fn lang(&self) -> Lang {
        Lang::from_code(&self.settings.language)
    }

    fn tick(&mut self, cx: &mut Context<Self>) {
        let finished = self.countdown.poll(Instant::now());
        if finished {
            beep();
        }
        if self.countdown.is_running() || finished {
            cx.notify();
        }
    }

    fn start_timer(&mut self, cx: &mut Context<Self>) {
        let mut rng = rand::thread_rng();
        let plan = self.countdown.start(
            Instant::now(),
            self.settings.countdown_seconds,
            self.settings.random_offset_seconds,
            &mut rng,
        );
        self.last_plan = Some(plan);
        self.recording = None;
        cx.notify();
    }

    fn stop_timer(&mut self, cx: &mut Context<Self>) {
        self.countdown.stop();
        cx.notify();
    }

    fn adjust_countdown(&mut self, delta: f64, cx: &mut Context<Self>) {
        let value = (self.settings.countdown_seconds + delta).clamp(1.0, 99_999.0);
        self.settings.countdown_seconds = value;
        // Keep the offset strictly below the countdown, as the Python setup does.
        self.settings.random_offset_seconds = self
            .settings
            .random_offset_seconds
            .min((value - 0.1).max(0.0));
        self.persist();
        cx.notify();
    }

    fn adjust_offset(&mut self, delta: f64, cx: &mut Context<Self>) {
        let max = (self.settings.countdown_seconds - 0.1).max(0.0);
        self.settings.random_offset_seconds =
            (self.settings.random_offset_seconds + delta).clamp(0.0, max);
        self.persist();
        cx.notify();
    }

    fn toggle_language(&mut self, cx: &mut Context<Self>) {
        self.settings.language = self.lang().other().code().into();
        self.persist();
        cx.notify();
    }

    fn begin_recording(&mut self, slot: Slot, cx: &mut Context<Self>) {
        self.recording = Some(slot);
        self.notice = None;
        cx.notify();
    }

    fn on_key_down(&mut self, event: &KeyDownEvent, _window: &mut Window, cx: &mut Context<Self>) {
        let key = event.keystroke.key.as_str();
        if MODIFIER_KEYS.contains(&key) {
            return;
        }

        if let Some(slot) = self.recording {
            if key == "escape" {
                self.recording = None;
                self.notice = None;
                cx.notify();
                return;
            }
            let name = config::key_to_config_name(key);
            let other = match slot {
                Slot::Start => self.settings.stop_key.clone(),
                Slot::Stop => self.settings.trigger_key.clone(),
            };
            self.recording = None;
            if name == other {
                self.notice = Some(tr(self.lang(), "same_key_error").into());
            } else {
                match slot {
                    Slot::Start => self.settings.trigger_key = name,
                    Slot::Stop => self.settings.stop_key = name,
                }
                self.persist();
            }
            cx.notify();
            return;
        }

        if event.is_held {
            return;
        }
        if key == config::config_name_to_key(&self.settings.trigger_key) {
            self.start_timer(cx);
        } else if key == config::config_name_to_key(&self.settings.stop_key) {
            self.stop_timer(cx);
        }
    }

    fn persist(&mut self) {
        self.notice = Some(match config::save(&self.settings_path, &self.settings) {
            Ok(()) => fmt(
                tr(self.lang(), "saved_to"),
                &[self.settings_path.display().to_string()],
            ),
            Err(err) => fmt(tr(self.lang(), "save_error"), &[err.to_string()]),
        });
    }

    // ---- rendering -------------------------------------------------------

    fn button(id: impl Into<gpui::ElementId>, label: String, color: u32) -> Stateful<Div> {
        div()
            .id(id)
            .px_3()
            .py_1()
            .rounded_md()
            .bg(rgb(color))
            .text_color(rgb(0xffffff))
            .cursor_pointer()
            .child(label)
    }

    /// `[-big] [-small] value [+small] [+big]` row.
    fn stepper(
        &self,
        cx: &mut Context<Self>,
        prefix: &'static str,
        value: String,
        small: f64,
        big: f64,
        on_change: fn(&mut Self, f64, &mut Context<Self>),
    ) -> Div {
        let step = |id: String, label: String, delta: f64| {
            Self::button(SharedString::from(id), label, BUTTON).on_click(
                cx.listener(move |this, _: &ClickEvent, _window, cx| on_change(this, delta, cx)),
            )
        };
        div()
            .flex()
            .items_center()
            .justify_center()
            .gap_1()
            .child(step(format!("{prefix}-big-minus"), format!("-{big}"), -big))
            .child(step(format!("{prefix}-minus"), format!("-{small}"), -small))
            .child(
                div()
                    .w(px(72.))
                    .text_center()
                    .font_weight(FontWeight::SEMIBOLD)
                    .child(value),
            )
            .child(step(format!("{prefix}-plus"), format!("+{small}"), small))
            .child(step(format!("{prefix}-big-plus"), format!("+{big}"), big))
    }

    fn hotkey_row(&self, cx: &mut Context<Self>, slot: Slot, label: String) -> Div {
        let lang = self.lang();
        let (name, id) = match slot {
            Slot::Start => (self.settings.trigger_key.clone(), "hotkey-start"),
            Slot::Stop => (self.settings.stop_key.clone(), "hotkey-stop"),
        };
        let recording = self.recording == Some(slot);
        let value = if recording {
            tr(lang, "press_key").to_string()
        } else {
            name.to_uppercase()
        };
        div()
            .flex()
            .justify_between()
            .items_center()
            .child(label)
            .child(
                div()
                    .flex()
                    .items_center()
                    .gap_2()
                    .child(
                        div()
                            .min_w(px(120.))
                            .text_right()
                            .text_color(rgb(if recording { WARN } else { TEXT }))
                            .child(value),
                    )
                    .child(
                        Self::button(id, tr(lang, "change").into(), BUTTON).on_click(cx.listener(
                            move |this, _: &ClickEvent, _window, cx| this.begin_recording(slot, cx),
                        )),
                    ),
            )
    }
}

impl Render for TimerApp {
    fn render(&mut self, _window: &mut Window, cx: &mut Context<Self>) -> impl IntoElement {
        let lang = self.lang();
        let now = Instant::now();
        let phase = self.countdown.phase;

        // Clock: remaining time while running, the configured total otherwise.
        let (clock_label, clock_seconds) = match phase {
            Phase::Running => (
                tr(lang, "remaining"),
                self.countdown.remaining(now).unwrap_or(0.0),
            ),
            Phase::Finished => (tr(lang, "remaining"), 0.0),
            Phase::Idle | Phase::Stopped => {
                (tr(lang, "countdown_total"), self.settings.countdown_seconds)
            }
        };

        let (status, status_color) = match phase {
            Phase::Idle => (tr(lang, "status_idle").to_string(), MUTED),
            Phase::Running => {
                let detail = self.last_plan.map(|p| {
                    fmt(
                        tr(lang, "timer_started"),
                        &[
                            format!("{:.1}", p.actual),
                            format!("{:.1}", p.base),
                            format!("{:+.1}", p.applied_offset()),
                        ],
                    )
                });
                let text = match detail {
                    Some(d) => format!("{} {}", tr(lang, "status_running"), d),
                    None => tr(lang, "status_running").to_string(),
                };
                (text, TEXT)
            }
            Phase::Finished => (tr(lang, "status_finished").to_string(), WARN),
            Phase::Stopped => (tr(lang, "status_stopped").to_string(), MUTED),
        };

        let progress = self.countdown.progress(now) as f32;

        let header = div()
            .flex()
            .justify_between()
            .items_center()
            .child(
                div()
                    .text_xl()
                    .font_weight(FontWeight::BOLD)
                    .child(tr(lang, "title")),
            )
            .child(
                Self::button("lang-toggle", lang.other().native_name().into(), PANEL).on_click(
                    cx.listener(|this, _: &ClickEvent, _window, cx| this.toggle_language(cx)),
                ),
            );

        let clock = div()
            .flex()
            .flex_col()
            .items_center()
            .gap_1()
            .py_4()
            .rounded_lg()
            .bg(rgb(PANEL))
            .child(div().text_sm().text_color(rgb(MUTED)).child(clock_label))
            .child(
                div()
                    .text_3xl()
                    .font_weight(FontWeight::BOLD)
                    .child(format_mmss(clock_seconds)),
            );

        let bar = div()
            .w_full()
            .h(px(12.))
            .rounded_full()
            .bg(rgb(BAR_TRACK))
            .child(
                div()
                    .h_full()
                    .w(relative(progress))
                    .rounded_full()
                    .bg(rgb(BAR_FILL)),
            );

        let controls = div()
            .flex()
            .gap_3()
            .child(
                Self::button("start", tr(lang, "start").into(), ACCENT).on_click(
                    cx.listener(|this, _: &ClickEvent, _window, cx| this.start_timer(cx)),
                ),
            )
            .child(
                Self::button("stop", tr(lang, "stop").into(), DANGER)
                    .on_click(cx.listener(|this, _: &ClickEvent, _window, cx| this.stop_timer(cx))),
            );

        let countdown_row = div()
            .flex()
            .flex_col()
            .gap_2()
            .child(tr(lang, "countdown_seconds"))
            .child(self.stepper(
                cx,
                "countdown",
                format!("{}", self.settings.countdown_seconds),
                1.0,
                10.0,
                Self::adjust_countdown,
            ));

        let offset_row = div()
            .flex()
            .flex_col()
            .gap_1()
            .child(
                div()
                    .flex()
                    .flex_col()
                    .gap_2()
                    .child(tr(lang, "random_offset"))
                    .child(self.stepper(
                        cx,
                        "offset",
                        format!("±{}", self.settings.random_offset_seconds),
                        0.5,
                        1.0,
                        Self::adjust_offset,
                    )),
            )
            .child(
                div()
                    .text_xs()
                    .text_color(rgb(MUTED))
                    .child(tr(lang, "offset_hint")),
            );

        let settings = div()
            .flex()
            .flex_col()
            .gap_3()
            .p_4()
            .rounded_lg()
            .bg(rgb(PANEL))
            .child(
                div()
                    .font_weight(FontWeight::SEMIBOLD)
                    .child(tr(lang, "settings")),
            )
            .child(countdown_row)
            .child(offset_row)
            .child(self.hotkey_row(cx, Slot::Start, tr(lang, "start_key").into()))
            .child(self.hotkey_row(cx, Slot::Stop, tr(lang, "stop_key").into()));

        let mut footer = div()
            .flex()
            .flex_col()
            .gap_1()
            .text_xs()
            .text_color(rgb(MUTED))
            .child(tr(lang, "hotkey_scope"));
        if let Some(notice) = &self.notice {
            let color = if notice == tr(lang, "same_key_error") {
                DANGER
            } else {
                MUTED
            };
            footer = footer.child(div().text_color(rgb(color)).child(notice.clone()));
        }

        div()
            .id("root")
            .track_focus(&self.focus)
            .on_key_down(cx.listener(Self::on_key_down))
            .size_full()
            .flex()
            .flex_col()
            .gap_4()
            .p_5()
            .bg(rgb(BG))
            .text_color(rgb(TEXT))
            .child(header)
            .child(clock)
            .child(bar)
            .child(div().text_sm().text_color(rgb(status_color)).child(status))
            .child(controls)
            .child(settings)
            .child(footer)
    }
}

/// Play the Windows default "exclamation" system sound (like the Python
/// version's `winsound.MessageBeep(MB_ICONEXCLAMATION)`). No-op elsewhere.
#[cfg(windows)]
fn beep() {
    #[link(name = "user32")]
    extern "system" {
        fn MessageBeep(utype: u32) -> i32;
    }
    const MB_ICONEXCLAMATION: u32 = 0x0000_0030;
    // SAFETY: MessageBeep takes a plain integer and has no pointer arguments.
    unsafe {
        MessageBeep(MB_ICONEXCLAMATION);
    }
}

#[cfg(not(windows))]
fn beep() {}

fn main() {
    let settings_path = config::config_path();
    let settings = config::load(&settings_path);

    Application::new().run(move |cx: &mut App| {
        let bounds = Bounds::centered(None, size(px(460.), px(680.)), cx);
        cx.open_window(
            WindowOptions {
                window_bounds: Some(WindowBounds::Windowed(bounds)),
                titlebar: Some(TitlebarOptions {
                    title: Some("ringer".into()),
                    ..Default::default()
                }),
                ..Default::default()
            },
            move |window, cx| {
                let view = cx.new(|cx| TimerApp::new(settings, settings_path, cx));
                // Keyboard hotkeys are delivered to the focused element.
                let focus = view.read(cx).focus.clone();
                window.focus(&focus);
                view
            },
        )
        .expect("failed to open window");
        cx.activate(true);
    });
}
