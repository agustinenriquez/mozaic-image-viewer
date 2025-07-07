"""Keyboard input handling"""

import logging

logger = logging.getLogger(__name__)


class KeyboardHandler:
    """Handles keyboard shortcuts and events"""
    
    def __init__(self, root, callbacks):
        self.root = root
        self.callbacks = callbacks
        self.setup_bindings()
    
    def setup_bindings(self):
        """Setup keyboard shortcuts"""
        # File operations
        self.root.bind('<Control-o>', lambda e: self._call('open_image'))
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # View operations
        self.root.bind('<Escape>', lambda e: self._call('exit_fullscreen'))
        self.root.bind('<F11>', lambda e: self._call('toggle_fullscreen'))
        self.root.bind('<Control-i>', lambda e: self._call('toggle_sidebar'))
        
        # Zoom operations
        self.root.bind('<Control-plus>', lambda e: self._call('zoom_in'))
        self.root.bind('<Control-equal>', lambda e: self._call('zoom_in'))
        self.root.bind('<Control-minus>', lambda e: self._call('zoom_out'))
        self.root.bind('<Control-0>', lambda e: self._call('zoom_original'))
        self.root.bind('<Control-f>', lambda e: self._call('fit_to_window'))
        
        # Zoom operations without Control modifier
        self.root.bind('<plus>', lambda e: self._call('zoom_in'))
        self.root.bind('<equal>', lambda e: self._call('zoom_in'))  # + without shift
        self.root.bind('<minus>', lambda e: self._call('zoom_out'))
        self.root.bind('<KP_Add>', lambda e: self._call('zoom_in'))  # Numpad +
        self.root.bind('<KP_Subtract>', lambda e: self._call('zoom_out'))  # Numpad -
        
        # Navigation
        self.root.bind('<Left>', lambda e: self._call('prev_image'))
        self.root.bind('<Right>', lambda e: self._call('next_image'))
        
        # Focus
        self.root.focus_set()
        
        logger.info("Keyboard shortcuts configured")
    
    def _call(self, callback_name):
        """Call a callback function if it exists"""
        callback = self.callbacks.get(callback_name)
        if callback:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error calling callback {callback_name}: {e}")
        else:
            logger.warning(f"Callback {callback_name} not found")
    
    def add_binding(self, key_sequence, callback):
        """Add a custom key binding"""
        self.root.bind(key_sequence, lambda e: callback())
    
    def remove_binding(self, key_sequence):
        """Remove a key binding"""
        self.root.unbind(key_sequence)