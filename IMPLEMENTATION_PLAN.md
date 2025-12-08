# Image Annotation Software - Implementation Plan

## Executive Summary

This document provides a comprehensive implementation plan for a PyQt-based image annotation software with clean architecture that supports future ML model integration and web deployment.

**Timeline**: 1-hour MVP
**Language**: Python 3.10+
**UI Framework**: PyQt6
**Architecture**: Three-layer design (UI → Business Logic → Data)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Design Diagrams](#system-design-diagrams)
3. [Project Structure](#project-structure)
4. [Class Designs](#class-designs)
5. [Implementation Sequence](#implementation-sequence)
6. [Dependencies](#dependencies)
7. [Future Extensibility](#future-extensibility)
8. [Code Quality Standards](#code-quality-standards)

---

## Architecture Overview

### Three-Layer Architecture

The system is designed with strict separation of concerns to enable future extensibility:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│              (PyQt UI - Replaceable for Web)                 │
│  - MainWindow, ImageCanvas, ToolBar, AnnotationListWidget   │
└──────────────────────┬──────────────────────────────────────┘
                       │ (calls methods, receives events)
┌──────────────────────▼──────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                       │
│              (Framework-Agnostic Core Logic)                 │
│  - AnnotationManager, ImageManager, ExportService            │
│  - Domain Models: Image, Annotation, BoundingBox            │
└──────────────────────┬──────────────────────────────────────┘
                       │ (reads/writes data)
┌──────────────────────▼──────────────────────────────────────┐
│                      DATA LAYER                              │
│              (Persistence & File I/O)                        │
│  - ImageLoader, AnnotationStorage, ExportWriter             │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **UI Independence**: Business logic has ZERO PyQt dependencies
2. **Future ML Ready**: Clean integration points for SAM/DINO models
3. **Web Migration Ready**: Business logic can be wrapped with REST API (FastAPI)
4. **Single Responsibility**: Each class has one clear purpose
5. **Testability**: Core logic fully testable without UI

---

## System Design Diagrams

### 1. Overall System Architecture

```mermaid
graph TB
    subgraph "Presentation Layer (PyQt)"
        MW[MainWindow]
        IC[ImageCanvas]
        ALW[AnnotationListWidget]
        TB[ToolBar]
        DLG[Dialogs]
    end

    subgraph "Business Logic Layer (Framework-Agnostic)"
        AM[AnnotationManager]
        IM[ImageManager]
        ES[ExportService]
        MOD[Models: BoundingBox<br/>Annotation<br/>ImageMetadata]
    end

    subgraph "Data Layer"
        IL[ImageLoader]
        AS[AnnotationStorage]
    end

    subgraph "External"
        FS[File System]
        USER[User]
    end

    USER -->|interacts| MW
    MW --> IC
    MW --> ALW
    MW --> TB
    MW --> DLG

    MW -->|delegates| AM
    MW -->|delegates| IM
    MW -->|delegates| ES

    IC -->|uses| MOD
    ALW -->|uses| MOD

    AM -->|manages| MOD
    IM -->|manages| MOD
    ES -->|reads| MOD

    IM -->|uses| IL
    AM -->|uses| AS
    ES -->|writes| FS
    IL -->|reads| FS

    style MW fill:#e1f5ff
    style IC fill:#e1f5ff
    style ALW fill:#e1f5ff
    style TB fill:#e1f5ff
    style DLG fill:#e1f5ff

    style AM fill:#fff4e1
    style IM fill:#fff4e1
    style ES fill:#fff4e1
    style MOD fill:#fff4e1

    style IL fill:#e8f5e9
    style AS fill:#e8f5e9
```

### 2. Class Diagram - Core Models

```mermaid
classDiagram
    class BoundingBox {
        +int x
        +int y
        +int width
        +int height
        +to_dict() dict
        +from_dict(dict) BoundingBox
        +contains_point(x, y) bool
        +to_coco_format() list~float~
        +to_csv_format() str
    }

    class Annotation {
        +str id
        +BoundingBox bounding_box
        +str label
        +str image_id
        +datetime created_at
        +datetime modified_at
        +to_dict() dict
        +from_dict(dict) Annotation
        +update_box(BoundingBox) None
        +update_label(str) None
    }

    class ImageMetadata {
        +str id
        +str file_path
        +str filename
        +int width
        +int height
        +str format
        +list~Annotation~ annotations
        +to_dict() dict
        +from_dict(dict) ImageMetadata
        +add_annotation(Annotation) None
        +remove_annotation(str) bool
        +get_annotation(str) Annotation
    }

    Annotation --> BoundingBox : contains
    ImageMetadata --> Annotation : manages
```

### 3. Class Diagram - Business Logic Layer

```mermaid
classDiagram
    class AnnotationManager {
        -dict~str,Annotation~ _annotations
        -bool _validation_enabled
        +create_annotation(image_id, box, label) Annotation
        +get_annotation(annotation_id) Annotation
        +update_annotation(annotation_id, box, label) bool
        +delete_annotation(annotation_id) bool
        +get_annotations_for_image(image_id) list~Annotation~
        +get_all_annotations() list~Annotation~
        +validate_annotation(Annotation) tuple
        +suggest_annotations(image_id, model) list~Annotation~
    }

    class ImageManager {
        -dict~str,ImageMetadata~ _images
        -list~str~ _image_order
        -int _current_index
        +add_image(file_path, metadata) str
        +remove_image(image_id) bool
        +get_current_image() ImageMetadata
        +next_image() ImageMetadata
        +previous_image() ImageMetadata
        +goto_image(image_id) bool
        +get_image_count() int
        +get_current_index() int
        +get_image(image_id) ImageMetadata
        +get_all_images() list~ImageMetadata~
    }

    class ExportService {
        +export_to_csv(images, output_path) bool
        +export_to_coco(images, output_path) bool
        -_generate_csv_rows(images) list~dict~
        -_generate_coco_structure(images) dict
        -_get_unique_labels(images) list~str~
    }

    AnnotationManager ..> Annotation : manages
    ImageManager ..> ImageMetadata : manages
    ExportService ..> ImageMetadata : reads
    ExportService ..> Annotation : reads
```

### 4. Class Diagram - UI Layer

```mermaid
classDiagram
    class MainWindow {
        -AnnotationManager annotation_manager
        -ImageManager image_manager
        -ExportService export_service
        -ImageLoader image_loader
        -ImageCanvas canvas
        -ToolBar toolbar
        -AnnotationListWidget annotation_list
        -QStatusBar status_bar
        +load_images() None
        +export_annotations() None
        -_init_ui() None
        -_setup_menu_bar() None
        -_connect_signals() None
        -_on_annotation_created(Annotation) None
        -_on_annotation_selected(str) None
        -_on_annotation_deleted(str) None
        -_on_next_image() None
        -_on_previous_image() None
    }

    class ImageCanvas {
        -QPixmap _pixmap
        -list~Annotation~ _current_annotations
        -str _drawing_mode
        -BoundingBox _temp_box
        -str _selected_annotation_id
        +set_image(QPixmap) None
        +set_annotations(list~Annotation~) None
        +clear() None
        +set_mode(str) None
        +paintEvent(QPaintEvent) None
        +mousePressEvent(QMouseEvent) None
        +mouseMoveEvent(QMouseEvent) None
        +mouseReleaseEvent(QMouseEvent) None
        -_draw_bounding_box(painter, box, selected) None
        -_draw_label(painter, box, label) None
    }

    class AnnotationListWidget {
        +set_annotations(list~Annotation~) None
        +clear() None
        +select_annotation(str) None
        -_on_delete_clicked() None
        -_on_edit_clicked() None
    }

    class ToolBar {
        +_init_tools() None
    }

    class LabelInputDialog {
        +get_label() str
    }

    class ExportDialog {
        +get_export_config() dict
    }

    MainWindow --> ImageCanvas : contains
    MainWindow --> AnnotationListWidget : contains
    MainWindow --> ToolBar : contains
    MainWindow ..> LabelInputDialog : uses
    MainWindow ..> ExportDialog : uses
    MainWindow ..> AnnotationManager : delegates to
    MainWindow ..> ImageManager : delegates to
    MainWindow ..> ExportService : delegates to
```

### 5. Sequence Diagram - Create Annotation Workflow

```mermaid
sequenceDiagram
    actor User
    participant IC as ImageCanvas
    participant MW as MainWindow
    participant DLG as LabelInputDialog
    participant AM as AnnotationManager
    participant ALW as AnnotationListWidget

    User->>IC: Draw rectangle (mouse drag)
    IC->>IC: mousePressEvent() - start point
    IC->>IC: mouseMoveEvent() - draw temporary box
    IC->>IC: mouseReleaseEvent() - end point
    IC->>MW: emit annotation_created(BoundingBox)

    MW->>DLG: Show label input dialog
    User->>DLG: Enter label "person"
    DLG->>MW: Return label "person"

    MW->>AM: create_annotation(image_id, box, "person")
    AM->>AM: Validate annotation
    AM->>AM: Generate UUID
    AM->>AM: Store annotation
    AM-->>MW: Return Annotation object

    MW->>IC: set_annotations(updated_list)
    IC->>IC: Repaint canvas with new annotation

    MW->>ALW: set_annotations(updated_list)
    ALW->>ALW: Update list display

    MW->>User: Show "Annotation created" in status bar
```

### 6. Sequence Diagram - Export Workflow

```mermaid
sequenceDiagram
    actor User
    participant MW as MainWindow
    participant DLG as ExportDialog
    participant ES as ExportService
    participant IM as ImageManager
    participant AM as AnnotationManager
    participant FS as FileSystem

    User->>MW: Click "Export" menu
    MW->>DLG: Show export dialog
    User->>DLG: Select format (COCO JSON) and path
    DLG-->>MW: Return {format: "coco", path: "/path/to/output.json"}

    MW->>IM: get_all_images()
    IM-->>MW: Return list[ImageMetadata]

    MW->>AM: get_all_annotations()
    AM-->>MW: Return list[Annotation]

    Note over MW: ImageMetadata already contains<br/>its annotations, so this step<br/>is optional for validation

    MW->>ES: export_to_coco(images, "/path/to/output.json")
    ES->>ES: _generate_coco_structure(images)
    ES->>ES: Build COCO JSON format
    ES->>FS: Write JSON to file
    FS-->>ES: Success
    ES-->>MW: Return True

    MW->>User: Show "Export successful" message
```

### 7. Sequence Diagram - Navigate Between Images

```mermaid
sequenceDiagram
    actor User
    participant TB as ToolBar
    participant MW as MainWindow
    participant IM as ImageManager
    participant IL as ImageLoader
    participant IC as ImageCanvas
    participant ALW as AnnotationListWidget

    User->>TB: Click "Next" button
    TB->>MW: emit next_image_requested()

    MW->>IM: next_image()
    IM->>IM: _current_index += 1
    IM->>IM: Get next ImageMetadata
    IM-->>MW: Return ImageMetadata

    MW->>IL: load_image(file_path)
    IL->>IL: Load from disk/cache
    IL-->>MW: Return QPixmap

    MW->>IC: set_image(QPixmap)
    IC->>IC: Update display

    MW->>IC: set_annotations(ImageMetadata.annotations)
    IC->>IC: Repaint with annotations

    MW->>ALW: set_annotations(ImageMetadata.annotations)
    ALW->>ALW: Update list

    MW->>MW: Update status bar "Image 2/5"
```

### 8. Component Interaction Diagram

```mermaid
graph LR
    subgraph "User Actions"
        A[Load Images]
        B[Draw Annotation]
        C[Edit Annotation]
        D[Navigate Images]
        E[Export Data]
    end

    subgraph "UI Layer"
        F[MainWindow]
        G[ImageCanvas]
        H[AnnotationListWidget]
        I[ToolBar]
    end

    subgraph "Business Logic"
        J[ImageManager]
        K[AnnotationManager]
        L[ExportService]
    end

    subgraph "Data Layer"
        M[ImageLoader]
        N[AnnotationStorage]
        O[FileSystem]
    end

    A -->|file dialog| F
    F -->|load file| M
    M -->|read| O
    M -->|return pixmap| J
    J -->|store metadata| F
    F -->|display| G

    B -->|mouse events| G
    G -->|emit signal| F
    F -->|create| K
    K -->|store| N
    F -->|update| G
    F -->|update| H

    C -->|select/edit| H
    H -->|emit signal| F
    F -->|update| K
    K -->|modify| N

    D -->|click next/prev| I
    I -->|emit signal| F
    F -->|navigate| J
    J -->|get image| F
    F -->|update| G

    E -->|click export| F
    F -->|get data| J
    F -->|get data| K
    F -->|export| L
    L -->|write| O

    style F fill:#e1f5ff
    style G fill:#e1f5ff
    style H fill:#e1f5ff
    style I fill:#e1f5ff

    style J fill:#fff4e1
    style K fill:#fff4e1
    style L fill:#fff4e1

    style M fill:#e8f5e9
    style N fill:#e8f5e9
    style O fill:#e8f5e9
```

### 9. Data Model Relationships

```mermaid
erDiagram
    ImageMetadata ||--o{ Annotation : contains
    Annotation ||--|| BoundingBox : has

    ImageMetadata {
        string id PK
        string file_path
        string filename
        int width
        int height
        string format
    }

    Annotation {
        string id PK
        string image_id FK
        string label
        datetime created_at
        datetime modified_at
    }

    BoundingBox {
        int x
        int y
        int width
        int height
    }
```

### 10. State Machine - Drawing Mode

```mermaid
stateDiagram-v2
    [*] --> Select: Default mode

    Select --> Draw: User clicks "Draw" tool
    Draw --> Select: User clicks "Select" tool

    state Draw {
        [*] --> Idle
        Idle --> Drawing: Mouse down
        Drawing --> Drawing: Mouse move
        Drawing --> Idle: Mouse up (create annotation)
    }

    state Select {
        [*] --> NoSelection
        NoSelection --> Selected: Click on annotation
        Selected --> NoSelection: Click empty area
        Selected --> Moving: Drag annotation
        Moving --> Selected: Mouse up
        Selected --> Resizing: Drag resize handle
        Resizing --> Selected: Mouse up
    }
```

---

## Project Structure

### Directory Layout

```
/Users/aloksh/Documents/sandbox/image_annotate/
├── app.py                          # Entry point (PyQt application setup)
├── requirements.txt                # Project dependencies
│
├── core/                           # Business Logic Layer (Framework-Agnostic)
│   ├── __init__.py
│   ├── models.py                   # Domain models: Image, Annotation, BoundingBox
│   ├── annotation_manager.py      # Core annotation business logic
│   ├── image_manager.py           # Image handling and navigation
│   └── export_service.py          # Export logic (CSV, COCO JSON)
│
├── data/                           # Data Layer (Persistence)
│   ├── __init__.py
│   ├── image_loader.py            # Image file loading/caching
│   ├── annotation_storage.py     # In-memory annotation storage
│   └── export_writer.py          # File writing utilities
│
├── ui/                             # Presentation Layer (PyQt-specific)
│   ├── __init__.py
│   ├── main_window.py             # Main application window
│   ├── image_canvas.py            # Interactive image display & drawing
│   ├── annotation_list_widget.py  # List of annotations with edit/delete
│   ├── toolbar.py                 # Tool selection (rectangle, select, etc.)
│   └── dialogs.py                 # Label input, export dialogs
│
└── utils/                          # Shared utilities
    ├── __init__.py
    ├── constants.py               # App-wide constants
    └── validators.py              # Input validation utilities
```

---

## Class Designs

### Core Layer (`core/models.py`)

**Purpose**: Framework-agnostic domain models that can be used by both desktop and web versions.

```python
class BoundingBox:
    """Represents a rectangular bounding box."""

    Attributes:
        - x: int (top-left x coordinate)
        - y: int (top-left y coordinate)
        - width: int
        - height: int

    Methods:
        - to_dict() -> dict  # For JSON serialization
        - from_dict(data: dict) -> BoundingBox
        - contains_point(x: int, y: int) -> bool
        - to_coco_format() -> list[float]  # [x, y, width, height]
        - to_csv_format() -> str  # "x,y,width,height"


class Annotation:
    """Single annotation on an image."""

    Attributes:
        - id: str (UUID)
        - bounding_box: BoundingBox
        - label: str
        - image_id: str (reference to parent image)
        - created_at: datetime
        - modified_at: datetime

    Methods:
        - to_dict() -> dict
        - from_dict(data: dict) -> Annotation
        - update_box(box: BoundingBox) -> None
        - update_label(label: str) -> None


class ImageMetadata:
    """Image information without pixel data."""

    Attributes:
        - id: str (UUID)
        - file_path: str (absolute path)
        - filename: str
        - width: int
        - height: int
        - format: str (JPEG, PNG)
        - annotations: list[Annotation]

    Methods:
        - to_dict() -> dict
        - from_dict(data: dict) -> ImageMetadata
        - add_annotation(annotation: Annotation) -> None
        - remove_annotation(annotation_id: str) -> bool
        - get_annotation(annotation_id: str) -> Annotation | None
```

### Core Layer (`core/annotation_manager.py`)

**Purpose**: Business logic for annotation operations (framework-agnostic).

```python
class AnnotationManager:
    """
    Central business logic for managing annotations.
    Framework-agnostic - can be used with PyQt, web API, or CLI.

    FUTURE EXTENSIBILITY:
    - add_auto_annotation() method for ML model integration
    - validate_annotation() hook for custom validation rules
    """

    Attributes:
        - _annotations: dict[str, Annotation]  # annotation_id -> Annotation
        - _validation_enabled: bool

    Methods:
        # Core CRUD operations
        - create_annotation(image_id: str, box: BoundingBox, label: str) -> Annotation
        - get_annotation(annotation_id: str) -> Annotation | None
        - update_annotation(annotation_id: str, box: BoundingBox = None, label: str = None) -> bool
        - delete_annotation(annotation_id: str) -> bool

        # Query operations
        - get_annotations_for_image(image_id: str) -> list[Annotation]
        - get_all_annotations() -> list[Annotation]

        # Validation
        - validate_annotation(annotation: Annotation) -> tuple[bool, str]

        # Future ML integration point
        - suggest_annotations(image_id: str, model_name: str) -> list[Annotation]
            # Placeholder for SAM/DINO integration
```

### Core Layer (`core/image_manager.py`)

**Purpose**: Manage image collection and navigation.

```python
class ImageManager:
    """
    Manages loaded images and navigation between them.
    Framework-agnostic business logic.
    """

    Attributes:
        - _images: dict[str, ImageMetadata]  # image_id -> metadata
        - _image_order: list[str]  # Ordered list of image IDs
        - _current_index: int

    Methods:
        # Image loading
        - add_image(file_path: str, metadata: ImageMetadata) -> str  # Returns image_id
        - remove_image(image_id: str) -> bool

        # Navigation
        - get_current_image() -> ImageMetadata | None
        - next_image() -> ImageMetadata | None
        - previous_image() -> ImageMetadata | None
        - goto_image(image_id: str) -> bool
        - get_image_count() -> int
        - get_current_index() -> int

        # Query
        - get_image(image_id: str) -> ImageMetadata | None
        - get_all_images() -> list[ImageMetadata]
```

### Core Layer (`core/export_service.py`)

**Purpose**: Framework-agnostic export logic.

```python
class ExportService:
    """
    Handles export of annotations to various formats.
    Framework-agnostic - works with any UI or API.
    """

    Methods:
        # CSV Export
        - export_to_csv(images: list[ImageMetadata], output_path: str) -> bool
            # Format: image_name, x, y, width, height, label

        # COCO JSON Export
        - export_to_coco(images: list[ImageMetadata], output_path: str) -> bool
            # Standard COCO format with images, annotations, categories

        # Helper methods
        - _generate_csv_rows(images: list[ImageMetadata]) -> list[dict]
        - _generate_coco_structure(images: list[ImageMetadata]) -> dict
        - _get_unique_labels(images: list[ImageMetadata]) -> list[str]
```

**COCO JSON Structure:**

```json
{
  "images": [
    {"id": 1, "file_name": "image1.jpg", "width": 1920, "height": 1080}
  ],
  "annotations": [
    {"id": 1, "image_id": 1, "category_id": 1, "bbox": [100, 200, 50, 75]}
  ],
  "categories": [
    {"id": 1, "name": "person"}
  ]
}
```

### Data Layer (`data/image_loader.py`)

**Purpose**: Handle actual image file I/O and pixel data.

```python
class ImageLoader:
    """
    Loads image files and manages pixel data caching.
    Separated from business logic for clean architecture.
    """

    Attributes:
        - _cache: dict[str, QPixmap]  # image_id -> cached pixmap (optional)
        - _cache_size_limit: int

    Methods:
        - load_image(file_path: str) -> tuple[QPixmap, ImageMetadata]
            # Returns both pixel data and metadata

        - validate_file(file_path: str) -> bool
            # Check if file exists and is valid image format

        - get_supported_formats() -> list[str]
            # Returns ['.jpg', '.jpeg', '.png']

        - clear_cache() -> None
```

### UI Layer (`ui/main_window.py`)

**Purpose**: Main PyQt window that orchestrates UI components.

```python
class MainWindow(QMainWindow):
    """
    Main application window.
    Coordinates UI components and delegates business logic to core layer.
    """

    Attributes:
        - annotation_manager: AnnotationManager  # Business logic
        - image_manager: ImageManager  # Business logic
        - export_service: ExportService  # Business logic
        - image_loader: ImageLoader  # Data layer

        # UI Components
        - canvas: ImageCanvas
        - toolbar: ToolBar
        - annotation_list: AnnotationListWidget
        - status_bar: QStatusBar

    Methods:
        # Setup
        - _init_ui() -> None
        - _setup_menu_bar() -> None
        - _connect_signals() -> None

        # File operations (delegates to managers)
        - load_images() -> None  # Opens file dialog, calls image_manager
        - export_annotations() -> None  # Opens dialog, calls export_service

        # Event handlers
        - _on_annotation_created(annotation: Annotation) -> None
        - _on_annotation_selected(annotation_id: str) -> None
        - _on_annotation_deleted(annotation_id: str) -> None
        - _on_next_image() -> None
        - _on_previous_image() -> None
```

### UI Layer (`ui/image_canvas.py`)

**Purpose**: Interactive canvas for displaying images and drawing annotations.

```python
class ImageCanvas(QWidget):
    """
    Custom widget for image display and interactive annotation drawing.
    Emits signals for user actions, delegates business logic to AnnotationManager.
    """

    Signals:
        - annotation_created: Signal(BoundingBox, str)  # box, label
        - annotation_selected: Signal(str)  # annotation_id
        - annotation_moved: Signal(str, BoundingBox)  # annotation_id, new_box

    Attributes:
        - _pixmap: QPixmap  # Current image
        - _current_annotations: list[Annotation]  # Annotations for current image
        - _drawing_mode: str  # 'draw', 'select', 'edit'
        - _temp_box: BoundingBox | None  # Box being drawn
        - _selected_annotation_id: str | None

    Methods:
        # Display
        - set_image(pixmap: QPixmap) -> None
        - set_annotations(annotations: list[Annotation]) -> None
        - clear() -> None

        # Drawing state
        - set_mode(mode: str) -> None  # 'draw', 'select', 'edit'

        # Event handlers
        - paintEvent(event: QPaintEvent) -> None
            # Renders image + all bounding boxes
        - mousePressEvent(event: QMouseEvent) -> None
        - mouseMoveEvent(event: QMouseEvent) -> None
        - mouseReleaseEvent(event: QMouseEvent) -> None

        # Rendering helpers
        - _draw_bounding_box(painter: QPainter, box: BoundingBox, selected: bool) -> None
        - _draw_label(painter: QPainter, box: BoundingBox, label: str) -> None
```

### UI Layer (`ui/annotation_list_widget.py`)

**Purpose**: Display and manage list of annotations.

```python
class AnnotationListWidget(QWidget):
    """
    List widget showing all annotations for current image.
    Allows selection, editing, deletion.
    """

    Signals:
        - annotation_selected: Signal(str)  # annotation_id
        - annotation_deleted: Signal(str)  # annotation_id
        - annotation_edited: Signal(str, str)  # annotation_id, new_label

    Methods:
        - set_annotations(annotations: list[Annotation]) -> None
        - clear() -> None
        - select_annotation(annotation_id: str) -> None
        - _on_delete_clicked() -> None
        - _on_edit_clicked() -> None
```

### UI Layer (`ui/toolbar.py`)

**Purpose**: Tool selection and actions.

```python
class ToolBar(QToolBar):
    """
    Main toolbar with drawing tools and actions.
    """

    Signals:
        - mode_changed: Signal(str)  # 'draw', 'select', 'edit'
        - next_image_requested: Signal()
        - previous_image_requested: Signal()

    Methods:
        - _init_tools() -> None
            # Creates buttons for: Draw, Select, Next, Previous
```

### UI Layer (`ui/dialogs.py`)

**Purpose**: Dialog windows for user input.

```python
class LabelInputDialog(QDialog):
    """Simple dialog to input annotation label."""
    Methods:
        - get_label() -> str | None

class ExportDialog(QDialog):
    """Dialog for export options (format, path)."""
    Methods:
        - get_export_config() -> dict  # {format: 'csv'|'coco', path: str}
```

---

## Implementation Sequence

### Phase 1: Foundation (15 minutes)

**Goal**: Establish data models and business logic skeleton.

#### Step 1.1: Project Setup (3 min)

**Files to create:**
- All directories: `core/`, `data/`, `ui/`, `utils/`
- All `__init__.py` files
- `requirements.txt`

**Requirements.txt content:**
```
PyQt6>=6.4.0
Pillow>=9.5.0
```

#### Step 1.2: Core Models (7 min)

**File**: [core/models.py](core/models.py)

Implement in order:
1. `BoundingBox` class - Simple data class with x, y, width, height
2. `Annotation` class - Uses BoundingBox, adds label and metadata
3. `ImageMetadata` class - Contains list of Annotations

**Key implementation notes:**
- Use `@dataclass` decorator for clean code
- Add `to_dict()` and `from_dict()` for serialization
- Use `uuid.uuid4()` for generating IDs

#### Step 1.3: Core Managers (5 min)

**File**: [core/annotation_manager.py](core/annotation_manager.py)

Implement basic CRUD:
- `create_annotation()` - Generate UUID, store in dict
- `get_annotations_for_image()` - Filter by image_id
- `delete_annotation()` - Remove from dict

**File**: [core/image_manager.py](core/image_manager.py)

Implement basic navigation:
- `add_image()` - Store metadata, maintain order
- `get_current_image()` - Return current
- `next_image()` / `previous_image()` - Navigate with index

**Deliverable**: Foundation layer with data models and business logic skeleton.

---

### Phase 2: Data Layer (10 minutes)

**Goal**: Enable loading and validating image files.

#### Step 2.1: Image Loading (7 min)

**File**: [data/image_loader.py](data/image_loader.py)

Implement:
- `load_image()` - Use PyQt6's QPixmap to load image
- `validate_file()` - Check file exists and has valid extension
- Extract metadata (width, height, format) from loaded image

**Key implementation notes:**
```python
from PyQt6.QtGui import QPixmap, QImageReader

pixmap = QPixmap(file_path)
if pixmap.isNull():
    raise ValueError("Invalid image file")

width = pixmap.width()
height = pixmap.height()
```

#### Step 2.2: Constants (3 min)

**File**: [utils/constants.py](utils/constants.py)

Define:
```python
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png']
DEFAULT_BOX_COLOR = '#00FF00'
SELECTED_BOX_COLOR = '#FF0000'
BOX_LINE_WIDTH = 2
```

**Deliverable**: Can load and validate image files.

---

### Phase 3: Basic UI (20 minutes)

**Goal**: Working UI that can load images, draw rectangles, and assign labels.

#### Step 3.1: Main Window Structure (5 min)

**File**: [ui/main_window.py](ui/main_window.py)

Implement:
- Basic `QMainWindow` setup
- Menu bar with "File" → "Load Images" action
- Status bar
- Initialize business logic managers (AnnotationManager, ImageManager, etc.)

**Layout**:
```python
# Central widget with layout
central_widget = QWidget()
layout = QVBoxLayout()

# Will add canvas and annotation list later
central_widget.setLayout(layout)
self.setCentralWidget(central_widget)
```

#### Step 3.2: Image Canvas - Display Only (7 min)

**File**: [ui/image_canvas.py](ui/image_canvas.py)

Implement (display-only first):
- `set_image()` - Store QPixmap
- `paintEvent()` - Draw image scaled to fit widget
- Basic layout and sizing

**Key implementation notes:**
```python
def paintEvent(self, event):
    painter = QPainter(self)
    if self._pixmap:
        # Scale pixmap to fit widget while maintaining aspect ratio
        scaled = self._pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled)
```

#### Step 3.3: Wire Load Images (3 min)

**In**: [ui/main_window.py](ui/main_window.py)

Implement `load_images()`:
```python
def load_images(self):
    file_paths, _ = QFileDialog.getOpenFileNames(
        self,
        "Select Images",
        "",
        "Images (*.jpg *.jpeg *.png)"
    )

    for path in file_paths:
        pixmap, metadata = self.image_loader.load_image(path)
        image_id = self.image_manager.add_image(path, metadata)

    # Display first image
    current = self.image_manager.get_current_image()
    if current:
        pixmap, _ = self.image_loader.load_image(current.file_path)
        self.canvas.set_image(pixmap)
```

**Test**: Should be able to load and display an image!

#### Step 3.4: Image Canvas - Drawing (5 min)

**In**: [ui/image_canvas.py](ui/image_canvas.py)

Implement mouse events:
```python
def mousePressEvent(self, event):
    if self._drawing_mode == 'draw':
        self._start_point = event.pos()

def mouseMoveEvent(self, event):
    if self._drawing_mode == 'draw' and self._start_point:
        self._temp_box = BoundingBox(
            x=self._start_point.x(),
            y=self._start_point.y(),
            width=event.pos().x() - self._start_point.x(),
            height=event.pos().y() - self._start_point.y()
        )
        self.update()  # Trigger repaint

def mouseReleaseEvent(self, event):
    if self._drawing_mode == 'draw' and self._temp_box:
        self.annotation_created.emit(self._temp_box)
        self._temp_box = None
```

Update `paintEvent()` to draw temporary box and existing annotations.

#### Step 3.5: Label Dialog (3 min)

**File**: [ui/dialogs.py](ui/dialogs.py)

Simple implementation:
```python
class LabelInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Label")

        layout = QVBoxLayout()
        self.input = QLineEdit()
        layout.addWidget(QLabel("Annotation Label:"))
        layout.addWidget(self.input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_label(self):
        return self.input.text() if self.result() else None
```

#### Step 3.6: Wire Annotation Creation (2 min)

**In**: [ui/main_window.py](ui/main_window.py)

Connect canvas signal:
```python
def _connect_signals(self):
    self.canvas.annotation_created.connect(self._on_annotation_created)

def _on_annotation_created(self, box: BoundingBox):
    dialog = LabelInputDialog(self)
    if dialog.exec():
        label = dialog.get_label()
        if label:
            current_image = self.image_manager.get_current_image()
            annotation = self.annotation_manager.create_annotation(
                current_image.id, box, label
            )
            current_image.add_annotation(annotation)
            self.canvas.set_annotations(current_image.annotations)
            self.status_bar.showMessage(f"Created annotation: {label}")
```

#### Step 3.7: Entry Point (2 min)

**File**: [app.py](app.py)

```python
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Image Annotation Tool")
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

**Deliverable**: Can load image, draw rectangles, assign labels!

---

### Phase 4: Navigation & List (10 minutes)

**Goal**: Navigate between images and manage annotations.

#### Step 4.1: Annotation List Widget (5 min)

**File**: [ui/annotation_list_widget.py](ui/annotation_list_widget.py)

```python
class AnnotationListWidget(QWidget):
    annotation_deleted = pyqtSignal(str)  # annotation_id

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self._on_delete_clicked)

        layout.addWidget(QLabel("Annotations:"))
        layout.addWidget(self.list_widget)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)

    def set_annotations(self, annotations):
        self.list_widget.clear()
        for ann in annotations:
            item = QListWidgetItem(f"{ann.label} - {ann.id[:8]}")
            item.setData(Qt.ItemDataRole.UserRole, ann.id)
            self.list_widget.addItem(item)

    def _on_delete_clicked(self):
        current = self.list_widget.currentItem()
        if current:
            annotation_id = current.data(Qt.ItemDataRole.UserRole)
            self.annotation_deleted.emit(annotation_id)
```

#### Step 4.2: Toolbar (3 min)

**File**: [ui/toolbar.py](ui/toolbar.py)

```python
class ToolBar(QToolBar):
    next_image_requested = pyqtSignal()
    previous_image_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.prev_btn = QPushButton("← Previous")
        self.next_btn = QPushButton("Next →")

        self.prev_btn.clicked.connect(self.previous_image_requested.emit)
        self.next_btn.clicked.connect(self.next_image_requested.emit)

        self.addWidget(self.prev_btn)
        self.addWidget(self.next_btn)
```

#### Step 4.3: Wire Navigation in MainWindow (2 min)

**In**: [ui/main_window.py](ui/main_window.py)

Add toolbar and annotation list to layout:
```python
def _init_ui(self):
    # ... existing code ...

    self.toolbar = ToolBar()
    self.addToolBar(self.toolbar)

    self.annotation_list = AnnotationListWidget()

    # Layout: canvas on left, annotation list on right
    main_layout = QHBoxLayout()
    main_layout.addWidget(self.canvas, stretch=3)
    main_layout.addWidget(self.annotation_list, stretch=1)
```

Connect signals:
```python
def _connect_signals(self):
    # ... existing ...
    self.toolbar.next_image_requested.connect(self._on_next_image)
    self.toolbar.previous_image_requested.connect(self._on_previous_image)
    self.annotation_list.annotation_deleted.connect(self._on_annotation_deleted)

def _on_next_image(self):
    next_img = self.image_manager.next_image()
    if next_img:
        self._display_image(next_img)

def _on_previous_image(self):
    prev_img = self.image_manager.previous_image()
    if prev_img:
        self._display_image(prev_img)

def _display_image(self, image_metadata):
    pixmap, _ = self.image_loader.load_image(image_metadata.file_path)
    self.canvas.set_image(pixmap)
    self.canvas.set_annotations(image_metadata.annotations)
    self.annotation_list.set_annotations(image_metadata.annotations)

    idx = self.image_manager.get_current_index()
    total = self.image_manager.get_image_count()
    self.status_bar.showMessage(f"Image {idx+1}/{total}")

def _on_annotation_deleted(self, annotation_id):
    current_image = self.image_manager.get_current_image()
    current_image.remove_annotation(annotation_id)
    self.annotation_manager.delete_annotation(annotation_id)
    self._display_image(current_image)  # Refresh
```

**Deliverable**: Can navigate between images and delete annotations!

---

### Phase 5: Export (5 minutes)

**Goal**: Export annotations to CSV and COCO JSON.

#### Step 5.1: Export Service (10 min)

**File**: [core/export_service.py](core/export_service.py)

Implement CSV export:
```python
import csv
import json
from pathlib import Path

class ExportService:
    def export_to_csv(self, images: list, output_path: str) -> bool:
        try:
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['image_name', 'x', 'y', 'width', 'height', 'label'])

                for image in images:
                    for ann in image.annotations:
                        writer.writerow([
                            image.filename,
                            ann.bounding_box.x,
                            ann.bounding_box.y,
                            ann.bounding_box.width,
                            ann.bounding_box.height,
                            ann.label
                        ])
            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False
```

Implement COCO JSON export:
```python
def export_to_coco(self, images: list, output_path: str) -> bool:
    try:
        # Get unique labels for categories
        labels = self._get_unique_labels(images)
        categories = [
            {"id": idx+1, "name": label}
            for idx, label in enumerate(labels)
        ]
        label_to_id = {label: idx+1 for idx, label in enumerate(labels)}

        # Build COCO structure
        coco_data = {
            "images": [],
            "annotations": [],
            "categories": categories
        }

        annotation_id = 1
        for img_idx, image in enumerate(images, start=1):
            # Add image info
            coco_data["images"].append({
                "id": img_idx,
                "file_name": image.filename,
                "width": image.width,
                "height": image.height
            })

            # Add annotations
            for ann in image.annotations:
                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": img_idx,
                    "category_id": label_to_id[ann.label],
                    "bbox": [
                        ann.bounding_box.x,
                        ann.bounding_box.y,
                        ann.bounding_box.width,
                        ann.bounding_box.height
                    ],
                    "area": ann.bounding_box.width * ann.bounding_box.height,
                    "iscrowd": 0
                })
                annotation_id += 1

        with open(output_path, 'w') as f:
            json.dump(coco_data, f, indent=2)

        return True
    except Exception as e:
        print(f"COCO export error: {e}")
        return False

def _get_unique_labels(self, images: list) -> list:
    labels = set()
    for image in images:
        for ann in image.annotations:
            labels.add(ann.label)
    return sorted(list(labels))
```

#### Step 5.2: Export Dialog (2 min)

**In**: [ui/dialogs.py](ui/dialogs.py)

```python
class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Annotations")

        layout = QVBoxLayout()

        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "COCO JSON"])
        layout.addWidget(QLabel("Export Format:"))
        layout.addWidget(self.format_combo)

        # Path selection
        self.path_input = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
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
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Annotations",
            "",
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        if file_path:
            self.path_input.setText(file_path)

    def get_export_config(self):
        if self.result():
            return {
                'format': self.format_combo.currentText(),
                'path': self.path_input.text()
            }
        return None
