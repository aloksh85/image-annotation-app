"""
Import service for annotation data.

This module provides functionality to import annotations from COCO JSON format
and convert them to internal data models.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

from core.models import ImageMetadata, Annotation, BoundingBox


class ImportService:
    """
    Service for importing annotations from COCO JSON format.

    This class is framework-agnostic and operates on core data models only.
    It handles loading COCO JSON files and converting them to internal format.

    Example:
        >>> service = ImportService()
        >>> images, labels = service.import_from_coco("annotations.json", "/path/to/images")
        >>> print(f"Loaded {len(images)} images with annotations")
    """

    def import_from_coco(
        self,
        coco_path: str,
        base_image_path: Optional[str] = None
    ) -> tuple[list[ImageMetadata], dict[int, str]]:
        """
        Import annotations from COCO JSON format.

        This method loads a COCO JSON file, matches images to file paths,
        and converts annotations to internal format.

        Args:
            coco_path: Path to COCO JSON file
            base_image_path: Optional base directory for images.
                           If None, uses COCO JSON file directory as base.

        Returns:
            Tuple of (list of ImageMetadata, label_map)
            - ImageMetadata list contains images with annotations
            - label_map is {label_id: label_name} for updating LabelManager

        Raises:
            FileNotFoundError: If COCO file doesn't exist
            ValueError: If COCO JSON has invalid format

        Example:
            >>> service = ImportService()
            >>> images, labels = service.import_from_coco("data.json")
            >>> # labels = {1: "cat", 2: "dog"}
        """
        # Load COCO JSON file
        coco_path = Path(coco_path)
        if not coco_path.exists():
            raise FileNotFoundError(f"COCO file not found: {coco_path}")

        with open(coco_path, 'r', encoding='utf-8') as f:
            coco_data = json.load(f)

        # Validate format
        if not self._validate_coco_format(coco_data):
            raise ValueError(
                "Invalid COCO JSON format. Required keys: images, annotations, categories"
            )

        # Extract categories (labels)
        label_map = self._build_label_map(coco_data['categories'])

        # Determine base path for image matching
        if base_image_path is None:
            base_image_path = str(coco_path.parent)

        # Match COCO images to actual file paths
        image_path_map = self._match_images_to_files(
            coco_data['images'],
            base_image_path
        )

        # Convert annotations to internal format
        annotations_by_image = self._convert_annotations(
            coco_data['annotations'],
            label_map
        )

        # Build ImageMetadata objects
        image_metadata_list = []
        for coco_img in coco_data['images']:
            coco_img_id = coco_img['id']

            # Get resolved file path
            file_path = image_path_map.get(coco_img_id)
            if not file_path:
                print(f"Warning: Could not find file for image ID {coco_img_id}: {coco_img.get('file_name', 'unknown')}")
                continue

            # Create ImageMetadata
            metadata = ImageMetadata(
                id=str(uuid.uuid4()),  # Generate new internal ID
                file_path=file_path,
                filename=coco_img['file_name'],
                width=coco_img.get('width', 0),
                height=coco_img.get('height', 0),
                format=Path(coco_img['file_name']).suffix.upper().lstrip('.'),
                annotations=annotations_by_image.get(coco_img_id, [])
            )

            image_metadata_list.append(metadata)

        return image_metadata_list, label_map

    def _validate_coco_format(self, coco_data: dict) -> bool:
        """
        Validate COCO JSON has required structure.

        Args:
            coco_data: Loaded COCO JSON dictionary

        Returns:
            True if valid, False otherwise
        """
        required_keys = ['images', 'annotations', 'categories']
        return all(key in coco_data for key in required_keys)

    def _match_images_to_files(
        self,
        coco_images: list,
        base_path: str
    ) -> dict[int, str]:
        """
        Match COCO image entries to actual file paths.

        Tries multiple strategies to find images:
        1. Direct path (filename may include subdirectories - Phase 7 support)
        2. Basename search in base_path
        3. Recursive search in base_path subdirectories

        Args:
            coco_images: List of image dicts from COCO JSON
            base_path: Base directory to search for images

        Returns:
            Dictionary mapping {coco_image_id: resolved_file_path}
        """
        base_path = Path(base_path)
        image_map = {}

        for img in coco_images:
            img_id = img['id']
            filename = img['file_name']

            # Strategy 1: Direct path (filename may include subdirs like "train/images/cat.jpg")
            candidate = base_path / filename
            if candidate.exists() and candidate.is_file():
                image_map[img_id] = str(candidate.absolute())
                continue

            # Strategy 2: Search for filename only (ignore subdirs in file_name)
            basename = Path(filename).name
            candidate = base_path / basename
            if candidate.exists() and candidate.is_file():
                image_map[img_id] = str(candidate.absolute())
                continue

            # Strategy 3: Recursive search
            matches = list(base_path.rglob(basename))
            if matches:
                # Use first match
                for match in matches:
                    if match.is_file():
                        image_map[img_id] = str(match.absolute())
                        break
                if img_id in image_map:
                    continue

            print(f"Warning: Could not find image file: {filename}")

        return image_map

    def _build_label_map(self, categories: list) -> dict[int, str]:
        """
        Extract label mapping from COCO categories.

        Args:
            categories: List of category dicts from COCO JSON

        Returns:
            Dictionary mapping {label_id: label_name}
        """
        return {cat['id']: cat['name'] for cat in categories}

    def _convert_annotations(
        self,
        coco_annotations: list,
        label_map: dict[int, str]
    ) -> dict[int, list[Annotation]]:
        """
        Convert COCO annotations to internal Annotation objects.

        Args:
            coco_annotations: List of annotation dicts from COCO JSON
            label_map: Mapping of {label_id: label_name}

        Returns:
            Dictionary mapping {coco_image_id: [Annotation, ...]}
        """
        annotations_by_image: dict[int, list[Annotation]] = {}

        for coco_ann in coco_annotations:
            image_id = coco_ann['image_id']
            category_id = coco_ann['category_id']
            bbox_coco = coco_ann['bbox']  # [x, y, width, height]

            # Create BoundingBox
            box = BoundingBox(
                x=int(bbox_coco[0]),
                y=int(bbox_coco[1]),
                width=int(bbox_coco[2]),
                height=int(bbox_coco[3])
            )

            # Create Annotation
            annotation = Annotation(
                id=str(uuid.uuid4()),  # Generate new internal ID
                bounding_box=box,
                label_id=category_id,
                label_name=label_map.get(category_id, f"unknown_{category_id}"),
                image_id="",  # Will be set when added to ImageMetadata
                created_at=datetime.now(),
                modified_at=datetime.now()
            )

            # Group by image
            if image_id not in annotations_by_image:
                annotations_by_image[image_id] = []
            annotations_by_image[image_id].append(annotation)

        return annotations_by_image
