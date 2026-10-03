"""
Image Helper Functions for MSD-PRO Configurator.
Handles image loading, resizing, rotation, and validation for device displays.

This module provides utilities for:
- Loading and validating images
- Resizing images to device-specific dimensions
- Rotating and flipping images
- Converting between image formats
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Union
from PIL import Image, ImageOps, ImageQt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


# Image format specifications for MSD-PRO
KEY_IMAGE_FORMAT = {
    "size": (112, 112),
    "format": "PNG",
    "rotation": 180,
    "flip": (False, False)
}

SECONDARY_SCREEN_IMAGE_FORMAT = {
    "size": (176, 112),
    "format": "PNG",
    "rotation": 180,
    "flip": (False, False)
}

TOUCHSCREEN_IMAGE_FORMAT = {
    "size": (800, 480),
    "format": "JPEG",
    "rotation": 180,
    "flip": (False, False)
}


class ImageValidationError(Exception):
    """Raised when an image does not meet the required specifications."""
    pass


def validate_image(image: Image.Image, required_format: dict) -> bool:
    """
    Validate that an image meets the required specifications.
    
    Args:
        image: PIL Image to validate
        required_format: Dictionary with 'size', 'format' keys
    
    Returns:
        True if image is valid, False otherwise
    
    Raises:
        ImageValidationError: If image does not meet requirements
    """
    # Check size
    required_size = required_format.get("size", (0, 0))
    if required_size != (0, 0) and image.size != required_size:
        raise ImageValidationError(
            f"Image size must be {required_size}, got {image.size}"
        )
    
    return True


def load_image(image_path: Union[str, Path]) -> Image.Image:
    """
    Load an image from a file path.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        PIL Image object
    
    Raises:
        FileNotFoundError: If the image file does not exist
        Exception: If the image cannot be loaded
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        return Image.open(image_path)
    except Exception as e:
        raise Exception(f"Failed to load image: {e}")


def resize_image(image: Image.Image, size: Tuple[int, int]) -> Image.Image:
    """
    Resize an image to the specified dimensions using LANCZOS resampling.
    
    Args:
        image: PIL Image to resize
        size: Target size as (width, height)
    
    Returns:
        Resized PIL Image
    """
    return image.resize(size, Image.Resampling.LANCZOS)


def rotate_image(image: Image.Image, degrees: int) -> Image.Image:
    """
    Rotate an image by the specified degrees.
    
    Args:
        image: PIL Image to rotate
        degrees: Rotation angle in degrees (positive = counter-clockwise)
    
    Returns:
        Rotated PIL Image
    """
    return image.rotate(degrees, expand=True)


def flip_image(image: Image.Image, horizontal: bool = False, vertical: bool = False) -> Image.Image:
    """
    Flip an image horizontally and/or vertically.
    
    Args:
        image: PIL Image to flip
        horizontal: If True, flip horizontally
        vertical: If True, flip vertically
    
    Returns:
        Flipped PIL Image
    """
    if horizontal and vertical:
        return ImageOps.mirror(image)
    elif horizontal:
        return ImageOps.mirror(image)
    elif vertical:
        return ImageOps.flip(image)
    return image


def convert_format(image: Image.Image, target_format: str) -> Image.Image:
    """
    Convert an image to the specified format.
    
    Args:
        image: PIL Image to convert
        target_format: Target format (e.g., 'RGB', 'RGBA', 'L')
    
    Returns:
        Converted PIL Image
    """
    return image.convert(target_format)


def prepare_key_image(image_path: Union[str, Path], 
                      custom_format: Optional[dict] = None) -> Image.Image:
    """
    Prepare an image for use as a key icon.
    
    Args:
        image_path: Path to the source image
        custom_format: Optional custom format specifications
    
    Returns:
        Prepared PIL Image (112x112, rotated, flipped as needed)
    
    Raises:
        ImageValidationError: If image cannot be prepared
    """
    format_spec = custom_format or KEY_IMAGE_FORMAT
    
    # Load image
    image = load_image(image_path)
    
    # Convert to RGB if needed
    if image.mode != 'RGB' and image.mode != 'RGBA':
        image = convert_format(image, 'RGB')
    
    # Resize if necessary
    required_size = format_spec.get("size", (112, 112))
    if image.size != required_size:
        image = resize_image(image, required_size)
    
    # Apply rotation
    rotation = format_spec.get("rotation", 0)
    if rotation != 0:
        image = rotate_image(image, rotation)
    
    # Apply flip
    flip_h, flip_v = format_spec.get("flip", (False, False))
    if flip_h or flip_v:
        image = flip_image(image, flip_h, flip_v)
    
    return image


