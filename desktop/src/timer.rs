//! Countdown logic, independent of the UI so it can be unit-tested.
//!
//! Mirrors the Python `timer.py` behaviour:
//! * actual countdown = base ± random offset (never below 0.1 s)
//! * every 5th start, the base is shifted by a random amount in [-12, 12]
//!   (the "dynamic base offset" anti-detection feature)

use std::time::Instant;

use rand::Rng;

/// Every N-th start re-rolls the dynamic base offset (Python: `cycle_count % 5 == 0`).
pub const DYNAMIC_SHIFT_EVERY: u64 = 5;
/// Maximum magnitude of the dynamic base offset, in seconds.
pub const DYNAMIC_SHIFT_MAX: i64 = 12;

/// Result of planning one countdown run.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Plan {
    /// Configured countdown plus the dynamic base shift.
    pub base: f64,
    /// Final duration of this run (base ± random offset).
    pub actual: f64,
}

impl Plan {
    /// Random offset that was actually applied to `base`.
    pub fn applied_offset(&self) -> f64 {
        self.actual - self.base
    }
}

/// Pure planning function: `jitter` must be in [-1.0, 1.0].
pub fn plan_countdown(base: f64, offset: f64, jitter: f64) -> f64 {
    let raw = if offset > 0.0 {
        base + jitter.clamp(-1.0, 1.0) * offset
    } else {
        base
    };
    raw.max(0.1)
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Phase {
    /// Never started since launch.
    Idle,
    Running,
    /// Ran to the end (time's up).
    Finished,
    /// Cancelled by the user.
    Stopped,
}

#[derive(Debug)]
pub struct Countdown {
    pub phase: Phase,
    /// Number of starts so far (drives the dynamic base shift).
    pub cycle: u64,
    /// Current dynamic base shift in seconds.
    pub dynamic_base: i64,
    actual: f64,
    started: Option<Instant>,
}

impl Default for Countdown {
    fn default() -> Self {
        Self {
            phase: Phase::Idle,
            cycle: 0,
            dynamic_base: 0,
            actual: 0.0,
            started: None,
        }
    }
}

impl Countdown {
    /// Start (or restart) a countdown and return the plan that was used.
    pub fn start<R: Rng>(
        &mut self,
        now: Instant,
        countdown: f64,
        offset: f64,
        rng: &mut R,
    ) -> Plan {
        self.cycle += 1;
        if self.cycle.is_multiple_of(DYNAMIC_SHIFT_EVERY) {
            self.dynamic_base = rng.gen_range(-DYNAMIC_SHIFT_MAX..=DYNAMIC_SHIFT_MAX);
        }

        let base = countdown + self.dynamic_base as f64;
        let jitter = if offset > 0.0 {
            rng.gen_range(-1.0..=1.0)
        } else {
            0.0
        };
        let actual = plan_countdown(base, offset, jitter);

        self.actual = actual;
        self.started = Some(now);
        self.phase = Phase::Running;
        Plan { base, actual }
    }

    /// Cancel the running countdown. No-op unless running.
    pub fn stop(&mut self) {
        if self.phase == Phase::Running {
            self.phase = Phase::Stopped;
            self.started = None;
        }
    }

    /// Advance the state machine. Returns `true` exactly once, on the tick
    /// where the countdown reaches zero.
    pub fn poll(&mut self, now: Instant) -> bool {
        if self.phase != Phase::Running {
            return false;
        }
        if self.elapsed(now) >= self.actual {
            self.phase = Phase::Finished;
            self.started = None;
            return true;
        }
        false
    }

    pub fn is_running(&self) -> bool {
        self.phase == Phase::Running
    }

    pub fn elapsed(&self, now: Instant) -> f64 {
        match self.started {
            Some(start) => now.saturating_duration_since(start).as_secs_f64(),
            None => 0.0,
        }
    }

    /// Seconds left while running; `None` otherwise.
    pub fn remaining(&self, now: Instant) -> Option<f64> {
        self.is_running()
            .then(|| (self.actual - self.elapsed(now)).max(0.0))
    }

    /// Fraction completed in [0, 1].
    pub fn progress(&self, now: Instant) -> f64 {
        match self.phase {
            Phase::Running if self.actual > 0.0 => {
                (self.elapsed(now) / self.actual).clamp(0.0, 1.0)
            }
            Phase::Finished => 1.0,
            _ => 0.0,
        }
    }
}

/// Format seconds as `MM:SS`, rounding up so the display only reads `00:00`
/// once the countdown has really finished.
pub fn format_mmss(seconds: f64) -> String {
    let total = seconds.max(0.0).ceil() as u64;
    format!("{:02}:{:02}", total / 60, total % 60)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::{rngs::StdRng, SeedableRng};
    use std::time::Duration;

    #[test]
    fn plan_without_offset_is_exact_base() {
        assert_eq!(plan_countdown(130.0, 0.0, 0.7), 130.0);
    }

    #[test]
    fn plan_with_offset_stays_in_range() {
        for i in -100..=100 {
            let jitter = i as f64 / 100.0;
            let v = plan_countdown(130.0, 5.0, jitter);
            assert!((125.0..=135.0).contains(&v), "jitter {jitter} gave {v}");
        }
    }

    #[test]
    fn plan_never_below_minimum() {
        assert_eq!(plan_countdown(0.05, 0.0, 0.0), 0.1);
        assert_eq!(plan_countdown(1.0, 5.0, -1.0), 0.1);
    }

    #[test]
    fn jitter_is_clamped() {
        assert_eq!(plan_countdown(100.0, 5.0, 9.0), 105.0);
        assert_eq!(plan_countdown(100.0, 5.0, -9.0), 95.0);
    }

    #[test]
    fn start_respects_offset_bounds_for_many_seeds() {
        let now = Instant::now();
        for seed in 0..200u64 {
            let mut rng = StdRng::seed_from_u64(seed);
            let mut cd = Countdown::default();
            let plan = cd.start(now, 130.0, 5.0, &mut rng);
            let lo = plan.base - 5.0;
            let hi = plan.base + 5.0;
            assert!(
                plan.actual >= lo && plan.actual <= hi,
                "seed {seed}: {plan:?}"
            );
        }
    }

    #[test]
    fn dynamic_shift_only_on_every_fifth_cycle() {
        let now = Instant::now();
        let mut rng = StdRng::seed_from_u64(42);
        let mut cd = Countdown::default();
        for cycle in 1..=10u64 {
            let before = cd.dynamic_base;
            let plan = cd.start(now, 100.0, 0.0, &mut rng);
            assert_eq!(cd.cycle, cycle);
            assert!(cd.dynamic_base.abs() <= DYNAMIC_SHIFT_MAX);
            if cycle % 5 != 0 {
                assert_eq!(cd.dynamic_base, before, "cycle {cycle} should keep shift");
            }
            assert_eq!(plan.base, 100.0 + cd.dynamic_base as f64);
        }
    }

    #[test]
    fn poll_finishes_exactly_once() {
        let t0 = Instant::now();
        let mut rng = StdRng::seed_from_u64(1);
        let mut cd = Countdown::default();
        let plan = cd.start(t0, 10.0, 0.0, &mut rng);
        assert!(!cd.poll(t0 + Duration::from_secs_f64(plan.actual / 2.0)));
        assert!(cd.poll(t0 + Duration::from_secs_f64(plan.actual + 0.01)));
        assert_eq!(cd.phase, Phase::Finished);
        assert!(!cd.poll(t0 + Duration::from_secs(1000)));
        assert_eq!(cd.progress(t0), 1.0);
    }

    #[test]
    fn stop_cancels_without_finishing() {
        let t0 = Instant::now();
        let mut rng = StdRng::seed_from_u64(1);
        let mut cd = Countdown::default();
        cd.start(t0, 10.0, 0.0, &mut rng);
        cd.stop();
        assert_eq!(cd.phase, Phase::Stopped);
        assert!(!cd.poll(t0 + Duration::from_secs(1000)));
        assert_eq!(cd.remaining(t0), None);
    }

    #[test]
    fn remaining_and_progress_track_elapsed_time() {
        let t0 = Instant::now();
        let mut rng = StdRng::seed_from_u64(7);
        let mut cd = Countdown::default();
        let plan = cd.start(t0, 20.0, 0.0, &mut rng);
        let half = t0 + Duration::from_secs(10);
        assert!((cd.remaining(half).unwrap() - (plan.actual - 10.0)).abs() < 1e-6);
        assert!((cd.progress(half) - 10.0 / plan.actual).abs() < 1e-6);
    }

    #[test]
    fn format_mmss_rounds_up() {
        assert_eq!(format_mmss(0.0), "00:00");
        assert_eq!(format_mmss(0.2), "00:01");
        assert_eq!(format_mmss(60.0), "01:00");
        assert_eq!(format_mmss(130.0), "02:10");
        assert_eq!(format_mmss(-5.0), "00:00");
    }
}
