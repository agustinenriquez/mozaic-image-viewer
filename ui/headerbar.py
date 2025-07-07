"""GNOME-style headerbar component"""

import tkinter as tk
from gnome_theme import COLORS, FONTS, DIMENSIONS, ICONS


class HeaderBar:
    """GNOME-style headerbar with controls"""
    
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.headerbar = None
        self.create_headerbar()
    
    def create_headerbar(self):
        """Create GNOME-style headerbar"""
        self.headerbar = tk.Frame(
            self.parent, 
            bg=COLORS['headerbar_bg'], 
            height=DIMENSIONS['headerbar_height']
        )
        self.headerbar.pack(fill=tk.X, side=tk.TOP)
        self.headerbar.pack_propagate(False)
        
        # Left side - open button
        left_frame = tk.Frame(self.headerbar, bg=COLORS['headerbar_bg'])
        left_frame.pack(side=tk.LEFT, padx=DIMENSIONS['padding_medium'], pady=6)
        
        # Open button
        self.open_btn = self.create_header_button(
            left_frame, ICONS['open'], self.callbacks.get('open_image')
        )
        self.open_btn.pack(side=tk.LEFT)
        
        # Center - empty space (no title)
        center_frame = tk.Frame(self.headerbar, bg=COLORS['headerbar_bg'])
        center_frame.pack(expand=True)
        
        # Right side - view controls
        right_frame = tk.Frame(self.headerbar, bg=COLORS['headerbar_bg'])
        right_frame.pack(side=tk.RIGHT, padx=DIMENSIONS['padding_medium'], pady=6)
        
        # Info/sidebar toggle
        self.info_btn = self.create_header_button(
            right_frame, ICONS['info'], self.callbacks.get('toggle_sidebar')
        )
        self.info_btn.pack(side=tk.RIGHT, padx=3)
        
        # Fullscreen button
        self.fullscreen_btn = self.create_header_button(
            right_frame, ICONS['fullscreen'], self.callbacks.get('toggle_fullscreen')
        )
        self.fullscreen_btn.pack(side=tk.RIGHT, padx=3)
    
    def create_header_button(self, parent, text, command):
        """Create a GNOME-style header button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS['headerbar_bg'],
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
            btn.configure(bg=COLORS['headerbar_bg'])
            if self.callbacks.get('schedule_hide_controls'):
                self.callbacks['schedule_hide_controls']()
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def show(self):
        """Show the headerbar"""
        self.headerbar.pack(fill=tk.X, side=tk.TOP)
    
    def hide(self):
        """Hide the headerbar"""
        self.headerbar.pack_forget()
    
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
        
        self.headerbar.bind('<Motion>', on_motion)
        self.headerbar.bind('<Enter>', on_enter)
        self.headerbar.bind('<Leave>', on_leave)