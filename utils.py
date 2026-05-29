import sys
import os

def get_app_dir() -> str:
    """Zwraca folder z aplikacją, działa dla skryptu i exe"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def get_data_path(*parts) -> str:
    return os.path.join(get_app_dir(), *parts)