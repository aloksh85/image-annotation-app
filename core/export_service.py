"""
Export service for annotation data.

This module provides functionality to export annotations to various formats
(CSV, COCO JSON) for use in ML training pipelines.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from core.models import ImageMetadata


class ExportService:
    """
    Service for exporting annotations to different formats.

    Supports CSV and COCO JSON formats. All methods are framework-agnostic
    and operate on core data models only.

    Example:
        >>> service = ExportService()
        >>> service.export_to_csv(images, "annotations.csv")
        >>> service.export_to_coco(images, "annotations.json")
    """

    def export_to_csv(
        self,
        images: list[ImageMetadata],
        output_path: str
    ) -> None:
        """
        Export annotations to CSV format.

        CSV Format:
            image_name,x,y,width,height,label_id,label_name

        Args:
            images: List of ImageMetadata objects with annotations
            output_path: Path to output CSV file

        Raises:
            IOError: If file cannot be written
            ValueError: If images list is empty
        """
        if not images:
            raise ValueError("No images to export")

        # Collect all annotations from all images
        rows = []
        for image in images:
            for annotation in image.annotations:
                rows.append({
                    'image_name': image.filename,
                    'x': annotation.bounding_box.x,
                    'y': annotation.bounding_box.y,
                    'width': annotation.bounding_box.width,
                    'height': annotation.bounding_box.height,
                    'label_id': annotation.label_id,
                    'label_name': annotation.label_name
                })

        if not rows:
            raise ValueError("No annotations to export")

        # Write to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['image_name', 'x', 'y', 'width', 'height', 'label_id', 'label_name']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def export_to_coco(
        self,
        images: list[ImageMetadata],
        output_path: str
    ) -> None:
        """
        Export annotations to COCO JSON format.

        COCO Format Structure:
            {
                "info": {...},
                "licenses": [...],
                "images": [...],
                "annotations": [...],
                "categories": [...]
            }

        Args:
            images: List of ImageMetadata objects with annotations
            output_path: Path to output JSON file

        Raises:
            IOError: If file cannot be written
            ValueError: If images list is empty
        """
        if not images:
            raise ValueError("No images to export")

        # Build COCO structure
        coco_data = {
            "info": self._create_info_section(),
            "licenses": [],
            "images": [],
            "annotations": [],
            "categories": []
        }

        # Extract unique categories from all annotations
        categories_map = {}  # label_id -> category_info
        annotation_id = 1

        for image_idx, image in enumerate(images, start=1):
            # Add image entry
            coco_data["images"].append({
                "id": image_idx,
                "file_name": image.filename,
                "width": image.width,
                "height": image.height,
                "date_captured": "",
                "license": 0,
                "coco_url": "",
                "flickr_url": ""
            })

            # Add annotations for this image
            for annotation in image.annotations:
                # Track categories
                if annotation.label_id not in categories_map:
                    categories_map[annotation.label_id] = annotation.label_name

                # Convert bounding box to COCO format [x, y, width, height]
                bbox = [
                    annotation.bounding_box.x,
                    annotation.bounding_box.y,
                    annotation.bounding_box.width,
                    annotation.bounding_box.height
                ]

                # Calculate area
                area = annotation.bounding_box.width * annotation.bounding_box.height

                # Add annotation entry
                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": image_idx,
                    "category_id": annotation.label_id,
                    "bbox": bbox,
                    "area": area,
                    "segmentation": [],
                    "iscrowd": 0
                })

                annotation_id += 1

        # Build categories list
        for label_id in sorted(categories_map.keys()):
            coco_data["categories"].append({
                "id": label_id,
                "name": categories_map[label_id],
                "supercategory": ""
            })

        if not coco_data["annotations"]:
            raise ValueError("No annotations to export")

        # Write to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(coco_data, f, indent=2)

    def _create_info_section(self) -> dict[str, Any]:
        """
        Create the info section for COCO JSON.

        Returns:
            Dictionary with metadata about the dataset
        """
        return {
            "description": "Image Annotation Tool - Annotated Dataset",
            "url": "",
            "version": "1.0",
            "year": datetime.now().year,
            "contributor": "",
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_export_stats(self, images: list[ImageMetadata]) -> dict[str, Any]:
        """
        Get statistics about the dataset for export summary.

        Args:
            images: List of ImageMetadata objects

        Returns:
            Dictionary with dataset statistics
        """
        total_images = len(images)
        total_annotations = sum(len(img.annotations) for img in images)

        # Count annotations per label
        label_counts: dict[str, int] = {}
        for image in images:
            for annotation in image.annotations:
                label_name = annotation.label_name
                label_counts[label_name] = label_counts.get(label_name, 0) + 1

        return {
            "total_images": total_images,
            "total_annotations": total_annotations,
            "images_with_annotations": sum(1 for img in images if img.annotations),
            "images_without_annotations": sum(1 for img in images if not img.annotations),
            "label_distribution": label_counts
        }
