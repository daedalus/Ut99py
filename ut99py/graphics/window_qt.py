"""Qt-based OpenGL window for Ut99py - provides a real on-screen display.

Uses PyQt5's QGLWidget to wrap the FOpenGLRenderer so the demo
can actually render to a visible window instead of being headless.
"""
from typing import Optional

import math

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtOpenGL import QGLWidget

from .opengl import FOpenGLRenderer


class GLWidget(QGLWidget):
    """OpenGL widget that wraps FOpenGLRenderer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._renderer: Optional[FOpenGLRenderer] = None
        self._frame_count: int = 0
        self._fps_timer: float = 0.0
        self._fps: float = 0.0
        self._last_fps_update: float = 0.0
        self._cube_angle: float = 0.0

        # Set size policy
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(size_policy)

    def set_renderer(self, renderer: FOpenGLRenderer) -> None:
        self._renderer = renderer

    def initializeGL(self) -> None:
        if self._renderer:
            self._renderer.init()
            self._renderer.resize(self.width(), self.height())

    def resizeGL(self, w: int, h: int) -> None:
        if self._renderer:
            self._renderer.resize(w, h)

    def paintGL(self) -> None:
        if self._renderer:
            self._renderer.begin_scene()

            # Update cube angle
            self._cube_angle += 1.0
            if self._cube_angle >= 360.0:
                self._cube_angle -= 360.0

            # Draw a rotating red cube (larger, closer)
            self._renderer.set_color(1.0, 0.0, 0.0)
            self._renderer.load_identity()
            self._renderer.translate(0.0, 0.0, -8.0)
            self._renderer.rotate(self._cube_angle, 0.0, 1.0, 0.0)
            self._renderer.draw_cube(0.0, 0.0, 0.0, 4.0)

            # Draw a green line across the scene
            self._renderer.set_color(0.0, 1.0, 0.0)
            self._renderer.load_identity()
            self._renderer.translate(0.0, 0.0, -7.0)
            self._renderer.draw_line(-3.0, 0.0, 0.0, 3.0, 0.0, 0.0)

            # Draw a blue sphere (closer, in front of cube)
            self._renderer.set_color(0.0, 0.5, 1.0)
            self._renderer.load_identity()
            self._renderer.translate(0.0, 0.0, -6.0)
            self._renderer.draw_sphere(0.0, 0.0, 0.0, 1.5, 24)

            # Draw a yellow pyramid for extra visual interest
            self._renderer.set_color(1.0, 1.0, 0.0)
            self._renderer.load_identity()
            self._renderer.translate(0.0, 0.0, -5.0)
            self._renderer.rotate(45.0, 1.0, 0.0, 0.0)
            self._draw_pyramid(self._renderer, 1.0)

            # Draw a magenta cylinder
            self._renderer.set_color(1.0, 0.0, 1.0)
            self._renderer.load_identity()
            self._renderer.translate(-2.0, 0.0, -4.0)
            self._renderer.rotate(45.0, 0.0, 1.0, 0.0)
            self._draw_cylinder(self._renderer, 0.8, 1.5)

            # Draw a white teapot-like shape (just a sphere with facets)
            self._renderer.set_color(1.0, 1.0, 1.0)
            self._renderer.load_identity()
            self._renderer.translate(2.0, 0.0, -4.0)
            self._renderer.rotate(self._cube_angle * 0.5, 0.0, 1.0, 0.0)
            self._renderer.draw_sphere(0.0, 0.0, 0.0, 1.0, 16)

            self._renderer.end_scene()

            self._frame_count += 1

    def _draw_pyramid(self, renderer, size: float) -> None:
        """Draw a simple square pyramid."""
        s = size / 2.0
        h = size * 0.8

        # Base (square)
        renderer.draw_quad([
            (-s, -s, s), (s, -s, s), (s, -s, -s), (-s, -s, -s)
        ])

        # Sides
        renderer.draw_quad([
            (-s, -s, s), (s, -s, s), (0, h, 0), (-s, -s, s)
        ])
        renderer.draw_quad([
            (s, -s, s), (s, -s, -s), (0, h, 0), (s, -s, -s)
        ])
        renderer.draw_quad([
            (s, -s, -s), (-s, -s, -s), (0, h, 0), (s, -s, -s)
        ])
        renderer.draw_quad([
            (-s, -s, -s), (-s, -s, s), (0, h, 0), (-s, -s, s)
        ])

    def _draw_cylinder(self, renderer, radius: float, height: float) -> None:
        """Draw a simple cylinder using quads and circles."""
        segments = 16

        # Top circle
        renderer.draw_quad([(radius * math.cos(i * 2 * math.pi / segments),
                             radius * math.sin(i * 2 * math.pi / segments),
                             height / 2)
                           for i in range(segments)])

        # Bottom circle (at -height/2)
        renderer.draw_quad([(radius * math.cos(i * 2 * math.pi / segments),
                             radius * math.sin(i * 2 * math.pi / segments),
                             -height / 2)
                          for i in range(segments)])

        # Side quads
        for i in range(segments):
            j = (i + 1) % segments
            renderer.draw_quad([
                (radius * math.cos(i * 2 * math.pi / segments),
                 radius * math.sin(i * 2 * math.pi / segments),
                 height / 2),
                (radius * math.cos(j * 2 * math.pi / segments),
                 radius * math.sin(j * 2 * math.pi / segments),
                 height / 2),
                (radius * math.cos(j * 2 * math.pi / segments),
                 radius * math.sin(j * 2 * math.pi / segments),
                 -height / 2),
                (radius * math.cos(i * 2 * math.pi / segments),
                 radius * math.sin(i * 2 * math.pi / segments),
                 -height / 2),
            ])


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