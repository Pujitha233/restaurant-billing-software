# app.py
# Convenience launcher: `streamlit run ui/main_ui.py`
import subprocess, sys, os
if __name__ == "__main__":
    ui_path = os.path.join("ui", "main_ui.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", ui_path])
