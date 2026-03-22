# main.py
from models.drone import Drone
from services.trajectory_service import TrajectoryService
from services.deconfliction_service import DeconflictionService, detect_conflict
from visualization import plot_trajectories 
from scenarios import scenario_no_conflict, scenario_conflict, scenario_near_miss, scenario_cascade

def run_scenario(scenario_func, name):
    print(f"\n--- Running {name} scenario ---")
    drones, _ = scenario_func() # Ignore the manually defined conflict here
    
    # 5. Integration: Call detect_conflict() inside main.py
    conflicts = detect_conflict(drones)
    
    # 6. Output formatting
    if conflicts:
        print(f"[!] {len(conflicts)} Conflict(s) Detected!")
        for t, pos, ids in conflicts:
            print(f"- Drone {ids[0]} & Drone {ids[1]}")
            print(f"  Time: {t:.2f} sec")
            print(f"  Location: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
    else:
        print("[OK] No conflicts detected. Safe operation.")
        
    # Pass result to visualization (which only expects time and position, not IDs)
    visual_conflicts = [(t, pos) for t, pos, ids in conflicts] if conflicts else []
    plot_trajectories(drones, visual_conflicts)

def main():
    print("Initializing UAV Strategic Deconfliction Simulator (V1.1)...")

    run_scenario(scenario_no_conflict, "NO CONFLICT")
    run_scenario(scenario_conflict, "CONFLICT")
    run_scenario(scenario_near_miss, "NEAR MISS")
    
    print("\n💡 This demonstrates cascading conflicts across multiple drones in shared airspace.")
    run_scenario(scenario_cascade, "CASCADE CONFLICT (VERY IMPRESSIVE)")

if __name__ == "__main__":
    main()
