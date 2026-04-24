# Ut99py

Pure Python implementation of the Unreal Tournament 99 game engine with OpenGL/Vulkan graphics rendering.

## Status

**Early Development** - Package reading and texture loading working. Rendering system in progress.

## Features

- **Package System**: Read .u, .unr, .utx package files with full header/table parsing
- **Asset Loading**: Textures, sounds, meshes, and level data
- **Texture Support**: Mipmap generation and palettized (P8) texture format
- **Class Resolution**: Proper resolution of class references from import/export tables
- **OpenGL Rendering**: GPU-accelerated rendering pipeline

## Requirements

- Python 3.10+
- PyOpenGL
- PySide6 (for windowing)

## Installation

```bash
pip install -e .
```

## Usage

```python
from ut99py.engine.ut_reader import load_package

# Load a UT99 texture package
pkg = load_package('path/to/Ancient.utx')

# Find and read textures
for exp in pkg._export_table:
    if pkg.get_class_name(exp) == 'Texture':
        tex_data = pkg.read_texture_data(exp)
        print(f"Texture: {tex_data['name']} - {tex_data['u_size']}x{tex_data['v_size']}")
```

## Project Structure

```
ut99py/
├── core/           # Core engine classes (UObject, FArchive, etc.)
├── engine/         # Game engine systems
│   ├── assets.py   # Asset loading
│   ├── texture.py  # Texture system
│   └── ut_reader.py # Package file reader
├── graphics/       # OpenGL/Vulkan rendering
├── audio/          # Audio system
└── window/        # Window management
```

## License

MIT License - Port of Ut99PubSrc C++ codebase to Python

## References

- [Ut99PubSrc](https://github.com/SoonerBot/Ut99PubSrc) - Original C++ source
- [UTPackage.js](https://github.com/bunnytrack/UTPackage.js) - JavaScript reference implementation