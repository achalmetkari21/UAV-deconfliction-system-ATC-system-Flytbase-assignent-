# services/trajectory_service.py
from typing import List
from models.drone import Drone
from data_models import Position, TrajectorySegment
import math

class TrajectoryService:
    @staticmethod
    def calculate_segments(drone: Drone) -> List[TrajectorySegment]:
        """Converts drone waypoints into continuous time-based segments."""
        segments = []
        current_time = drone.start_time
        
        for i in range(len(drone.waypoints) - 1):
            w1 = drone.waypoints[i]
            w2 = drone.waypoints[i+1]
            
            p1 = Position(x=w1[0], y=w1[1], z=w1[2])
            p2 = Position(x=w2[0], y=w2[1], z=w2[2])
            
            # Calculate distance between waypoints
            distance = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)
            
            # Calculate time taken for this segment
            # time = distance / velocity
            time_taken = distance / drone.velocity if drone.velocity > 0 else 0
            
            end_time = current_time + time_taken
            
            segment = TrajectorySegment(
                start_pos=p1,
                end_pos=p2,
                start_time=current_time,
                end_time=end_time
            )
            segments.append(segment)
            current_time = end_time
            
        return segments
