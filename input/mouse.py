"""Mouse input handling"""

import logging
import time
from pynput import mouse

logger = logging.getLogger(__name__)


class MouseHandler:
    """Handles mouse events and gestures"""
    
    def __init__(self, root, callbacks):
        self.root = root
        self.callbacks = callbacks
        
        # Mouse state
        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.last_scroll_time = 0
        self.scroll_threshold = 0.1
        
        # Mouse listener for global gestures
        self.mouse_listener = None
        
        self.start_mouse_listener()
    
    def handle_mouse_press(self, event):
        """Handle mouse press for panning"""
        if self.callbacks.get('has_image') and self.callbacks['has_image']():
            self.panning = True
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            if self.callbacks.get('set_cursor'):
                self.callbacks['set_cursor']("fleur")
    
    def handle_mouse_drag(self, event):
        """Handle mouse drag for panning"""
        if self.panning and self.callbacks.get('has_image') and self.callbacks['has_image']():
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            
            if self.callbacks.get('update_pan_offset'):
                self.callbacks['update_pan_offset'](dx, dy)
            
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            
            if self.callbacks.get('update_display'):
                self.callbacks['update_display']()
    
    def handle_mouse_release(self, event):
        """Handle mouse release"""
        self.panning = False
        if self.callbacks.get('set_cursor'):
            self.callbacks['set_cursor']("")
    
    def handle_mouse_wheel(self, event):
        """Handle mouse wheel for zooming with throttling"""
        if not self.callbacks.get('has_image') or not self.callbacks['has_image']():
            return
        
        current_time = time.time()
        
        # Throttle mouse wheel events to prevent rapid zoom
        if current_time - self.last_scroll_time < self.scroll_threshold:
            return
        
        self.last_scroll_time = current_time
        
        # Zoom with mouse wheel
        if (hasattr(event, 'delta') and event.delta > 0) or event.num == 4:
            if self.callbacks.get('zoom_in'):
                self.callbacks['zoom_in']()
        elif (hasattr(event, 'delta') and event.delta < 0) or event.num == 5:
            if self.callbacks.get('zoom_out'):
                self.callbacks['zoom_out']()
    
    def handle_mouse_motion(self, event):
        """Handle mouse motion for auto-hide controls"""
        if self.callbacks.get('show_controls'):
            self.callbacks['show_controls']()
        if self.callbacks.get('schedule_hide_controls'):
            self.callbacks['schedule_hide_controls']()
    
    def handle_mouse_enter(self, event):
        """Handle mouse enter window"""
        if self.callbacks.get('show_controls'):
            self.callbacks['show_controls']()
        if self.callbacks.get('schedule_hide_controls'):
            self.callbacks['schedule_hide_controls']()
    
    def handle_mouse_leave(self, event):
        """Handle mouse leave window"""
        # Check if mouse is really outside the window
        try:
            x, y = self.root.winfo_pointerxy()
            win_x = self.root.winfo_rootx()
            win_y = self.root.winfo_rooty()
            win_width = self.root.winfo_width()
            win_height = self.root.winfo_height()
            
            if not (win_x <= x <= win_x + win_width and win_y <= y <= win_y + win_height):
                if self.callbacks.get('schedule_hide_controls'):
                    self.callbacks['schedule_hide_controls'](delay=1000)  # Hide faster when mouse leaves
        except Exception as e:
            logger.debug(f"Error in mouse leave handler: {e}")
    
    def start_mouse_listener(self):
        """Start background mouse listener for advanced gestures"""
        last_gesture_time = 0
        gesture_throttle = 0.2  # 200ms between gestures
        
        def on_scroll(x, y, dx, dy):
            nonlocal last_gesture_time
            current_time = time.time()
            
            if not self.callbacks.get('has_image') or not self.callbacks['has_image']():
                return
            
            # Heavy throttling to prevent rapid events
            if current_time - last_gesture_time < gesture_throttle:
                return
            
            try:
                widget_x = self.root.winfo_rootx()
                widget_y = self.root.winfo_rooty()
                widget_width = self.root.winfo_width()
                widget_height = self.root.winfo_height()
                
                if (widget_x <= x <= widget_x + widget_width and 
                    widget_y <= y <= widget_y + widget_height):
                    
                    # Conservative gesture detection
                    if abs(dx) > abs(dy) and abs(dx) > 2.0:
                        last_gesture_time = current_time
                        if dx > 0:
                            self.root.after(0, lambda: self.callbacks.get('zoom_in', lambda: None)())
                        else:
                            self.root.after(0, lambda: self.callbacks.get('zoom_out', lambda: None)())
                    elif abs(dy) > 3.0:
                        last_gesture_time = current_time
                        if dy > 0:
                            self.root.after(0, lambda: self.callbacks.get('zoom_in', lambda: None)())
                        else:
                            self.root.after(0, lambda: self.callbacks.get('zoom_out', lambda: None)())
            except Exception as e:
                logger.debug(f"Error in mouse gesture handler: {e}")
        
        try:
            self.mouse_listener = mouse.Listener(on_scroll=on_scroll)
            self.mouse_listener.daemon = True
            self.mouse_listener.start()
            logger.info("Mouse listener started")
        except Exception as e:
            logger.error(f"Failed to start mouse listener: {e}")
    
    def stop_mouse_listener(self):
        """Stop the mouse listener"""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            logger.info("Mouse listener stopped")
    
    def is_panning(self):
        """Check if currently panning"""
        return self.panning