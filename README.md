# Image Annotation Tool

A PyQt6-based desktop application for manual image annotation with clean architecture designed for extensibility.

## Features

### Core Functionality
- **Manual Annotation**: Draw rectangular bounding boxes with two-corner selection
- **Predefined Label Sets**: Define integer ID and name pairs before annotation
- **Quick Labeling**: Select labels from dropdown during annotation
- **Multi-Image Support**: Load and navigate between multiple images
- **Visual Annotation List**: See all annotations for current image in side panel
- **Interactive Selection**: Click annotations in list or on canvas to select

### Navigation & Controls
- **Navigation Toolbar**: Previous/Next buttons with image counter
- **Keyboard Shortcuts**: Arrow keys, Delete, mode toggles (D/S)
- **Mode Switching**: Toggle between Draw and Select modes
- **Bidirectional Sync**: Canvas and list selections stay synchronized

### Import & Export
- **Import COCO JSON**: Load existing annotations from COCO format with flexible image matching
- **Export to CSV**: Simple tabular format with label IDs and names
- **Export to COCO JSON**: Industry-standard format for ML training
- **Overwrite Protection**: Confirmation dialog before overwriting existing export files

### Annotation Management
- **Edit Labels**: Change label of existing annotations via dropdown
- **Smart Import**: Three-strategy image matching (direct path, basename, recursive search)
- **Label Merging**: Imported labels integrate seamlessly with existing label sets

## Architecture

Three-layer design for maintainability and future extensibility:

```
UI Layer (PyQt6) → Business Logic Layer → Data Layer
```

- **UI Independence**: Business logic has zero PyQt dependencies
- **Future Ready**: Designed for ML model integration (SAM/DINO)
- **Web Ready**: Business logic can be wrapped with REST API (FastAPI)

## Installation

### Requirements

- Python 3.10+
- PyQt6
- Pillow

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd image_annotate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
python app.py
```

---

## Usage Guide

### First-Time Setup

When you launch the application for the first time, you'll see a **Label Setup Dialog**:

1. **Define Your Label Set**:
   - Enter an integer ID (e.g., `1`, `2`, `3`)
   - Enter a label name (e.g., `cat`, `dog`, `person`)
   - Click **Add Label**
   - Repeat for all your classes
   - Click **OK** when done

   > **Note**: You can modify labels anytime via **File → Define Labels**

### Loading Images

**Option 1: Load Individual Images**

1. Click **File → Load Images** (or press `Ctrl+O`)
2. Select one or more image files (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`)
3. The first image will display automatically

**Option 2: Load from Subdirectories**

For datasets organized into subdirectories (e.g., train/val splits):

1. Click **File → Load from Subdirectories** (or press `Ctrl+Shift+O`)
2. Select a base directory
3. Add subdirectories (e.g., `train/images`, `val/images`)
4. All images from selected subdirectories will load with relative paths preserved

**Option 3: Import COCO Annotations**

Load existing annotations from COCO JSON format:

1. Click **File → Import COCO Annotations** (or press `Ctrl+I`)
2. Select a COCO JSON file
3. Optionally specify a base directory for images (or use JSON file directory)
4. Images and annotations load automatically with smart path matching
5. Labels from COCO file merge with your existing labels

### Annotating Images

#### Drawing Bounding Boxes

**Method 1: Mouse (Draw Mode - Default)**
1. Click and hold at one corner of the object
2. Drag to the opposite corner
3. Release mouse button
4. A yellow dashed preview shows while dragging
5. Select label from the dropdown dialog
6. Click **OK**

The annotation appears as a green box with the label name.

**Method 2: Keyboard Shortcuts**
- Press `D` to enter Draw mode
- Press `S` to enter Select mode

#### Managing Annotations

**Select an Annotation**:
- **On Canvas**: Click directly on the bounding box (turns red when selected)
- **In List**: Click the annotation in the right panel

**Delete an Annotation**:
- Select the annotation, then:
  - Press `Delete` key, OR
  - Click the **Delete** button in the annotation list

**Edit Label**:
- Select annotation in the list
- Click **Edit Label** button
- Choose new label from dropdown
- Click **OK** to update

