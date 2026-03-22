from typing import List, Dict, Optional
from models import Drone, TrajectorySegment, ConflictResult

CONFLICT_DISTANCE = 5.0
WARNING_DISTANCE = 10.0

def detect_future_conflicts(trajectories: Dict[str, List[TrajectorySegment]], current_time: float) -> List[ConflictResult]:
    """
    Detects continuous trajectory intersections from 'current_time' onwards.
    Used for early warnings.
    """
    all_conflicts = []
    drone_ids = list(trajectories.keys())
    
    for i in range(len(drone_ids)):
        for j in range(i + 1, len(drone_ids)):
            id1, id2 = drone_ids[i], drone_ids[j]
            segs1 = trajectories[id1]
            segs2 = trajectories[id2]
            
            earliest_conflict = None
            
            for s1 in segs1:
                for s2 in segs2:
                    # Only analyze future overlap logic
                    if s1.end_time < current_time or s2.end_time < current_time:
                        continue
                        
                    t_start = max(s1.start_time, s2.start_time, current_time)
                    t_end = min(s1.end_time, s2.end_time)
                    
                    if t_start > t_end:
                        continue
                        
                    dt1 = s1.end_time - s1.start_time
                    dt2 = s2.end_time - s2.start_time
                    if dt1 <= 0 or dt2 <= 0: continue
                    
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
                    
                    A = dvx**2 + dvy**2 + dvz**2
                    B = 2 * (dpx*dvx + dpy*dvy + dpz*dvz)
                    C_dist = dpx**2 + dpy**2 + dpz**2
                    
                    t_cpa = None
                    if A == 0:
                        t_cpa = t_start
                    else:
                        t_cpa = max(t_start, min(t_end, -B / (2 * A)))
                        
                    min_dist_sq = A * t_cpa**2 + B * t_cpa + C_dist
                    min_dist = max(0, min_dist_sq)**0.5
                    
                    if min_dist <= WARNING_DISTANCE:
                        severity = "HIGH" if min_dist <= CONFLICT_DISTANCE else "WARNING"
                        conf = max(0.5, 1.0 - (min_dist / WARNING_DISTANCE)*0.2)
                        
                        if earliest_conflict is None or t_cpa < earliest_conflict.time_to_impact + current_time:
                            earliest_conflict = ConflictResult(
                                drone1=id1,
                                drone2=id2,
                                time_to_impact=t_cpa - current_time,
                                severity=severity,
                                confidence=conf
                            )
            
            if earliest_conflict:
                all_conflicts.append(earliest_conflict)
                
    all_conflicts.sort(key=lambda x: x.time_to_impact)
    return all_conflicts
