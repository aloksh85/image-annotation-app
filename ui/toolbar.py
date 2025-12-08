"""
Toolbar for navigation and tool selection.

This module provides a toolbar with navigation buttons, image counter,
and drawing mode selection.
"""

from PyQt6.QtWidgets import (
    QToolBar, QPushButton, QLabel, QWidget,
    QHBoxLayout, QButtonGroup, QToolButton
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon


class ToolBar(QToolBar):
    """
    Main toolbar with navigation and tool selection.

    Provides buttons for navigating between images and selecting
    drawing/selection modes.

    Signals:
        next_image_requested: Emitted when Next button clicked
        previous_image_requested: Emitted when Previous button clicked
        mode_changed: Emitted when drawing mode changes (str: 'draw' or 'select')

    Example:
        >>> toolbar = ToolBar()
        >>> toolbar.next_image_requested.connect(on_next)
        >>> toolbar.update_image_counter(2, 5)  # Shows "Image 2/5"
    """

    # Signals
    next_image_requested = pyqtSignal()
    previous_image_requested = pyqtSignal()
    mode_changed = pyqtSignal(str)  # 'draw' or 'select'

    def __init__(self, parent=None):
        """
        Initialize the toolbar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.setMovable(False)
        self.setFloatable(False)

        # Navigation section
        self._setup_navigation()

        # Separator
        self.addSeparator()

        # Tool selection section
        self._setup_tools()

    def _setup_navigation(self) -> None:
        """Setup navigation buttons and image counter."""
        # Previous button
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self._on_previous_clicked)
        self.prev_btn.setEnabled(False)  # Disabled until images loaded
        self.addWidget(self.prev_btn)

        # Image counter label
        self.image_label = QLabel("No images")
        self.image_label.setStyleSheet(
            "padding: 0 10px; font-weight: bold; font-size: 11pt;"
        )
        self.image_label.setMinimumWidth(120)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addWidget(self.image_label)

        # Next button
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._on_next_clicked)
        self.next_btn.setEnabled(False)  # Disabled until images loaded
        self.addWidget(self.next_btn)

    def _setup_tools(self) -> None:
        """Setup drawing mode selection buttons."""
        # Create button group for exclusive selection
        self.tool_group = QButtonGroup(self)

        # Draw mode button
        self.draw_btn = QToolButton()
        self.draw_btn.setText("✏️ Draw")
        self.draw_btn.setCheckable(True)
        self.draw_btn.setChecked(True)  # Default mode
        self.draw_btn.setToolTip("Draw new annotations (D)")
        self.draw_btn.setShortcut("D")
        self.draw_btn.clicked.connect(lambda: self._on_mode_changed('draw'))
        self.tool_group.addButton(self.draw_btn)
        self.addWidget(self.draw_btn)

        # Select mode button
        self.select_btn = QToolButton()
        self.select_btn.setText("🖱️ Select")
        self.select_btn.setCheckable(True)
        self.select_btn.setToolTip("Select existing annotations (S)")
        self.select_btn.setShortcut("S")
        self.select_btn.clicked.connect(lambda: self._on_mode_changed('select'))
        self.tool_group.addButton(self.select_btn)
        self.addWidget(self.select_btn)

    def update_image_counter(self, current: int, total: int) -> None:
        """
        Update the image counter display.

        Args:
            current: Current image index (0-based, will display as 1-based)
            total: Total number of images
        """
        if total > 0:
            # Display as 1-based indexing for users
            self.image_label.setText(f"Image {current + 1}/{total}")

            # Enable/disable navigation buttons based on position
            self.prev_btn.setEnabled(current > 0)
            self.next_btn.setEnabled(current < total - 1)
        else:
            self.image_label.setText("No images")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)

    def _on_previous_clicked(self) -> None:
        """Handle Previous button click."""
        self.previous_image_requested.emit()

    def _on_next_clicked(self) -> None:
        """Handle Next button click."""
        self.next_image_requested.emit()

    def _on_mode_changed(self, mode: str) -> None:
        """
        Handle mode change.

        Args:
            mode: The new mode ('draw' or 'select')
        """
        self.mode_changed.emit(mode)

    def set_mode(self, mode: str) -> None:
        """
        Programmatically set the current mode.

        Args:
            mode: Mode to set ('draw' or 'select')
        """
        if mode == 'draw':
            self.draw_btn.setChecked(True)
        elif mode == 'select':
            self.select_btn.setChecked(True)

    def enable_navigation(self, enabled: bool) -> None:
        """
        Enable or disable all navigation controls.

        Args:
            enabled: Whether to enable navigation
        """
        if not enabled:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.image_label.setText("No images")
