"""
Main application window.

This module provides the main window that orchestrates all UI components
and delegates business logic to the core layer.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QStatusBar, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt

from core.annotation_manager import AnnotationManager
from core.image_manager import ImageManager
from core.label_manager import LabelManager
from core.export_service import ExportService
from data.image_loader import ImageLoader
from ui.image_canvas import ImageCanvas
from ui.dialogs import LabelSetupDialog, LabelSelectionDialog, ExportDialog, SubdirectoryLoadDialog
from ui.annotation_list_widget import AnnotationListWidget
from ui.toolbar import ToolBar


class MainWindow(QMainWindow):
    """
    Main application window.

    Coordinates UI components and delegates business logic to core layer.
    This class has ZERO business logic - it only orchestrates components.

    Architecture:
        - UI Layer: This class + child widgets
        - Business Logic: AnnotationManager, ImageManager, LabelManager
        - Data Layer: ImageLoader

    Example:
        >>> window = MainWindow()
        >>> window.show()
    """

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Initialize business logic managers (framework-agnostic)
        self.annotation_manager = AnnotationManager()
        self.image_manager = ImageManager()
        self.label_manager = LabelManager()
        self.export_service = ExportService()

        # Initialize data layer
        self.image_loader = ImageLoader()

        # UI components (will be created in _init_ui)
        self.canvas: ImageCanvas | None = None
        self.annotation_list: AnnotationListWidget | None = None
        self.toolbar: ToolBar | None = None
        self.status_bar: QStatusBar | None = None

        # Setup UI
        self._init_ui()
        self._setup_menu_bar()
        self._connect_signals()

        # Show label setup dialog on startup
        self._show_label_setup_dialog()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Image Annotation Tool")
        self.resize(1200, 800)

        # Create toolbar
        self.toolbar = ToolBar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Horizontal layout: canvas (75%) + annotation list (25%)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Create image canvas
        self.canvas = ImageCanvas()
        main_layout.addWidget(self.canvas, stretch=3)  # 75% width

        # Create annotation list widget
        self.annotation_list = AnnotationListWidget()
        main_layout.addWidget(self.annotation_list, stretch=1)  # 25% width

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Load images to begin")

    def _setup_menu_bar(self) -> None:
        """Setup the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # Load images action
        load_action = file_menu.addAction("Load Images")
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_images)

        # Load from subdirectories action
        load_subdirs_action = file_menu.addAction("Load from Subdirectories...")
        load_subdirs_action.setShortcut("Ctrl+Shift+O")
        load_subdirs_action.triggered.connect(self.load_from_subdirectories)

        # Define labels action
        labels_action = file_menu.addAction("Define Labels")
        labels_action.setShortcut("Ctrl+L")
        labels_action.triggered.connect(self._show_label_setup_dialog)

        file_menu.addSeparator()

        # Export annotations action
        export_action = file_menu.addAction("Export Annotations")
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_annotations)

        file_menu.addSeparator()

        # Exit action
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

    def _connect_signals(self) -> None:
        """Connect signals from UI components to handlers."""
        # Canvas signals
        if self.canvas:
            self.canvas.annotation_created.connect(self._on_annotation_created)
            self.canvas.annotation_selected.connect(self._on_annotation_selected)

        # Toolbar signals
        if self.toolbar:
            self.toolbar.next_image_requested.connect(self._next_image)
            self.toolbar.previous_image_requested.connect(self._previous_image)
            self.toolbar.mode_changed.connect(self.canvas.set_mode)

        # Annotation list signals
        if self.annotation_list:
            self.annotation_list.annotation_deleted.connect(self._on_annotation_deleted_from_list)
            self.annotation_list.annotation_selected.connect(self._on_annotation_selected)
            # Bidirectional sync: canvas selection → list selection
            self.canvas.annotation_selected.connect(self.annotation_list.select_annotation)

    def _show_label_setup_dialog(self) -> None:
        """
        Show the label setup dialog.

        This allows users to define the label set before annotation begins.
        """
        dialog = LabelSetupDialog(self)

        # Pre-populate with existing labels if any
        if self.label_manager.has_labels():
            existing_labels = self.label_manager.get_all_labels()
            dialog.labels = existing_labels.copy()
            # Update the list widget
            dialog.label_list.clear()
            for label_id, label_name in sorted(existing_labels.items()):
                dialog.label_list.addItem(f"{label_id}: {label_name}")

        if dialog.exec():
            labels = dialog.get_labels()
            self.label_manager.set_labels(labels)
            self.status_bar.showMessage(
                f"Label set defined: {len(labels)} labels"
            )
        elif not self.label_manager.has_labels():
            # User cancelled and no labels defined - show warning
            QMessageBox.warning(
                self,
                "No Labels Defined",
                "You must define at least one label before annotating.\n"
                "Use File → Define Labels to set up your label set."
            )

    def load_images(self) -> None:
        """
        Load images via file dialog.

        Opens a file dialog, loads selected images, and displays the first one.
        """
        # Check if labels are defined
        if not self.label_manager.has_labels():
            QMessageBox.warning(
                self,
                "No Labels Defined",
                "Please define labels first using File → Define Labels."
            )
            self._show_label_setup_dialog()
            if not self.label_manager.has_labels():
                return

        # Open file dialog
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.gif)"
        )

        if not file_paths:
            return

        # Load each image
        loaded_count = 0
        for file_path in file_paths:
            try:
                # Load image and extract metadata
                pixmap, metadata = self.image_loader.load_image(file_path)

                # Add to image manager
                self.image_manager.add_image(file_path, metadata)
                loaded_count += 1

            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error Loading Image",
                    f"Failed to load {file_path}:\n{str(e)}"
                )

        # Display first image if any were loaded
        if loaded_count > 0:
            self._display_current_image()
            self.status_bar.showMessage(
                f"Loaded {loaded_count} image(s)"
            )
        else:
            self.status_bar.showMessage("No images loaded")

    def load_from_subdirectories(self) -> None:
        """
        Load images from multiple subdirectories.

        Opens a dialog to select base path and subdirectories, then loads
        all images while preserving relative paths for COCO export.
        """
        # Check if labels are defined
        if not self.label_manager.has_labels():
            QMessageBox.warning(
                self,
                "No Labels Defined",
                "Please define labels first using File → Define Labels."
            )
            self._show_label_setup_dialog()
            if not self.label_manager.has_labels():
                return

        # Show subdirectory selection dialog
        dialog = SubdirectoryLoadDialog(self)
        if not dialog.exec():
            return

        config = dialog.get_config()
        if not config:
            return

        try:
            # Show progress message
            self.status_bar.showMessage("Loading images from subdirectories...")

            # Load images from subdirectories
            loaded_count = self.image_manager.load_from_subdirectories(
                config,
                self.image_loader
            )

            if loaded_count > 0:
                self._display_current_image()
                QMessageBox.information(
                    self,
                    "Load Successful",
                    f"Loaded {loaded_count} image(s) from subdirectories.\n\n"
                    f"Base path: {config.base_path}\n"
                    f"Subdirectories: {', '.join(config.subdirectories)}"
                )
                self.status_bar.showMessage(
                    f"Loaded {loaded_count} image(s) from subdirectories"
                )
            else:
                QMessageBox.warning(
                    self,
                    "No Images",
                    "No supported images found in specified subdirectories."
                )
                self.status_bar.showMessage("No images loaded")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Failed to load images from subdirectories:\n{str(e)}"
            )
            self.status_bar.showMessage("Load failed")

    def _display_current_image(self) -> None:
        """Display the current image and its annotations."""
        current_image = self.image_manager.get_current_image()

        if not current_image:
            self.canvas.clear()
            self.annotation_list.clear()
            self.toolbar.update_image_counter(0, 0)
            self.status_bar.showMessage("No images loaded")
            return

        try:
            # Load pixmap
            pixmap, _ = self.image_loader.load_image(current_image.file_path)

            # Display on canvas
            self.canvas.set_image(pixmap)
            self.canvas.set_annotations(current_image.annotations)

            # Update annotation list
            self.annotation_list.set_annotations(current_image.annotations)

            # Update toolbar counter
            current_idx = self.image_manager.get_current_index()
            total = self.image_manager.get_image_count()
            self.toolbar.update_image_counter(current_idx, total)

            # Update status bar
            self.status_bar.showMessage(
                f"Image {current_idx + 1}/{total}: {current_image.filename} "
                f"({len(current_image.annotations)} annotations)"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to display image:\n{str(e)}"
            )

    def _on_annotation_created(self, box) -> None:
        """
        Handle annotation created signal from canvas.

        Shows label selection dialog and creates the annotation.

        Args:
            box: BoundingBox from the canvas
        """
        current_image = self.image_manager.get_current_image()
        if not current_image:
            return

        # Show label selection dialog
        dialog = LabelSelectionDialog(
            self.label_manager.get_all_labels(),
            self
        )

        if dialog.exec():
            result = dialog.get_selected_label()
            if result:
                label_id, label_name = result

                try:
                    # Create annotation using business logic
                    annotation = self.annotation_manager.create_annotation(
                        current_image.id,
                        box,
                        label_id,
                        label_name
                    )

                    # Add to image metadata
                    current_image.add_annotation(annotation)

                    # Refresh display
                    self.canvas.set_annotations(current_image.annotations)
                    self.annotation_list.set_annotations(current_image.annotations)

                    # Update status
                    self.status_bar.showMessage(
                        f"Created annotation: {label_name} "
                        f"({len(current_image.annotations)} total)"
                    )

                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Failed to create annotation:\n{str(e)}"
                    )

    def _on_annotation_selected(self, annotation_id: str) -> None:
        """
        Handle annotation selected signal from canvas.

        Args:
            annotation_id: ID of selected annotation
        """
        annotation = self.annotation_manager.get_annotation(annotation_id)
        if annotation:
            self.status_bar.showMessage(
                f"Selected: {annotation.label_name} (ID: {annotation_id[:8]}...)"
            )

    def keyPressEvent(self, event):
        """
        Handle keyboard shortcuts.

        Args:
            event: Key event
        """
        # Navigate between images with arrow keys
        if event.key() == Qt.Key.Key_Right or event.key() == Qt.Key.Key_Down:
            self._next_image()
        elif event.key() == Qt.Key.Key_Left or event.key() == Qt.Key.Key_Up:
            self._previous_image()
        elif event.key() == Qt.Key.Key_Delete:
            self._delete_selected_annotation()
        else:
            super().keyPressEvent(event)

    def _next_image(self) -> None:
        """Navigate to the next image."""
        next_img = self.image_manager.next_image()
        if next_img:
            self._display_current_image()

    def _previous_image(self) -> None:
        """Navigate to the previous image."""
        prev_img = self.image_manager.previous_image()
        if prev_img:
            self._display_current_image()

    def _delete_selected_annotation(self) -> None:
        """Delete the currently selected annotation (from keyboard)."""
        if not self.canvas or not self.canvas._selected_annotation_id:
            return

        current_image = self.image_manager.get_current_image()
        if not current_image:
            return

        annotation_id = self.canvas._selected_annotation_id

        # Remove from managers
        current_image.remove_annotation(annotation_id)
        self.annotation_manager.delete_annotation(annotation_id)

        # Refresh display
        self.canvas.set_annotations(current_image.annotations)
        self.annotation_list.set_annotations(current_image.annotations)
        self.status_bar.showMessage(
            f"Deleted annotation ({len(current_image.annotations)} remaining)"
        )

    def _on_annotation_deleted_from_list(self, annotation_id: str) -> None:
        """
        Handle annotation deletion from annotation list widget.

        Args:
            annotation_id: ID of annotation to delete
        """
        current_image = self.image_manager.get_current_image()
        if not current_image:
            return

        # Remove from managers
        current_image.remove_annotation(annotation_id)
        self.annotation_manager.delete_annotation(annotation_id)

        # Refresh display
        self.canvas.set_annotations(current_image.annotations)
        self.annotation_list.set_annotations(current_image.annotations)
        self.status_bar.showMessage(
            f"Deleted annotation ({len(current_image.annotations)} remaining)"
        )

    def export_annotations(self) -> None:
        """
        Export annotations to file.

        Shows export dialog and exports annotations in selected format.
        """
        # Check if there are any images loaded
        if self.image_manager.get_image_count() == 0:
            QMessageBox.warning(
                self,
                "No Images",
                "Please load images before exporting."
            )
            return

        # Get all images
        images = self.image_manager.get_all_images()

        # Check if there are any annotations
        total_annotations = sum(len(img.annotations) for img in images)
        if total_annotations == 0:
            QMessageBox.warning(
                self,
                "No Annotations",
                "There are no annotations to export."
            )
            return

        # Show export dialog
        dialog = ExportDialog(self)
        if not dialog.exec():
            return

        export_format = dialog.get_export_format()
        if not export_format:
            return

        # Determine file extension and filter based on format
        if export_format == "csv":
            file_filter = "CSV Files (*.csv)"
            default_ext = ".csv"
        else:  # coco
            file_filter = "JSON Files (*.json)"
            default_ext = ".json"

        # Show file save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Annotations",
            f"annotations{default_ext}",
            file_filter
        )

        if not file_path:
            return

        try:
            # Export using the service
            if export_format == "csv":
                self.export_service.export_to_csv(images, file_path)
            else:  # coco
                self.export_service.export_to_coco(images, file_path)

            # Get export statistics
            stats = self.export_service.get_export_stats(images)

            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported {stats['total_annotations']} annotations "
                f"from {stats['total_images']} images.\n\n"
                f"File saved to:\n{file_path}"
            )

            self.status_bar.showMessage(
                f"Exported {stats['total_annotations']} annotations to {file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export annotations:\n{str(e)}"
            )

    def closeEvent(self, event):
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Check if there are unsaved annotations
        if self.image_manager.get_image_count() > 0:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit?\n"
                "Make sure you've exported your annotations!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
