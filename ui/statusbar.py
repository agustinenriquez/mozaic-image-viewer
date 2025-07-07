"""Status bar component"""

import tkinter as tk
from gnome_theme import COLORS, FONTS, DIMENSIONS


class StatusBar:
    """Status bar for displaying application status"""
    
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.statusbar = None
        self.status_label = None
        self.create_statusbar()
    
    def create_statusbar(self):
        """Create status bar"""
        self.statusbar = tk.Frame(self.parent, bg=COLORS['bg_secondary'], height=24)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        self.statusbar.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.statusbar,
            text="Ready",
            bg=COLORS['bg_secondary'],
            fg=COLORS['fg_tertiary'],
            font=FONTS['small'],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=DIMENSIONS['padding_small'], fill=tk.X, expand=True)
    
    def set_status(self, text):
        """Update status text"""
        if self.status_label:
            self.status_label.config(text=text)
    
    def show(self):
        """Show the status bar"""
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def hide(self):
        """Hide the status bar"""
        self.statusbar.pack_forget()
    
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
        
        self.statusbar.bind('<Motion>', on_motion)
        self.statusbar.bind('<Enter>', on_enter)
        self.statusbar.bind('<Leave>', on_leave)