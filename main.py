import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os
import threading
import time
from pynput import mouse
import math
import logging
import glob
import gc  # For garbage collection
from pathlib import Path
from gnome_theme import COLORS, FONTS, DIMENSIONS, ICONS

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


class GnomeImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS['bg_primary'])
        
        # Image state
        self.current_image = None
        self.original_image = None
        self.current_file_path = None
        self.image_list = []
        self.current_index = 0
        
        # Display state
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 20.0
        self.zoom_step = 0.1
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        
        # UI state
        self.sidebar_visible = False
        self.fullscreen_mode = False
        self.toolbar_visible = True
        self.controls_visible = True
        self.hide_timer = None
        self.auto_hide_delay = 3000  # 3 seconds
        
        # Panning state
        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        # Mouse listener for gestures
        self.mouse_listener = None
        self.last_scroll_time = 0
        self.scroll_threshold = 0.1
        
        # Throttling for zoom operations to prevent memory leaks
        self.zoom_throttle_time = 0
        self.zoom_throttle_delay = 0.05  # 50ms between zoom operations
        self.pending_zoom_update = None
        self.max_image_size = 4000  # Max width/height to prevent memory issues
        
        self.setup_ui()
        self.setup_bindings()
        self.start_mouse_listener()
        self.schedule_hide_controls()  # Start auto-hide timer
    
    def setup_ui(self):
        """Create the GNOME-style interface"""
        # Create main container
        self.main_container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create headerbar (GNOME-style top bar)
        self.create_headerbar()
        
        # Create main content area
        self.content_frame = tk.Frame(self.main_container, bg=COLORS['bg_primary'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar (initially hidden)
        self.create_sidebar()
        
        # Create main image area
        self.create_image_area()
        
        # Create toolbar (bottom controls)
        self.create_toolbar()
        
        # Create status bar
        self.create_statusbar()
    
    def create_headerbar(self):
        """Create GNOME-style headerbar"""
        self.headerbar = tk.Frame(
            self.main_container, 
            bg=COLORS['headerbar_bg'], 
            height=DIMENSIONS['headerbar_height']
        )
        self.headerbar.pack(fill=tk.X, side=tk.TOP)
        self.headerbar.pack_propagate(False)
        
        # Left side - just open button
        left_frame = tk.Frame(self.headerbar, bg=COLORS['headerbar_bg'])
        left_frame.pack(side=tk.LEFT, padx=DIMENSIONS['padding_medium'], pady=6)
        
        # Open button
        self.open_btn = self.create_header_button(left_frame, ICONS['open'], self.open_image)
        self.open_btn.pack(side=tk.LEFT)
        
        # Center - empty space (no title)
        center_frame = tk.Frame(self.headerbar, bg=COLORS['headerbar_bg'])
        center_frame.pack(expand=True)
        
        # Right side - view controls
        right_frame = tk.Frame(self.headerbar, bg=COLORS['headerbar_bg'])
        right_frame.pack(side=tk.RIGHT, padx=DIMENSIONS['padding_medium'], pady=6)
        
        # Info/sidebar toggle
        self.info_btn = self.create_header_button(right_frame, ICONS['info'], self.toggle_sidebar)
        self.info_btn.pack(side=tk.RIGHT, padx=3)
        
        # Fullscreen button
        self.fullscreen_btn = self.create_header_button(right_frame, ICONS['fullscreen'], self.toggle_fullscreen)
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
        
        # Hover effects and auto-hide interaction
        def on_enter(e):
            btn.configure(bg=COLORS['bg_tertiary'])
            self.show_controls()
            self.cancel_hide_timer()  # Don't hide while hovering over buttons
        
        def on_leave(e):
            btn.configure(bg=COLORS['headerbar_bg'])
            self.schedule_hide_controls()  # Resume auto-hide when leaving button
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def create_sidebar(self):
        """Create GNOME-style sidebar with image info and thumbnails"""
        self.sidebar = tk.Frame(
            self.content_frame,
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
    
    def create_image_area(self):
        """Create the main image display area"""
        self.image_container = tk.Frame(self.content_frame, bg=COLORS['bg_primary'])
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
            font=FONTS['default'], 
            justify=tk.CENTER
        )
    
    def create_toolbar(self):
        """Create GNOME-style bottom toolbar"""
        self.toolbar = tk.Frame(
            self.main_container,
            bg=COLORS['toolbar_bg'],
            height=DIMENSIONS['toolbar_height']
        )
        self.toolbar.pack(fill=tk.X, side=tk.BOTTOM)
        self.toolbar.pack_propagate(False)
        
        # Zoom controls
        zoom_frame = tk.Frame(self.toolbar, bg=COLORS['toolbar_bg'])
        zoom_frame.pack(side=tk.LEFT, padx=DIMENSIONS['padding_medium'], pady=6)
        
        self.zoom_out_btn = self.create_toolbar_button(zoom_frame, "−", self.zoom_out)
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
        
        self.zoom_in_btn = self.create_toolbar_button(zoom_frame, "+", self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_fit_btn = self.create_toolbar_button(zoom_frame, ICONS['zoom_fit'], self.fit_to_window)
        self.zoom_fit_btn.pack(side=tk.LEFT, padx=(12, 2))
        
        self.zoom_orig_btn = self.create_toolbar_button(zoom_frame, ICONS['zoom_original'], self.zoom_original)
        self.zoom_orig_btn.pack(side=tk.LEFT, padx=2)
        
        # Crop button (right side)
        crop_frame = tk.Frame(self.toolbar, bg=COLORS['toolbar_bg'])
        crop_frame.pack(side=tk.RIGHT, padx=DIMENSIONS['padding_medium'], pady=6)
        
        self.crop_btn = self.create_toolbar_button(crop_frame, "✂", self.crop_to_window)
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
        
        # Hover effects and auto-hide interaction
        def on_enter(e):
            btn.configure(bg=COLORS['bg_tertiary'])
            self.show_controls()
            self.cancel_hide_timer()  # Don't hide while hovering over buttons
        
        def on_leave(e):
            btn.configure(bg=COLORS['toolbar_bg'])
            self.schedule_hide_controls()  # Resume auto-hide when leaving button
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def create_statusbar(self):
        """Create status bar"""
        self.statusbar = tk.Frame(self.main_container, bg=COLORS['bg_secondary'], height=24)
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
    
    def setup_bindings(self):
        """Setup keyboard shortcuts and mouse events"""
        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-equal>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.zoom_original())
        self.root.bind('<Control-f>', lambda e: self.fit_to_window())
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<Control-i>', lambda e: self.toggle_sidebar())
        
        # Add + and - key zoom (without Control)
        self.root.bind('<plus>', lambda e: self.zoom_in())
        self.root.bind('<equal>', lambda e: self.zoom_in())  # + without shift
        self.root.bind('<minus>', lambda e: self.zoom_out())
        self.root.bind('<KP_Add>', lambda e: self.zoom_in())  # Numpad +
        self.root.bind('<KP_Subtract>', lambda e: self.zoom_out())  # Numpad -
        
        # Mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_press)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_release)
        self.canvas.bind('<Double-Button-1>', lambda e: self.toggle_fullscreen())
        self.canvas.bind('<Button-4>', self.on_mouse_wheel)
        self.canvas.bind('<Button-5>', self.on_mouse_wheel)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # Auto-hide controls mouse events
        self.root.bind('<Motion>', self.on_mouse_motion)
        self.canvas.bind('<Motion>', self.on_mouse_motion)
        self.canvas.bind('<Enter>', self.on_mouse_enter)
        self.canvas.bind('<Leave>', self.on_mouse_leave)
        
        # Bind motion events to controls too so they don't hide when hovering over them
        self.headerbar.bind('<Motion>', self.on_mouse_motion)
        self.toolbar.bind('<Motion>', self.on_mouse_motion)
        self.statusbar.bind('<Motion>', self.on_mouse_motion)
        
        # Also bind enter/leave events to control areas
        self.headerbar.bind('<Enter>', lambda e: self.cancel_hide_timer())
        self.headerbar.bind('<Leave>', lambda e: self.schedule_hide_controls())
        self.toolbar.bind('<Enter>', lambda e: self.cancel_hide_timer())
        self.toolbar.bind('<Leave>', lambda e: self.schedule_hide_controls())
        self.statusbar.bind('<Enter>', lambda e: self.cancel_hide_timer())
        self.statusbar.bind('<Leave>', lambda e: self.schedule_hide_controls())
        
        self.root.focus_set()
    
    # Image loading and navigation methods
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
        """Load an image and populate the image list"""
        try:
            logger.info(f"Loading image: {file_path}")
            self.original_image = Image.open(file_path)
            self.current_file_path = file_path
            
            # Reset transformations
            self.zoom_factor = 1.0
            self.rotation_angle = 0
            self.flip_horizontal = False
            self.flip_vertical = False
            self.image_offset_x = 0
            self.image_offset_y = 0
            
            # Update image list from the same directory
            self.update_image_list()
            
            # Update UI
            self.fit_to_window()
            self.update_title()
            self.update_sidebar_info()
            self.update_navigation_buttons()
            self.set_status(f"Loaded: {os.path.basename(file_path)}")
            
            # Hide welcome text
            self.canvas.delete(self.welcome_text)
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def update_image_list(self):
        """Update the list of images in the current directory"""
        if not self.current_file_path:
            return
        
        directory = os.path.dirname(self.current_file_path)
        image_extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.webp')
        
        self.image_list = []
        for ext in image_extensions:
            self.image_list.extend(glob.glob(os.path.join(directory, ext)))
            self.image_list.extend(glob.glob(os.path.join(directory, ext.upper())))
        
        self.image_list.sort()
        
        # Find current image index
        try:
            self.current_index = self.image_list.index(self.current_file_path)
        except ValueError:
            self.current_index = 0
        
        logger.info(f"Found {len(self.image_list)} images in directory")
    
    def prev_image(self):
        """Navigate to previous image"""
        if len(self.image_list) > 1:
            self.current_index = (self.current_index - 1) % len(self.image_list)
            self.load_image(self.image_list[self.current_index])
    
    def next_image(self):
        """Navigate to next image"""
        if len(self.image_list) > 1:
            self.current_index = (self.current_index + 1) % len(self.image_list)
            self.load_image(self.image_list[self.current_index])
    
    def update_navigation_buttons(self):
        """Update navigation button states (no buttons to update now)"""
        # Navigation buttons removed for minimal interface
        # Arrow keys still work for navigation
        pass
    
    # Display and transformation methods
    def update_image_display(self):
        """Update the image display with current zoom and transformations"""
        if not self.original_image:
            return
        
        try:
            # Clear pending updates
            self.pending_zoom_update = None
            
            # Apply transformations
            display_image = self.original_image.copy()
            
            # Apply rotation
            if self.rotation_angle != 0:
                display_image = display_image.rotate(-self.rotation_angle, expand=True)
            
            # Apply flips
            if self.flip_horizontal:
                display_image = display_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if self.flip_vertical:
                display_image = display_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            
            # Calculate new size with zoom
            new_width = int(display_image.width * self.zoom_factor)
            new_height = int(display_image.height * self.zoom_factor)
            
            # Limit maximum image size to prevent memory issues
            if new_width > self.max_image_size or new_height > self.max_image_size:
                logger.warning(f"Image too large ({new_width}x{new_height}), limiting size")
                if new_width > new_height:
                    ratio = self.max_image_size / new_width
                else:
                    ratio = self.max_image_size / new_height
                new_width = int(new_width * ratio)
                new_height = int(new_height * ratio)
                # Adjust zoom factor to reflect actual size
                self.zoom_factor = new_width / display_image.width
            
            # Apply zoom with size check
            if self.zoom_factor != 1.0:
                display_image = display_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Clean up previous image to free memory
            if hasattr(self, 'current_image') and self.current_image:
                del self.current_image
                gc.collect()  # Force garbage collection
            
            # Update canvas
            self.current_image = ImageTk.PhotoImage(display_image)
            
            # Clear and redraw
            self.canvas.delete("image")
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Center the image
            x_center = max(display_image.width // 2, canvas_width // 2) + self.image_offset_x
            y_center = max(display_image.height // 2, canvas_height // 2) + self.image_offset_y
            
            self.canvas.create_image(x_center, y_center, image=self.current_image, tags="image")
            
            # Configure scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Hide scrollbars for minimal interface
            self.h_scrollbar.pack_forget()
            self.v_scrollbar.pack_forget()
            
            # Update zoom label
            self.zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")
            
            # Clean up temporary image
            del display_image
            
        except Exception as e:
            logger.error(f"Error updating image display: {e}")
            # Force garbage collection on error
            gc.collect()
    
    # Zoom methods with throttling
    def zoom_in(self):
        """Zoom in with throttling"""
        if self.original_image:
            # Smaller zoom step to prevent memory spikes
            new_zoom = min(self.zoom_factor * 1.1, self.max_zoom)
            if new_zoom != self.zoom_factor:
                self.zoom_factor = new_zoom
                self.throttled_update_display()
                logger.debug(f"Zoomed to {int(self.zoom_factor * 100)}%")
    
    def zoom_out(self):
        """Zoom out with throttling"""
        if self.original_image:
            # Smaller zoom step to prevent memory spikes
            new_zoom = max(self.zoom_factor / 1.1, self.min_zoom)
            if new_zoom != self.zoom_factor:
                self.zoom_factor = new_zoom
                self.throttled_update_display()
                logger.debug(f"Zoomed to {int(self.zoom_factor * 100)}%")
    
    def throttled_update_display(self):
        """Throttle display updates to prevent memory leaks"""
        current_time = time.time()
        
        # Cancel pending update
        if self.pending_zoom_update:
            self.root.after_cancel(self.pending_zoom_update)
        
        # Check if enough time has passed since last update
        if current_time - self.zoom_throttle_time >= self.zoom_throttle_delay:
            self.zoom_throttle_time = current_time
            self.update_image_display()
        else:
            # Schedule update after throttle delay
            delay_ms = int((self.zoom_throttle_delay - (current_time - self.zoom_throttle_time)) * 1000)
            self.pending_zoom_update = self.root.after(delay_ms, self.update_image_display)
    
    def zoom_original(self):
        """Zoom to original size (100%)"""
        if self.original_image:
            self.zoom_factor = 1.0
            self.image_offset_x = 0
            self.image_offset_y = 0
            self.update_image_display()
    
    def fit_to_window(self):
        """Fit image to window"""
        if not self.original_image:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.fit_to_window)
            return
        
        # Account for current rotation
        img = self.original_image
        if self.rotation_angle in [90, 270]:
            img_width, img_height = img.height, img.width
        else:
            img_width, img_height = img.width, img.height
        
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        self.zoom_factor = ratio
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.update_image_display()
    
    # Transform methods
    def rotate_left(self):
        """Rotate image 90 degrees counter-clockwise"""
        if self.original_image:
            self.rotation_angle = (self.rotation_angle + 90) % 360
            self.fit_to_window()
            logger.info(f"Rotated to {self.rotation_angle} degrees")
    
    def rotate_right(self):
        """Rotate image 90 degrees clockwise"""
        if self.original_image:
            self.rotation_angle = (self.rotation_angle - 90) % 360
            self.fit_to_window()
            logger.info(f"Rotated to {self.rotation_angle} degrees")
    
    def crop_to_window(self):
        """Crop the image to what's currently visible in the window"""
        if not self.original_image:
            return
        
        try:
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Apply current transformations to get the display image
            display_image = self.original_image.copy()
            
            # Apply rotation
            if self.rotation_angle != 0:
                display_image = display_image.rotate(-self.rotation_angle, expand=True)
            
            # Apply flips
            if self.flip_horizontal:
                display_image = display_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if self.flip_vertical:
                display_image = display_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            
            # Apply zoom
            if self.zoom_factor != 1.0:
                new_size = (
                    int(display_image.width * self.zoom_factor),
                    int(display_image.height * self.zoom_factor)
                )
                display_image = display_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Calculate the visible area based on current pan offset
            img_width, img_height = display_image.size
            
            # Calculate image position on canvas
            x_center = max(img_width // 2, canvas_width // 2) + self.image_offset_x
            y_center = max(img_height // 2, canvas_height // 2) + self.image_offset_y
            
            # Calculate the top-left corner of the image
            img_left = x_center - img_width // 2
            img_top = y_center - img_height // 2
            
            # Calculate the visible region (intersection of image and canvas)
            visible_left = max(0, -img_left)
            visible_top = max(0, -img_top)
            visible_right = min(img_width, canvas_width - img_left)
            visible_bottom = min(img_height, canvas_height - img_top)
            
            # Check if there's a visible area to crop
            if visible_right <= visible_left or visible_bottom <= visible_top:
                messagebox.showwarning("Crop Error", "No visible area to crop!")
                return
            
            # Crop the image to the visible area
            cropped_image = display_image.crop((visible_left, visible_top, visible_right, visible_bottom))
            
            # Ask user for save location
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
                # Save the cropped image
                if save_path.lower().endswith('.jpg') or save_path.lower().endswith('.jpeg'):
                    # Convert to RGB for JPEG (removes transparency)
                    if cropped_image.mode in ('RGBA', 'LA'):
                        rgb_image = Image.new('RGB', cropped_image.size, (255, 255, 255))
                        rgb_image.paste(cropped_image, mask=cropped_image.split()[-1] if cropped_image.mode == 'RGBA' else None)
                        cropped_image = rgb_image
                
                cropped_image.save(save_path)
                self.set_status(f"Cropped image saved: {os.path.basename(save_path)}")
                logger.info(f"Image cropped and saved to: {save_path}")
                
                # Ask if user wants to open the cropped image
                if messagebox.askyesno("Open Cropped Image", "Do you want to open the cropped image?"):
                    self.load_image(save_path)
            
            # Clean up
            del display_image
            del cropped_image
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error cropping image: {e}")
            messagebox.showerror("Crop Error", f"Failed to crop image: {str(e)}")
    
    # UI methods
    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
            # Resume auto-hide when sidebar is closed
            self.schedule_hide_controls()
        else:
            self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
            self.sidebar_visible = True
            # Cancel auto-hide when sidebar is open and show controls
            self.cancel_hide_timer()
            self.show_controls()
        
        logger.info(f"Sidebar {'shown' if self.sidebar_visible else 'hidden'}")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.fullscreen_mode:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        self.fullscreen_mode = True
        self.root.attributes('-fullscreen', True)
        self.headerbar.pack_forget()
        self.toolbar.pack_forget()
        self.statusbar.pack_forget()
        if self.sidebar_visible:
            self.sidebar.pack_forget()
        # Cancel auto-hide timer in fullscreen
        self.cancel_hide_timer()
        self.controls_visible = False
        logger.info("Entered fullscreen mode")
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.fullscreen_mode:
            self.fullscreen_mode = False
            self.root.attributes('-fullscreen', False)
            # Show controls when exiting fullscreen
            self.controls_visible = True
            self.headerbar.pack(fill=tk.X, side=tk.TOP)
            self.toolbar.pack(fill=tk.X, side=tk.BOTTOM)
            self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
            if self.sidebar_visible:
                self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
            # Resume auto-hide after exiting fullscreen
            if not self.sidebar_visible:
                self.schedule_hide_controls()
            logger.info("Exited fullscreen mode")
    
    def update_title(self):
        """Update window title"""
        # Keep window title as "Image Viewer", no headerbar title
        self.root.title("Image Viewer")
    
    def update_sidebar_info(self):
        """Update sidebar with current image information"""
        if not self.current_file_path or not self.original_image:
            return
        
        filename = os.path.basename(self.current_file_path)
        file_size = os.path.getsize(self.current_file_path)
        
        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        self.filename_label.config(text=f"File: {filename}")
        self.size_label.config(text=f"Size: {size_str}")
        self.dimensions_label.config(text=f"Dimensions: {self.original_image.width} × {self.original_image.height}")
    
    def set_status(self, text):
        """Update status bar"""
        self.status_label.config(text=text)
    
    # Auto-hide controls methods
    def show_controls(self):
        """Show all UI controls"""
        if not self.controls_visible and not self.fullscreen_mode:
            self.controls_visible = True
            self.headerbar.pack(fill=tk.X, side=tk.TOP, before=self.content_frame)
            self.toolbar.pack(fill=tk.X, side=tk.BOTTOM, after=self.content_frame)
            self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
            logger.debug("Controls shown")
    
    def hide_controls(self):
        """Hide UI controls for clean viewing"""
        if self.controls_visible and not self.fullscreen_mode:
            self.controls_visible = False
            self.headerbar.pack_forget()
            self.toolbar.pack_forget()
            self.statusbar.pack_forget()
            logger.debug("Controls hidden")
    
    def on_mouse_enter(self, event):
        """Mouse entered the window"""
        self.show_controls()
        self.schedule_hide_controls()
    
    def on_mouse_leave(self, event):
        """Mouse left the window"""
        # Check if mouse is really outside the window
        x, y = self.root.winfo_pointerxy()
        win_x = self.root.winfo_rootx()
        win_y = self.root.winfo_rooty()
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        
        if not (win_x <= x <= win_x + win_width and win_y <= y <= win_y + win_height):
            self.schedule_hide_controls(delay=1000)  # Hide faster when mouse leaves
    
    def on_mouse_motion(self, event):
        """Mouse moved - show controls and reset hide timer"""
        self.show_controls()
        self.schedule_hide_controls()
    
    def schedule_hide_controls(self, delay=None):
        """Schedule hiding controls after delay"""
        if delay is None:
            delay = self.auto_hide_delay
        
        # Cancel existing timer
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
        
        # Don't auto-hide if sidebar is open or in fullscreen
        if self.sidebar_visible or self.fullscreen_mode:
            return
        
        # Schedule new hide
        self.hide_timer = self.root.after(delay, self.hide_controls)
    
    def cancel_hide_timer(self):
        """Cancel the auto-hide timer"""
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
            self.hide_timer = None
    
    # Mouse event handlers
    def on_mouse_press(self, event):
        """Handle mouse press for panning"""
        if self.original_image:
            self.panning = True
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.canvas.configure(cursor="fleur")
    
    def on_mouse_drag(self, event):
        """Handle mouse drag for panning"""
        if self.panning and self.original_image:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            
            self.image_offset_x += dx
            self.image_offset_y += dy
            
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            
            self.update_image_display()
    
    def on_mouse_release(self, event):
        """Handle mouse release"""
        self.panning = False
        self.canvas.configure(cursor="")
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming with throttling"""
        if not self.original_image:
            return
        
        current_time = time.time()
        
        # Throttle mouse wheel events to prevent rapid zoom
        if current_time - self.last_scroll_time < self.scroll_threshold:
            return
        
        self.last_scroll_time = current_time
        
        # Zoom with mouse wheel (only with Control key to prevent accidental zoom)
        if event.state & 0x4:  # Control key pressed
            if (hasattr(event, 'delta') and event.delta > 0) or event.num == 4:
                self.zoom_in()
            elif (hasattr(event, 'delta') and event.delta < 0) or event.num == 5:
                self.zoom_out()
        # Allow touchpad zoom without Control key but with stricter throttling
        elif hasattr(event, 'delta') and abs(event.delta) > 1:
            if event.delta > 0:
                self.zoom_in()
            elif event.delta < 0:
                self.zoom_out()
    
    def on_drop(self, event):
        """Handle drag and drop"""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
            if file_path.lower().endswith(valid_extensions):
                self.load_image(file_path)
            else:
                messagebox.showwarning("Invalid File", "Please drop an image file.")
    
    def start_mouse_listener(self):
        """Start background mouse listener for advanced gestures with heavy throttling"""
        last_gesture_time = 0
        gesture_throttle = 0.2  # 200ms between gestures
        
        def on_scroll(x, y, dx, dy):
            nonlocal last_gesture_time
            current_time = time.time()
            
            if not self.original_image:
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
                    
                    # Much more conservative gesture detection
                    if abs(dx) > abs(dy) and abs(dx) > 2.0:  # Increased threshold
                        last_gesture_time = current_time
                        if dx > 0:
                            self.root.after(0, self.zoom_in)
                        else:
                            self.root.after(0, self.zoom_out)
                    elif abs(dy) > 3.0:  # Much higher threshold for vertical
                        last_gesture_time = current_time
                        if dy > 0:
                            self.root.after(0, self.zoom_in)
                        else:
                            self.root.after(0, self.zoom_out)
            except:
                pass
        
        try:
            self.mouse_listener = mouse.Listener(on_scroll=on_scroll)
            self.mouse_listener.daemon = True
            self.mouse_listener.start()
            logger.info("Mouse listener started with heavy throttling")
        except Exception as e:
            logger.error(f"Failed to start mouse listener: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.cancel_hide_timer()
        
        # Cancel any pending zoom updates
        if self.pending_zoom_update:
            self.root.after_cancel(self.pending_zoom_update)
        
        # Clean up images
        if hasattr(self, 'current_image') and self.current_image:
            del self.current_image
        if hasattr(self, 'original_image') and self.original_image:
            del self.original_image
            
        if self.mouse_listener:
            self.mouse_listener.stop()
            
        # Force garbage collection
        gc.collect()


def main():
    """Main application entry point"""
    logger.info("Starting GNOME Image Viewer clone")
    root = TkinterDnD.Tk()
    app = GnomeImageViewer(root)
    
    def on_closing():
        logger.info("Application closing...")
        app.cleanup()
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    logger.info("Application started")
    root.mainloop()


if __name__ == "__main__":
    main()