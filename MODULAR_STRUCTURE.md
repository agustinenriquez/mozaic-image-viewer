# Modular Image Viewer Structure

## Overview
The original monolithic `main.py` (1071 lines) has been refactored into a modular structure with clear separation of concerns.

## Directory Structure
```
mozaic-image-viewer/
├── main.py                 # Original monolithic file (backed up as main_original.py)
├── main_modular.py         # New modular entry point
├── gnome_theme.py         # Theme constants (unchanged)
├── core/                  # Core application logic
│   ├── __init__.py
│   ├── app.py             # Main application controller (340 lines)
│   └── state.py           # Application state management (80 lines)
├── ui/                    # UI components
│   ├── __init__.py
│   ├── headerbar.py       # Header bar with controls (100 lines)
│   ├── sidebar.py         # Info panel and thumbnails (130 lines)
│   ├── toolbar.py         # Bottom toolbar with zoom (110 lines)
│   ├── canvas.py          # Main image display area (140 lines)
│   └── statusbar.py       # Status bar (50 lines)
├── image/                 # Image processing
│   ├── __init__.py
│   ├── processor.py       # Image transformations (150 lines)
│   └── loader.py          # Image loading and file management (80 lines)
└── input/                 # Input handling
    ├── __init__.py
    ├── keyboard.py        # Keyboard shortcuts (60 lines)
    ├── mouse.py           # Mouse events and gestures (120 lines)
    └── drag_drop.py       # Drag and drop handling (50 lines)
```

## Benefits of Modular Structure

### 1. **Separation of Concerns**
- **UI Components**: Each UI element is self-contained
- **Image Processing**: Isolated image manipulation logic
- **Input Handling**: Centralized input event management
- **State Management**: Clean state container

### 2. **Maintainability**
- **Smaller Files**: Each module is focused and manageable
- **Clear Dependencies**: Easy to understand relationships
- **Testability**: Components can be tested in isolation

### 3. **Reusability**
- **Pluggable Components**: UI elements can be easily swapped
- **Extensibility**: New features can be added without touching core logic
- **Theme Support**: UI components use consistent theming

### 4. **Debugging**
- **Isolated Logic**: Easier to pinpoint issues
- **Modular Logging**: Each component has its own logging
- **Clean Interfaces**: Clear API boundaries

## Key Design Patterns

### 1. **Callback Pattern**
Components communicate through callback dictionaries, maintaining loose coupling.

### 2. **State Container**
Centralized state management prevents data inconsistencies.

### 3. **Factory Pattern**
UI components are created with dependency injection via callbacks.

### 4. **Observer Pattern**
Input handlers notify the application of events.

## Usage

### Running the Modular Version
```bash
uv run python main_modular.py
```

### Running the Original Version
```bash
uv run python main_original.py
```

## Component Responsibilities

### Core Components
- **`core/app.py`**: Main application controller, orchestrates all components
- **`core/state.py`**: Manages application state and provides state queries

### UI Components
- **`ui/headerbar.py`**: File open, sidebar toggle, fullscreen controls
- **`ui/sidebar.py`**: Image info display and thumbnail navigation
- **`ui/toolbar.py`**: Zoom controls and image operations
- **`ui/canvas.py`**: Main image display with pan/zoom support
- **`ui/statusbar.py`**: Status messages and feedback

### Image Processing
- **`image/processor.py`**: Image transformations, cropping, format conversion
- **`image/loader.py`**: File loading, directory navigation, format validation

### Input Handling
- **`input/keyboard.py`**: Keyboard shortcuts and hotkeys
- **`input/mouse.py`**: Mouse events, wheel zoom, pan gestures
- **`input/drag_drop.py`**: File drag and drop support

## Migration Notes

The modular version maintains 100% feature compatibility with the original while providing:
- Better code organization
- Easier maintenance
- Improved testability
- Clear separation of concerns
- Reduced coupling between components

All original functionality including mouse wheel zoom, auto-hide controls, fullscreen mode, and image transformations work exactly as before.