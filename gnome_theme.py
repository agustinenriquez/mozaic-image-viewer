# GNOME Image Viewer Theme Configuration

# GNOME Color Palette (Adwaita theme)
COLORS = {
    # Main colors
    'bg_primary': '#242424',      # Dark background
    'bg_secondary': '#303030',    # Slightly lighter background
    'bg_tertiary': '#3a3a3a',     # Widget backgrounds
    'fg_primary': '#ffffff',      # Primary text
    'fg_secondary': '#cccccc',    # Secondary text
    'fg_tertiary': '#999999',     # Muted text
    
    # Accent colors
    'accent_blue': '#3584e4',     # GNOME blue
    'accent_hover': '#4a90e2',    # Hover state
    'accent_pressed': '#2b74d6',  # Pressed state
    
    # Status colors
    'success': '#26a269',
    'warning': '#e5a50a',
    'error': '#e01b24',
    
    # Special elements
    'headerbar_bg': '#2d2d2d',
    'sidebar_bg': '#262626',
    'toolbar_bg': '#2a2a2a',
    'border': '#1e1e1e',
    'shadow': '#000000',
}

# Typography
FONTS = {
    'default': ('Cantarell', 11),
    'header': ('Cantarell', 12, 'bold'),
    'small': ('Cantarell', 9),
    'mono': ('Source Code Pro', 10),
}

# Dimensions
DIMENSIONS = {
    'headerbar_height': 46,
    'toolbar_height': 42,
    'sidebar_width': 300,
    'thumbnail_size': 128,
    'button_size': 32,
    'icon_size': 16,
    'border_radius': 6,
    'padding_small': 6,
    'padding_medium': 12,
    'padding_large': 24,
}

# Icons (using Unicode symbols for now)
ICONS = {
    'open': '📁',
    'prev': '◀',
    'next': '▶',
    'zoom_in': '🔍',
    'zoom_out': '🔍',
    'zoom_fit': '⌂',
    'zoom_original': '1:1',
    'rotate_left': '↶',
    'rotate_right': '↷',
    'flip_h': '↔',
    'flip_v': '↕',
    'fullscreen': '⛶',
    'info': 'ℹ',
    'menu': '☰',
    'close': '✕',
}