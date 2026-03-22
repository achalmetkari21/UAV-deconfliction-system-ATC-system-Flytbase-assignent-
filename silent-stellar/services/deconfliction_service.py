# services/deconfliction_service.py
from typing import Dict, List, Tuple
from data_models import TrajectorySegment, ConflictResult, Position
from path_utils import euclidean_distance, interpolate_position
import math

class DeconflictionService:
    CONFLICT_DISTANCE = 5.0
    DANGER_DISTANCE = 10.0
    TIME_STEP = 0.1 # seconds

    @staticmethod
    def detect_conflicts(drone_segments: Dict[str, List[TrajectorySegment]]) -> List[ConflictResult]:
        """
        Detects conflicts among all drones by stepping through time.
        """
        results = []
        drone_ids = list(drone_segments.keys())
        
        if len(drone_ids) < 2:
            return results

        # Find overall simulation start and end times
        all_start = min(seg.start_time for segs in drone_segments.values() for seg in segs)
        all_end = max(seg.end_time for segs in drone_segments.values() for seg in segs)

        # Dictionary to track if a pair has already had a conflict reported
        # to avoid spamming the same conflict at every time step
        recorded_conflict_pairs = set()

        current_time = all_start
        while current_time <= all_end:
            # Get current position of all active drones
            current_positions = {}
            for d_id, segments in drone_segments.items():
                pos = DeconflictionService._get_position_at_time(segments, current_time)
                if pos:
                    current_positions[d_id] = pos

            active_ids = list(current_positions.keys())
            
            # Compare all pairs
            for i in range(len(active_ids)):
                for j in range(i + 1, len(active_ids)):
                    id1 = active_ids[i]
                    id2 = active_ids[j]
                    
                    pair_key = tuple(sorted([id1, id2]))
                    if pair_key in recorded_conflict_pairs:
                        continue # Already recorded the start of a conflict for this pair

                    p1 = current_positions[id1]
                    p2 = current_positions[id2]
                    
                    dist = euclidean_distance(p1, p2)
                    
                    if dist < DeconflictionService.CONFLICT_DISTANCE:
                        # Record conflict
                        # Conflict location is halfway between the two drones
                        conflict_loc = Position(
                            x=(p1.x + p2.x) / 2,
                            y=(p1.y + p2.y) / 2,
                            z=(p1.z + p2.z) / 2
                        )
                        results.append(ConflictResult(
                            conflict_time=current_time,
                            location=conflict_loc,
                            drone_ids=(id1, id2),
                            is_danger=True,
                            is_conflict=True
                        ))
                        recorded_conflict_pairs.add(pair_key)
                        
            current_time += DeconflictionService.TIME_STEP

        return results

    @staticmethod
    def _get_position_at_time(segments: List[TrajectorySegment], time: float) -> Position:
        """Helper to get position of a drone at a specific time."""
        for seg in segments:
            if seg.start_time <= time <= seg.end_time:
                duration = seg.end_time - seg.start_time
                if duration == 0:
                    return seg.start_pos
                
                fraction = (time - seg.start_time) / duration
                return interpolate_position(seg.start_pos, seg.end_pos, fraction)
        
        return None # Drone not active at this time

