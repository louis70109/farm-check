# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Human-like mouse movement animation** for auto-click feature
  - Mouse now smoothly glides to each window instead of instant teleportation
  - Random movement duration (0.3-0.8 seconds) simulates natural mouse speed
  - Added reaction time pause (0.05-0.15 seconds) after movement before clicking
  - Improved anti-detection capabilities
- **CI/CD Pipeline with mandatory testing**
  - GitHub Actions workflow now runs full test suite before building
  - Build only proceeds if all tests pass
  - Automated test coverage reporting
  - Pre-commit hooks for local development (optional)

### Changed
- Updated auto-click sequence to use `pyautogui.moveTo()` with duration parameter
- Extended total auto-click time to ~5-8 seconds to accommodate mouse animations
- Updated test suite to verify mouse movement animation behavior (52 tests total)
- GitHub Actions workflow split into test and build jobs with dependency

### Technical Details
- `click_maple_windows()`: Added `pyautogui.moveTo(x, y, duration=...)` before click
- Random movement duration generated using `random.uniform(0.3, 0.8)`
- Small pause after movement using `random.uniform(0.05, 0.15)`
- Tests updated to mock `pyautogui.moveTo` and verify animation parameters
- Added test for mouse movement duration range validation
- Created `validate_tests.py` script for easy local test execution
- Added `.pre-commit-config.yaml` for automated pre-commit testing

## [1.0.0] - 2026-01-03

### Added
- Initial release
- Customizable countdown timer with configurable hotkeys
- Configuration persistence via JSON file
- Random time offset for anti-detection (±N seconds)
- Real-time progress bar with percentage and time remaining
- Auto-restart with ESC cancellation option
- Auto-click MapleRoyals windows feature
- Window selection (all windows or specific selection)
- Randomized click positions (±30% offset from center)
- Shuffled window order for unpredictability
- Variable inter-click delays (0.5-2.5 seconds)
- Runtime reconfiguration via `/setup` command
- System sound alert on timer expiration
- PyInstaller packaging for standalone executable
- Comprehensive test suite (51 test cases, ~82% coverage)
- Complete documentation (spec, plan, quickstart, research, data model, API contracts)

### Features
- Global hotkey registration for start/stop controls
- Background command listener thread
- Multi-threaded architecture (main, timer, progress, command listener)
- Graceful handling of missing optional dependencies (pygetwindow, pyautogui)
- Configuration validation with sensible defaults
- Cross-session configuration persistence
- Interactive first-time setup wizard

### Non-Functional
- Response time < 100ms for hotkeys
- Memory footprint < 50MB
- Single-file executable deployment
- Windows 10/11 compatible
- No external runtime dependencies (when packaged)

---

## Version History

- **v1.0.0** (2026-01-03): Initial release with full feature set
- **Unreleased**: Added mouse movement animation for enhanced anti-detection
