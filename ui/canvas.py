"""Main image canvas component"""

import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES
from gnome_theme import COLORS


class ImageCanvas:
    """Main image display canvas with scrollbars and drag/drop support"""
    
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.canvas = None
        self.h_scrollbar = None
        self.v_scrollbar = None
        self.welcome_text = None
        self.create_canvas()
    
    def create_canvas(self):
        """Create the main image display area"""
        self.image_container = tk.Frame(self.parent, bg=COLORS['bg_primary'])
        self.image_container.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Main canvas for image display
        self.canvas = tk.Canvas(
            self.image_container,
            bg=COLORS['bg_primary'],
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Enable drag and drop
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.on_drop)
        
        # Scrollbars for panning
        self.h_scrollbar = ttk.Scrollbar(self.image_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = ttk.Scrollbar(self.image_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        # Welcome message
        self.welcome_text = self.canvas.create_text(
            500, 350, 
            text="Drop an image here or click Open to get started",
            fill=COLORS['fg_tertiary'], 
            font=('Arial', 12), 
            justify=tk.CENTER
        )
        
        # Bind mouse events
        self.bind_mouse_events()
    
    def bind_mouse_events(self):
        """Bind mouse events for canvas interaction"""
        self.canvas.bind('<Button-1>', self.on_mouse_press)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_release)
        self.canvas.bind('<Double-Button-1>', self.on_double_click)
        self.canvas.bind('<Button-4>', self.on_mouse_wheel)
        self.canvas.bind('<Button-5>', self.on_mouse_wheel)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.bind('<Motion>', self.on_mouse_motion)
        self.canvas.bind('<Enter>', self.on_mouse_enter)
        self.canvas.bind('<Leave>', self.on_mouse_leave)
    
    def on_mouse_press(self, event):
        """Handle mouse press events"""
        if self.callbacks.get('on_mouse_press'):
            self.callbacks['on_mouse_press'](event)
    
    def on_mouse_drag(self, event):
        """Handle mouse drag events"""
        if self.callbacks.get('on_mouse_drag'):
            self.callbacks['on_mouse_drag'](event)
    
    def on_mouse_release(self, event):
        """Handle mouse release events"""
        if self.callbacks.get('on_mouse_release'):
            self.callbacks['on_mouse_release'](event)
    
    def on_double_click(self, event):
        """Handle double-click events"""
        if self.callbacks.get('toggle_fullscreen'):
            self.callbacks['toggle_fullscreen']()
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel events"""
        if self.callbacks.get('on_mouse_wheel'):
            self.callbacks['on_mouse_wheel'](event)
    
    def on_mouse_motion(self, event):
        """Handle mouse motion events"""
        if self.callbacks.get('on_mouse_motion'):
            self.callbacks['on_mouse_motion'](event)
    
    def on_mouse_enter(self, event):
        """Handle mouse enter events"""
        if self.callbacks.get('on_mouse_enter'):
            self.callbacks['on_mouse_enter'](event)
    
    def on_mouse_leave(self, event):
        """Handle mouse leave events"""
        if self.callbacks.get('on_mouse_leave'):
            self.callbacks['on_mouse_leave'](event)
    
    def on_drop(self, event):
        """Handle drag and drop events"""
        if self.callbacks.get('on_drop'):
            self.callbacks['on_drop'](event)
    
    def clear(self):
        """Clear all canvas contents"""
        self.canvas.delete("all")
    
    def create_image(self, x, y, image, tags=None):
        """Create an image on the canvas"""
        return self.canvas.create_image(x, y, image=image, tags=tags)
    
    def delete_by_tag(self, tag):
        """Delete canvas items by tag"""
        self.canvas.delete(tag)
    
    def configure_scroll_region(self, bbox):
        """Configure the scroll region"""
        self.canvas.configure(scrollregion=bbox)
    
    def hide_scrollbars(self):
        """Hide scrollbars for minimal interface"""
        self.h_scrollbar.pack_forget()
        self.v_scrollbar.pack_forget()
    
    def show_scrollbars(self):
        """Show scrollbars"""
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def hide_welcome_text(self):
        """Hide the welcome message"""
        if self.welcome_text:
            self.canvas.delete(self.welcome_text)
            self.welcome_text = None
    
    def set_cursor(self, cursor):
        """Set the canvas cursor"""
        self.canvas.configure(cursor=cursor)
    
    def get_dimensions(self):
        """Get canvas dimensions"""
        return self.canvas.winfo_width(), self.canvas.winfo_height()
    
    def get_bbox(self, tag):
        """Get bounding box of tagged items"""
        return self.canvas.bbox(tag)