```

#### Step 5.3: Wire Export in MainWindow (1 min)

**In**: [ui/main_window.py](ui/main_window.py)

Add menu action:
```python
def _setup_menu_bar(self):
    menubar = self.menuBar()
    file_menu = menubar.addMenu("File")

    load_action = file_menu.addAction("Load Images")
    load_action.triggered.connect(self.load_images)

    export_action = file_menu.addAction("Export Annotations")
    export_action.triggered.connect(self.export_annotations)
```

Implement export:
```python
def export_annotations(self):
    dialog = ExportDialog(self)
    config = dialog.get_export_config()

    if config:
        images = self.image_manager.get_all_images()

        if config['format'] == 'CSV':
            success = self.export_service.export_to_csv(images, config['path'])
        else:  # COCO JSON
            success = self.export_service.export_to_coco(images, config['path'])

        if success:
            self.status_bar.showMessage(f"Exported to {config['path']}")
        else:
            self.status_bar.showMessage("Export failed!")
```

**Deliverable**: FULL MVP - Can annotate images and export to CSV/COCO JSON!

---

## Dependencies

### requirements.txt

```
PyQt6>=6.4.0          # UI framework (GPL with exceptions - free for open source)
Pillow>=9.5.0         # Image loading fallback (MIT-like license)
```

**Installation:**
```bash
pip install -r requirements.txt
```

**License Compatibility**: Both libraries use permissive licenses suitable for open-source and commercial projects.

---

## Future Extensibility

### 1. ML Model Integration (SAM, DINO)

**Integration Point**: [core/annotation_manager.py](core/annotation_manager.py)

```python
class AnnotationManager:
    def suggest_annotations(
        self,
        image_id: str,
        model: str = 'sam'
    ) -> list[Annotation]:
        """
        Generate automatic annotation suggestions using ML models.

        Future implementation steps:
        1. Get image pixel data from ImageManager
        2. Load model (SAM/DINO) - lazy loading to avoid startup cost
        3. Run inference on image
        4. Convert model output (masks/boxes) to Annotation objects
        5. Return suggestions (user can accept/reject in UI)

        Args:
            image_id: ID of image to annotate
            model: 'sam' (Segment Anything) or 'dino' (Detection Transformer)

        Returns:
            List of suggested Annotation objects
        """
        image_metadata = self._get_image_metadata(image_id)

        if model == 'sam':
            return self._suggest_with_sam(image_metadata)
        elif model == 'dino':
            return self._suggest_with_dino(image_metadata)
        else:
            raise ValueError(f"Unknown model: {model}")

    def _suggest_with_sam(self, image_metadata):
        """
        Future: Load SAM model and generate segmentation masks.

        Pseudo-code:
        1. from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
        2. sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h.pth")
        3. mask_generator = SamAutomaticMaskGenerator(sam)
        4. masks = mask_generator.generate(image_array)
        5. Convert masks to BoundingBox objects
        6. Return as Annotation objects with label="auto_detected"
        """
        # Placeholder for future implementation
        return []

    def _suggest_with_dino(self, image_metadata):
        """
        Future: Load DINO model and generate object detections.

        Pseudo-code:
        1. from transformers import DetrImageProcessor, DetrForObjectDetection
        2. processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        3. model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
        4. Run inference
        5. Convert detections to BoundingBox + labels
        6. Return as Annotation objects
        """
        # Placeholder for future implementation
        return []
