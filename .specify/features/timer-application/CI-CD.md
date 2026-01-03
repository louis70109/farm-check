# CI/CD Pipeline Documentation

**Project**: Timer Application  
**Date**: 2026-01-03  
**Status**: ✅ Active

---

## Overview

The Timer Application uses GitHub Actions for automated building and releasing. When you push a version tag, GitHub automatically builds a Windows executable and creates a release.

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
│  Build Job      │◄─── Runs on Windows
│  - Install deps │
│  - PyInstaller  │
│  - Create EXE   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Release        │
│  - Upload EXE   │
│  - Auto Release │
└─────────────────┘
```

---

## Build Job

**Purpose**: Package application as Windows executable  
**Runs on**: `windows-latest`  
**Trigger**: Tag push (`v*`)

**Steps**:
1. Checkout code
2. Setup Python 3.11
3. Install dependencies from requirements.txt
4. Build with PyInstaller (`--onefile --console timer.py`)
5. Upload artifact (`timer.exe`)
6. Create GitHub Release with executable

**Output**:
- `dist/timer.exe` - Standalone Windows executable
- GitHub Release with executable automatically attached

---

## Configuration Files

### `.github/workflows/build.yml`

Main workflow configuration:
- **Triggers**: Tag push (`v*`), manual workflow dispatch
- **Job**: build
- **Permissions**: `contents: write` for releases
- **Environment**: Windows-latest, Python 3.11

---

## Usage

### Triggering a Build

```bash
# 1. Commit your changes
git add .
git commit -m "Add new feature"

# 2. Create version tag
git tag v1.0.1

# 3. Push tag to trigger pipeline
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

## Troubleshooting

### Build Fails

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

✅ Test the application manually on Windows  
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

- **Average build duration**: ~2-3 minutes
- **Total pipeline time**: ~2-3 minutes
- **Success rate**: Target >95%

---

## Future Enhancements

### Planned Improvements

- [ ] Automated release notes generation
- [ ] Security scanning
- [ ] Dependency vulnerability checks

### CI/CD Improvements

- [ ] Matrix testing (multiple Python versions)
- [ ] Caching dependencies for faster builds
- [ ] Nightly builds for main branch
- [ ] Automated version bumping

---

## Support

### Resources

- **Workflow logs**: GitHub Actions tab
- **Build artifacts**: Actions → Workflow run → Artifacts section
- **Releases**: Repository → Releases section

### Getting Help

- Check workflow logs for detailed error messages
- Consult GitHub Actions documentation
- Check PyInstaller documentation for build issues

---

**Last Updated**: 2026-01-03  
**Pipeline Status**: ✅ Operational
