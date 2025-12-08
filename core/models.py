"""
Core domain models for image annotation.

This module contains framework-agnostic data models that can be used
with any UI framework (PyQt, web, CLI, etc.).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class BoundingBox:
    """
    Represents a rectangular bounding box.

    Attributes:
        x: Top-left x coordinate
        y: Top-left y coordinate
        width: Box width
        height: Box height
    """
    x: int
    y: int
    width: int
    height: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BoundingBox':
        """Create BoundingBox from dictionary."""
        return cls(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height']
        )

    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is inside this bounding box."""
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def to_coco_format(self) -> list[float]:
        """Convert to COCO format [x, y, width, height]."""
        return [float(self.x), float(self.y), float(self.width), float(self.height)]

    def to_csv_format(self) -> str:
        """Convert to CSV format string."""
        return f"{self.x},{self.y},{self.width},{self.height}"


@dataclass
class Annotation:
    """
    Single annotation on an image.

    Attributes:
        id: Unique identifier (UUID)
        bounding_box: The bounding box for this annotation
        label_id: Integer ID of the label category
        label_name: Name of the label (for convenience)
        image_id: Reference to parent image
        created_at: Creation timestamp
        modified_at: Last modification timestamp
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    bounding_box: Optional[BoundingBox] = None
    label_id: int = 0
    label_name: str = ""
    image_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'bounding_box': self.bounding_box.to_dict() if self.bounding_box else None,
            'label_id': self.label_id,
            'label_name': self.label_name,
            'image_id': self.image_id,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Annotation':
        """Create Annotation from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            bounding_box=BoundingBox.from_dict(data['bounding_box']) if data.get('bounding_box') else None,
            label_id=data.get('label_id', 0),
            label_name=data.get('label_name', ''),
            image_id=data.get('image_id', ''),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            modified_at=datetime.fromisoformat(data['modified_at']) if 'modified_at' in data else datetime.now()
        )

    def update_box(self, box: BoundingBox) -> None:
        """Update the bounding box and modification timestamp."""
        self.bounding_box = box
        self.modified_at = datetime.now()

    def update_label(self, label_id: int, label_name: str) -> None:
        """Update the label and modification timestamp."""
        self.label_id = label_id
        self.label_name = label_name
        self.modified_at = datetime.now()


@dataclass
class ImageMetadata:
    """
    Image information without pixel data.

    Attributes:
        id: Unique identifier (UUID)
        file_path: Absolute path to image file
        filename: Base filename
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (JPEG, PNG, etc.)
        annotations: List of annotations for this image
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_path: str = ""
    filename: str = ""
    width: int = 0
    height: int = 0
    format: str = ""
    annotations: list[Annotation] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'filename': self.filename,
            'width': self.width,
            'height': self.height,
            'format': self.format,
            'annotations': [ann.to_dict() for ann in self.annotations]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ImageMetadata':
        """Create ImageMetadata from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            file_path=data.get('file_path', ''),
            filename=data.get('filename', ''),
            width=data.get('width', 0),
            height=data.get('height', 0),
            format=data.get('format', ''),
            annotations=[Annotation.from_dict(ann) for ann in data.get('annotations', [])]
        )

    def add_annotation(self, annotation: Annotation) -> None:
        """Add an annotation to this image."""
        self.annotations.append(annotation)

    def remove_annotation(self, annotation_id: str) -> bool:
        """
        Remove an annotation by ID.

        Returns:
            True if annotation was removed, False if not found
        """
        initial_length = len(self.annotations)
        self.annotations = [ann for ann in self.annotations if ann.id != annotation_id]
        return len(self.annotations) < initial_length

    def get_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """Get an annotation by ID."""
        for ann in self.annotations:
            if ann.id == annotation_id:
                return ann
        return None