```

**UI Changes Needed:**

In [ui/toolbar.py](ui/toolbar.py), add:
```python
self.auto_annotate_btn = QPushButton("🤖 Auto-Annotate")
self.auto_annotate_btn.clicked.connect(self.auto_annotate_requested.emit)
```

In [ui/main_window.py](ui/main_window.py), add:
```python
def _on_auto_annotate(self):
    current_image = self.image_manager.get_current_image()

    # Show loading indicator
    self.status_bar.showMessage("Running auto-annotation...")

    # Get suggestions from ML model
    suggestions = self.annotation_manager.suggest_annotations(
        current_image.id,
        model='sam'  # or 'dino'
    )

    # Display suggestions in different color (e.g., orange instead of green)
    self.canvas.set_suggested_annotations(suggestions)

    # User can accept/reject each suggestion
    self.status_bar.showMessage(f"Found {len(suggestions)} suggestions")
```

**No Refactoring Required**: Business logic is already isolated, just add new methods!

---

### 2. Web API Deployment (FastAPI)

**Integration Point**: New `api/` module wraps existing core layer.

**Directory structure:**
```
api/
├── __init__.py
├── main.py              # FastAPI app
├── routes.py            # API endpoints
└── schemas.py           # Pydantic models for API
```

**File**: `api/main.py`

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.annotation_manager import AnnotationManager
from core.image_manager import ImageManager
from core.export_service import ExportService
from core.models import BoundingBox, Annotation
from api.schemas import AnnotationCreate, AnnotationUpdate

# Initialize app and business logic (same as desktop app!)
app = FastAPI(title="Image Annotation API")
annotation_manager = AnnotationManager()
image_manager = ImageManager()
export_service = ExportService()

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints - all reuse existing business logic

@app.post("/api/images")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file."""
    # Save file temporarily
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Use existing ImageLoader (same as desktop!)
    from data.image_loader import ImageLoader
    loader = ImageLoader()
    _, metadata = loader.load_image(file_path)

    # Use existing ImageManager (same as desktop!)
    image_id = image_manager.add_image(file_path, metadata)

    return {"image_id": image_id, "filename": file.filename}

@app.get("/api/images")
async def list_images():
    """Get all loaded images."""
    images = image_manager.get_all_images()
    return [img.to_dict() for img in images]

@app.get("/api/images/{image_id}")
async def get_image(image_id: str):
    """Get specific image metadata."""
    image = image_manager.get_image(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image.to_dict()

@app.post("/api/annotations")
async def create_annotation(data: AnnotationCreate):
    """
    Create a new annotation.
    Uses EXACT SAME business logic as desktop app!
    """
    box = BoundingBox(
        x=data.bbox['x'],
        y=data.bbox['y'],
        width=data.bbox['width'],
        height=data.bbox['height']
    )

    # Same method PyQt app uses!
    annotation = annotation_manager.create_annotation(
        data.image_id,
        box,
        data.label
    )

    return annotation.to_dict()

@app.get("/api/images/{image_id}/annotations")
async def get_annotations(image_id: str):
    """Get all annotations for an image."""
    annotations = annotation_manager.get_annotations_for_image(image_id)
    return [ann.to_dict() for ann in annotations]

@app.put("/api/annotations/{annotation_id}")
async def update_annotation(annotation_id: str, data: AnnotationUpdate):
    """Update an existing annotation."""
    box = None
    if data.bbox:
        box = BoundingBox(**data.bbox)

    success = annotation_manager.update_annotation(
        annotation_id,
        box=box,
        label=data.label
    )

    if not success:
        raise HTTPException(status_code=404, detail="Annotation not found")

    return {"success": True}

@app.delete("/api/annotations/{annotation_id}")
async def delete_annotation(annotation_id: str):
    """Delete an annotation."""
    success = annotation_manager.delete_annotation(annotation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Annotation not found")
    return {"success": True}

@app.post("/api/export")
async def export_annotations(format: str = "csv"):
    """
    Export all annotations.
    Uses EXACT SAME export logic as desktop app!
    """
    images = image_manager.get_all_images()
    output_path = f"/tmp/export.{format}"

    if format == "csv":
        success = export_service.export_to_csv(images, output_path)
    elif format == "coco":
        success = export_service.export_to_coco(images, output_path)
    else:
        raise HTTPException(status_code=400, detail="Invalid format")

    if not success:
        raise HTTPException(status_code=500, detail="Export failed")

    return {"download_url": f"/downloads/{output_path}"}
```

