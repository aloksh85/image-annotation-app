"""
Label set management.

This module manages the predefined set of labels and their integer IDs
for an annotation project.
"""

from typing import Optional


class LabelManager:
    """
    Manages the label set for an annotation project.

    Labels are defined before annotation begins, with each label having
    an integer ID and a name.

    Attributes:
        _labels: Dictionary mapping label IDs to label names

    Example:
        >>> manager = LabelManager()
        >>> manager.set_labels({1: "cat", 2: "dog", 3: "person"})
        >>> label_name = manager.get_label_name(1)  # "cat"
        >>> label_id = manager.get_label_id("dog")  # 2
    """

    def __init__(self):
        """Initialize the label manager."""
        self._labels: dict[int, str] = {}

    def set_labels(self, labels: dict[int, str]) -> None:
        """
        Set the complete label set for the project.

        Args:
            labels: Dictionary mapping label IDs to names
                   e.g., {1: "cat", 2: "dog", 3: "person"}
        """
        self._labels = labels.copy()

    def add_label(self, label_id: int, label_name: str) -> None:
        """
        Add a single label to the set.

        Args:
            label_id: Integer ID for the label
            label_name: Name of the label
        """
        self._labels[label_id] = label_name

    def get_label_name(self, label_id: int) -> Optional[str]:
        """
        Get the label name for a given ID.

        Args:
            label_id: The label ID

        Returns:
            Label name if found, None otherwise
        """
        return self._labels.get(label_id)

    def get_label_id(self, label_name: str) -> Optional[int]:
        """
        Get the label ID for a given name.

        Args:
            label_name: The label name

        Returns:
            Label ID if found, None otherwise
        """
        for label_id, name in self._labels.items():
            if name == label_name:
                return label_id
        return None

    def get_all_labels(self) -> dict[int, str]:
        """
        Get all labels.

        Returns:
            Dictionary mapping label IDs to names
        """
        return self._labels.copy()

    def get_label_list(self) -> list[tuple[int, str]]:
        """
        Get labels as a sorted list of (id, name) tuples.

        Returns:
            List of (label_id, label_name) tuples sorted by ID
        """
        return sorted(self._labels.items(), key=lambda x: x[0])

    def has_labels(self) -> bool:
        """
        Check if any labels are defined.

        Returns:
            True if labels are defined, False otherwise
        """
        return len(self._labels) > 0

    def clear_labels(self) -> None:
        """Clear all labels."""
        self._labels.clear()
