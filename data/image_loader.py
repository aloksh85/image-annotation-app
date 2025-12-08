"""
Image file loading and caching.

This module handles the actual file I/O operations for loading images.
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtGui import QPixmap
from core.models import ImageMetadata
from utils.constants import SUPPORTED_FORMATS


class ImageLoader:
    """
    Loads image files and manages pixel data caching.

    This class is separated from business logic for clean architecture.
    It handles the actual file I/O and pixel data management.

    Attributes:
        _cache: Optional cache of loaded pixmaps
        _cache_enabled: Whether caching is enabled

    Example:
        >>> loader = ImageLoader()
        >>> pixmap, metadata = loader.load_image("/path/to/image.jpg")
        >>> print(f"Loaded {metadata.width}x{metadata.height} image")
    """

    def __init__(self, cache_enabled: bool = False):
        """
        Initialize the image loader.

        Args:
            cache_enabled: Whether to enable pixmap caching (default: False)
        """
        self._cache: dict[str, QPixmap] = {}
        self._cache_enabled = cache_enabled

    def load_image(self, file_path: str) -> tuple[QPixmap, ImageMetadata]:
        """
        Load an image file and extract metadata.

        Args:
            file_path: Absolute path to the image file

        Returns:
            Tuple of (QPixmap, ImageMetadata)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid image
        """
        # Validate file exists
        if not self.validate_file(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")

        # Check cache if enabled
        if self._cache_enabled and file_path in self._cache:
            pixmap = self._cache[file_path]
        else:
            # Load pixmap
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                raise ValueError(
                    f"Invalid image file or unsupported format: {file_path}"
                )

            # Cache if enabled
            if self._cache_enabled:
                self._cache[file_path] = pixmap

        # Extract metadata
        path = Path(file_path)
        metadata = ImageMetadata(
            file_path=file_path,
            filename=path.name,
            width=pixmap.width(),
            height=pixmap.height(),
            format=path.suffix.upper().replace('.', '')  # e.g., 'JPG', 'PNG'
        )

        return pixmap, metadata

    def validate_file(self, file_path: str) -> bool:
        """
        Check if file exists and has a valid image extension.

        Args:
            file_path: Path to check

        Returns:
            True if file is valid, False otherwise
        """
        path = Path(file_path)

        if not path.exists():
            return False

        if not path.is_file():
            return False

        # Check extension
        extension = path.suffix.lower()
        return extension in SUPPORTED_FORMATS

    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported image formats.

        Returns:
            List of supported file extensions (e.g., ['.jpg', '.png'])
        """
        return SUPPORTED_FORMATS.copy()

    def clear_cache(self) -> None:
        """Clear the pixmap cache."""
        self._cache.clear()

    def enable_cache(self, enabled: bool = True) -> None:
        """
        Enable or disable caching.

        Args:
            enabled: Whether to enable caching
        """
        self._cache_enabled = enabled
        if not enabled:
            self.clear_cache()