**File**: `api/schemas.py`

```python
from pydantic import BaseModel
from typing import Optional

class AnnotationCreate(BaseModel):
    image_id: str
    bbox: dict  # {x: int, y: int, width: int, height: int}
    label: str

class AnnotationUpdate(BaseModel):
    bbox: Optional[dict] = None
    label: Optional[str] = None
```

**Web Frontend (React example)**:

```javascript
// Web UI calls REST API instead of Python methods directly
// Canvas drawing logic reimplemented in JavaScript

const canvas = document.getElementById('annotation-canvas');
let startPoint = null;

canvas.addEventListener('mousedown', (e) => {
    startPoint = {x: e.offsetX, y: e.offsetY};
});

canvas.addEventListener('mouseup', async (e) => {
    if (!startPoint) return;

    const bbox = {
        x: startPoint.x,
        y: startPoint.y,
        width: e.offsetX - startPoint.x,
        height: e.offsetY - startPoint.y
    };

    const label = prompt("Enter label:");

    // Call API - same business logic as desktop!
    const response = await fetch('/api/annotations', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            image_id: currentImageId,
            bbox: bbox,
            label: label
        })
    });

    const annotation = await response.json();
    drawAnnotation(annotation);  // Render on canvas

    startPoint = null;
});
```

**Key Points:**
- **Zero changes to core layer** - it's already framework-agnostic!
- FastAPI wraps existing business logic with HTTP endpoints
- Web UI implements drawing in JavaScript, calls API for storage
- Same data models (JSON serialization already implemented)
- Desktop and web versions share 100% of business logic code

