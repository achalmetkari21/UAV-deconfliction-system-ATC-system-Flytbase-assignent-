# path_utils.py
import math
from data_models import Position

def euclidean_distance(p1: Position, p2: Position) -> float:
    """Calculates 3D Euclidean distance between two positions."""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

def interpolate_position(start_pos: Position, end_pos: Position, fraction: float) -> Position:
    """Interpolates a position between start and end based on fraction (0.0 to 1.0)."""
    return Position(
        x=start_pos.x + (end_pos.x - start_pos.x) * fraction,
        y=start_pos.y + (end_pos.y - start_pos.y) * fraction,
        z=start_pos.z + (end_pos.z - start_pos.z) * fraction
    )
