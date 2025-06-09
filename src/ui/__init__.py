"""
UI Package for HTS Tariff Agent

This package contains user interface components:
- streamlit_app.py: Web-based Streamlit application
- cli.py: Command-line interface
"""

__version__ = "1.0.0"
__author__ = "HTS Tariff Agent Team"

# Import main UI components for easy access
try:
    from .streamlit_app import main as run_streamlit_app
except ImportError:
    run_streamlit_app = None

# try:
#     from .cli import TariffCLI, main as run_cli
# except ImportError:
#     TariffCLI = None
#     run_cli = None

__all__ = [
    'TariffCLI',
    'run_streamlit_app',
    'run_cli'
]