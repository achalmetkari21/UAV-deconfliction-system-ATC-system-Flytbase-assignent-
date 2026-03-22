from models import Drone

# 1. NO CONFLICT
def scenario_no_conflict():
    d1 = Drone("Drone_A", [(0, 0, 0), (10, 0, 5)], 2.0, 0)
    d2 = Drone("Drone_B", [(0, 10, 0), (10, 10, 5)], 2.0, 0)
    return [d1, d2]

# 2. CONFLICT (same point, same time)
def scenario_conflict():
    d1 = Drone("Drone_A", [(0, 0, 0), (10, 10, 5)], 2.0, 0)
    d2 = Drone("Drone_B", [(10, 0, 0), (0, 10, 5)], 2.0, 0)
    return [d1, d2]

# 3. NEAR MISS (same location, different time)
def scenario_near_miss():
    d1 = Drone("Drone_A", [(0, 0, 0), (10, 10, 5)], 2.0, 0)
    d2 = Drone("Drone_B", [(10, 0, 0), (0, 10, 5)], 2.0, 5)  # delayed start
    return [d1, d2]

# 4. CASCADE CONFLICT 
def scenario_cascade():
    d_A = Drone("Drone_A", [(-100, 0, 20), (200, 0, 20)], 40.0, 0.0)
    d_B = Drone("Drone_B", [(0, -120, -70), (0, 240, 200)], 75.0, 0.5)
    d_C = Drone("Drone_C", [(100, -400, -280), (100, 240, 200)], 100.0, 1.25)
    d_D = Drone("Drone_D", [(-500, 80, 530), (300, 80, -70)], 200.0, 3.75)
    d_E = Drone("Drone_E", [(0, 0, 100), (0, 0, -100)], 20.0, 2.0)
    return [d_A, d_B, d_C, d_D, d_E]

# 5. MASS TRAFFIC (30+ drones, mixed unknown)
def scenario_mass_traffic():
    import random
    random.seed(42)  # For reproducible chaos
    drones = []
    
    # Generate 25 controlled drones doing parallel transit
    for i in range(25):
        y_offset = -500 + i * 40
        speed = random.uniform(20.0, 40.0)
        start_t = random.uniform(0.0, 5.0)
        drones.append(Drone(f"Control_{i}", [(-500, y_offset, 50), (500, y_offset, 50)], speed, start_t, "controlled"))
        
    # Generate 10 unknown drones doing erratic perpendicular paths
    for i in range(10):
        x_offset = -400 + i * 80
        speed = random.uniform(15.0, 80.0)
        start_t = random.uniform(1.0, 10.0)
        drones.append(Drone(f"Unknown_{i}", [(x_offset, -500, 60), (x_offset, 500, 60)], speed, start_t, "unknown"))
        
    return drones

def get_scenarios():
    return {
        "No Conflict": scenario_no_conflict,
        "Conflict": scenario_conflict,
        "Near Miss": scenario_near_miss,
        "Cascade Conflict": scenario_cascade,
        "Mass Traffic": scenario_mass_traffic
    }
