"""
Dialog windows for user input.

This module contains PyQt6 dialogs for getting user input.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QDialogButtonBox,
    QComboBox, QFileDialog, QSpinBox, QListWidget,
    QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt


class LabelSetupDialog(QDialog):
    """
    Dialog to define the label set before annotation begins.

    User specifies label ID and label name pairs.

    Example:
        >>> dialog = LabelSetupDialog()
        >>> if dialog.exec():
        >>>     labels = dialog.get_labels()  # {1: "cat", 2: "dog", 3: "person"}
    """

    def __init__(self, parent=None):
        """
        Initialize the label setup dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Define Label Set")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.labels: dict[int, str] = {}

        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Define your label set before starting annotation.\n"
            "Each label needs an integer ID and a name."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Input section
        input_layout = QHBoxLayout()

        self.id_input = QSpinBox()
        self.id_input.setMinimum(1)
        self.id_input.setMaximum(9999)
        self.id_input.setValue(1)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., cat, dog, person")
        self.name_input.returnPressed.connect(self._add_label)

        add_btn = QPushButton("Add Label")
        add_btn.clicked.connect(self._add_label)

        input_layout.addWidget(QLabel("ID:"))
        input_layout.addWidget(self.id_input)
        input_layout.addWidget(QLabel("Name:"))
        input_layout.addWidget(self.name_input, stretch=1)
        input_layout.addWidget(add_btn)

        layout.addLayout(input_layout)

        # Label list
        layout.addWidget(QLabel("Defined Labels:"))
        self.label_list = QListWidget()
        layout.addWidget(self.label_list)

        # Remove button
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_label)
        layout.addWidget(remove_btn)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        # Focus on name input
        self.name_input.setFocus()

    def _add_label(self):
        """Add a label to the set."""
        label_id = self.id_input.value()
        label_name = self.name_input.text().strip()

        if not label_name:
            QMessageBox.warning(self, "Invalid Input", "Label name cannot be empty.")
            return

        if label_id in self.labels:
            QMessageBox.warning(
                self,
                "Duplicate ID",
                f"Label ID {label_id} already exists. Please use a different ID."
            )
            return

        # Check if name already exists
        if label_name in self.labels.values():
            QMessageBox.warning(
                self,
                "Duplicate Name",
                f"Label '{label_name}' already exists. Please use a different name."
            )
            return

        # Add to dictionary and list
        self.labels[label_id] = label_name
        self.label_list.addItem(f"{label_id}: {label_name}")

        # Auto-increment ID and clear name
        self.id_input.setValue(label_id + 1)
        self.name_input.clear()
        self.name_input.setFocus()

    def _remove_label(self):
        """Remove selected label from the set."""
        current_item = self.label_list.currentItem()
        if not current_item:
            return

        # Extract ID from the item text (format: "ID: name")
        text = current_item.text()
        label_id = int(text.split(':')[0].strip())

        # Remove from dictionary and list
        del self.labels[label_id]
        self.label_list.takeItem(self.label_list.row(current_item))

    def _validate_and_accept(self):
        """Validate that at least one label is defined before accepting."""
        if len(self.labels) == 0:
            QMessageBox.warning(
                self,
                "No Labels",
                "Please define at least one label before proceeding."
            )
            return

        self.accept()

    def get_labels(self) -> dict[int, str]:
        """
        Get the defined label set.

        Returns:
            Dictionary mapping label IDs to names
        """
        return self.labels.copy()


class LabelSelectionDialog(QDialog):
    """
    Simple dropdown to select a label from the predefined set.

    Used during annotation after drawing a bounding box.

    Example:
        >>> dialog = LabelSelectionDialog(labels={1: "cat", 2: "dog"})
        >>> if dialog.exec():
        >>>     label_id, label_name = dialog.get_selected_label()
    """

    def __init__(self, labels: dict[int, str], parent=None):
        """
        Initialize the label selection dialog.

        Args:
            labels: Dictionary of available labels {id: name}
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Select Label")
        self.setMinimumWidth(300)

        self.labels = labels

        layout = QVBoxLayout()

        # Label selection
        self.label_combo = QComboBox()
        for label_id, label_name in sorted(labels.items()):
            self.label_combo.addItem(f"{label_id}: {label_name}", userData=label_id)

        layout.addWidget(QLabel("Select annotation label:"))
        layout.addWidget(self.label_combo)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        # Focus on combo box
        self.label_combo.setFocus()

    def get_selected_label(self) -> tuple[int, str] | None:
        """
        Get the selected label.

        Returns:
            Tuple of (label_id, label_name) if accepted, None if canceled
        """
        if self.result() == QDialog.DialogCode.Accepted:
            label_id = self.label_combo.currentData()
            label_name = self.labels[label_id]
            return label_id, label_name
        return None


class ExportDialog(QDialog):
    """
    Dialog for export options (format and path).

    Example:
        >>> dialog = ExportDialog()
        >>> config = dialog.get_export_config()
        >>> if config:
        >>>     print(f"Export to {config['path']} as {config['format']}")
    """

    def __init__(self, parent=None):
        """
        Initialize the export dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Export Annotations")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "COCO JSON"])
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        layout.addWidget(QLabel("Export Format:"))
        layout.addWidget(self.format_combo)

        # Path selection
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select output file...")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input, stretch=1)
        path_layout.addWidget(browse_btn)

        layout.addWidget(QLabel("Output File:"))
        layout.addLayout(path_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def _browse(self):
        """Open file browser to select output path."""
        current_format = self.format_combo.currentText()

        if current_format == "CSV":
            filter_str = "CSV Files (*.csv)"
            default_ext = ".csv"
        else:  # COCO JSON
            filter_str = "JSON Files (*.json)"
            default_ext = ".json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Annotations",
            "",
            filter_str
        )

        if file_path:
            # Ensure correct extension
            if not file_path.endswith(default_ext):
                file_path += default_ext
            self.path_input.setText(file_path)

    def _on_format_changed(self, format_text: str):
        """
        Update file extension when format changes.

        Args:
            format_text: The selected format
        """
        current_path = self.path_input.text()
        if not current_path:
            return

        # Update extension
        if format_text == "CSV":
            new_path = current_path.rsplit('.', 1)[0] + '.csv'
        else:  # COCO JSON
            new_path = current_path.rsplit('.', 1)[0] + '.json'

        self.path_input.setText(new_path)

    def get_export_config(self) -> dict | None:
        """
        Get the export configuration.

        Returns:
            Dictionary with 'format' and 'path' keys, or None if canceled
        """
        if self.result() == QDialog.DialogCode.Accepted:
            path = self.path_input.text().strip()
            if path:
                return {
                    'format': self.format_combo.currentText(),
                    'path': path
                }
        return None
