import math
from typing import List, Dict, Optional
from models import Drone, Position, TrajectorySegment

class TrajectoryService:
    @staticmethod
    def calculate_segments(drone: Drone) -> List[TrajectorySegment]:
        segments = []
        current_time = drone.start_time
        
        for i in range(len(drone.waypoints) - 1):
            w1 = drone.waypoints[i]
            w2 = drone.waypoints[i+1]
            
            p1 = Position(x=w1[0], y=w1[1], z=w1[2])
            p2 = Position(x=w2[0], y=w2[1], z=w2[2])
            
            distance = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)
            time_taken = distance / drone.velocity if drone.velocity > 0 else 0
            
            end_time = current_time + time_taken
            segments.append(TrajectorySegment(p1, p2, current_time, end_time))
            current_time = end_time
            
        return segments

def get_position_at_time(segments: List[TrajectorySegment], time: float) -> Optional[Position]:
    for seg in segments:
        if seg.start_time <= time <= seg.end_time:
            duration = seg.end_time - seg.start_time
            if duration == 0:
                return seg.start_pos
            
            ratio = (time - seg.start_time) / duration
            return Position(
                x=seg.start_pos.x + ratio * (seg.end_pos.x - seg.start_pos.x),
                y=seg.start_pos.y + ratio * (seg.end_pos.y - seg.start_pos.y),
                z=seg.start_pos.z + ratio * (seg.end_pos.z - seg.start_pos.z)
            )
            
    # Hold position if simulation time is beyond segment ends natively
    if segments and time > segments[-1].end_time:
        return segments[-1].end_pos
        
    return None

class Simulator:
    def __init__(self, drones: List[Drone]):
        self.drones = {d.id: d for d in drones}
        self.trajectories = {d.id: TrajectoryService.calculate_segments(d) for d in drones}
        self.paused_drones: Dict[str, float] = {} # d_id -> pause start time
        self.drone_time_offsets: Dict[str, float] = {d.id: 0.0 for d in drones}
        self.unknown_offsets: Dict[str, Position] = {} # d_id -> current offset
    
    def pause_drone(self, drone_id: str, current_sim_time: float):
        if drone_id not in self.paused_drones and drone_id in self.drones:
            self.paused_drones[drone_id] = current_sim_time
            
    def resume_drone(self, drone_id: str, current_sim_time: float):
        if drone_id in self.paused_drones:
            paused_at = self.paused_drones.pop(drone_id)
            pause_duration = current_sim_time - paused_at
            self.drone_time_offsets[drone_id] += pause_duration

    def get_drone_effective_time(self, drone_id: str, current_time: float) -> float:
        if drone_id in self.paused_drones:
            return self.paused_drones[drone_id] - self.drone_time_offsets[drone_id]
        return current_time - self.drone_time_offsets[drone_id]

    def simulate_drones(self, current_time: float) -> List[Dict]:
        """Returns list of active drone states."""
        import random
        states = []
        for d_id, drone in self.drones.items():
            eff_time = self.get_drone_effective_time(d_id, current_time)
            if eff_time < drone.start_time:
                continue # Not yet started
                
            pos = get_position_at_time(self.trajectories[d_id], eff_time)
            if pos:
                # Apply random walk behavior to unknown drones
                if drone.drone_type == "unknown":
                    if d_id not in self.unknown_offsets:
                        self.unknown_offsets[d_id] = Position(0.0, 0.0, 0.0)
                        
                    # Add jitter to the position (-2 to +2 m per axis)
                    self.unknown_offsets[d_id].x += random.uniform(-2.0, 2.0)
                    self.unknown_offsets[d_id].y += random.uniform(-2.0, 2.0)
                    self.unknown_offsets[d_id].z += random.uniform(-1.0, 1.0)
                    
                    pos = Position(
                        x=pos.x + self.unknown_offsets[d_id].x,
                        y=pos.y + self.unknown_offsets[d_id].y,
                        z=pos.z + self.unknown_offsets[d_id].z
                    )

                is_paused = d_id in self.paused_drones
                duration_paused = current_time - self.paused_drones[d_id] if is_paused else 0.0
                states.append({
                    "id": d_id,
                    "type": drone.drone_type,
                    "x": pos.x,
                    "y": pos.y,
                    "z": pos.z,
                    "status": "PAUSED" if is_paused else "ACTIVE",
                    "pause_duration": duration_paused
                })
        return states