### Navigation

**Navigate Between Images**:
- Click **Previous** (`←`) or **Next** (`→`) buttons in toolbar
- Use arrow keys: `Left`/`Up` (previous) or `Right`/`Down` (next)
- Image counter shows current position: **"Image 2/5"**

### Exporting Annotations

1. Click **File → Export Annotations** (or press `Ctrl+E`)
2. Choose export format:
   - **CSV**: Simple tabular format
   - **COCO JSON**: Industry-standard format for ML training
3. Select output file path
4. If file exists, confirm whether to overwrite (defaults to No)
5. Click **OK**

**Tip**: When using subdirectory loading, COCO JSON exports preserve relative paths for portability

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| **Load Images** | `Ctrl+O` |
| **Load from Subdirectories** | `Ctrl+Shift+O` |
| **Import COCO Annotations** | `Ctrl+I` |
| **Define Labels** | `Ctrl+L` |
| **Export Annotations** | `Ctrl+E` |
| **Exit Application** | `Ctrl+Q` |
| **Next Image** | `Right Arrow` or `Down Arrow` |
| **Previous Image** | `Left Arrow` or `Up Arrow` |
| **Delete Selected Annotation** | `Delete` |
| **Switch to Draw Mode** | `D` |
| **Switch to Select Mode** | `S` |

---

## Complete Workflow Example

### Scenario: Annotating a Pet Photo Dataset

1. **Launch Application**
   ```bash
   python app.py
   ```

2. **Define Labels**
   - Label 1: `cat`
   - Label 2: `dog`
   - Label 3: `bird`

3. **Load Images**
   - File → Load Images
   - Select all pet photos from your folder
   - First image displays

4. **Annotate First Image**
   - Draw box around the cat
   - Select "1: cat" from dropdown
   - Annotation appears in green with "cat" label

5. **Navigate and Annotate**
   - Click **Next** button (or press `→`)
   - Draw box around the dog
   - Select "2: dog"
   - Continue through all images

6. **Review Annotations**
   - Use Previous/Next to review
   - Click annotations in the list to highlight them
   - Delete any mistakes with Delete button

7. **Export Dataset**
   - File → Export Annotations
   - Choose **COCO JSON** for ML training
   - Save as `annotations.json`

8. **Done!** Your dataset is ready for model training.

---

## UI Overview

```
┌─────────────────────────────────────────────────────────┐
│ File                                         [Menu Bar] │
├─────────────────────────────────────────────────────────┤
│ [← Prev]  Image 2/5  [Next →]  [Draw] [Select] [Toolbar]│
├──────────────────────────────┬──────────────────────────┤
│                              │ Annotations (3)          │
│                              ├──────────────────────────┤
│                              │ ☑ 1: cat - abc12345      │
│      Image Canvas            │ ☐ 2: dog - def67890      │
│   (Draw/View Annotations)    │ ☐ 1: cat - ghi11121      │
│                              ├──────────────────────────┤
│                              │ [Edit Label] [Delete]    │
│                              │                          │
│                              │  Annotation List Panel   │
├──────────────────────────────┴──────────────────────────┤
│ Status: Image 2/5: dog.jpg (3 annotations)              │
└─────────────────────────────────────────────────────────┘
```

**Components**:
- **Menu Bar**: File operations (Load, Export, Define Labels, Exit)
- **Toolbar**: Navigation buttons and mode toggles
- **Image Canvas**: Main area for viewing and annotating images
- **Annotation List**: Shows all annotations for current image
- **Status Bar**: Displays current image info and feedback

## Project Structure

