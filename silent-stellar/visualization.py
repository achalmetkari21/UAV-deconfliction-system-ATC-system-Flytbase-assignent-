import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple, Optional

from models.drone import Drone
from services.trajectory_service import TrajectoryService


class Plotter:
    def plot_routes(self, drones: List[Drone], conflict_info=None):
        # Apply dark theme
        plt.style.use('dark_background')
        
        fig = plt.figure(figsize=(12, 9), facecolor='#111111')
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('#111111')

        drone_segments = []
        min_t, max_t = float('inf'), 0.0

        for drone in drones:
            segments = TrajectoryService.calculate_segments(drone)
            if segments:
                min_t = min(min_t, segments[0].start_time)
                max_t = max(max_t, segments[-1].end_time)
            drone_segments.append(segments)

        colors = ['#00d2ff', '#3a7bd5', '#f12711', '#f5af19']
        drone_points = []
        glow_points = []

        # Make axes cleaner
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.grid(color='#333333', linestyle=':', linewidth=0.5)

        for i, (drone, segments) in enumerate(zip(drones, drone_segments)):
            xs, ys, zs = [], [], []

            for seg in segments:
                xs.append(seg.start_pos.x)
                ys.append(seg.start_pos.y)
                zs.append(seg.start_pos.z)

            if segments:
                xs.append(segments[-1].end_pos.x)
                ys.append(segments[-1].end_pos.y)
                zs.append(segments[-1].end_pos.z)

            ax.plot(xs, ys, zs, linestyle='--', color=colors[i % len(colors)], alpha=0.5, label=f"{drone.id} Path")

            point, = ax.plot([], [], [], marker='o', markersize=8, color=colors[i % len(colors)], label=f"{drone.id} UAV")
            drone_points.append(point)
            
            glow, = ax.plot([], [], [], marker='o', markersize=15, alpha=0.3, color=colors[i % len(colors)])
            glow_points.append(glow)

        conflict_scatters = []
        if conflict_info:
            for idx, (t, pos) in enumerate(conflict_info):
                lbl = "Conflict Point" if idx == 0 else ""
                cs = ax.scatter(pos[0], pos[1], pos[2], color='#ff3333', s=150, marker='X', label=lbl)
                ax.scatter(pos[0], pos[1], pos[2], color='#ff3333', s=400, alpha=0.2, marker='o') # Conflict glow
                conflict_scatters.append(cs)

        # Add Time Display
        time_text = ax.text2D(0.05, 0.95, '', transform=ax.transAxes, color='white', fontsize=12, fontweight='bold')

        ax.set_title("UAV Deconfliction Dashboard", color='white', fontsize=14, pad=20)
        ax.set_xlabel("X (m)", color='lightgrey')
        ax.set_ylabel("Y (m)", color='lightgrey')
        ax.set_zlabel("Z (m)", color='lightgrey')
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.0), facecolor='#222222', edgecolor='none', labelcolor='white')
        
        plt.tight_layout()

        fps = 60
        duration = max_t - min_t
        total_frames = max(int(duration * fps), 1) if duration > 0 else 60

        def get_pos(segments, t):
            for seg in segments:
                if seg.start_time <= t <= seg.end_time:
                    dt = seg.end_time - seg.start_time
                    if dt == 0:
                        return (seg.start_pos.x, seg.start_pos.y, seg.start_pos.z)

                    ratio = (t - seg.start_time) / dt
                    return (
                        seg.start_pos.x + ratio * (seg.end_pos.x - seg.start_pos.x),
                        seg.start_pos.y + ratio * (seg.end_pos.y - seg.start_pos.y),
                        seg.start_pos.z + ratio * (seg.end_pos.z - seg.start_pos.z)
                    )
            return (segments[-1].end_pos.x, segments[-1].end_pos.y, segments[-1].end_pos.z)

        def update(frame):
            t = min_t + frame / fps
            time_text.set_text(f'Time: {t:.2f}s')

            for i, segments in enumerate(drone_segments):
                pos = get_pos(segments, t)

                drone_points[i].set_data([pos[0]], [pos[1]])
                drone_points[i].set_3d_properties([pos[2]])
                
                glow_points[i].set_data([pos[0]], [pos[1]])
                glow_points[i].set_3d_properties([pos[2]])

            # Add pulsating glow effect for all conflicts
            if conflict_scatters:
                scale = 150 + 100 * (frame % 20) / 20.0
                for cs in conflict_scatters:
                    cs.set_sizes([scale])

            return drone_points + glow_points + [time_text]

        self.anim = animation.FuncAnimation(fig, update, frames=total_frames + fps, interval=1000/fps, blit=False)
        plt.show(block=True)


def plot_trajectories(drones, conflict_info=None):
    plotter = Plotter()
    plotter.plot_routes(drones, conflict_info)