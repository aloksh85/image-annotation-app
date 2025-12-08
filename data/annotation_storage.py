"""
Annotation persistence layer.

This module handles storage and retrieval of annotations.
MVP uses in-memory storage; can be extended to SQLite/PostgreSQL.
"""

from typing import Optional
from core.models import Annotation


class AnnotationStorage:
    """
    Storage adapter for annotations.

    MVP implementation uses in-memory storage.
    Future versions can extend this to persist to disk or database.

    Example:
        >>> storage = AnnotationStorage()
        >>> storage.save_annotations("img_1", [annotation1, annotation2])
        >>> annotations = storage.load_annotations("img_1")
    """

    def __init__(self):
        """Initialize the storage."""
        self._storage: dict[str, list[Annotation]] = {}

    def save_annotations(self, image_id: str, annotations: list[Annotation]) -> bool:
        """
        Save annotations for an image.

        Args:
            image_id: ID of the image
            annotations: List of annotations to save

        Returns:
            True if successful
        """
        self._storage[image_id] = annotations.copy()
        return True

    def load_annotations(self, image_id: str) -> list[Annotation]:
        """
        Load annotations for an image.

        Args:
            image_id: ID of the image

        Returns:
            List of annotations (empty list if none exist)
        """
        return self._storage.get(image_id, []).copy()

    def delete_annotations(self, image_id: str) -> bool:
        """
        Delete all annotations for an image.

        Args:
            image_id: ID of the image

        Returns:
            True if annotations existed and were deleted
        """
        if image_id in self._storage:
            del self._storage[image_id]
            return True
        return False

    # Future: Add persistence methods
    # def persist_to_file(self, file_path: str) -> bool:
    #     """Save all annotations to a file."""
    #     pass
    #
    # def load_from_file(self, file_path: str) -> bool:
    #     """Load all annotations from a file."""
    #     pass
