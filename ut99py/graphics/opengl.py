"""OpenGL rendering implementation for Ut99py"""

from typing import Optional, Tuple
import math

try:
    import OpenGL.GL as gl
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False


class FOpenGLRenderer:
    """OpenGL renderer implementation"""
    
    def __init__(self, width: int = 640, height: int = 480):
        self._width = width
        self._height = height
        self._initialized = False
        self._shader_program = None
        self._vertex_buffer = None
        self._vao = None
        
        # Matrices
        self._projection_matrix = [0.0] * 16
        self._modelview_matrix = [0.0] * 16
        
        # Rendering state
        self._wireframe = False
        self._depth_test = True
        self._cull_face = True
        self._blend = False
        
        # Colors
        self._clear_color = (0.0, 0.0, 0.0, 1.0)
        self._current_color = (1.0, 1.0, 1.0, 1.0)
        
    def init(self) -> bool:
        """Initialize OpenGL"""
        if not OPENGL_AVAILABLE:
            print("OpenGL not available - install PyOpenGL")
            return False
            
        try:
            # Setup OpenGL state
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glEnable(gl.GL_CULL_FACE)
            gl.glCullFace(gl.GL_BACK)
            gl.glFrontFace(gl.GL_CCW)
            
            # Set clear color
            gl.glClearColor(*self._clear_color)
            
            self._initialized = True
            return True
        except Exception as e:
            print(f"OpenGL init failed: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown OpenGL"""
        if self._shader_program:
            gl.glDeleteProgram(self._shader_program)
        if self._vertex_buffer:
            gl.glDeleteBuffers(1, [self._vertex_buffer])
        if self._vao:
            gl.glDeleteVertexArrays(1, [self._vao])
        self._initialized = False
    
    def resize(self, width: int, height: int) -> None:
        """Handle window resize"""
        self._width = width
        self._height = height
        if height == 0:
            height = 1
        gl.glViewport(0, 0, width, height)
        self._set_perspective(45.0, width / height, 0.1, 1000.0)
    
    def clear(self) -> None:
        """Clear the screen"""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    
    def begin_scene(self) -> None:
        """Begin a new frame"""
        self.clear()
    
    def end_scene(self) -> None:
        """End the current frame"""
        pass
    
    def set_wireframe(self, wireframe: bool) -> None:
        """Set wireframe mode"""
        self._wireframe = wireframe
        if wireframe:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        else:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    
    def set_depth_test(self, enabled: bool) -> None:
        """Enable/disable depth testing"""
        self._depth_test = enabled
        if enabled:
            gl.glEnable(gl.GL_DEPTH_TEST)
        else:
            gl.glDisable(gl.GL_DEPTH_TEST)
    
    def set_blend(self, enabled: bool) -> None:
        """Enable/disable blending"""
        self._blend = enabled
        if enabled:
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        else:
            gl.glDisable(gl.GL_BLEND)
    
    def set_clear_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """Set clear color"""
        self._clear_color = (r, g, b, a)
        gl.glClearColor(r, g, b, a)
    
    def set_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """Set current drawing color"""
        self._current_color = (r, g, b, a)
        gl.glColor4f(r, g, b, a)
    
    # Matrix operations
    def _set_perspective(self, fov: float, aspect: float, near: float, far: float) -> None:
        """Set perspective projection matrix"""
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        
        self._projection_matrix = [
            f / aspect, 0.0, 0.0, 0.0,
            0.0, f, 0.0, 0.0,
            0.0, 0.0, (far + near) / (near - far), -1.0,
            0.0, 0.0, (2.0 * far * near) / (near - far), 0.0
        ]
    
    def _set_ortho(self, left: float, right: float, bottom: float, top: float, near: float, far: float) -> None:
        """Set orthographic projection matrix"""
        self._projection_matrix = [
            2.0 / (right - left), 0.0, 0.0, 0.0,
            0.0, 2.0 / (top - bottom), 0.0, 0.0,
            0.0, 0.0, -2.0 / (far - near), 0.0,
            -(right + left) / (right - left), -(top + bottom) / (top - bottom), -(far + near) / (far - near), 1.0
        ]
    
    def load_identity(self) -> None:
        """Load identity matrix"""
        self._modelview_matrix = [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0
        ]
    
    def translate(self, x: float, y: float, z: float) -> None:
        """Translate the modelview matrix"""
        self._modelview_matrix[12] += x
        self._modelview_matrix[13] += y
        self._modelview_matrix[14] += z
    
    def rotate(self, angle: float, x: float, y: float, z: float) -> None:
        """Rotate the modelview matrix"""
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        
        # Normalize axis
        length = math.sqrt(x*x + y*y + z*z)
        if length > 0:
            x /= length
            y /= length
            z /= length
        
        # Build rotation matrix (simplified)
        rot = [
            x*x*(1-c)+c,   x*y*(1-c)-z*s, x*z*(1-c)+y*s, 0.0,
            y*x*(1-c)+z*s, y*y*(1-c)+c,   y*z*(1-c)-x*s, 0.0,
            z*x*(1-c)-y*s, z*y*(1-c)+x*s, z*z*(1-c)+c,   0.0,
            0.0, 0.0, 0.0, 1.0
        ]
        
        # Multiply matrices
        self._modelview_matrix = self._multiply_matrices(self._modelview_matrix, rot)
    
    def scale(self, x: float, y: float, z: float) -> None:
        """Scale the modelview matrix"""
        self._modelview_matrix[0] *= x
        self._modelview_matrix[5] *= y
        self._modelview_matrix[10] *= z
    
    def _multiply_matrices(self, a: list, b: list) -> list:
        """Multiply two 4x4 matrices"""
        result = [0.0] * 16
        for i in range(4):
            for j in range(4):
                result[i * 4 + j] = (
                    a[i * 4 + 0] * b[0 * 4 + j] +
                    a[i * 4 + 1] * b[1 * 4 + j] +
                    a[i * 4 + 2] * b[2 * 4 + j] +
                    a[i * 4 + 3] * b[3 * 4 + j]
                )
        return result
    
    def push_matrix(self) -> list:
        """Push current matrix to stack"""
        return self._modelview_matrix.copy()
    
    def pop_matrix(self, matrix: list) -> None:
        """Pop matrix from stack"""
        self._modelview_matrix = matrix.copy()
    
    # Drawing primitives
    def draw_point(self, x: float, y: float, z: float) -> None:
        """Draw a point"""
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex3f(x, y, z)
        gl.glEnd()
    
    def draw_line(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> None:
        """Draw a line"""
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3f(x1, y1, z1)
        gl.glVertex3f(x2, y2, z2)
        gl.glEnd()
    
    def draw_triangle(self, verts: list) -> None:
        """Draw a triangle (verts = [(x,y,z), (x,y,z), (x,y,z)])"""
        gl.glBegin(gl.GL_TRIANGLES)
        for v in verts:
            gl.glVertex3f(*v)
        gl.glEnd()
    
    def draw_quad(self, verts: list) -> None:
        """Draw a quad (verts = [(x,y,z), (x,y,z), (x,y,z), (x,y,z)])"""
        gl.glBegin(gl.GL_QUADS)
        for v in verts:
            gl.glVertex3f(*v)
        gl.glEnd()
    
    def draw_cube(self, x: float, y: float, z: float, size: float = 1.0) -> None:
        """Draw a cube at position with given size"""
        s = size / 2.0
        
        # Front
        self.draw_quad([
            (x-s, y-s, z+s), (x+s, y-s, z+s), (x+s, y+s, z+s), (x-s, y+s, z+s)
        ])
        # Back
        self.draw_quad([
            (x+s, y-s, z-s), (x-s, y-s, z-s), (x-s, y+s, z-s), (x+s, y+s, z-s)
        ])
        # Top
        self.draw_quad([
            (x-s, y+s, z+s), (x+s, y+s, z+s), (x+s, y+s, z-s), (x-s, y+s, z-s)
        ])
        # Bottom
        self.draw_quad([
            (x-s, y-s, z-s), (x+s, y-s, z-s), (x+s, y-s, z+s), (x-s, y-s, z+s)
        ])
        # Right
        self.draw_quad([
            (x+s, y-s, z+s), (x+s, y-s, z-s), (x+s, y+s, z-s), (x+s, y+s, z+s)
        ])
        # Left
        self.draw_quad([
            (x-s, y-s, z-s), (x-s, y-s, z+s), (x-s, y+s, z+s), (x-s, y+s, z-s)
        ])
    
    def draw_sphere(self, x: float, y: float, z: float, radius: float = 1.0, segments: int = 16) -> None:
        """Draw a sphere at position with given radius"""
        lat_lines = segments
        lon_lines = segments * 2
        
        for i in range(lat_lines):
            lat0 = math.pi * (i / lat_lines)
            lat1 = math.pi * ((i + 1) / lat_lines)
            
            for j in range(lon_lines):
                lon0 = 2 * math.pi * (j / lon_lines)
                lon1 = 2 * math.pi * ((j + 1) / lon_lines)
                
                # Calculate vertices
                def get_vertex(lat, lon):
                    px = x + radius * math.sin(lat) * math.cos(lon)
                    py = y + radius * math.cos(lat)
                    pz = z + radius * math.sin(lat) * math.sin(lon)
                    return (px, py, pz)
                
                v1 = get_vertex(lat0, lon0)
                v2 = get_vertex(lat0, lon1)
                v3 = get_vertex(lat1, lon1)
                v4 = get_vertex(lat1, lon0)
                
                # Draw quad as two triangles
                self.draw_triangle([v1, v2, v3])
                self.draw_triangle([v1, v3, v4])
    
    def draw_text(self, x: float, y: float, text: str) -> None:
        """Draw text at position (requires font setup)"""
        # This would need font rendering setup
        pass
    
    # Getters
    def get_width(self) -> int:
        return self._width
    
    def get_height(self) -> int:
        return self._height
    
    def is_initialized(self) -> bool:
        return self._initialized


class VulkanRenderer:
    """Vulkan renderer (placeholder - requires vulkan SDK)"""
    
    def __init__(self, width: int = 640, height: int = 480):
        self._width = width
        self._height = height
        self._initialized = False
        
    def init(self) -> bool:
        print("Vulkan support not yet implemented")
        return False
    
    def shutdown(self) -> None:
        pass
    
    def resize(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
    
    def clear(self) -> None:
        pass
    
    def begin_scene(self) -> None:
        pass
    
    def end_scene(self) -> None:
        pass


def create_renderer(backend: str = "opengl", width: int = 640, height: int = 480):
    """Factory function to create a renderer"""
    if backend.lower() == "opengl":
        return FOpenGLRenderer(width, height)
    elif backend.lower() == "vulkan":
        return VulkanRenderer(width, height)
    else:
        raise ValueError(f"Unknown renderer: {backend}")


if __name__ == "__main__":
    # Test the renderer
    renderer = create_renderer("opengl", 800, 600)
    if renderer.init():
        print(f"OpenGL Renderer initialized: {renderer.get_width()}x{renderer.get_height()}")
        
        # Draw a test scene
        renderer.begin_scene()
        
        renderer.set_color(1.0, 0.0, 0.0)
        renderer.draw_cube(0, 0, -5, 2.0)
        
        renderer.set_color(0.0, 1.0, 0.0)
        renderer.draw_line(-2, 0, -5, 2, 0, -5)
        
        renderer.end_scene()
        
        renderer.shutdown()
    else:
        print("Failed to initialize OpenGL")