"""
Application-wide constants.
"""

# Supported image formats
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

# UI Colors (hex format for PyQt compatibility)
DEFAULT_BOX_COLOR = '#00FF00'  # Green for normal annotations
SELECTED_BOX_COLOR = '#FF0000'  # Red for selected annotation
TEMP_BOX_COLOR = '#FFFF00'  # Yellow for box being drawn

# Drawing settings
BOX_LINE_WIDTH = 2
LABEL_FONT_SIZE = 12
LABEL_BACKGROUND_ALPHA = 180  # 0-255

# Canvas settings
MIN_BOX_SIZE = 5  # Minimum width/height for a valid bounding box
