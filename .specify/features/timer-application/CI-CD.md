# CI/CD Pipeline Documentation

**Project**: Timer Application  
**Date**: 2026-01-03  
**Status**: ✅ Active

---

## Overview

The Timer Application uses GitHub Actions for automated testing and building. The pipeline ensures that all tests pass before creating release builds.

---

## Pipeline Architecture

```
┌─────────────────┐
│  Push Tag       │
│  (v*.*.*)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Test Job       │◄─── Runs on Windows
│  - Install deps │
│  - Run pytest   │
│  - Generate cov │
└────────┬────────┘
         │
         │ ✅ Tests Pass
         ▼
┌─────────────────┐
│  Build Job      │◄─── Only if tests pass
│  - Install deps │
│  - PyInstaller  │
│  - Create EXE   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Release        │
│  - Upload EXE   │
│  - Create tag   │
└─────────────────┘
```

---

## Jobs

### Job 1: Test

**Purpose**: Validate code quality and functionality  
**Runs on**: `windows-latest`  
**Trigger**: Tag push (`v*`)

**Steps**:
1. Checkout code
2. Setup Python 3.11
3. Install dependencies (including pytest, pytest-cov)
4. Run test suite with coverage
5. Upload coverage report to Codecov (optional)

**Success Criteria**:
- All 52 tests must pass
- No test failures or errors
- Coverage report generated

**Failure Handling**:
- If tests fail, build job is skipped
- Workflow fails with error status
- No release is created

---

### Job 2: Build

**Purpose**: Package application as Windows executable  
**Runs on**: `windows-latest`  
**Dependencies**: Requires `test` job to pass  
**Trigger**: After test job succeeds

**Steps**:
1. Checkout code
2. Setup Python 3.11
3. Install dependencies
4. Build with PyInstaller (`--onefile --console`)
5. Upload artifact (`timer.exe`)
6. Create GitHub Release (if tag push)

**Output**:
- `dist/timer.exe` - Standalone Windows executable
- GitHub Release with executable attached

---

## Configuration Files

### `.github/workflows/build.yml`

Main workflow configuration:
- **Triggers**: Tag push (`v*`), manual workflow dispatch
- **Jobs**: test, build
- **Permissions**: `contents: write` for releases
- **Environment**: Windows-latest, Python 3.11

### `pytest.ini`

Test configuration:
- Test discovery patterns
- Coverage settings (>80% target)
- Output formatting
- Branch coverage enabled

### `.pre-commit-config.yaml`

Optional pre-commit hooks:
- Code formatting (black)
- Import sorting (isort)
- Linting (flake8)
- Test execution before commit

---

## Usage

### Triggering a Build

```bash
# 1. Ensure all tests pass locally
python validate_tests.py

# 2. Commit your changes
git add .
git commit -m "Add new feature"

# 3. Create version tag
git tag v1.0.1

# 4. Push tag to trigger pipeline
git push origin v1.0.1
```

### Manual Workflow Trigger

Via GitHub UI:
1. Go to "Actions" tab
2. Select "Build Windows EXE" workflow
3. Click "Run workflow"
4. Select branch and run

### Monitoring Pipeline

1. Go to repository "Actions" tab
2. Find your workflow run
3. Click to see logs and status
4. Download artifacts if needed

---

## Test Requirements

### Mandatory Test Pass

**All tests must pass for build to proceed**

Current test suite:
- **tests/test_config.py**: 20 tests
- **tests/test_timer.py**: 17 tests
- **tests/test_automation.py**: 15 tests
- **Total**: 52 tests

### Coverage Requirements

- **Target**: >80% code coverage
- **Current**: ~82% coverage
- **Reporting**: HTML report generated in `htmlcov/`

---

## Local Development

### Running Tests Locally

```bash
# Quick validation
python validate_tests.py

# Detailed pytest
pytest tests/ -v --cov=timer --cov-report=html

# View coverage
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### Setting Up Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Troubleshooting

### Tests Fail in CI but Pass Locally

**Possible causes**:
- Environment differences (Python version, OS)
- Missing dependencies in requirements.txt
- Hardcoded paths or assumptions

**Solution**:
- Check workflow logs for specific error
- Ensure all dependencies listed in requirements.txt
- Use platform-independent code

### Build Fails After Tests Pass

**Possible causes**:
- PyInstaller configuration issue
- Import errors in packaged executable
- Missing runtime dependencies

**Solution**:
- Test PyInstaller locally: `pyinstaller --onefile --console timer.py`
- Check for hidden imports
- Verify executable runs on clean Windows machine

### Workflow Doesn't Trigger

**Possible causes**:
- Tag format incorrect (must be `v*`)
- Workflow file syntax error
- GitHub Actions disabled

**Solution**:
- Verify tag format: `git tag -l`
- Validate YAML syntax
- Check repository Actions settings

---

## Best Practices

### Before Pushing Tag

✅ Run tests locally: `python validate_tests.py`  
✅ Review changes: `git diff`  
✅ Update CHANGELOG.md  
✅ Verify version number in tag  
✅ Test build locally: `pyinstaller --onefile --console timer.py`

### Version Numbering

Follow Semantic Versioning (semver):
- `v1.0.0` - Major release (breaking changes)
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)

### Release Notes

Include in GitHub Release:
- What's new
- Bug fixes
- Breaking changes
- Installation instructions

---

## Metrics

### Pipeline Performance

- **Average test duration**: ~30-60 seconds
- **Average build duration**: ~2-3 minutes
- **Total pipeline time**: ~4-5 minutes
- **Success rate**: Target >95%

### Test Statistics

- **Total tests**: 52
- **Code coverage**: ~82%
- **Test files**: 3
- **Lines of test code**: ~1,200+

---

## Future Enhancements

### Planned Improvements

- [ ] Add integration tests for real window interactions
- [ ] Performance benchmarks
- [ ] Cross-platform testing (macOS, Linux)
- [ ] Automated release notes generation
- [ ] Code quality gates (complexity, duplication)
- [ ] Security scanning
- [ ] Dependency vulnerability checks

### CI/CD Improvements

- [ ] Matrix testing (multiple Python versions)
- [ ] Caching dependencies for faster builds
- [ ] Parallel test execution
- [ ] Nightly builds for main branch
- [ ] Pull request testing
- [ ] Automated version bumping

---

## Support

### Resources

- **Workflow logs**: GitHub Actions tab
- **Test results**: Actions → Workflow run → Test job
- **Coverage reports**: Codecov (if configured)
- **Artifacts**: Actions → Workflow run → Artifacts section

### Getting Help

- Check workflow logs for detailed error messages
- Review test output for failure details
- Consult GitHub Actions documentation
- Check pytest documentation for test issues

---

**Last Updated**: 2026-01-03  
**Pipeline Status**: ✅ Operational  
**Test Success Rate**: 100%
