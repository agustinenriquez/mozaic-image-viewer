"""Drag and drop handling"""

import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)


class DragDropHandler:
    """Handles drag and drop operations"""
    
    def __init__(self, root, callbacks):
        self.root = root
        self.callbacks = callbacks
    
    def handle_drop(self, event):
        """Handle drag and drop events"""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0]
                
                # Check if it's a valid image file
                if self.callbacks.get('is_valid_image_file'):
                    if self.callbacks['is_valid_image_file'](file_path):
                        if self.callbacks.get('load_image'):
                            self.callbacks['load_image'](file_path)
                        logger.info(f"Dropped file loaded: {file_path}")
                    else:
                        messagebox.showwarning("Invalid File", "Please drop an image file.")
                        logger.warning(f"Invalid file dropped: {file_path}")
                else:
                    # Fallback: try to load any file
                    if self.callbacks.get('load_image'):
                        self.callbacks['load_image'](file_path)
                    logger.info(f"File dropped (no validation): {file_path}")
        except Exception as e:
            logger.error(f"Error handling dropped file: {e}")
            messagebox.showerror("Drop Error", f"Failed to handle dropped file: {str(e)}")
    
    def setup_drop_target(self, widget):
        """Setup a widget as a drop target"""
        try:
            from tkinterdnd2 import DND_FILES
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', self.handle_drop)
            logger.info("Drag and drop configured")
        except Exception as e:
            logger.error(f"Failed to setup drag and drop: {e}")
    
    def get_dropped_files(self, event):
        """Get list of dropped files"""
        try:
            return self.root.tk.splitlist(event.data)
        except Exception as e:
            logger.error(f"Error getting dropped files: {e}")
            return []