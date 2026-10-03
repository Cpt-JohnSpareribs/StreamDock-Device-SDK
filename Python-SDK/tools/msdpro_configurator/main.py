"""
MSD-PRO Configurator - Main Entry Point

This module provides the main entry point for the MSD-PRO configuration tool.
It can be run directly or imported as a module.

Usage:
    python -m msdpro_configurator.main    # Run with mock devices
    python -m msdpro_configurator.main --real  # Run with real SDK
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import run_application


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="MSD-PRO Configurator - Configure your Mars Gaming MSD-PRO device"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use real StreamDock SDK (requires hardware)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="Use mock devices for testing (default)"
    )
    
    args = parser.parse_args()
    
    # Determine if we should use mock or real
    use_mock = not args.real
    
    print(f"Starting MSD-PRO Configurator ({'Mock Mode' if use_mock else 'Real Mode'})")
    
    # Run the application
    run_application(use_mock=use_mock)


if __name__ == "__main__":
    main()