def prepare_secondary_screen_image(image_path: Union[str, Path], 
                                   custom_format: Optional[dict] = None) -> Image.Image:
    """
    Prepare an image for use as a secondary screen key icon.
    
    Args:
        image_path: Path to the source image
        custom_format: Optional custom format specifications
    
    Returns:
        Prepared PIL Image (176x112, rotated, flipped as needed)
    """
    format_spec = custom_format or SECONDARY_SCREEN_IMAGE_FORMAT
    
    # Load image
    image = load_image(image_path)
    
    # Convert to RGB if needed
    if image.mode != 'RGB' and image.mode != 'RGBA':
        image = convert_format(image, 'RGB')
    
    # Resize if necessary
    required_size = format_spec.get("size", (176, 112))
    if image.size != required_size:
        image = resize_image(image, required_size)
    
    # Apply rotation
    rotation = format_spec.get("rotation", 0)
    if rotation != 0:
        image = rotate_image(image, rotation)
    
    # Apply flip
    flip_h, flip_v = format_spec.get("flip", (False, False))
    if flip_h or flip_v:
        image = flip_image(image, flip_h, flip_v)
    
    return image


def prepare_touchscreen_image(image_path: Union[str, Path], 
                              custom_format: Optional[dict] = None) -> Image.Image:
    """
    Prepare an image for use as touchscreen background.
    
    Args:
        image_path: Path to the source image
        custom_format: Optional custom format specifications
    
    Returns:
        Prepared PIL Image (800x480, rotated, flipped as needed)
    """
    format_spec = custom_format or TOUCHSCREEN_IMAGE_FORMAT
    
    # Load image
    image = load_image(image_path)
    
    # Convert to RGB if needed (JPEG doesn't support alpha)
    if image.mode != 'RGB':
        if image.mode == 'RGBA':
            # Create white background for alpha
            background = Image.new('RGB', image.size, (0, 0, 0))
            background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
            image = background
        else:
            image = convert_format(image, 'RGB')
    
    # Resize if necessary
    required_size = format_spec.get("size", (800, 480))
    if image.size != required_size:
        image = resize_image(image, required_size)
    
    # Apply rotation
    rotation = format_spec.get("rotation", 0)
    if rotation != 0:
        image = rotate_image(image, rotation)
    
    # Apply flip
    flip_h, flip_v = format_spec.get("flip", (False, False))
    if flip_h or flip_v:
        image = flip_image(image, flip_h, flip_v)
    
    return image


def pil_to_qpixmap(image: Image.Image) -> QPixmap:
    """
    Convert a PIL Image to a QPixmap.
    
    Args:
        image: PIL Image to convert
    
    Returns:
        QPixmap object
    """
    if image.mode == 'RGBA':
        # Convert RGBA to ARGB (Qt format)
        image = image.convert('RGBA')
        data = image.tobytes('raw', 'RGBA')
        qimage = QImage(data, image.width, image.height, QImage.Format.Format_ARGB8888)
    else:
        # Convert RGB to RGB888
        image = image.convert('RGB')
        data = image.tobytes('raw', 'RGB')
        qimage = QImage(data, image.width, image.height, QImage.Format.Format_RGB888)
    
    return QPixmap.fromImage(qimage)


def qpixmap_to_pil(qpixmap: QPixmap) -> Image.Image:
    """
    Convert a QPixmap to a PIL Image.
    
    Args:
        qpixmap: QPixmap to convert
    
    Returns:
        PIL Image object
    """
    qimage = qpixmap.toImage()
    width = qimage.width()
    height = qimage.height()
    
    # Convert to bytes
    bytes_per_line = 4 if qimage.format() == QImage.Format.Format_ARGB8888 else 3
    bytes_data = qimage.bits().tobytes()
    
    # Create PIL image
    if qimage.format() == QImage.Format.Format_ARGB8888:
        return Image.frombytes('RGBA', (width, height), bytes_data, 'raw', 'RGBA', 0, 1)
    elif qimage.format() == QImage.Format.Format_RGB888:
        return Image.frombytes('RGB', (width, height), bytes_data, 'raw', 'RGB', 0, 1)
    else:
        # Convert to RGB
        qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
        bytes_data = qimage.bits().tobytes()
        return Image.frombytes('RGB', (width, height), bytes_data, 'raw', 'RGB', 0, 1)


def save_temp_image(image: Image.Image, prefix: str = "temp") -> str:
    """
    Save an image to a temporary file.
    
    Args:
        image: PIL Image to save
        prefix: Prefix for the temporary filename
    
    Returns:
        Path to the temporary image file
    """
    import tempfile
    import random
    
    # Determine format based on image mode
    format = 'PNG' if image.mode == 'RGBA' else 'JPEG'
    extension = 'png' if format == 'PNG' else 'jpg'
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    filename = f"{prefix}_{random.randint(10000, 99999)}.{extension}"
    temp_path = os.path.join(temp_dir, filename)
    
    # Save image
    if format == 'PNG':
        image.save(temp_path, format='PNG')
    else:
        image.save(temp_path, format='JPEG', quality=95)
    
    return temp_path


def get_image_info(image_path: Union[str, Path]) -> dict:
    """
    Get information about an image file without loading it completely.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Dictionary with image information (size, format, mode, etc.)
    """
    try:
        with Image.open(image_path) as img:
            return {
                "path": str(image_path),
                "size": img.size,
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height
            }
    except Exception as e:
        return {"error": str(e)}
