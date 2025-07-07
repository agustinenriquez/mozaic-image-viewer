"""
Modular Image Viewer Application
Entry point for the refactored image viewer using modular components.
"""

import tkinter as tk
from tkinterdnd2 import TkinterDnD
import os
import logging
from pathlib import Path

# Set up logging
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
log_level = logging.DEBUG if DEBUG_MODE else logging.INFO

logging.basicConfig(
    level=log_level,
    format='%(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logging.getLogger('pynput').setLevel(logging.WARNING)

logger.info(f"Debug mode: {'ON' if DEBUG_MODE else 'OFF'} (set DEBUG=true to enable debug logs)")

# Import modular components
from core.app import GnomeImageViewer


def main():
    """Main application entry point"""
    logger.info("Starting Modular GNOME Image Viewer")
    
    try:
        root = TkinterDnD.Tk()
        app = GnomeImageViewer(root)
        
        def on_closing():
            logger.info("Application closing...")
            app.cleanup()
            root.quit()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        logger.info("Application started successfully")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    main()