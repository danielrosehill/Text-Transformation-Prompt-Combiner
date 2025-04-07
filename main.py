#!/usr/bin/env python3
"""
Main entry point for the Text Transformation Prompt Combiner.
"""
import os
import subprocess
import sys


def main():
    """Main entry point for the application."""
    print("Launching Text Transformation Prompt Combiner Streamlit App...")
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")
    
    # Launch the Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to launch Streamlit app.")
        print("Make sure Streamlit is installed: pip install streamlit")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStreamlit app terminated.")


if __name__ == "__main__":
    main()
