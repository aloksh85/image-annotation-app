"""
Annotation list widget for managing annotations.

This module provides a widget that displays all annotations for the current
image and allows selection, editing, and deletion.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import Annotation


class AnnotationListWidget(QWidget):
    """
    Widget for displaying and managing annotations.

    Shows a list of all annotations for the current image with options
    to select, edit, and delete annotations.

    Signals:
        annotation_selected: Emitted when user selects an annotation (str: annotation_id)
        annotation_deleted: Emitted when user deletes an annotation (str: annotation_id)
        annotation_edit_requested: Emitted when user wants to edit (str: annotation_id)

    Example:
        >>> widget = AnnotationListWidget()
        >>> widget.set_annotations(annotations)
        >>> widget.annotation_deleted.connect(on_delete)
    """

    # Signals
    annotation_selected = pyqtSignal(str)  # annotation_id
    annotation_deleted = pyqtSignal(str)   # annotation_id
    annotation_edit_requested = pyqtSignal(str)  # annotation_id

    def __init__(self, parent=None):
        """
        Initialize the annotation list widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._current_annotations: list[Annotation] = []

        # Setup UI
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Header label
        self.header_label = QLabel("Annotations (0)")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(self.header_label)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

        # Button layout
        button_layout = QHBoxLayout()

        self.edit_btn = QPushButton("Edit Label")
        self.edit_btn.clicked.connect(self._on_edit_clicked)
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setMinimumWidth(250)

    def set_annotations(self, annotations: list[Annotation]) -> None:
        """
        Set the annotations to display.

        Args:
            annotations: List of Annotation objects
        """
        self._current_annotations = annotations

        # Clear and repopulate list
        self.list_widget.clear()

        for annotation in annotations:
            # Format: "ID: name - uuid"
            display_text = f"{annotation.label_id}: {annotation.label_name} - {annotation.id[:8]}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, annotation.id)
            self.list_widget.addItem(item)

        # Update header
        count = len(annotations)
        self.header_label.setText(f"Annotations ({count})")

        # Disable buttons if no annotations
        has_items = count > 0
        self.edit_btn.setEnabled(False)  # Enable only when selected
        self.delete_btn.setEnabled(False)

    def clear(self) -> None:
        """Clear all annotations from the list."""
        self.list_widget.clear()
        self._current_annotations = []
        self.header_label.setText("Annotations (0)")
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def select_annotation(self, annotation_id: str) -> None:
        """
        Select an annotation in the list.

        Args:
            annotation_id: ID of annotation to select
        """
        # Find and select the item with this annotation ID
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == annotation_id:
                self.list_widget.setCurrentItem(item)
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                return

        # Deselect if not found
        self.list_widget.clearSelection()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """
        Handle item click in the list.

        Args:
            item: Clicked list item
        """
        annotation_id = item.data(Qt.ItemDataRole.UserRole)
        if annotation_id:
            self.annotation_selected.emit(annotation_id)
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)

    def _on_delete_clicked(self) -> None:
        """Handle delete button click."""
        current_item = self.list_widget.currentItem()
        if current_item:
            annotation_id = current_item.data(Qt.ItemDataRole.UserRole)
            if annotation_id:
                self.annotation_deleted.emit(annotation_id)

    def _on_edit_clicked(self) -> None:
        """Handle edit button click."""
        current_item = self.list_widget.currentItem()
        if current_item:
            annotation_id = current_item.data(Qt.ItemDataRole.UserRole)
            if annotation_id:
                self.annotation_edit_requested.emit(annotation_id)

    def get_selected_annotation_id(self) -> str | None:
        """
        Get the currently selected annotation ID.

        Returns:
            Annotation ID if one is selected, None otherwise
        """
        current_item = self.list_widget.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