---

## Code Quality Standards

### PEP 8 Compliance

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 88 characters (Black formatter compatible)
- **Naming conventions**:
  - Classes: `PascalCase`
  - Functions/methods: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

### Type Hints

All function signatures must include type hints:

```python
def create_annotation(
    self,
    image_id: str,
    box: BoundingBox,
    label: str
) -> Annotation:
    """Create a new annotation."""
    pass
```

### Docstrings

All public classes and methods must have docstrings:

```python
class AnnotationManager:
    """
    Central business logic for managing annotations.

    This class is framework-agnostic and can be used with PyQt,
    web APIs, or command-line interfaces.

    Attributes:
        _annotations: Dictionary mapping annotation IDs to Annotation objects
        _validation_enabled: Whether to validate annotations before creation

    Example:
        >>> manager = AnnotationManager()
        >>> box = BoundingBox(x=100, y=200, width=50, height=75)
        >>> ann = manager.create_annotation("img_1", box, "person")
        >>> print(ann.label)
        "person"
    """
```

### Comments

- **Module-level**: Purpose of the module and key design decisions
- **Inline comments**: Only for non-obvious logic
- **TODO comments**: Mark future improvements

```python
# TODO: Add caching to avoid reloading images from disk
# TODO: Implement undo/redo functionality
```

