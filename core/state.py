"""Application state management"""

import os
import logging

logger = logging.getLogger(__name__)


class ApplicationState:
    """Manages the application's state"""
    
    def __init__(self):
        # Image state
        self.current_image = None
        self.original_image = None
        self.current_file_path = None
        self.image_list = []
        self.current_index = 0
        
        # Display state
        self.zoom_factor = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 5.0
        self.zoom_step = 0.1
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        
        # UI state
        self.sidebar_visible = False
        self.fullscreen_mode = False
        self.toolbar_visible = True
        self.controls_visible = True
        
        # Panning state
        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        # Auto-hide state
        self.hide_timer = None
        self.auto_hide_delay = 3000  # 3 seconds
        
        # Mouse listener state
        self.mouse_listener = None
        self.last_scroll_time = 0
        self.scroll_threshold = 0.1
        
        # Throttling state
        self.zoom_throttle_time = 0
        self.zoom_throttle_delay = 0.05  # 50ms between zoom operations
        self.pending_zoom_update = None
        self.max_image_size = 4000  # Max width/height to prevent memory issues
    
    def reset_transformations(self):
        """Reset all image transformations to defaults"""
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        self.image_offset_x = 0
        self.image_offset_y = 0
        logger.debug("Transformations reset to defaults")
    
    def set_image(self, image, file_path):
        """Set the current image and file path"""
        self.original_image = image
        self.current_file_path = file_path
        self.reset_transformations()
        logger.info(f"Image state updated: {os.path.basename(file_path) if file_path else 'None'}")
    
    def get_image_info(self):
        """Get current image information"""
        if not self.current_file_path or not self.original_image:
            return None
        
        filename = os.path.basename(self.current_file_path)
        file_size = os.path.getsize(self.current_file_path)
        
        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        return {
            'filename': filename,
            'size': size_str,
            'dimensions': f"{self.original_image.width} × {self.original_image.height}",
            'zoom': f"{int(self.zoom_factor * 100)}%"
        }