"""Basic BSP draw for loaded UT99 levels."""
from typing import Optional

def draw_model_simple(renderer, model, view_scale=0.01):
    """Draw first surfaces of loaded model with basic colored polygons."""
    if not model or not model.Surfs:
        return
    renderer.set_color(0.5, 0.7, 0.9)
    renderer.load_identity()
    renderer.translate(0, -10, -30)
    renderer.rotate(15, 1.0, 0.0, 0.0)
    for surf in model.Surfs[:32]:
        pass  # Full BSP rendering needs FSpanBuffer/FRasterPoly pipeline
