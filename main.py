#!/usr/bin/env python3
"""
AI Study Scheduler - Main Application Entry Point

This application helps students create personalized study plans using AI optimization.
"""

import sys
import os
import traceback
from datetime import datetime

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create user_data directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data"), exist_ok=True)

def main():
    """Main entry point with error handling."""
    try:
        from study_scheduler.ui.app import launch_app
        print(f"Starting AI Study Scheduler at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        launch_app()
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Make sure you have all the required dependencies installed.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Error details:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()