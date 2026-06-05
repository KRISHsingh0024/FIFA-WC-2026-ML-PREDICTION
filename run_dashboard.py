"""
Streamlit Dashboard Runner.
Launches the interactive dashboard app.
"""

import os
import sys
import subprocess

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_dir, "app", "streamlit_app.py")
    
    print("Launching FIFA World Cup 2026 Prediction Model Dashboard...")
    print(f"Running command: streamlit run {app_path}")
    
    try:
        subprocess.run(["python", "-m", "streamlit", "run", app_path], check=True)
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    except Exception as e:
        print(f"Error launching dashboard: {e}")

if __name__ == "__main__":
    main()