### Error Handling

- **Validate at boundaries**: User input (UI layer), file I/O (data layer)
- **Raise specific exceptions**: `ValueError`, `FileNotFoundError`, etc.
- **Clear error messages**: Help user understand what went wrong

```python
def load_image(self, file_path: str) -> tuple[QPixmap, ImageMetadata]:
    """Load an image file."""
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")

    pixmap = QPixmap(file_path)
    if pixmap.isNull():
        raise ValueError(f"Invalid image file or unsupported format: {file_path}")

    # ... rest of implementation
```

### Logging (Post-MVP)

For future debugging, add Python logging:

```python
import logging

logger = logging.getLogger(__name__)

class AnnotationManager:
    def create_annotation(self, image_id: str, box: BoundingBox, label: str):
        logger.info(f"Creating annotation for image {image_id} with label '{label}'")
        # ... implementation
```

---

## Testing Strategy (Post-MVP)

### Unit Tests

Test business logic in isolation:

```python
# tests/test_annotation_manager.py
import unittest
from core.annotation_manager import AnnotationManager
from core.models import BoundingBox

class TestAnnotationManager(unittest.TestCase):
    def setUp(self):
        self.manager = AnnotationManager()

    def test_create_annotation(self):
        box = BoundingBox(x=10, y=20, width=30, height=40)
        ann = self.manager.create_annotation("img_1", box, "cat")

        self.assertEqual(ann.label, "cat")
        self.assertEqual(ann.bounding_box.x, 10)
        self.assertIsNotNone(ann.id)

    def test_get_annotations_for_image(self):
        box1 = BoundingBox(x=10, y=20, width=30, height=40)
        box2 = BoundingBox(x=50, y=60, width=70, height=80)

        self.manager.create_annotation("img_1", box1, "cat")
        self.manager.create_annotation("img_2", box2, "dog")

        img1_anns = self.manager.get_annotations_for_image("img_1")
        self.assertEqual(len(img1_anns), 1)
        self.assertEqual(img1_anns[0].label, "cat")
```

### Integration Tests

Test full workflows:

```python
# tests/test_export.py
import unittest
import json
from core.export_service import ExportService
from core.models import ImageMetadata, Annotation, BoundingBox

class TestExport(unittest.TestCase):
    def test_coco_export_format(self):
        # Create test data
        img = ImageMetadata(
            id="img_1",
            file_path="/path/to/image.jpg",
            filename="image.jpg",
            width=1920,
            height=1080,
            format="JPEG",
            annotations=[]
        )

        box = BoundingBox(x=100, y=200, width=50, height=75)
        ann = Annotation(
            id="ann_1",
            bounding_box=box,
            label="person",
            image_id="img_1"
        )
        img.add_annotation(ann)

        # Export
        service = ExportService()
        output_path = "/tmp/test_export.json"
        success = service.export_to_coco([img], output_path)

        self.assertTrue(success)

        # Validate COCO format
        with open(output_path) as f:
            data = json.load(f)

        self.assertIn("images", data)
        self.assertIn("annotations", data)
        self.assertIn("categories", data)
        self.assertEqual(len(data["images"]), 1)
        self.assertEqual(len(data["annotations"]), 1)
        self.assertEqual(data["annotations"][0]["bbox"], [100, 200, 50, 75])
```

### Manual Testing Checklist

Before release, verify:

- [ ] Load JPEG image successfully
- [ ] Load PNG image successfully
- [ ] Draw multiple annotations on one image
- [ ] Annotations persist when navigating away and back
- [ ] Edit annotation label
- [ ] Delete annotation
- [ ] Navigate between multiple images (Next/Previous)
- [ ] Export to CSV produces valid format
- [ ] Export to COCO JSON produces valid format
- [ ] Application handles 4K image without freezing
- [ ] Error handling for invalid image files
- [ ] Error handling for file write failures

---

## Summary

This implementation plan provides:

✅ **Clean Architecture**: Three-layer design (UI → Business Logic → Data)
✅ **Framework Independence**: Core logic has zero PyQt dependencies
✅ **Future ML Ready**: Clear integration point for SAM/DINO models
✅ **Future Web Ready**: Business logic can be wrapped with FastAPI
✅ **1-Hour MVP Feasible**: Incremental phases with clear deliverables
✅ **Maintainability**: Well-structured, documented, testable code
✅ **Extensibility**: Easy to add features without refactoring

### Critical Files (Implementation Priority Order)

1. **[core/models.py](core/models.py)** - Foundation data structures
2. **[core/annotation_manager.py](core/annotation_manager.py)** - Core business logic
3. **[ui/image_canvas.py](ui/image_canvas.py)** - User interaction
4. **[ui/main_window.py](ui/main_window.py)** - Integration
5. **[core/export_service.py](core/export_service.py)** - Deliverable feature

### Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Follow implementation sequence Phase 1 → Phase 5
3. Test after each phase to catch issues early
4. Iterate based on user feedback

---

**Questions or clarifications?** Feel free to ask before starting implementation!

---

## Phase 6: Import & Edit COCO Annotations (Post-MVP Enhancement)

**Status**: Not yet implemented
**Estimated Time**: 20-25 minutes
**Goal**: Load existing COCO JSON annotations, render them on canvas, and enable label editing for all annotations.

### Overview

This phase enables users to:
1. Import existing COCO JSON annotation files
2. Match imported annotations to loaded images
3. Render imported annotations on canvas (identical to manually created ones)
4. Edit labels of ANY annotation (both imported and manually created)
5. Continue annotating after import (seamless workflow)

**Important**: Imported annotations behave identically to manually created annotations - they can be selected, deleted, and edited.

### 6.1: Import Service (12 min)

**New File**: `core/import_service.py`

**Purpose**: Framework-agnostic service to load COCO JSON and convert to internal models.

```python
class ImportService:
    """
    Service for importing annotations from COCO JSON format.
    Framework-agnostic - works with any UI.
    """

    Methods:
        # Import from COCO JSON
        - import_from_coco(
            coco_path: str,
            base_image_path: str = None
          ) -> tuple[list[ImageMetadata], dict[str, str]]
            """
            Load COCO JSON and return ImageMetadata objects with annotations.

            Args:
                coco_path: Path to COCO JSON file
                base_image_path: Optional base directory for images
                                (if None, uses COCO file_name as-is)

            Returns:
                Tuple of (list of ImageMetadata, label_map)
                label_map: {label_id: label_name} for updating LabelManager

            Raises:
                FileNotFoundError: If COCO file doesn't exist
                ValueError: If COCO JSON is invalid format
            """

        # Helper methods
        - _validate_coco_format(coco_data: dict) -> bool
            # Validate has required keys: images, annotations, categories

        - _match_images_to_files(
            coco_images: list,
            base_path: str
          ) -> dict[int, str]
            # Match COCO image IDs to actual file paths
            # Returns: {coco_image_id: resolved_file_path}

        - _build_label_map(categories: list) -> dict[int, str]
            # Extract {label_id: label_name} from COCO categories

        - _convert_annotations(
            coco_annotations: list,
            label_map: dict
          ) -> dict[int, list[Annotation]]
            # Convert COCO annotations to internal Annotation objects
            # Returns: {coco_image_id: [Annotation, ...]}
```

**Implementation Details:**

```python
import json
from pathlib import Path
from datetime import datetime
from core.models import ImageMetadata, Annotation, BoundingBox

class ImportService:
    def import_from_coco(
        self,
        coco_path: str,
        base_image_path: str = None
    ) -> tuple[list[ImageMetadata], dict[str, str]]:
        """Import annotations from COCO JSON format."""

        # Load COCO JSON
        coco_path = Path(coco_path)
        if not coco_path.exists():
            raise FileNotFoundError(f"COCO file not found: {coco_path}")

        with open(coco_path, 'r') as f:
            coco_data = json.load(f)

        # Validate format
        if not self._validate_coco_format(coco_data):
            raise ValueError("Invalid COCO JSON format")

        # Extract categories (labels)
        label_map = self._build_label_map(coco_data['categories'])

        # Match COCO images to file paths
        image_path_map = self._match_images_to_files(
            coco_data['images'],
            base_image_path or str(coco_path.parent)
        )

        # Convert annotations
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
                print(f"Warning: Could not find file for image ID {coco_img_id}")
                continue

            # Create ImageMetadata
            metadata = ImageMetadata(
                id=str(uuid.uuid4()),  # Generate new internal ID
                file_path=file_path,
                filename=coco_img['file_name'],
                width=coco_img['width'],
                height=coco_img['height'],
                format=Path(coco_img['file_name']).suffix.upper().lstrip('.'),
                annotations=annotations_by_image.get(coco_img_id, [])
            )

            image_metadata_list.append(metadata)

        return image_metadata_list, label_map

    def _validate_coco_format(self, coco_data: dict) -> bool:
        """Validate COCO JSON has required structure."""
        required_keys = ['images', 'annotations', 'categories']
        return all(key in coco_data for key in required_keys)

    def _match_images_to_files(
        self,
        coco_images: list,
        base_path: str
    ) -> dict[int, str]:
        """
        Match COCO image entries to actual file paths.

        Tries multiple strategies:
        1. Exact filename match in base_path
        2. Recursive search in base_path subdirectories
        3. Use file_name as relative path from base_path
        """
        base_path = Path(base_path)
        image_map = {}

        for img in coco_images:
            img_id = img['id']
            filename = img['file_name']

            # Strategy 1: Direct path (filename may include subdirs)
            candidate = base_path / filename
            if candidate.exists():
                image_map[img_id] = str(candidate.absolute())
                continue

            # Strategy 2: Search for filename only (ignore subdirs in file_name)
            basename = Path(filename).name
            candidate = base_path / basename
            if candidate.exists():
                image_map[img_id] = str(candidate.absolute())
                continue

            # Strategy 3: Recursive search
            matches = list(base_path.rglob(basename))
            if matches:
                image_map[img_id] = str(matches[0].absolute())
                continue

            print(f"Warning: Could not find image file: {filename}")

        return image_map

    def _build_label_map(self, categories: list) -> dict[int, str]:
        """Extract label mapping from COCO categories."""
        return {cat['id']: cat['name'] for cat in categories}

    def _convert_annotations(
        self,
        coco_annotations: list,
        label_map: dict
    ) -> dict[int, list[Annotation]]:
        """Convert COCO annotations to internal format."""
        annotations_by_image = {}

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
```

