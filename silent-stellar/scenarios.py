from models.drone import Drone


# 
#  1. NO CONFLICT
def scenario_no_conflict():
    d1 = Drone("Drone_A", [(0, 0, 0), (10, 0, 5)], 2.0, 0)
    d2 = Drone("Drone_B", [(0, 10, 0), (10, 10, 5)], 2.0, 0)

    return [d1, d2], None


# 2. CONFLICT (same point, same time)
def scenario_conflict():
    d1 = Drone("Drone_A", [(0, 0, 0), (10, 10, 5)], 2.0, 0)
    d2 = Drone("Drone_B", [(10, 0, 0), (0, 10, 5)], 2.0, 0)

    # approximate conflict point
    conflict_info = (5.0, (5, 5, 2.5))

    return [d1, d2], conflict_info


# ⚠️ 3. NEAR MISS (same location, different time)
def scenario_near_miss():
    d1 = Drone("Drone_A", [(0, 0, 0), (10, 10, 5)], 2.0, 0)
    d2 = Drone("Drone_B", [(10, 0, 0), (0, 10, 5)], 2.0, 5)  # delayed start

    return [d1, d2], None

# 💥 4. CASCADE CONFLICT (Chain of conflicts with completely different 3D pos, velocities & timings)
def scenario_cascade():
    # Drone A starts at t=0s, Vel: 40
    d_A = Drone("Drone_A", [(-100, 0, 20), (200, 0, 20)], 40.0, 0.0)
    
    # Drone B starts at t=0.5s, moves faster (Vel: 75.0) to hit A at t=2.5s
    d_B = Drone("Drone_B", [(0, -120, -70), (0, 240, 200)], 75.0, 0.5)
    
    # Drone C starts at t=1.25s (Vel: 100) to cross A's path at t=6.25s (Near miss!)
    d_C = Drone("Drone_C", [(100, -400, -280), (100, 240, 200)], 100.0, 1.25)
    
    # Drone D starts at t=3.75s (Missile speed Vel: 200) and hits C at t=7.5s
    d_D = Drone("Drone_D", [(-500, 80, 530), (300, 80, -70)], 200.0, 3.75)

    # Drone E takes off at t=2.0s right before the first crash, safely dropping through (Vel: 20)
    d_E = Drone("Drone_E", [(0, 0, 100), (0, 0, -100)], 20.0, 2.0)

    return [d_A, d_B, d_C, d_D, d_E], None