```
image-annotation-app/
├── core/                        # Business logic (framework-agnostic)
│   ├── models.py               # Data models (BoundingBox, Annotation, ImageMetadata, SubdirectoryConfig)
│   ├── annotation_manager.py  # Annotation CRUD operations (with label editing)
│   ├── image_manager.py        # Image collection & navigation (with subdirectory support)
│   ├── label_manager.py        # Label set management
│   ├── import_service.py       # Import from COCO JSON (with smart path matching)
│   └── export_service.py       # Export to CSV/COCO (with relative path support)
├── data/                        # Data layer (I/O and persistence)
│   ├── image_loader.py         # Image file loading
│   └── annotation_storage.py   # Annotation persistence
├── ui/                          # Presentation layer (PyQt6)
│   ├── main_window.py          # Main application window
│   ├── image_canvas.py         # Interactive canvas for drawing
│   ├── annotation_list_widget.py  # Annotation list panel
│   ├── toolbar.py              # Navigation toolbar
│   └── dialogs.py              # Label setup, selection, export, subdirectory, edit label dialogs
├── utils/                       # Shared utilities
│   └── constants.py            # App-wide constants
├── app.py                       # Application entry point
└── requirements.txt             # Python dependencies
```

## Export Formats

### CSV Format

```csv
image_name,x,y,width,height,label_id,label_name
cat1.jpg,100,150,100,100,1,cat
dog1.jpg,200,200,150,150,2,dog
```

### COCO JSON Format

Standard COCO format with categories, images, and annotations.

**With Subdirectory Support (Phase 7)**:
When loading images from subdirectories, the exported COCO JSON preserves relative paths:

```json
{
  "images": [
    {"id": 1, "file_name": "train/images/cat1.jpg", "width": 640, "height": 480},
    {"id": 2, "file_name": "val/images/dog1.jpg", "width": 640, "height": 480}
  ],
  "annotations": [...],
  "categories": [...]
}
```

This makes the COCO JSON portable across different systems.

## Future Extensions

### ML Model Integration

The architecture supports integration with:
- **SAM (Segment Anything Model)**: Auto-segmentation
- **DINO**: Object detection

Integration point: `core/annotation_manager.py::suggest_annotations()`

### Web Deployment

Business logic can be wrapped with FastAPI to create a REST API, allowing:
- Web-based UI (React/Vue)
- Multi-user collaboration
- Cloud deployment

No changes to core business logic required.

## Development Status

**Current**: Phase 6 & 7 Complete - Full-Featured Annotation Tool! 🎉

### Completed Phases

- ✅ **Phase 1-2**: Core Architecture
  - Data models (BoundingBox, Annotation, ImageMetadata)
  - Business logic layer (AnnotationManager, ImageManager, LabelManager)
  - Data layer (ImageLoader, AnnotationStorage)
  - Framework-agnostic design

- ✅ **Phase 3**: Basic UI
  - Application entry point
  - Interactive image canvas with drawing
  - Label setup and selection dialogs
  - Main window orchestration
  - Keyboard shortcuts

- ✅ **Phase 4**: Navigation & Management
  - Annotation list widget with selection/deletion
  - Navigation toolbar with Previous/Next buttons
  - Image counter display
  - Draw/Select mode toggles
  - Bidirectional sync (canvas ↔ list)

- ✅ **Phase 5**: Export Functionality
  - CSV export implementation
  - COCO JSON export implementation
  - Export statistics and validation
  - Integration with export dialog

- ✅ **Phase 6**: Import & Edit
  - ImportService with three-strategy image matching
  - Import from COCO JSON format with label merging
  - EditLabelDialog for changing annotation labels
  - update_annotation_label() method in AnnotationManager
  - Overwrite protection for exports (defaults to No)
  - Full integration with existing annotation workflow

- ✅ **Phase 7**: Subdirectory Support
  - SubdirectoryConfig model for base + relative paths
  - SubdirectoryLoadDialog for directory selection
  - Enhanced ImageManager with subdirectory loading
  - Relative path preservation in COCO export
  - Support for datasets organized in train/val/test splits
  - Portable COCO JSON files with relative paths

### Future Enhancements

- ⏳ **ML Model Integration**: Auto-annotation suggestions
  - SAM (Segment Anything Model) integration
  - DINO object detection integration
  - Integration point: `core/annotation_manager.py::suggest_annotations()`

- ⏳ **Web Deployment**: REST API wrapper
  - FastAPI backend with core business logic
  - Web-based UI (React/Vue)
  - Multi-user collaboration
  - Cloud deployment

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed design and implementation guide.

## License

MIT

## Contributing

Contributions welcome! Please ensure code follows PEP 8 standards and includes appropriate docstrings.
