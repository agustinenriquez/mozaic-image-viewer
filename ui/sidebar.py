"""GNOME-style sidebar component"""

import tkinter as tk
from tkinter import ttk
from gnome_theme import COLORS, FONTS, DIMENSIONS


class Sidebar:
    """GNOME-style sidebar with image info and thumbnails"""
    
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.sidebar = None
        self.visible = False
        
        # Info labels
        self.filename_label = None
        self.size_label = None
        self.dimensions_label = None
        
        # Thumbnail components
        self.thumb_canvas = None
        self.thumb_scrollbar = None
        self.thumb_frame = None
        
        self.create_sidebar()
    
    def create_sidebar(self):
        """Create GNOME-style sidebar with image info and thumbnails"""
        self.sidebar = tk.Frame(
            self.parent,
            bg=COLORS['sidebar_bg'],
            width=DIMENSIONS['sidebar_width']
        )
        # Initially not packed (hidden)
        
        # Sidebar header
        sidebar_header = tk.Frame(self.sidebar, bg=COLORS['sidebar_bg'])
        sidebar_header.pack(fill=tk.X, padx=DIMENSIONS['padding_medium'], pady=DIMENSIONS['padding_small'])
        
        tk.Label(
            sidebar_header,
            text="Image Information",
            bg=COLORS['sidebar_bg'],
            fg=COLORS['fg_primary'],
            font=FONTS['header']
        ).pack(anchor=tk.W)
        
        # Image info section
        self.info_frame = tk.Frame(self.sidebar, bg=COLORS['sidebar_bg'])
        self.info_frame.pack(fill=tk.X, padx=DIMENSIONS['padding_medium'], pady=DIMENSIONS['padding_small'])
        
        # File info labels
        self.filename_label = tk.Label(
            self.info_frame, bg=COLORS['sidebar_bg'], fg=COLORS['fg_secondary'], 
            font=FONTS['small'], anchor=tk.W, justify=tk.LEFT
        )
        self.filename_label.pack(fill=tk.X, pady=(0, 3))
        
        self.size_label = tk.Label(
            self.info_frame, bg=COLORS['sidebar_bg'], fg=COLORS['fg_secondary'],
            font=FONTS['small'], anchor=tk.W
        )
        self.size_label.pack(fill=tk.X, pady=3)
        
        self.dimensions_label = tk.Label(
            self.info_frame, bg=COLORS['sidebar_bg'], fg=COLORS['fg_secondary'],
            font=FONTS['small'], anchor=tk.W
        )
        self.dimensions_label.pack(fill=tk.X, pady=3)
        
        # Thumbnails section
        thumb_header = tk.Frame(self.sidebar, bg=COLORS['sidebar_bg'])
        thumb_header.pack(fill=tk.X, padx=DIMENSIONS['padding_medium'], pady=(DIMENSIONS['padding_large'], DIMENSIONS['padding_small']))
        
        tk.Label(
            thumb_header,
            text="Folder Images",
            bg=COLORS['sidebar_bg'],
            fg=COLORS['fg_primary'],
            font=FONTS['header']
        ).pack(anchor=tk.W)
        
        # Thumbnail scrollable area
        self.thumb_canvas = tk.Canvas(
            self.sidebar,
            bg=COLORS['sidebar_bg'],
            highlightthickness=0
        )
        self.thumb_scrollbar = ttk.Scrollbar(self.sidebar, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)
        
        self.thumb_frame = tk.Frame(self.thumb_canvas, bg=COLORS['sidebar_bg'])
        self.thumb_canvas.create_window((0, 0), window=self.thumb_frame, anchor=tk.NW)
        
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(DIMENSIONS['padding_medium'], 0))
        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show(self):
        """Show the sidebar"""
        if not self.visible:
            self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
            self.visible = True
    
    def hide(self):
        """Hide the sidebar"""
        if self.visible:
            self.sidebar.pack_forget()
            self.visible = False
    
    def toggle(self):
        """Toggle sidebar visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
        return self.visible
    
    def update_info(self, info):
        """Update sidebar with image information"""
        if not info:
            return
        
        self.filename_label.config(text=f"File: {info['filename']}")
        self.size_label.config(text=f"Size: {info['size']}")
        self.dimensions_label.config(text=f"Dimensions: {info['dimensions']}")
    
    def clear_info(self):
        """Clear sidebar information"""
        self.filename_label.config(text="")
        self.size_label.config(text="")
        self.dimensions_label.config(text="")
    
    def is_visible(self):
        """Check if sidebar is visible"""
        return self.visible