"""
Image collection and navigation management.

This module provides framework-agnostic business logic for managing
a collection of images and navigating between them.
"""

from typing import Optional
from pathlib import Path
from core.models import ImageMetadata, SubdirectoryConfig


class ImageManager:
    """
    Manages loaded images and navigation between them.

    This class is framework-agnostic and handles the business logic
    of image collection management.

    Attributes:
        _images: Dictionary mapping image IDs to ImageMetadata objects
        _image_order: Ordered list of image IDs for navigation
        _current_index: Index of currently displayed image

    Example:
        >>> manager = ImageManager()
        >>> img_id = manager.add_image("/path/to/image.jpg", metadata)
        >>> current = manager.get_current_image()
        >>> next_img = manager.next_image()
    """

    def __init__(self):
        """Initialize the image manager."""
        self._images: dict[str, ImageMetadata] = {}
        self._image_order: list[str] = []
        self._current_index: int = -1
        self._base_path: Optional[str] = None  # Optional base path for relative paths

    def add_image(self, file_path: str, metadata: ImageMetadata) -> str:
        """
        Add an image to the collection.

        Args:
            file_path: Path to the image file
            metadata: ImageMetadata object

        Returns:
            The image ID
        """
        # Ensure metadata has correct file path
        metadata.file_path = file_path

        self._images[metadata.id] = metadata
        self._image_order.append(metadata.id)

        # Set as current if it's the first image
        if len(self._image_order) == 1:
            self._current_index = 0

        return metadata.id

    def remove_image(self, image_id: str) -> bool:
        """
        Remove an image from the collection.

        Args:
            image_id: ID of image to remove

        Returns:
            True if image was removed, False if not found
        """
        if image_id not in self._images:
            return False

        del self._images[image_id]
        self._image_order.remove(image_id)

        # Adjust current index if necessary
        if self._current_index >= len(self._image_order):
            self._current_index = max(0, len(self._image_order) - 1)

        if len(self._image_order) == 0:
            self._current_index = -1

        return True

    def get_current_image(self) -> Optional[ImageMetadata]:
        """
        Get the currently displayed image.

        Returns:
            ImageMetadata if an image is selected, None otherwise
        """
        if 0 <= self._current_index < len(self._image_order):
            image_id = self._image_order[self._current_index]
            return self._images.get(image_id)
        return None

    def next_image(self) -> Optional[ImageMetadata]:
        """
        Navigate to the next image.

        Returns:
            ImageMetadata of next image if available, current image otherwise
        """
        if len(self._image_order) == 0:
            return None

        if self._current_index < len(self._image_order) - 1:
            self._current_index += 1

        return self.get_current_image()

    def previous_image(self) -> Optional[ImageMetadata]:
        """
        Navigate to the previous image.

        Returns:
            ImageMetadata of previous image if available, current image otherwise
        """
        if len(self._image_order) == 0:
            return None

        if self._current_index > 0:
            self._current_index -= 1

        return self.get_current_image()

    def goto_image(self, image_id: str) -> bool:
        """
        Navigate to a specific image by ID.

        Args:
            image_id: ID of image to navigate to

        Returns:
            True if navigation successful, False if image not found
        """
        if image_id not in self._images:
            return False

        try:
            self._current_index = self._image_order.index(image_id)
            return True
        except ValueError:
            return False

    def get_image_count(self) -> int:
        """
        Get the total number of images.

        Returns:
            Number of images in collection
        """
        return len(self._image_order)

    def get_current_index(self) -> int:
        """
        Get the current image index (0-based).

        Returns:
            Current index, or -1 if no images
        """
        return self._current_index

    def get_image(self, image_id: str) -> Optional[ImageMetadata]:
        """
        Get a specific image by ID.

        Args:
            image_id: The image ID

        Returns:
            ImageMetadata if found, None otherwise
        """
        return self._images.get(image_id)

    def get_all_images(self) -> list[ImageMetadata]:
        """
        Get all images in order.

        Returns:
            List of all ImageMetadata objects in navigation order
        """
        return [self._images[img_id] for img_id in self._image_order if img_id in self._images]

    def set_base_path(self, base_path: str) -> None:
        """
        Set base path for relative path resolution.

        Args:
            base_path: Base directory path
        """
        self._base_path = base_path

    def get_base_path(self) -> Optional[str]:
        """
        Get current base path.

        Returns:
            Base path if set, None otherwise
        """
        return self._base_path

    def load_from_subdirectories(self, config: SubdirectoryConfig, image_loader) -> int:
        """
        Load all images from specified subdirectories.

        This method walks through each subdirectory finding supported image files
        and stores relative paths in ImageMetadata.filename for COCO export.

        Args:
            config: SubdirectoryConfig with base path and subdirectories
            image_loader: ImageLoader instance for loading images

        Returns:
            Number of images loaded

        Example:
            >>> config = SubdirectoryConfig("/dataset", ["train/images", "val/images"])
            >>> count = manager.load_from_subdirectories(config, loader)
            >>> print(f"Loaded {count} images")
        """
        self._base_path = config.base_path
        loaded_count = 0

        # Supported image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

        for subdir in config.subdirectories:
            full_path = Path(config.base_path) / subdir

            # Find all images in this subdirectory
            for ext in image_extensions:
                # Case-insensitive matching
                for img_path in list(full_path.glob(f'*{ext}')) + list(full_path.glob(f'*{ext.upper()}')):
                    if not img_path.is_file():
                        continue

                    try:
                        # Load image using image_loader
                        pixmap, metadata = image_loader.load_image(str(img_path))

                        # Store relative path in filename for COCO export
                        relative_path = img_path.relative_to(config.base_path)
                        metadata.filename = str(relative_path)

                        # Add to manager
                        self.add_image(str(img_path), metadata)
                        loaded_count += 1
                    except Exception as e:
                        # Skip files that can't be loaded
                        print(f"Warning: Could not load {img_path}: {e}")
                        continue

        return loaded_count
