# models/drone.py
from typing import List, Tuple
from dataclasses import dataclass, field

@dataclass
class Drone:
    id: str
    waypoints: List[Tuple[float, float, float]]
    velocity: float
    start_time: float
    
    def __post_init__(self):
        if not self.waypoints:
            raise ValueError("Drone must have at least one waypoint")
        if self.velocity <= 0:
            raise ValueError("Drone velocity must be positive")
