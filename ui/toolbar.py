"""GNOME-style toolbar component"""

import tkinter as tk
from gnome_theme import COLORS, FONTS, DIMENSIONS, ICONS


class Toolbar:
    """GNOME-style bottom toolbar with zoom controls"""
    
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.toolbar = None
        self.zoom_label = None
        self.create_toolbar()
    
    def create_toolbar(self):
        """Create GNOME-style bottom toolbar"""
        self.toolbar = tk.Frame(
            self.parent,
            bg=COLORS['toolbar_bg'],
            height=DIMENSIONS['toolbar_height']
        )
        self.toolbar.pack(fill=tk.X, side=tk.BOTTOM)
        self.toolbar.pack_propagate(False)
        
        # Zoom controls
        zoom_frame = tk.Frame(self.toolbar, bg=COLORS['toolbar_bg'])
        zoom_frame.pack(side=tk.LEFT, padx=DIMENSIONS['padding_medium'], pady=6)
        
        self.zoom_out_btn = self.create_toolbar_button(
            zoom_frame, "−", self.callbacks.get('zoom_out')
        )
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = tk.Label(
            zoom_frame,
            text="100%",
            bg=COLORS['toolbar_bg'],
            fg=COLORS['fg_primary'],
            font=FONTS['default'],
            width=6
        )
        self.zoom_label.pack(side=tk.LEFT, padx=6)
        
        self.zoom_in_btn = self.create_toolbar_button(
            zoom_frame, "+", self.callbacks.get('zoom_in')
        )
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_fit_btn = self.create_toolbar_button(
            zoom_frame, ICONS['zoom_fit'], self.callbacks.get('fit_to_window')
        )
        self.zoom_fit_btn.pack(side=tk.LEFT, padx=(12, 2))
        
        self.zoom_orig_btn = self.create_toolbar_button(
            zoom_frame, ICONS['zoom_original'], self.callbacks.get('zoom_original')
        )
        self.zoom_orig_btn.pack(side=tk.LEFT, padx=2)
        
        # Crop button (right side)
        crop_frame = tk.Frame(self.toolbar, bg=COLORS['toolbar_bg'])
        crop_frame.pack(side=tk.RIGHT, padx=DIMENSIONS['padding_medium'], pady=6)
        
        self.crop_btn = self.create_toolbar_button(
            crop_frame, "✂", self.callbacks.get('crop_to_window')
        )
        self.crop_btn.pack(side=tk.RIGHT)
    
    def create_toolbar_button(self, parent, text, command):
        """Create a GNOME-style toolbar button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS['toolbar_bg'],
            fg=COLORS['fg_secondary'],
            relief=tk.FLAT,
            font=FONTS['default'],
            width=3,
            height=1,
            bd=1,
            highlightthickness=0
        )
        
        # Hover effects
        def on_enter(e):
            btn.configure(bg=COLORS['bg_tertiary'])
            if self.callbacks.get('show_controls'):
                self.callbacks['show_controls']()
            if self.callbacks.get('cancel_hide_timer'):
                self.callbacks['cancel_hide_timer']()
        
        def on_leave(e):
            btn.configure(bg=COLORS['toolbar_bg'])
            if self.callbacks.get('schedule_hide_controls'):
                self.callbacks['schedule_hide_controls']()
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def update_zoom_label(self, zoom_factor):
        """Update the zoom percentage label"""
        if self.zoom_label:
            self.zoom_label.config(text=f"{int(zoom_factor * 100)}%")
    
    def show(self):
        """Show the toolbar"""
        self.toolbar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def hide(self):
        """Hide the toolbar"""
        self.toolbar.pack_forget()
    
    def bind_motion_events(self):
        """Bind motion events for auto-hide functionality"""
        def on_motion(e):
            if self.callbacks.get('on_mouse_motion'):
                self.callbacks['on_mouse_motion'](e)
        
        def on_enter(e):
            if self.callbacks.get('cancel_hide_timer'):
                self.callbacks['cancel_hide_timer']()
        
        def on_leave(e):
            if self.callbacks.get('schedule_hide_controls'):
                self.callbacks['schedule_hide_controls']()
        
        self.toolbar.bind('<Motion>', on_motion)
        self.toolbar.bind('<Enter>', on_enter)
        self.toolbar.bind('<Leave>', on_leave)