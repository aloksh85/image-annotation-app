"""
UI presentation layer.

This module contains PyQt6-specific UI components.
These components can be replaced for web deployment while keeping
the core business logic intact.
"""

from ui.main_window import MainWindow
from ui.image_canvas import ImageCanvas
from ui.dialogs import LabelSetupDialog, LabelSelectionDialog, ExportDialog

__all__ = [
    'MainWindow',
    'ImageCanvas',
    'LabelSetupDialog',
    'LabelSelectionDialog',
    'ExportDialog',
]
