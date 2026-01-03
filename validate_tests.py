#!/usr/bin/env python3
"""
Quick test validation script
Runs tests and reports results for CI/CD verification
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run pytest and check results"""
    print("="*60)
    print("Running Timer Application Test Suite")
    print("="*60)
    print()
    
    # Get Python executable from virtual environment if available
    venv_python = Path(__file__).parent / ".venv" / "bin" / "python"
    if not venv_python.exists():
        venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    
    python_exe = str(venv_python) if venv_python.exists() else sys.executable
    
    # Run pytest with coverage
    cmd = [
        python_exe, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--cov=timer',
        '--cov-report=term-missing',
        '--cov-report=html',
        '--cov-branch'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    print()
    print("="*60)
    
    if result.returncode == 0:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Coverage report generated in: htmlcov/index.html")
        print("="*60)
        return 0
    else:
        print("❌ TESTS FAILED!")
        print()
        print("Please fix failing tests before building.")
        print("="*60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
