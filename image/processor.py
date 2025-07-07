"""Image processing and transformation logic"""

import logging
import gc
import time
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles image processing operations"""
    
    def __init__(self, max_image_size=4000):
        self.max_image_size = max_image_size
        self.zoom_throttle_time = 0
        self.zoom_throttle_delay = 0.05
    
    def process_image(self, original_image, zoom_factor=1.0, rotation_angle=0, 
                     flip_horizontal=False, flip_vertical=False):
        """Process image with transformations"""
        if not original_image:
            return None
        
        try:
            # Apply transformations
            display_image = original_image.copy()
            
            # Apply rotation
            if rotation_angle != 0:
                display_image = display_image.rotate(-rotation_angle, expand=True)
            
            # Apply flips
            if flip_horizontal:
                display_image = display_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if flip_vertical:
                display_image = display_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            
            # Calculate new size with zoom
            new_width = int(display_image.width * zoom_factor)
            new_height = int(display_image.height * zoom_factor)
            
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
                zoom_factor = new_width / display_image.width
            
            # Apply zoom with size check
            if zoom_factor != 1.0:
                display_image = display_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return display_image, zoom_factor
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None, zoom_factor
    
    def create_photo_image(self, pil_image):
        """Convert PIL image to PhotoImage for tkinter"""
        if not pil_image:
            return None
        
        try:
            return ImageTk.PhotoImage(pil_image)
        except Exception as e:
            logger.error(f"Error creating PhotoImage: {e}")
            return None
    
    def calculate_fit_zoom(self, image_width, image_height, canvas_width, canvas_height, rotation_angle=0):
        """Calculate zoom factor to fit image in canvas"""
        if canvas_width <= 1 or canvas_height <= 1:
            return 1.0
        
        # Account for rotation
        if rotation_angle in [90, 270]:
            img_width, img_height = image_height, image_width
        else:
            img_width, img_height = image_width, image_height
        
        return min(canvas_width / img_width, canvas_height / img_height)
    
    def crop_image(self, processed_image, canvas_width, canvas_height, image_offset_x=0, image_offset_y=0):
        """Crop image to visible area"""
        if not processed_image:
            return None
        
        try:
            img_width, img_height = processed_image.size
            
            # Calculate image position on canvas
            x_center = max(img_width // 2, canvas_width // 2) + image_offset_x
            y_center = max(img_height // 2, canvas_height // 2) + image_offset_y
            
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
                return None
            
            # Crop the image to the visible area
            cropped_image = processed_image.crop((visible_left, visible_top, visible_right, visible_bottom))
            return cropped_image
            
        except Exception as e:
            logger.error(f"Error cropping image: {e}")
            return None
    
    def should_throttle_zoom(self):
        """Check if zoom should be throttled"""
        current_time = time.time()
        return current_time - self.zoom_throttle_time < self.zoom_throttle_delay
    
    def update_throttle_time(self):
        """Update the throttle time"""
        self.zoom_throttle_time = time.time()
    
    @staticmethod
    def cleanup_image(image):
        """Clean up image resources"""
        try:
            if image:
                del image
            gc.collect()
        except Exception as e:
            logger.error(f"Error cleaning up image: {e}")
    
    @staticmethod
    def save_image_with_format(image, file_path):
        """Save image with proper format handling"""
        try:
            if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                # Convert to RGB for JPEG (removes transparency)
                if image.mode in ('RGBA', 'LA'):
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = rgb_image
            
            image.save(file_path)
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False