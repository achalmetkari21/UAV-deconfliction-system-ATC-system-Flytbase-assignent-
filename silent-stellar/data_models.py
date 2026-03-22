# data_models.py
from dataclasses import dataclass
from typing import Tuple

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
class ConflictResult:
    conflict_time: float
    location: Position
    drone_ids: Tuple[str, str]
    is_danger: bool
    is_conflict: bool
