# Image Annotation Software - Project Requirements

## Project Overview
**Goal**: Design and implement a minimal image annotation software application

**Project Type**: Desktop application with future web deployment capability

## Technical Stack Requirements

### Primary Language
- **Python** (full stack)
- All components must be implemented in Python

### Key Priorities
1. **Maintainability**: Code must be clean, well-structured, and easy to understand
2. **Extensibility**: Architecture must support future enhancements
3. **Modularity**: Clear separation of concerns between components

## Core Features (MVP - Minimum Viable Product)

### 1. Manual Image Annotation
- Load and display images
- Draw rectangular bounding boxes on images
- Label annotations (assign class/category to each box)
- Edit existing annotations (move, resize, delete)
- Navigate between multiple images

### 2. Annotation Export
Support two export formats:
- **CSV Format**: Simple tabular format with image name, box coordinates, and labels
- **COCO Format JSON**: Industry-standard format for computer vision datasets

### 3. Basic UI Requirements
- Image viewing area
- Annotation tools (rectangle drawing)
- Annotation list/management
- Export functionality

## Future Extensibility Requirements

The architecture MUST be designed to accommodate these future features:

### 1. Auto-Annotation Integration
- Integration with zero-shot object detection models:
  - **SAM (Segment Anything Model)**: For automatic segmentation
  - **DINO (Detection Transformer)**: For object detection
- Ability to suggest annotations automatically
- Manual review and correction of auto-annotations

### 2. Web Application Deployment
- Architecture should allow migration to web-based interface
- Separation of backend logic from UI layer
- API-ready design for future client-server architecture

## Quality Requirements

### Code Quality
- Well-commented code
- Consistent coding style (PEP 8 for Python)
- Modular design with single responsibility principle
- Clear separation of concerns

### Architecture
- **Maintainable**: Easy to understand and modify
- **Extensible**: Can add new features without major refactoring
- **Testable**: Components should be testable independently
- **Documented**: Clear documentation for setup, usage, and architecture

### User Experience
- Intuitive interface
- Clear feedback for user actions
- Error handling with helpful messages
- Responsive UI (no freezing during operations)

## Technical Constraints

### Must Support
- Common image formats (JPEG, PNG, etc.)
- Reasonable performance with images up to 4K resolution
- Multiple annotations per image
- Batch processing of multiple images

### Should Avoid
- Dependency on platform-specific libraries (prefer cross-platform)
- Overly complex frameworks that hinder maintainability
- Tight coupling between UI and business logic

## Success Criteria

The project is successful when:
1. ✓ User can load images and create rectangular annotations
2. ✓ Annotations can be exported to both CSV and COCO JSON formats
3. ✓ Code is clean, well-documented, and maintainable
4. ✓ Architecture supports future extension for auto-annotation
5. ✓ Architecture supports future web deployment
6. ✓ Developer fully understands all components of the system

## Development Approach

- Start with core functionality (image loading, annotation, export)
- Build with extensibility in mind from the beginning
- Incremental development with frequent testing
- Prioritize clean architecture over rapid feature addition

## Notes for Implementation

- Consider using established Python libraries for UI (e.g., tkinter, PyQt, Streamlit)
- Design data models that can work with both manual and auto-annotation
- Keep file I/O operations separate from annotation logic
- Plan for both desktop and web UI from the start (shared backend)

---

**Usage**: Attach this file along with `software_development_prompt.md` when starting development of this project.