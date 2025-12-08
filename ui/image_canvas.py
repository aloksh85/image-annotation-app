"""
Interactive image canvas for annotation.

This module provides the main canvas widget where users can view images,
draw bounding boxes, and see existing annotations.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QFont, QPaintEvent, QMouseEvent
from core.models import BoundingBox, Annotation
from utils.constants import (
    DEFAULT_BOX_COLOR,
    SELECTED_BOX_COLOR,
    TEMP_BOX_COLOR,
    BOX_LINE_WIDTH,
    LABEL_FONT_SIZE,
    LABEL_BACKGROUND_ALPHA,
    MIN_BOX_SIZE
)


class ImageCanvas(QWidget):
    """
    Custom widget for image display and interactive annotation drawing.

    This widget displays images, allows users to draw bounding boxes with
    the mouse, and renders existing annotations.

    Signals:
        annotation_created: Emitted when user finishes drawing a box (BoundingBox)
        annotation_selected: Emitted when user clicks an annotation (str: annotation_id)

    Example:
        >>> canvas = ImageCanvas()
        >>> canvas.set_image(pixmap)
        >>> canvas.set_annotations(annotations)
        >>> canvas.annotation_created.connect(on_annotation_created)
    """

    # Signals
    annotation_created = pyqtSignal(BoundingBox)
    annotation_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initialize the image canvas.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Display data
        self._pixmap: QPixmap | None = None
        self._scaled_pixmap: QPixmap | None = None
        self._current_annotations: list[Annotation] = []
        self._image_offset_x = 0
        self._image_offset_y = 0
        self._scale_factor = 1.0

        # Drawing state
        self._drawing_mode = 'draw'  # 'draw' or 'select'
        self._is_drawing = False
        self._start_point: QPoint | None = None
        self._current_point: QPoint | None = None
        self._temp_box: BoundingBox | None = None

        # Selection state
        self._selected_annotation_id: str | None = None

        # Widget settings
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)

    def set_image(self, pixmap: QPixmap) -> None:
        """
        Set the image to display.

        Args:
            pixmap: QPixmap to display
        """
        self._pixmap = pixmap
        self._update_scaled_pixmap()
        self.update()  # Trigger repaint

    def set_annotations(self, annotations: list[Annotation]) -> None:
        """
        Set the annotations to display.

        Args:
            annotations: List of Annotation objects to render
        """
        self._current_annotations = annotations
        self.update()  # Trigger repaint

    def clear(self) -> None:
        """Clear the canvas (remove image and annotations)."""
        self._pixmap = None
        self._scaled_pixmap = None
        self._current_annotations = []
        self._temp_box = None
        self._selected_annotation_id = None
        self.update()

    def set_mode(self, mode: str) -> None:
        """
        Set the interaction mode.

        Args:
            mode: 'draw' for drawing new boxes, 'select' for selecting existing
        """
        self._drawing_mode = mode
        self._is_drawing = False
        self._start_point = None
        self._current_point = None

    def resizeEvent(self, event):
        """Handle widget resize by rescaling the image."""
        super().resizeEvent(event)
        if self._pixmap:
            self._update_scaled_pixmap()

    def _update_scaled_pixmap(self) -> None:
        """Update the scaled pixmap and calculate offset for centering."""
        if not self._pixmap:
            return

        # Scale pixmap to fit widget while maintaining aspect ratio
        self._scaled_pixmap = self._pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Calculate offset to center the image
        self._image_offset_x = (self.width() - self._scaled_pixmap.width()) // 2
        self._image_offset_y = (self.height() - self._scaled_pixmap.height()) // 2

        # Calculate scale factor for coordinate conversion
        if self._pixmap.width() > 0 and self._scaled_pixmap.width() > 0:
            self._scale_factor = self._pixmap.width() / self._scaled_pixmap.width()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Paint the canvas.

        Renders:
        1. The scaled image
        2. All saved annotations (bounding boxes + labels)
        3. Temporary box being drawn (if any)

        Args:
            event: Paint event
        """
        painter = QPainter(self)

        # Fill background
        painter.fillRect(self.rect(), QColor(50, 50, 50))

        if not self._scaled_pixmap:
            return

        # Draw the scaled image
        painter.drawPixmap(
            self._image_offset_x,
            self._image_offset_y,
            self._scaled_pixmap
        )

        # Draw all saved annotations
        for annotation in self._current_annotations:
            is_selected = (annotation.id == self._selected_annotation_id)
            self._draw_annotation(painter, annotation, is_selected)

        # Draw temporary box being drawn
        if self._is_drawing and self._start_point and self._current_point:
            self._draw_temporary_box(painter)

    def _draw_annotation(self, painter: QPainter, annotation: Annotation, selected: bool) -> None:
        """
        Draw a single annotation (bounding box + label).

        Args:
            painter: QPainter instance
            annotation: Annotation to draw
            selected: Whether this annotation is selected
        """
        if not annotation.bounding_box:
            return

        # Convert image coordinates to widget coordinates
        box = self._image_to_widget_coords(annotation.bounding_box)

        # Choose color based on selection state
        color = QColor(SELECTED_BOX_COLOR) if selected else QColor(DEFAULT_BOX_COLOR)

        # Draw bounding box
        pen = QPen(color, BOX_LINE_WIDTH)
        painter.setPen(pen)
        painter.drawRect(box.x, box.y, box.width, box.height)

        # Draw label background and text
        self._draw_label(painter, box, annotation.label_name, color)

    def _draw_temporary_box(self, painter: QPainter) -> None:
        """
        Draw the temporary box being drawn by the user.

        Args:
            painter: QPainter instance
        """
        if not self._start_point or not self._current_point:
            return

        # Calculate box dimensions from two opposite corners
        x = min(self._start_point.x(), self._current_point.x())
        y = min(self._start_point.y(), self._current_point.y())
        width = abs(self._current_point.x() - self._start_point.x())
        height = abs(self._current_point.y() - self._start_point.y())

        # Draw temporary box in yellow with dashed line
        pen = QPen(QColor(TEMP_BOX_COLOR), BOX_LINE_WIDTH)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(x, y, width, height)

    def _draw_label(self, painter: QPainter, box: BoundingBox, label: str, color: QColor) -> None:
        """
        Draw label text with background above the bounding box.

        Args:
            painter: QPainter instance
            box: Bounding box (in widget coordinates)
            label: Label text to display
            color: Color for the label background
        """
        # Setup font
        font = QFont()
        font.setPointSize(LABEL_FONT_SIZE)
        font.setBold(True)
        painter.setFont(font)

        # Calculate label dimensions
        metrics = painter.fontMetrics()
        label_width = metrics.horizontalAdvance(label) + 8
        label_height = metrics.height() + 4

        # Position label above the box (or inside if box is at top)
        label_x = box.x
        label_y = box.y - label_height if box.y > label_height else box.y

        # Draw label background
        bg_color = QColor(color)
        bg_color.setAlpha(LABEL_BACKGROUND_ALPHA)
        painter.fillRect(label_x, label_y, label_width, label_height, bg_color)

        # Draw label text
        painter.setPen(QColor(255, 255, 255))  # White text
        painter.drawText(
            label_x + 4,
            label_y + metrics.ascent() + 2,
            label
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press event.

        In draw mode: Start drawing a new bounding box (first corner).
        In select mode: Select annotation at click position.

        Args:
            event: Mouse event
        """
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Check if click is within image bounds
        if not self._is_point_on_image(event.pos()):
            return

        if self._drawing_mode == 'draw':
            # Start drawing - capture first corner
            self._is_drawing = True
            self._start_point = event.pos()
            self._current_point = event.pos()

        elif self._drawing_mode == 'select':
            # Try to select annotation at this point
            self._select_annotation_at_point(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move event.

        In draw mode: Update temporary box while dragging (second corner updates).

        Args:
            event: Mouse event
        """
        if self._is_drawing and self._drawing_mode == 'draw':
            self._current_point = event.pos()
            self.update()  # Trigger repaint to show temporary box

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse release event.

        In draw mode: Finalize the bounding box (second corner captured) and emit signal.

        Args:
            event: Mouse event
        """
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self._is_drawing and self._drawing_mode == 'draw':
            self._is_drawing = False

            if self._start_point and self._current_point:
                # Create box from two opposite corners
                box = self._create_bounding_box(self._start_point, self._current_point)

                # Only emit if box is large enough
                if box and box.width >= MIN_BOX_SIZE and box.height >= MIN_BOX_SIZE:
                    self.annotation_created.emit(box)

            # Clear temporary drawing state
            self._start_point = None
            self._current_point = None
            self.update()

    def _create_bounding_box(self, start: QPoint, end: QPoint) -> BoundingBox | None:
        """
        Create a BoundingBox from two opposite corners in widget coordinates.

        Converts to image coordinates and normalizes (works for any drag direction).

        Args:
            start: First corner (widget coords)
            end: Second corner (widget coords)

        Returns:
            BoundingBox in image coordinates, or None if invalid
        """
        # Calculate widget coordinates (normalized to top-left + width/height)
        x = min(start.x(), end.x())
        y = min(start.y(), end.y())
        width = abs(end.x() - start.x())
        height = abs(end.y() - start.y())

        # Convert from widget coordinates to image coordinates
        x_img = int((x - self._image_offset_x) * self._scale_factor)
        y_img = int((y - self._image_offset_y) * self._scale_factor)
        width_img = int(width * self._scale_factor)
        height_img = int(height * self._scale_factor)

        # Clamp to image bounds
        if self._pixmap:
            x_img = max(0, min(x_img, self._pixmap.width()))
            y_img = max(0, min(y_img, self._pixmap.height()))
            width_img = min(width_img, self._pixmap.width() - x_img)
            height_img = min(height_img, self._pixmap.height() - y_img)

        return BoundingBox(x=x_img, y=y_img, width=width_img, height=height_img)

    def _image_to_widget_coords(self, box: BoundingBox) -> BoundingBox:
        """
        Convert bounding box from image coordinates to widget coordinates.

        Args:
            box: BoundingBox in image coordinates

        Returns:
            BoundingBox in widget coordinates
        """
        x = int(box.x / self._scale_factor) + self._image_offset_x
        y = int(box.y / self._scale_factor) + self._image_offset_y
        width = int(box.width / self._scale_factor)
        height = int(box.height / self._scale_factor)

        return BoundingBox(x=x, y=y, width=width, height=height)

    def _is_point_on_image(self, point: QPoint) -> bool:
        """
        Check if a point is within the displayed image bounds.

        Args:
            point: Point in widget coordinates

        Returns:
            True if point is on image, False otherwise
        """
        if not self._scaled_pixmap:
            return False

        return (self._image_offset_x <= point.x() <= self._image_offset_x + self._scaled_pixmap.width() and
                self._image_offset_y <= point.y() <= self._image_offset_y + self._scaled_pixmap.height())

    def _select_annotation_at_point(self, point: QPoint) -> None:
        """
        Select an annotation at the given point.

        Args:
            point: Point in widget coordinates
        """
        # Convert to image coordinates
        x_img = int((point.x() - self._image_offset_x) * self._scale_factor)
        y_img = int((point.y() - self._image_offset_y) * self._scale_factor)

        # Find annotation containing this point
        for annotation in self._current_annotations:
            if annotation.bounding_box and annotation.bounding_box.contains_point(x_img, y_img):
                self._selected_annotation_id = annotation.id
                self.annotation_selected.emit(annotation.id)
                self.update()
                return

        # No annotation found - deselect
        self._selected_annotation_id = None
        self.update()
