"""
Annotation management business logic.

This module provides framework-agnostic business logic for managing annotations.
Can be used with PyQt, web APIs, or any other interface.
"""

from typing import Optional
from datetime import datetime
from core.models import Annotation, BoundingBox


class AnnotationManager:
    """
    Central business logic for managing annotations.

    This class is framework-agnostic and can be used with PyQt, web API, or CLI.

    Attributes:
        _annotations: Dictionary mapping annotation IDs to Annotation objects
        _validation_enabled: Whether to validate annotations before creation

    Example:
        >>> manager = AnnotationManager()
        >>> box = BoundingBox(x=100, y=200, width=50, height=75)
        >>> ann = manager.create_annotation("img_1", box, "person")
        >>> print(ann.label)
        "person"
    """

    def __init__(self, validation_enabled: bool = True):
        """
        Initialize the annotation manager.

        Args:
            validation_enabled: Whether to validate annotations (default: True)
        """
        self._annotations: dict[str, Annotation] = {}
        self._validation_enabled = validation_enabled

    def create_annotation(
        self,
        image_id: str,
        box: BoundingBox,
        label_id: int,
        label_name: str
    ) -> Annotation:
        """
        Create a new annotation.

        Args:
            image_id: ID of the image this annotation belongs to
            box: Bounding box for the annotation
            label_id: Integer ID of the label
            label_name: Name of the label

        Returns:
            The created Annotation object

        Raises:
            ValueError: If validation fails
        """
        annotation = Annotation(
            bounding_box=box,
            label_id=label_id,
            label_name=label_name,
            image_id=image_id,
            created_at=datetime.now(),
            modified_at=datetime.now()
        )

        if self._validation_enabled:
            is_valid, error_msg = self.validate_annotation(annotation)
            if not is_valid:
                raise ValueError(f"Invalid annotation: {error_msg}")

        self._annotations[annotation.id] = annotation
        return annotation

    def get_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """
        Get an annotation by ID.

        Args:
            annotation_id: The annotation ID

        Returns:
            The Annotation object if found, None otherwise
        """
        return self._annotations.get(annotation_id)

    def update_annotation(
        self,
        annotation_id: str,
        box: Optional[BoundingBox] = None,
        label_id: Optional[int] = None,
        label_name: Optional[str] = None
    ) -> bool:
        """
        Update an existing annotation.

        Args:
            annotation_id: ID of annotation to update
            box: New bounding box (optional)
            label_id: New label ID (optional)
            label_name: New label name (optional)

        Returns:
            True if annotation was updated, False if not found
        """
        annotation = self._annotations.get(annotation_id)
        if not annotation:
            return False

        if box is not None:
            annotation.update_box(box)

        if label_id is not None and label_name is not None:
            annotation.update_label(label_id, label_name)

        return True

    def delete_annotation(self, annotation_id: str) -> bool:
        """
        Delete an annotation.

        Args:
            annotation_id: ID of annotation to delete

        Returns:
            True if annotation was deleted, False if not found
        """
        if annotation_id in self._annotations:
            del self._annotations[annotation_id]
            return True
        return False

    def get_annotations_for_image(self, image_id: str) -> list[Annotation]:
        """
        Get all annotations for a specific image.

        Args:
            image_id: The image ID

        Returns:
            List of annotations for the image
        """
        return [
            ann for ann in self._annotations.values()
            if ann.image_id == image_id
        ]

    def get_all_annotations(self) -> list[Annotation]:
        """
        Get all annotations.

        Returns:
            List of all annotations
        """
        return list(self._annotations.values())

    def validate_annotation(self, annotation: Annotation) -> tuple[bool, str]:
        """
        Validate an annotation.

        Args:
            annotation: The annotation to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if annotation.label_id <= 0:
            return False, "Label ID must be positive"

        if not annotation.label_name or not annotation.label_name.strip():
            return False, "Label name cannot be empty"

        if not annotation.bounding_box:
            return False, "Bounding box is required"

        if annotation.bounding_box.width <= 0 or annotation.bounding_box.height <= 0:
            return False, "Bounding box must have positive width and height"

        return True, ""

    def suggest_annotations(
        self,
        image_id: str,
        model_name: str = 'sam'
    ) -> list[Annotation]:
        """
        Generate automatic annotation suggestions using ML models.

        This is a placeholder for future ML model integration (SAM, DINO).

        Args:
            image_id: ID of image to annotate
            model_name: Model to use ('sam' or 'dino')

        Returns:
            List of suggested Annotation objects

        Note:
            Future implementation will:
            1. Load the specified ML model (SAM/DINO)
            2. Run inference on the image
            3. Convert model output to Annotation objects
            4. Return suggestions for user review
        """
        # Placeholder for future implementation
        # TODO: Implement SAM/DINO model integration
        return []