def detect_conflict(drones: List['Drone']):
    """
    Automatic Conflict Detection using continuous trajectory analysis.
    Iterates through segment overlaps and mathematically computes the exact
    time of conflict without relying on discrete fixed loop steps.
    
    Returns a list of conflicts: [(time, position, drone_ids), ...]
    """
    from services.trajectory_service import TrajectoryService
    
    all_conflicts = []
    
    # 1. Generate segments for all drones
    trajectories = {d.id: TrajectoryService.calculate_segments(d) for d in drones}
    drone_ids = list(trajectories.keys())
    
    # 2. Compare pairs continuously
    for i in range(len(drone_ids)):
        for j in range(i + 1, len(drone_ids)):
            id1, id2 = drone_ids[i], drone_ids[j]
            segs1 = trajectories[id1]
            segs2 = trajectories[id2]
            
            # Iterate through time based on segment overlap
            for s1 in segs1:
                for s2 in segs2:
                    t_start = max(s1.start_time, s2.start_time)
                    t_end = min(s1.end_time, s2.end_time)
                    
                    if t_start > t_end:
                        continue # No overlap
                        
                    dt1 = s1.end_time - s1.start_time
                    dt2 = s2.end_time - s2.start_time
                    if dt1 == 0 or dt2 == 0: continue
                    
                    # Compute relative velocity and position at t=0
                    # V = (End - Start) / duration
                    v1x = (s1.end_pos.x - s1.start_pos.x) / dt1
                    v1y = (s1.end_pos.y - s1.start_pos.y) / dt1
                    v1z = (s1.end_pos.z - s1.start_pos.z) / dt1
                    
                    v2x = (s2.end_pos.x - s2.start_pos.x) / dt2
                    v2y = (s2.end_pos.y - s2.start_pos.y) / dt2
                    v2z = (s2.end_pos.z - s2.start_pos.z) / dt2
                    
                    p10x = s1.start_pos.x - v1x * s1.start_time
                    p10y = s1.start_pos.y - v1y * s1.start_time
                    p10z = s1.start_pos.z - v1z * s1.start_time
                    
                    p20x = s2.start_pos.x - v2x * s2.start_time
                    p20y = s2.start_pos.y - v2y * s2.start_time
                    p20z = s2.start_pos.z - v2z * s2.start_time
                    
                    dvx, dvy, dvz = v1x - v2x, v1y - v2y, v1z - v2z
                    dpx, dpy, dpz = p10x - p20x, p10y - p20y, p10z - p20z
                    
                    # Distance squared: A*t^2 + B*t + C_dist
                    A = dvx**2 + dvy**2 + dvz**2
                    B = 2 * (dpx*dvx + dpy*dvy + dpz*dvz)
                    C_dist = dpx**2 + dpy**2 + dpz**2
                    
                    conflict_t = None
                    if A == 0:
                        if C_dist < 25.0: conflict_t = t_start
                    else:
                        # Find Closest Point of Approach (CPA)
                        t_cpa = -B / (2 * A)
                        
                        # Clamp CPA to the segment overlap interval
                        t_cpa = max(t_start, min(t_end, t_cpa))
                        
                        # Evaluate if distance at CPA is within 5 units threshold
                        min_dist_sq = A * t_cpa**2 + B * t_cpa + C_dist
                        
                        if min_dist_sq < 25.0:
                            conflict_t = t_cpa
                                
                    if conflict_t is not None:
                        # Find exactly where it is utilizing interpolation rules
                        ratio1 = (conflict_t - s1.start_time) / dt1
                        pos_1_x = s1.start_pos.x + ratio1 * (s1.end_pos.x - s1.start_pos.x)
                        pos_1_y = s1.start_pos.y + ratio1 * (s1.end_pos.y - s1.start_pos.y)
                        pos_1_z = s1.start_pos.z + ratio1 * (s1.end_pos.z - s1.start_pos.z)
                        
                        ratio2 = (conflict_t - s2.start_time) / dt2
                        pos_2_x = s2.start_pos.x + ratio2 * (s2.end_pos.x - s2.start_pos.x)
                        pos_2_y = s2.start_pos.y + ratio2 * (s2.end_pos.y - s2.start_pos.y)
                        pos_2_z = s2.start_pos.z + ratio2 * (s2.end_pos.z - s2.start_pos.z)
                        
                        loc = (
                            (pos_1_x + pos_2_x) / 2,
                            (pos_1_y + pos_2_y) / 2,
                            (pos_1_z + pos_2_z) / 2
                        )
                        
                        all_conflicts.append((conflict_t, loc, (id1, id2)))
                        
    # Sort conflicts by time
    all_conflicts.sort(key=lambda x: x[0])
    return all_conflicts
