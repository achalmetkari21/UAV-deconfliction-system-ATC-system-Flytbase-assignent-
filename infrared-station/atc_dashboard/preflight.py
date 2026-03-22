from typing import List, Dict, Tuple
from models import Drone, TrajectorySegment
from simulation import TrajectoryService
from conflict_engine import detect_future_conflicts

def check_preflight(
    new_drone: Drone, 
    active_trajectories: Dict[str, List[TrajectorySegment]], 
    current_time: float
) -> Tuple[str, str]:
    """
    Simulates placing the new drone into the airspace to verify if it will conflict.
    Returns (ApprovalStatus, DetailedMessage)
    """
    new_trajectory = TrajectoryService.calculate_segments(new_drone)
    
    # Create an isolated copy to evaluate futures without mutating active states
    temp_trajectories = active_trajectories.copy()
    temp_trajectories[new_drone.id] = new_trajectory
    
    # We predict ahead based on the current time
    # Note: If the drone's start time is in the future, early segments are empty, which is handled correctly
    conflicts = detect_future_conflicts(temp_trajectories, current_time)
    
    # Filter only conflicts directly involving the new drone
    new_drone_conflicts = [c for c in conflicts if c.drone1 == new_drone.id or c.drone2 == new_drone.id]
    
    if not new_drone_conflicts:
        return "APPROVE", "Trajectory confirmed clear."
        
    severe_conflicts = [c for c in new_drone_conflicts if c.severity == "HIGH"]
    if severe_conflicts:
        c = severe_conflicts[0]
        other_drone = c.drone1 if c.drone2 == new_drone.id else c.drone2
        return "REJECT", f"Critical conflict with {other_drone} in {c.time_to_impact:.1f}s."
    else:
        c = new_drone_conflicts[0]
        other_drone = c.drone1 if c.drone2 == new_drone.id else c.drone2
        return "DELAY", f"Proximity warning with {other_drone}. Consider delaying start."
