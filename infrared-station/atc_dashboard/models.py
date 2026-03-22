from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class Position:
    x: float
    y: float
    z: float

@dataclass
class TrajectorySegment:
    start_pos: Position
    end_pos: Position
    start_time: float
    end_time: float

@dataclass
class Drone:
    id: str
    waypoints: List[Tuple[float, float, float]]
    velocity: float
    start_time: float
    drone_type: str = "controlled"
    
    def __post_init__(self):
        if not self.waypoints:
            raise ValueError("Drone must have at least one waypoint")
        if self.velocity <= 0:
            raise ValueError("Drone velocity must be positive")
        if self.drone_type not in ["controlled", "unknown"]:
            self.drone_type = "controlled"

@dataclass
class ConflictResult:
    drone1: str
    drone2: str
    time_to_impact: float
    severity: str
    confidence: float
