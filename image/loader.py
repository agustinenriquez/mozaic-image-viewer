"""Image loading and file management"""

import os
import glob
import logging
from PIL import Image

logger = logging.getLogger(__name__)


class ImageLoader:
    """Handles image loading and file list management"""
    
    def __init__(self):
        self.supported_extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.webp')
    
    def load_image(self, file_path):
        """Load an image from file path"""
        try:
            logger.info(f"Loading image: {file_path}")
            image = Image.open(file_path)
            return image
        except Exception as e:
            logger.error(f"Failed to load image {file_path}: {e}")
            return None
    
    def get_image_list(self, file_path):
        """Get list of images in the same directory as the given file"""
        if not file_path:
            return []
        
        try:
            directory = os.path.dirname(file_path)
            image_list = []
            
            for ext in self.supported_extensions:
                image_list.extend(glob.glob(os.path.join(directory, ext)))
                image_list.extend(glob.glob(os.path.join(directory, ext.upper())))
            
            image_list.sort()
            logger.info(f"Found {len(image_list)} images in directory")
            return image_list
            
        except Exception as e:
            logger.error(f"Error getting image list: {e}")
            return []
    
    def get_current_index(self, image_list, current_file_path):
        """Get the index of the current file in the image list"""
        try:
            return image_list.index(current_file_path)
        except ValueError:
            return 0
    
    def get_next_image(self, image_list, current_index):
        """Get the next image in the list"""
        if len(image_list) <= 1:
            return None, current_index
        
        next_index = (current_index + 1) % len(image_list)
        return image_list[next_index], next_index
    
    def get_previous_image(self, image_list, current_index):
        """Get the previous image in the list"""
        if len(image_list) <= 1:
            return None, current_index
        
        prev_index = (current_index - 1) % len(image_list)
        return image_list[prev_index], prev_index
    
    def is_valid_image_file(self, file_path):
        """Check if file is a valid image file"""
        if not file_path:
            return False
        
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
        return file_path.lower().endswith(valid_extensions)
    
    def get_file_info(self, file_path):
        """Get file information"""
        if not file_path or not os.path.exists(file_path):
            return None
        
        try:
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            
            return {
                'filename': filename,
                'size': file_size,
                'path': file_path
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None