### 6.2: Edit Label Functionality (5 min)

**Modify**: `core/annotation_manager.py`

Add method to update annotation label:

```python
class AnnotationManager:
    # ... existing methods ...

    def update_annotation_label(
        self,
        annotation_id: str,
        new_label_id: int,
        new_label_name: str
    ) -> bool:
        """
        Update the label of an existing annotation.

        Args:
            annotation_id: ID of annotation to update
            new_label_id: New integer label ID
            new_label_name: New label name

        Returns:
            True if successful, False if annotation not found
        """
        annotation = self._annotations.get(annotation_id)
        if not annotation:
            return False

        annotation.label_id = new_label_id
        annotation.label_name = new_label_name
        annotation.modified_at = datetime.now()

        return True
```

### 6.3: Edit Label Dialog (3 min)

**Modify**: `ui/dialogs.py`

Add new dialog for editing labels:

```python
class EditLabelDialog(QDialog):
    """
    Dialog for editing an annotation's label.
    Shows dropdown of available labels from LabelManager.
    """

    def __init__(self, current_label_id: int, label_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Label")
        self.label_manager = label_manager

        layout = QVBoxLayout()

        # Label dropdown
        self.label_combo = QComboBox()
        labels = label_manager.get_all_labels()  # {id: name}
        for label_id, label_name in sorted(labels.items()):
            self.label_combo.addItem(f"{label_id}: {label_name}", label_id)

        # Set current label as selected
        for i in range(self.label_combo.count()):
            if self.label_combo.itemData(i) == current_label_id:
                self.label_combo.setCurrentIndex(i)
                break

        layout.addWidget(QLabel("Select new label:"))
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

    def get_selected_label(self) -> tuple[int, str] | None:
        """Return (label_id, label_name) if OK clicked, None otherwise."""
        if self.result():
            label_id = self.label_combo.currentData()
            label_name = self.label_combo.currentText().split(': ', 1)[1]
            return (label_id, label_name)
        return None
```

### 6.4: UI Integration - Import (4 min)

**Modify**: `ui/main_window.py`

Add import functionality:

```python
class MainWindow(QMainWindow):
    def __init__(self):
        # ... existing initialization ...
        self.import_service = ImportService()  # Add import service

    def _setup_menu_bar(self):
        # ... existing menu setup ...

        # Add Import action after Load Images
        import_action = file_menu.addAction("Import COCO Annotations")
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_annotations)

    def import_annotations(self) -> None:
        """
        Import annotations from COCO JSON file.
        Merges with existing images or loads new ones.
        """
        # Select COCO JSON file
        coco_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select COCO JSON File",
            "",
            "JSON Files (*.json)"
        )

        if not coco_path:
            return

        # Ask for base image directory (optional)
        reply = QMessageBox.question(
            self,
            "Base Image Directory",
            "Do you want to specify a base directory for images?\n"
            "(If No, will use COCO JSON directory)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        base_path = None
        if reply == QMessageBox.StandardButton.Yes:
            base_path = QFileDialog.getExistingDirectory(
                self,
                "Select Base Image Directory"
            )

        try:
            # Import annotations
            self.status_bar.showMessage("Importing annotations...")

            imported_images, label_map = self.import_service.import_from_coco(
                coco_path,
                base_path
            )

            # Update LabelManager with imported labels
            existing_labels = self.label_manager.get_all_labels()
            for label_id, label_name in label_map.items():
                if label_id not in existing_labels:
                    self.label_manager.add_label(label_id, label_name)

            # Add imported images to ImageManager
            loaded_count = 0
            for img_metadata in imported_images:
                # Add to image manager
                self.image_manager.add_image(img_metadata.file_path, img_metadata)

                # Register annotations with AnnotationManager
                for annotation in img_metadata.annotations:
                    annotation.image_id = img_metadata.id
                    self.annotation_manager._annotations[annotation.id] = annotation

                loaded_count += 1

            # Display first imported image
            if loaded_count > 0:
                self._display_current_image()

                total_annotations = sum(
                    len(img.annotations) for img in imported_images
                )

                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Imported {loaded_count} images with "
                    f"{total_annotations} annotations."
                )

                self.status_bar.showMessage(
                    f"Imported {loaded_count} images, {total_annotations} annotations"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import annotations:\n{str(e)}"
            )
            self.status_bar.showMessage("Import failed")
```

### 6.5: UI Integration - Edit Label (2 min)

**Modify**: `ui/main_window.py`

Wire up the "Edit Label" button:

```python
class MainWindow(QMainWindow):
    def _connect_signals(self):
        # ... existing signals ...

        # Connect Edit Label button from annotation list
        if self.annotation_list:
            self.annotation_list.annotation_edit_requested.connect(
                self._on_edit_label_requested
            )

    def _on_edit_label_requested(self, annotation_id: str) -> None:
        """
        Handle edit label request from annotation list.
        Shows dialog to select new label.
        """
        # Get current annotation
        annotation = self.annotation_manager.get_annotation(annotation_id)
        if not annotation:
            return

        # Show edit dialog
        dialog = EditLabelDialog(
            annotation.label_id,
            self.label_manager,
            self
        )

        if dialog.exec():
            result = dialog.get_selected_label()
            if result:
                new_label_id, new_label_name = result

                # Update annotation
                success = self.annotation_manager.update_annotation_label(
                    annotation_id,
                    new_label_id,
                    new_label_name
                )

                if success:
                    # Refresh display
                    current_image = self.image_manager.get_current_image()
                    if current_image:
                        self.canvas.set_annotations(current_image.annotations)
                        self.annotation_list.set_annotations(current_image.annotations)

                    self.status_bar.showMessage(
                        f"Updated label to: {new_label_name}"
                    )
```

### 6.6: Export Behavior Update (1 min)

**Modify**: `ui/main_window.py`

Update export to prevent accidental overwrites:

```python
def export_annotations(self) -> None:
    """Export annotations to file."""
    # ... existing validation code ...

    # Show file save dialog
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Export Annotations",
        f"annotations{default_ext}",
        file_filter,
        options=QFileDialog.Option.DontConfirmOverwrite  # We'll confirm manually
    )

    if not file_path:
        return

    # Check if file exists and warn
    if Path(file_path).exists():
        reply = QMessageBox.question(
            self,
            "File Exists",
            f"File already exists:\n{file_path}\n\n"
            "Do you want to overwrite it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Default to No
        )

        if reply == QMessageBox.StandardButton.No:
            return

    # ... continue with export ...
```

### Phase 6 Deliverables

✅ **Import from COCO JSON**: Load existing annotations with image matching
✅ **Render imported annotations**: Display identically to manual annotations
✅ **Edit any annotation label**: Works for both imported and manual annotations
✅ **Label compatibility**: Merge imported labels with existing label set
✅ **Export protection**: Warn before overwriting existing files

---

## Phase 7: Subdirectory Support (Post-MVP Enhancement)

**Status**: Not yet implemented
**Estimated Time**: 15-20 minutes
**Goal**: Support loading images from multiple subdirectories and preserve relative paths in COCO JSON.

### Overview

This phase enables users to:
1. Load images from multiple subdirectories under a base directory
2. Specify base path + list of relative subdirectory paths
3. Export COCO JSON with relative paths (e.g., `"train/images/cat.jpg"`)
4. Import COCO JSON and resolve images using base + relative paths
5. Maintain backward compatibility (optional feature)

**Use Case**:
```
dataset/
├── train/
│   └── images/
│       ├── cat1.jpg
│       ├── cat2.jpg
├── val/
│   └── images/
│       ├── dog1.jpg
│       ├── dog2.jpg
└── annotations.json  # Contains relative paths like "train/images/cat1.jpg"
```

### 7.1: Subdirectory Configuration Model (3 min)

**New File**: `core/models.py` (add new classes)

