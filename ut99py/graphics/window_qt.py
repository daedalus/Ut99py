"""Qt-based OpenGL window for Ut99py - provides a real on-screen display.

Uses PyQt5's QGLWidget to wrap the FOpenGLRenderer so the demo
can actually render to a visible window instead of being headless.
"""

from typing import Dict, Optional, Tuple

import math
import os

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QSizePolicy,
)
from PyQt5.QtCore import QTimer
from PyQt5.QtOpenGL import QGLWidget

from .opengl import FOpenGLRenderer
from .bsp_draw import draw_model_simple


class GLWidget(QGLWidget):
    """OpenGL widget that wraps FOpenGLRenderer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        from .opengl import FOpenGLRenderer
        self._renderer = FOpenGLRenderer()
        self._frame_count: int = 0
        self._fps_timer: float = 0.0
        self._fps: float = 0.0
        self._last_fps_update: float = 0.0
        self._cube_angle: float = 0.0
        # Real .utx textures: name -> (gl_tex_id, width, height)
        self._textures: Dict[str, Tuple[int, int, int]] = {}

        # Set size policy
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(size_policy)

    def set_renderer(self, renderer: FOpenGLRenderer) -> None:
        self._renderer = renderer

    def initializeGL(self) -> None:
        if self._renderer:
            self._renderer.init()
            self._renderer.resize(self.width(), self.height())
            self._load_game_textures()

    def _load_game_textures(self) -> None:
        """Upload real .utx textures through AssetLoader for paintGL."""
        from ..engine.assets import AssetLoader

        game_dir = os.path.expandvars(
            os.path.join(os.environ.get("UT99_GAME_DIR", ""), "")
        ) or os.path.expanduser("~/Games/UnrealTournament")
        loader = AssetLoader()
        loader.set_package_path(os.path.join(game_dir, "Textures"))
        for package, name in (
            ("Ancient.utx", "az-floor"),
            ("Ancient.utx", "HIWALL1D"),
            ("CTF.utx", "ston_red"),
        ):
            rgba = loader.get_texture_rgba(package, name)
            if rgba is None:
                continue
            height, width = rgba.shape[:2]
            tex_id = self._renderer.create_texture_rgba(width, height, rgba)
            self._textures[name] = (tex_id, width, height)

    def resizeGL(self, w: int, h: int) -> None:
        if self._renderer:
            self._renderer.resize(w, h)

    def paintGL(self) -> None:
        if self._renderer:
            self._renderer.begin_scene()

            # Rotate objects each frame
            self._cube_angle += 1.0
            if self._cube_angle >= 360.0:
                self._cube_angle -= 360.0

            # ---- Red cube (left) ----
            self._renderer.set_color(1.0, 0.0, 0.0)
            self._renderer.load_identity()
            self._renderer.translate(-2.0, 1.0, -8.0)
            self._renderer.rotate(self._cube_angle, 0.0, 1.0, 0.0)
            self._renderer.draw_cube(0.0, 0.0, 0.0, 1.5)

            # ---- Textured wall (real .utx textures, behind demo forms) ----
            self._draw_texture_wall()

            # ---- Textured cube (spinning, real az-floor texture) ----
            if "az-floor" in self._textures:
                self._renderer.set_color(1.0, 1.0, 1.0)
                self._renderer.load_identity()
                self._renderer.translate(3.0, -1.0, -9.0)
                self._renderer.rotate(self._cube_angle, 1.0, 1.0, 0.0)
                self._draw_textured_cube(self._textures["az-floor"][0], 1.5)

            # ---- Green line (middle-left) ----
            self._renderer.set_color(0.0, 1.0, 0.0)
            self._renderer.load_identity()
            self._renderer.translate(-1.0, 0.0, -7.0)
            self._renderer.draw_line(-1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

            # ---- Blue sphere (center) ----
            self._renderer.set_color(0.0, 0.5, 1.0)
            self._renderer.load_identity()
            self._renderer.translate(0.0, -1.0, -7.0)
            self._renderer.draw_sphere(0.0, 0.0, 0.0, 1.0, 24)

            # ---- Yellow pyramid (middle-right) ----
            self._renderer.set_color(1.0, 1.0, 0.0)
            self._renderer.load_identity()
            self._renderer.translate(1.0, 1.0, -7.0)
            self._renderer.rotate(self._cube_angle * 0.5, 1.0, 0.0, 0.0)
            self._draw_pyramid(self._renderer, 1.0)

            # ---- Magenta cylinder (right) ----
            self._renderer.set_color(1.0, 0.0, 1.0)
            self._renderer.load_identity()
            self._renderer.translate(2.0, -1.0, -7.0)
            self._renderer.rotate(self._cube_angle * 0.5, 0.0, 1.0, 0.0)
            self._draw_cylinder(self._renderer, 0.6, 1.2)

            # ---- White sphere (far right) ----
            self._renderer.set_color(1.0, 1.0, 1.0)
            self._renderer.load_identity()
            self._renderer.translate(3.0, 1.0, -7.0)
            self._renderer.draw_sphere(0.0, 0.0, 0.0, 0.8, 16)

            # ---- Loaded UT99 level BSP (if available) ----
            try:
                from ..core.linkers import load_package
                from ..engine.levelload import load_level
                lk = load_package("/home/dclavijo/Games/UnrealTournament/Maps/DM-Morpheus.unr")
                level = load_level(lk, lk.export_map[1082])
                if level.Model:
                    draw_model_simple(self._renderer, level.Model)
            except Exception:
                pass  # Level render optional

            self._renderer.end_scene()

            self._frame_count += 1

    def _draw_texture_wall(self) -> None:
        """Row of textured quads showing decoded .utx assets."""
        if not self._textures:
            return
        self._renderer.set_color(1.0, 1.0, 1.0)
        # Full-quad UVs; v flipped since our decode starts at the top row.
        uvs = [(0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]
        for i, (tex_id, width, height) in enumerate(self._textures.values()):
            half_h = 1.5 * height / width
            self._renderer.load_identity()
            self._renderer.translate(-1.5 + i * 1.5, 1.8, -11.0)
            self._renderer.bind_texture(tex_id)
            self._renderer.draw_textured_quad(
                [
                    (-0.7, -half_h, 0.0),
                    (0.7, -half_h, 0.0),
                    (0.7, half_h, 0.0),
                    (-0.7, half_h, 0.0),
                ],
                uvs,
            )
        self._renderer.bind_texture(0)

    def _draw_textured_cube(self, tex_id: int, size: float) -> None:
        """Cube whose six faces carry the given texture."""
        s = size / 2.0
        faces = [
            [(-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)],  # front
            [(s, -s, -s), (-s, -s, -s), (-s, s, -s), (s, s, -s)],  # back
            [(s, -s, s), (s, -s, -s), (s, s, -s), (s, s, s)],  # right
            [(-s, -s, -s), (-s, -s, s), (-s, s, s), (-s, s, -s)],  # left
            [(-s, s, s), (s, s, s), (s, s, -s), (-s, s, -s)],  # top
            [(-s, -s, -s), (s, -s, -s), (s, -s, s), (-s, -s, s)],  # bottom
        ]
        uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        self._renderer.bind_texture(tex_id)
        for face in faces:
            self._renderer.draw_textured_quad(face, uvs)
        self._renderer.bind_texture(0)

    def _draw_pyramid(self, renderer, size: float) -> None:
        """Draw a simple square pyramid."""
        s = size / 2.0
        h = size * 0.8

        # Base (square)
        renderer.draw_quad([(-s, -s, s), (s, -s, s), (s, -s, -s), (-s, -s, -s)])

        # Sides
        renderer.draw_quad([(-s, -s, s), (s, -s, s), (0, h, 0), (-s, -s, s)])
        renderer.draw_quad([(s, -s, s), (s, -s, -s), (0, h, 0), (s, -s, -s)])
        renderer.draw_quad([(s, -s, -s), (-s, -s, -s), (0, h, 0), (s, -s, -s)])
        renderer.draw_quad([(-s, -s, -s), (-s, -s, s), (0, h, 0), (-s, -s, s)])

    def _draw_cylinder(self, renderer, radius: float, height: float) -> None:
        """Draw a simple cylinder using quads and circles."""
        segments = 16

        # Top circle
        renderer.draw_quad(
            [
                (
                    radius * math.cos(i * 2 * math.pi / segments),
                    radius * math.sin(i * 2 * math.pi / segments),
                    height / 2,
                )
                for i in range(segments)
            ]
        )

        # Bottom circle (at -height/2)
        renderer.draw_quad(
            [
                (
                    radius * math.cos(i * 2 * math.pi / segments),
                    radius * math.sin(i * 2 * math.pi / segments),
                    -height / 2,
                )
                for i in range(segments)
            ]
        )

        # Side quads
        for i in range(segments):
            j = (i + 1) % segments
            renderer.draw_quad(
                [
                    (
                        radius * math.cos(i * 2 * math.pi / segments),
                        radius * math.sin(i * 2 * math.pi / segments),
                        height / 2,
                    ),
                    (
                        radius * math.cos(j * 2 * math.pi / segments),
                        radius * math.sin(j * 2 * math.pi / segments),
                        height / 2,
                    ),
                    (
                        radius * math.cos(j * 2 * math.pi / segments),
                        radius * math.sin(j * 2 * math.pi / segments),
                        -height / 2,
                    ),
                    (
                        radius * math.cos(i * 2 * math.pi / segments),
                        radius * math.sin(i * 2 * math.pi / segments),
                        -height / 2,
                    ),
                ]
            )


class GameWindow(QMainWindow):
    """Main game window with OpenGL viewport."""

    def __init__(self, width: int = 800, height: int = 600):
        super().__init__()
        self._renderer: Optional[FOpenGLRenderer] = None
        self._gl_widget: Optional[GLWidget] = None

        self.setWindowTitle("Ut99py - Unreal Tournament 99")
        self.resize(width, height)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Create OpenGL widget
        self._gl_widget = GLWidget()
        self._renderer = FOpenGLRenderer(width, height)
        self._gl_widget.set_renderer(self._renderer)

        # Layout
        from PyQt5.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._gl_widget)

        # FPS timer
        self._fps_timer = QTimer(self)
        self._fps_timer.timeout.connect(self._update_fps)
        self._fps_timer.start(1000)

        self._frame_count: int = 0

    def _update_fps(self) -> None:
        self.setWindowTitle(f"Ut99py - Unreal Tournament 99 | FPS: {self._frame_count}")
        self._frame_count = 0

    def closeEvent(self, event) -> None:
        if self._renderer:
            self._renderer.shutdown()
        event.accept()


def run_game(width: int = 800, height: int = 600) -> int:
    """Create and run the game window. Returns application exit code."""
    app = QApplication.instance() or QApplication([])

    window = GameWindow(width, height)
    window.show()

    return app.exec_()


if __name__ == "__main__":
    import sys
    import math

    sys.exit(run_game())
