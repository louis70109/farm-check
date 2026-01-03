#!/usr/bin/env python3
"""
Test Runner Script

Runs the pytest test suite with common options.
Usage: python run_tests.py [options]

Options:
  --quick     Run tests without coverage (faster)
  --verbose   Show detailed test output
  --file FILE Run specific test file
  --coverage  Generate HTML coverage report (default)
"""

import sys
import subprocess
import os
from pathlib import Path


def main():
    """Run pytest with appropriate options"""
    args = sys.argv[1:]
    
    # Base pytest command
    cmd = [sys.executable, '-m', 'pytest']
    
    # Parse simple options
    quick = '--quick' in args
    verbose = '--verbose' in args or '-v' in args
    specific_file = None
    
    # Check for --file option
    if '--file' in args:
        idx = args.index('--file')
        if idx + 1 < len(args):
            specific_file = args[idx + 1]
    
    # Build command
    if specific_file:
        cmd.append(specific_file)
    else:
        cmd.append('tests/')
    
    if verbose:
        cmd.append('-vv')
    else:
        cmd.append('-v')
    
    if not quick:
        # Add coverage options
        cmd.extend([
            '--cov=timer',
            '--cov-report=term-missing',
            '--cov-report=html',
            '--cov-branch'
        ])
    
    # Add common options
    cmd.extend([
        '--tb=short',
        '--strict-markers'
    ])
    
    # Print command
    print(f"Running: {' '.join(cmd)}\n")
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        if not quick:
            print("\n📊 Coverage report generated in: htmlcov/index.html")
            print("   Open with: open htmlcov/index.html (macOS) or start htmlcov/index.html (Windows)")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