```python
@dataclass
class SubdirectoryConfig:
    """
    Configuration for loading images from subdirectories.
    """
    base_path: str
    subdirectories: list[str]  # Relative paths from base

    def __post_init__(self):
        """Validate paths exist."""
        base = Path(self.base_path)
        if not base.exists():
            raise ValueError(f"Base path does not exist: {self.base_path}")

        for subdir in self.subdirectories:
            full_path = base / subdir
            if not full_path.exists():
                raise ValueError(f"Subdirectory does not exist: {full_path}")

    def get_full_path(self, relative_path: str) -> str:
        """Convert relative path to absolute path."""
        return str(Path(self.base_path) / relative_path)

    def get_relative_path(self, absolute_path: str) -> str:
        """Convert absolute path to relative path (from base)."""
        abs_path = Path(absolute_path)
        base = Path(self.base_path)
        try:
            return str(abs_path.relative_to(base))
        except ValueError:
            # Path is not relative to base, return filename only
            return abs_path.name
```

### 7.2: Enhanced Image Loading (5 min)

**Modify**: `ui/dialogs.py`

Add new dialog for subdirectory loading:

```python
class SubdirectoryLoadDialog(QDialog):
    """
    Dialog for loading images from subdirectories.
    Allows user to specify base path and subdirectory list.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Images from Subdirectories")
        self.resize(500, 400)

        layout = QVBoxLayout()

        # Base path selection
        base_layout = QHBoxLayout()
        self.base_path_input = QLineEdit()
        base_browse_btn = QPushButton("Browse...")
        base_browse_btn.clicked.connect(self._browse_base_path)
        base_layout.addWidget(QLabel("Base Directory:"))
        base_layout.addWidget(self.base_path_input)
        base_layout.addWidget(base_browse_btn)
        layout.addLayout(base_layout)

        # Subdirectory list
        layout.addWidget(QLabel("Subdirectories (relative to base):"))

        # List widget + add/remove buttons
        list_layout = QHBoxLayout()
        self.subdir_list = QListWidget()
        list_layout.addWidget(self.subdir_list)

        button_layout = QVBoxLayout()
        add_btn = QPushButton("Add...")
        remove_btn = QPushButton("Remove")
        add_btn.clicked.connect(self._add_subdirectory)
        remove_btn.clicked.connect(self._remove_subdirectory)
        button_layout.addWidget(add_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addStretch()
        list_layout.addLayout(button_layout)

        layout.addLayout(list_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def _browse_base_path(self):
        """Browse for base directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Base Directory"
        )
        if path:
            self.base_path_input.setText(path)

    def _add_subdirectory(self):
        """Add subdirectory to list."""
        base_path = self.base_path_input.text()
        if not base_path:
            QMessageBox.warning(
                self,
                "No Base Path",
                "Please select a base directory first."
            )
            return

        subdir = QFileDialog.getExistingDirectory(
            self,
            "Select Subdirectory",
            base_path
        )

        if subdir:
            # Make path relative to base
            try:
                relative = Path(subdir).relative_to(Path(base_path))
                self.subdir_list.addItem(str(relative))
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Selection",
                    "Subdirectory must be under the base directory."
                )

    def _remove_subdirectory(self):
        """Remove selected subdirectory from list."""
        current = self.subdir_list.currentRow()
        if current >= 0:
            self.subdir_list.takeItem(current)

    def get_config(self) -> SubdirectoryConfig | None:
        """Return SubdirectoryConfig if OK clicked."""
        if self.result():
            base_path = self.base_path_input.text()
            subdirs = [
                self.subdir_list.item(i).text()
                for i in range(self.subdir_list.count())
            ]

            if not base_path or not subdirs:
                return None

            try:
                return SubdirectoryConfig(base_path, subdirs)
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Configuration", str(e))
                return None

        return None
```

### 7.3: Enhanced Image Manager (3 min)

**Modify**: `core/image_manager.py`

Add support for relative paths:

```python
class ImageManager:
    def __init__(self):
        # ... existing attributes ...
        self._base_path: str | None = None  # Optional base path for relative paths

    def set_base_path(self, base_path: str) -> None:
        """Set base path for relative path resolution."""
        self._base_path = base_path

    def get_base_path(self) -> str | None:
        """Get current base path."""
        return self._base_path

    def load_from_subdirectories(
        self,
        config: SubdirectoryConfig,
        image_loader
    ) -> int:
        """
        Load all images from specified subdirectories.

        Args:
            config: SubdirectoryConfig with base path and subdirs
            image_loader: ImageLoader instance

        Returns:
            Number of images loaded
        """
        self._base_path = config.base_path
        loaded_count = 0

        for subdir in config.subdirectories:
            full_path = Path(config.base_path) / subdir

            # Find all images in this subdirectory
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
            for ext in image_extensions:
                for img_path in full_path.glob(f'*{ext}'):
                    try:
                        pixmap, metadata = image_loader.load_image(str(img_path))

                        # Store relative path in filename for COCO export
                        relative_path = img_path.relative_to(config.base_path)
                        metadata.filename = str(relative_path)

                        self.add_image(str(img_path), metadata)
                        loaded_count += 1
                    except Exception as e:
                        print(f"Error loading {img_path}: {e}")

        return loaded_count
```

### 7.4: Enhanced Export Service (3 min)

**Modify**: `core/export_service.py`

Update COCO export to use relative paths:

```python
class ExportService:
    def export_to_coco(
        self,
        images: list[ImageMetadata],
        output_path: str,
        use_relative_paths: bool = True
    ) -> None:
        """
        Export annotations to COCO JSON format.

        Args:
            images: List of ImageMetadata objects
            output_path: Output JSON file path
            use_relative_paths: If True, use relative paths in file_name
                               (requires images to have relative paths in filename)
        """
        # ... existing validation ...

        for image_idx, image in enumerate(images, start=1):
            # Use filename field (may contain relative path like "train/images/cat.jpg")
            file_name = image.filename if use_relative_paths else Path(image.file_path).name

            coco_data["images"].append({
                "id": image_idx,
                "file_name": file_name,  # May be relative path
                "width": image.width,
                "height": image.height,
                "date_captured": "",
                "license": 0,
                "coco_url": "",
                "flickr_url": ""
            })

            # ... rest of annotation export ...
```

### 7.5: Enhanced Import Service (3 min)

**Modify**: `core/import_service.py`

Update import to handle relative paths with base path:

```python
class ImportService:
    def import_from_coco(
        self,
        coco_path: str,
        base_image_path: str = None
    ) -> tuple[list[ImageMetadata], dict[str, str]]:
        """
        Import annotations from COCO JSON format.

        Args:
            coco_path: Path to COCO JSON file
            base_image_path: Base directory for resolving relative image paths
                            If None, uses COCO JSON directory as base

        Returns:
            Tuple of (list of ImageMetadata, label_map)
        """
        # ... existing code ...

        # Use base_image_path if provided, otherwise use COCO file directory
        base_path = base_image_path or str(coco_path.parent)

        # _match_images_to_files already handles relative paths correctly
        image_path_map = self._match_images_to_files(
            coco_data['images'],
            base_path
        )

        # ... rest of import logic ...
```

### 7.6: UI Integration (3 min)

**Modify**: `ui/main_window.py`

Add menu option for subdirectory loading:

```python
class MainWindow(QMainWindow):
    def _setup_menu_bar(self):
        # ... existing menu setup ...

        # Add subdirectory loading option
        load_subdirs_action = file_menu.addAction("Load from Subdirectories...")
        load_subdirs_action.setShortcut("Ctrl+Shift+O")
        load_subdirs_action.triggered.connect(self.load_from_subdirectories)

    def load_from_subdirectories(self) -> None:
        """Load images from multiple subdirectories."""
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
        config = dialog.get_config()

        if not config:
            return

        try:
            # Load images from subdirectories
            self.status_bar.showMessage("Loading images from subdirectories...")

            loaded_count = self.image_manager.load_from_subdirectories(
                config,
                self.image_loader
            )

            if loaded_count > 0:
                self._display_current_image()
                QMessageBox.information(
                    self,
                    "Load Successful",
                    f"Loaded {loaded_count} images from subdirectories."
                )
                self.status_bar.showMessage(
                    f"Loaded {loaded_count} images"
                )
            else:
                QMessageBox.warning(
                    self,
                    "No Images",
                    "No images found in specified subdirectories."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Failed to load images:\n{str(e)}"
            )
```

### Phase 7 Deliverables

✅ **Subdirectory loading**: Load images from multiple subdirs under base path
✅ **Relative path preservation**: Store relative paths in COCO JSON export
✅ **Import with base path**: Resolve relative paths when importing COCO JSON
✅ **Backward compatibility**: Optional feature, doesn't break existing workflow
✅ **Flexible path resolution**: Handles various directory structures

---

## Updated Keyboard Shortcuts

After Phase 6 and 7:

| Action | Shortcut |
|--------|----------|
| **Load Images** | `Ctrl+O` |
| **Load from Subdirectories** | `Ctrl+Shift+O` |
| **Define Labels** | `Ctrl+L` |
| **Import COCO Annotations** | `Ctrl+I` |
| **Export Annotations** | `Ctrl+E` |
| **Exit Application** | `Ctrl+Q` |
| **Next Image** | `Right Arrow` or `Down Arrow` |
| **Previous Image** | `Left Arrow` or `Up Arrow` |
| **Delete Selected Annotation** | `Delete` |
| **Switch to Draw Mode** | `D` |
| **Switch to Select Mode** | `S` |

---

## Summary of Post-MVP Enhancements

**Phase 6 - Import & Edit**:
- Import existing COCO JSON annotations
- Match annotations to images intelligently
- Edit labels for any annotation (imported or manual)
- Seamless workflow integration

**Phase 7 - Subdirectory Support**:
- Load images from multiple subdirectories
- Preserve relative paths in COCO JSON
- Flexible path resolution on import
- Maintains backward compatibility

Both phases maintain the clean three-layer architecture and add zero dependencies to the core business logic layer.