"""Main application controller"""

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD
import os
import logging
import threading
import time
import gc

from gnome_theme import COLORS, FONTS, DIMENSIONS, ICONS
from core.state import ApplicationState
from ui.headerbar import HeaderBar
from ui.sidebar import Sidebar
from ui.toolbar import Toolbar
from ui.canvas import ImageCanvas
from ui.statusbar import StatusBar
from image.processor import ImageProcessor
from image.loader import ImageLoader
from input.keyboard import KeyboardHandler
from input.mouse import MouseHandler
from input.drag_drop import DragDropHandler

logger = logging.getLogger(__name__)


class GnomeImageViewer:
    """Main application class using modular components"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS['bg_primary'])
        
        # Initialize core components
        self.state = ApplicationState()
        self.image_processor = ImageProcessor()
        self.image_loader = ImageLoader()
        
        # UI components will be initialized after setup
        self.headerbar = None
        self.sidebar = None
        self.toolbar = None
        self.canvas = None
        self.statusbar = None
        
        # Input handlers
        self.keyboard_handler = None
        self.mouse_handler = None
        self.drag_drop_handler = None
        
        # Setup UI and handlers
        self.setup_ui()
        self.setup_input_handlers()
        self.schedule_hide_controls()
    
    def setup_ui(self):
        """Initialize UI components"""
        # Create main container
        self.main_container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create content frame
        self.content_frame = tk.Frame(self.main_container, bg=COLORS['bg_primary'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create UI components with callbacks
        callbacks = self.get_ui_callbacks()
        
        self.headerbar = HeaderBar(self.main_container, callbacks)
        self.sidebar = Sidebar(self.content_frame, callbacks)
        self.toolbar = Toolbar(self.main_container, callbacks)
        self.canvas = ImageCanvas(self.content_frame, callbacks)
        self.statusbar = StatusBar(self.main_container, callbacks)
        
        # Bind motion events for auto-hide
        self.bind_motion_events()
        
        logger.info("UI components initialized")
    
    def setup_input_handlers(self):
        """Initialize input handlers"""
        callbacks = self.get_input_callbacks()
        
        self.keyboard_handler = KeyboardHandler(self.root, callbacks)
        self.mouse_handler = MouseHandler(self.root, callbacks)
        self.drag_drop_handler = DragDropHandler(self.root, callbacks)
        
        # Setup drag and drop on canvas
        self.drag_drop_handler.setup_drop_target(self.canvas.canvas)
        
        logger.info("Input handlers initialized")
    
    def get_ui_callbacks(self):
        """Get callbacks for UI components"""
        return {
            'open_image': self.open_image,
            'toggle_sidebar': self.toggle_sidebar,
            'toggle_fullscreen': self.toggle_fullscreen,
            'zoom_in': self.zoom_in,
            'zoom_out': self.zoom_out,
            'zoom_original': self.zoom_original,
            'fit_to_window': self.fit_to_window,
            'crop_to_window': self.crop_to_window,
            'show_controls': self.show_controls,
            'cancel_hide_timer': self.cancel_hide_timer,
            'schedule_hide_controls': self.schedule_hide_controls,
            'on_mouse_motion': self.on_mouse_motion,
            'on_mouse_press': lambda e: self.mouse_handler.handle_mouse_press(e) if self.mouse_handler else None,
            'on_mouse_drag': lambda e: self.mouse_handler.handle_mouse_drag(e) if self.mouse_handler else None,
            'on_mouse_release': lambda e: self.mouse_handler.handle_mouse_release(e) if self.mouse_handler else None,
            'on_mouse_wheel': lambda e: self.mouse_handler.handle_mouse_wheel(e) if self.mouse_handler else None,
            'on_mouse_enter': lambda e: self.mouse_handler.handle_mouse_enter(e) if self.mouse_handler else None,
            'on_mouse_leave': lambda e: self.mouse_handler.handle_mouse_leave(e) if self.mouse_handler else None,
            'on_drop': lambda e: self.drag_drop_handler.handle_drop(e) if self.drag_drop_handler else None,
        }
    
    def get_input_callbacks(self):
        """Get callbacks for input handlers"""
        return {
            'open_image': self.open_image,
            'exit_fullscreen': self.exit_fullscreen,
            'toggle_fullscreen': self.toggle_fullscreen,
            'toggle_sidebar': self.toggle_sidebar,
            'zoom_in': self.zoom_in,
            'zoom_out': self.zoom_out,
            'zoom_original': self.zoom_original,
            'fit_to_window': self.fit_to_window,
            'prev_image': self.prev_image,
            'next_image': self.next_image,
            'has_image': lambda: self.state.original_image is not None,
            'set_cursor': self.canvas.set_cursor,
            'update_pan_offset': self.update_pan_offset,
            'update_display': self.update_image_display,
            'show_controls': self.show_controls,
            'schedule_hide_controls': self.schedule_hide_controls,
            'is_valid_image_file': self.image_loader.is_valid_image_file,
            'load_image': self.load_image,
        }
    
    def bind_motion_events(self):
        """Bind motion events for auto-hide functionality"""
        self.root.bind('<Motion>', self.on_mouse_motion)
        
        # Bind motion events to UI components
        if self.headerbar:
            self.headerbar.bind_motion_events()
        if self.toolbar:
            self.toolbar.bind_motion_events()
        if self.statusbar:
            self.statusbar.bind_motion_events()
    
    # Image operations
    def open_image(self):
        """Open image file dialog"""
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """Load an image and update UI"""
        try:
            # Load image
            image = self.image_loader.load_image(file_path)
            if not image:
                messagebox.showerror("Error", "Failed to load image")
                return
            
            # Update state
            self.state.set_image(image, file_path)
            
            # Update image list
            self.state.image_list = self.image_loader.get_image_list(file_path)
            self.state.current_index = self.image_loader.get_current_index(
                self.state.image_list, file_path
            )
            
            # Update UI
            self.fit_to_window()
            self.update_sidebar_info()
            self.set_status(f"Loaded: {os.path.basename(file_path)}")
            
            # Hide welcome text
            self.canvas.hide_welcome_text()
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def prev_image(self):
        """Navigate to previous image"""
        if len(self.state.image_list) > 1:
            prev_file, prev_index = self.image_loader.get_previous_image(
                self.state.image_list, self.state.current_index
            )
            if prev_file:
                self.state.current_index = prev_index
                self.load_image(prev_file)
    
    def next_image(self):
        """Navigate to next image"""
        if len(self.state.image_list) > 1:
            next_file, next_index = self.image_loader.get_next_image(
                self.state.image_list, self.state.current_index
            )
            if next_file:
                self.state.current_index = next_index
                self.load_image(next_file)
    
    # Display operations
    def update_image_display(self):
        """Update the image display"""
        if not self.state.original_image:
            return
        
        try:
            # Process image
            processed_image, actual_zoom = self.image_processor.process_image(
                self.state.original_image,
                self.state.zoom_factor,
                self.state.rotation_angle,
                self.state.flip_horizontal,
                self.state.flip_vertical
            )
            
            if not processed_image:
                return
            
            # Update actual zoom factor
            self.state.zoom_factor = actual_zoom
            
            # Create PhotoImage
            photo_image = self.image_processor.create_photo_image(processed_image)
            if not photo_image:
                return
            
            # Clean up previous image
            if self.state.current_image:
                self.image_processor.cleanup_image(self.state.current_image)
            
            # Update canvas
            self.state.current_image = photo_image
            self.canvas.delete_by_tag("image")
            
            # Calculate positioning
            canvas_width, canvas_height = self.canvas.get_dimensions()
            x_center = max(processed_image.width // 2, canvas_width // 2) + self.state.image_offset_x
            y_center = max(processed_image.height // 2, canvas_height // 2) + self.state.image_offset_y
            
            # Create image on canvas
            self.canvas.create_image(x_center, y_center, photo_image, tags="image")
            
            # Configure scroll region
            self.canvas.configure_scroll_region(self.canvas.get_bbox("all"))
            
            # Hide scrollbars for minimal interface
            self.canvas.hide_scrollbars()
            
            # Update toolbar
            if self.toolbar:
                self.toolbar.update_zoom_label(self.state.zoom_factor)
            
            # Clean up processed image
            self.image_processor.cleanup_image(processed_image)
            
        except Exception as e:
            logger.error(f"Error updating image display: {e}")
            gc.collect()
    
    def update_pan_offset(self, dx, dy):
        """Update pan offset"""
        self.state.image_offset_x += dx
        self.state.image_offset_y += dy
    
    # Zoom operations
    def zoom_in(self):
        """Zoom in"""
        if self.state.original_image:
            new_zoom = min(self.state.zoom_factor * 1.1, self.state.max_zoom)
            if new_zoom != self.state.zoom_factor:
                self.state.zoom_factor = new_zoom
                self.throttled_update_display()
    
    def zoom_out(self):
        """Zoom out"""
        if self.state.original_image:
            new_zoom = max(self.state.zoom_factor / 1.1, self.state.min_zoom)
            if new_zoom != self.state.zoom_factor:
                self.state.zoom_factor = new_zoom
                self.throttled_update_display()
    
    def zoom_original(self):
        """Zoom to original size"""
        if self.state.original_image:
            self.state.zoom_factor = 1.0
            self.state.image_offset_x = 0
            self.state.image_offset_y = 0
            self.update_image_display()
    
    def fit_to_window(self):
        """Fit image to window"""
        if not self.state.original_image:
            return
        
        canvas_width, canvas_height = self.canvas.get_dimensions()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.fit_to_window)
            return
        
        # Calculate fit zoom
        zoom_factor = self.image_processor.calculate_fit_zoom(
            self.state.original_image.width,
            self.state.original_image.height,
            canvas_width,
            canvas_height,
            self.state.rotation_angle
        )
        
        self.state.zoom_factor = zoom_factor
        self.state.image_offset_x = 0
        self.state.image_offset_y = 0
        self.update_image_display()
    
    def throttled_update_display(self):
        """Throttle display updates"""
        if self.image_processor.should_throttle_zoom():
            if self.state.pending_zoom_update:
                self.root.after_cancel(self.state.pending_zoom_update)
            self.state.pending_zoom_update = self.root.after(50, self.update_image_display)
        else:
            self.image_processor.update_throttle_time()
            self.update_image_display()
    
    def crop_to_window(self):
        """Crop image to visible window area"""
        if not self.state.original_image:
            return
        
        try:
            canvas_width, canvas_height = self.canvas.get_dimensions()
            
            # Process the image with current transformations
            processed_image, _ = self.image_processor.process_image(
                self.state.original_image,
                self.state.zoom_factor,
                self.state.rotation_angle,
                self.state.flip_horizontal,
                self.state.flip_vertical
            )
            
            if not processed_image:
                return
            
            # Crop to visible area
            cropped_image = self.image_processor.crop_image(
                processed_image,
                canvas_width,
                canvas_height,
                self.state.image_offset_x,
                self.state.image_offset_y
            )
            
            if not cropped_image:
                messagebox.showwarning("Crop Error", "No visible area to crop!")
                return
            
            # Ask for save location
            save_path = filedialog.asksaveasfilename(
                title="Save Cropped Image",
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ]
            )
            
            if save_path:
                if self.image_processor.save_image_with_format(cropped_image, save_path):
                    self.set_status(f"Cropped image saved: {os.path.basename(save_path)}")
                    
                    # Ask to open cropped image
                    if messagebox.askyesno("Open Cropped Image", "Do you want to open the cropped image?"):
                        self.load_image(save_path)
                else:
                    messagebox.showerror("Save Error", "Failed to save cropped image")
            
            # Clean up
            self.image_processor.cleanup_image(processed_image)
            self.image_processor.cleanup_image(cropped_image)
            
        except Exception as e:
            logger.error(f"Error cropping image: {e}")
            messagebox.showerror("Crop Error", f"Failed to crop image: {str(e)}")
    
    # UI operations
    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar:
            visible = self.sidebar.toggle()
            self.state.sidebar_visible = visible
            
            if visible:
                self.cancel_hide_timer()
                self.show_controls()
            else:
                self.schedule_hide_controls()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.state.fullscreen_mode:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        self.state.fullscreen_mode = True
        self.root.attributes('-fullscreen', True)
        
        # Hide UI components
        self.headerbar.hide()
        self.toolbar.hide()
        self.statusbar.hide()
        if self.sidebar.is_visible():
            self.sidebar.hide()
        
        self.cancel_hide_timer()
        self.state.controls_visible = False
        logger.info("Entered fullscreen mode")
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.state.fullscreen_mode:
            self.state.fullscreen_mode = False
            self.root.attributes('-fullscreen', False)
            
            # Show UI components
            self.state.controls_visible = True
            self.headerbar.show()
            self.toolbar.show()
            self.statusbar.show()
            if self.state.sidebar_visible:
                self.sidebar.show()
            
            if not self.state.sidebar_visible:
                self.schedule_hide_controls()
            
            logger.info("Exited fullscreen mode")
    
    def update_sidebar_info(self):
        """Update sidebar information"""
        if self.sidebar:
            info = self.state.get_image_info()
            if info:
                self.sidebar.update_info(info)
    
    def set_status(self, text):
        """Set status bar text"""
        if self.statusbar:
            self.statusbar.set_status(text)
    
    # Auto-hide functionality
    def show_controls(self):
        """Show UI controls"""
        if not self.state.controls_visible and not self.state.fullscreen_mode:
            self.state.controls_visible = True
            self.headerbar.show()
            self.toolbar.show()
            self.statusbar.show()
    
    def hide_controls(self):
        """Hide UI controls"""
        if self.state.controls_visible and not self.state.fullscreen_mode:
            self.state.controls_visible = False
            self.headerbar.hide()
            self.toolbar.hide()
            self.statusbar.hide()
    
    def on_mouse_motion(self, event):
        """Handle mouse motion"""
        self.show_controls()
        self.schedule_hide_controls()
    
    def schedule_hide_controls(self, delay=None):
        """Schedule hiding controls"""
        if delay is None:
            delay = self.state.auto_hide_delay
        
        if self.state.hide_timer:
            self.root.after_cancel(self.state.hide_timer)
        
        if self.state.sidebar_visible or self.state.fullscreen_mode:
            return
        
        self.state.hide_timer = self.root.after(delay, self.hide_controls)
    
    def cancel_hide_timer(self):
        """Cancel auto-hide timer"""
        if self.state.hide_timer:
            self.root.after_cancel(self.state.hide_timer)
            self.state.hide_timer = None
    
    # Cleanup
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up application...")
        
        self.cancel_hide_timer()
        
        if self.state.pending_zoom_update:
            self.root.after_cancel(self.state.pending_zoom_update)
        
        if self.state.current_image:
            self.image_processor.cleanup_image(self.state.current_image)
        
        if self.state.original_image:
            self.image_processor.cleanup_image(self.state.original_image)
        
        if self.mouse_handler:
            self.mouse_handler.stop_mouse_listener()
        
        gc.collect()
        logger.info("Application cleanup complete")