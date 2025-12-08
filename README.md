# Image Annotation Tool

A PyQt6-based desktop application for manual image annotation with clean architecture designed for extensibility.

## Features

- **Manual Annotation**: Draw rectangular bounding boxes on images
- **Predefined Label Sets**: Define integer ID and name pairs before annotation
- **Quick Labeling**: Select labels from dropdown during annotation
- **Multi-Image Support**: Navigate between multiple images
- **Export Formats**:
  - CSV (with label IDs and names)
  - COCO JSON (industry-standard format)

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

```bash
python app.py
```

### Workflow

1. **Define Labels**: On startup, define your label set (e.g., 1: cat, 2: dog, 3: person)
2. **Load Images**: File → Load Images
3. **Annotate**:
   - Draw rectangle with mouse
   - Select label from dropdown
4. **Navigate**: Use Previous/Next buttons to move between images
5. **Export**: File → Export Annotations (choose CSV or COCO JSON)

## Project Structure

```
image_annotate/
├── core/                   # Business logic (framework-agnostic)
│   ├── models.py          # Data models (BoundingBox, Annotation, ImageMetadata)
│   ├── annotation_manager.py
│   ├── image_manager.py
│   ├── label_manager.py
│   └── export_service.py
├── data/                   # Data layer (I/O and persistence)
│   ├── image_loader.py
│   └── annotation_storage.py
├── ui/                     # Presentation layer (PyQt6)
│   ├── main_window.py
│   ├── image_canvas.py
│   ├── annotation_list_widget.py
│   ├── toolbar.py
│   └── dialogs.py
├── utils/                  # Shared utilities
│   └── constants.py
├── app.py                  # Entry point
└── requirements.txt
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

**Current**: Phase 3 (60% complete)
- ✅ Core data models
- ✅ Business logic layer
- ✅ Data layer
- ✅ Label management
- ✅ Dialogs
- ⏳ UI components (in progress)

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed design and implementation guide.

## License

MIT

## Contributing

Contributions welcome! Please ensure code follows PEP 8 standards and includes appropriate docstrings.
