import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from models import Drone, Position
from scenarios import get_scenarios
from simulation import Simulator, TrajectoryService
from conflict_engine import detect_future_conflicts
from preflight import check_preflight
from replay import ReplayBuffer

st.set_page_config(page_title="UAV ATC Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for dark theme and clean alerts
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .safe-alert { background-color: #004d00; padding: 10px; border-radius: 5px; color: #00ff00; margin-bottom: 10px; }
    .warning-alert { background-color: #4d4d00; padding: 10px; border-radius: 5px; color: #ffff00; margin-bottom: 10px; }
    .conflict-alert { background-color: #4d0000; padding: 10px; border-radius: 5px; color: #ff3333; margin-bottom: 10px; }
    .metric-value { font-size: 1.5rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 1. Init Session State
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.running = False
    st.session_state.current_time = 0.0
    st.session_state.scenario_name = "Mass Traffic"
    st.session_state.simulator = None
    st.session_state.replay_buffer = ReplayBuffer(max_seconds=20)
    st.session_state.workflow_step = "1. Select Scenario"
    st.session_state.new_drone_counter = 1
    st.session_state.drone_count_history = []
    st.session_state.conflict_count_history = []
    st.session_state.last_time = time.time()

def init_scenario(name):
    scenarios = get_scenarios()
    drones = scenarios[name]()
    st.session_state.simulator = Simulator(drones)
    st.session_state.current_time = 0.0
    st.session_state.replay_buffer.clear()
    st.session_state.drone_count_history.clear()
    st.session_state.conflict_count_history.clear()
    st.session_state.running = False

if st.session_state.simulator is None:
    init_scenario(st.session_state.scenario_name)

# 2. Sidebar
st.sidebar.title("ATC Workflow")
workflow_steps = [
    "1. Select Scenario",
    "2. Preflight",
    "3. Start Simulation / Monitor",
    "4. Replay"
]
st.session_state.workflow_step = st.sidebar.radio(
    "Select Action", 
    workflow_steps, 
    index=workflow_steps.index(st.session_state.workflow_step) if st.session_state.workflow_step in workflow_steps else 0
)

filter_mode = "All Drones"
if "Monitor" in st.session_state.workflow_step:
    st.sidebar.markdown("### Simulation Controls")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("▶ Start/Resume"):
            st.session_state.running = True
            st.session_state.last_time = time.time()
    with col2:
        if st.button("⏸ Pause"):
            st.session_state.running = False

    st.sidebar.metric("Sim Time", f"{st.session_state.current_time:.1f} s")
    
    st.sidebar.markdown("### Smart Filter")
    filter_mode = st.sidebar.selectbox("Filter View", ["All Drones", "Only Conflicts", "Unknown Only", "Controlled Only"])


# Fetch Current State
sim = st.session_state.simulator
all_active_states = sim.simulate_drones(st.session_state.current_time)
conflicts = detect_future_conflicts(sim.trajectories, st.session_state.current_time)

# Apply Smart Filters
active_states = all_active_states
if filter_mode == "Unknown Only":
    active_states = [s for s in active_states if s.get('type') == 'unknown']
elif filter_mode == "Controlled Only":
    active_states = [s for s in active_states if s.get('type') == 'controlled']
elif filter_mode == "Only Conflicts":
    conflict_drones = {c.drone1 for c in conflicts}.union({c.drone2 for c in conflicts})
    active_states = [s for s in active_states if s['id'] in conflict_drones]

def render_3d_plot(states, conflicts=None, focus_mode=False):
    fig = go.Figure()
    
    # Render trajectories for visible states only to save perf
    visible_ids = {s['id'] for s in states}
    
    for d_id, segs in sim.trajectories.items():
        if focus_mode and d_id not in visible_ids:
            continue
            
        xs = [s.start_pos.x for s in segs] + ([segs[-1].end_pos.x] if segs else [])
        ys = [s.start_pos.y for s in segs] + ([segs[-1].end_pos.y] if segs else [])
        zs = [s.start_pos.z for s in segs] + ([segs[-1].end_pos.z] if segs else [])
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs, mode='lines',
            line=dict(dash='dash', width=2), opacity=0.2, name=f"{d_id} Path", showlegend=False
        ))

    # Render active drones
    for state in states:
        color = '#ffff00' if state.get('status') == 'PAUSED' else '#00ff00'
        if state.get('type') == 'unknown':
            color = '#ff9900'  # Orange for unknown
        
        # Highlight if in critical conflict
        is_high_risk = any(c.severity == "HIGH" for c in (conflicts or []) if c.drone1 == state['id'] or c.drone2 == state['id'])
        if is_high_risk: color = '#ff3333'
        
        symbol = 'diamond' if state.get('type') == 'unknown' else 'circle'
        
        fig.add_trace(go.Scatter3d(
            x=[state['x']], y=[state['y']], z=[state['z']],
            mode='markers+text',
            marker=dict(size=6, color=color, symbol=symbol),
            text=[state['id']], textposition='top center',
            name=state['id'], showlegend=False
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(showgrid=True, gridcolor='#333333', zeroline=False, showbackground=True, backgroundcolor='#111111'),
            yaxis=dict(showgrid=True, gridcolor='#333333', zeroline=False, showbackground=True, backgroundcolor='#111111'),
            zaxis=dict(showgrid=True, gridcolor='#333333', zeroline=False, showbackground=True, backgroundcolor='#111111'),
            bgcolor='#111111'
        ),
        paper_bgcolor='#0e1117',
        margin=dict(l=0, r=0, b=0, t=0),
        height=500
    )
    return fig

def render_mini_radar(states, conflicts):
    fig = go.Figure()
    
    # Add origin / range circles
    fig.add_shape(type="circle", x0=-500, y0=-500, x1=500, y1=500, line_color="#333", opacity=0.5)
    fig.add_shape(type="circle", x0=-250, y0=-250, x1=250, y1=250, line_color="#333", opacity=0.3)
    
    xs, ys, colors, texts, symbols = [], [], [], [], []
    for s in states:
        xs.append(s['x'])
        ys.append(s['y'])
        texts.append(s['id'])
        # check conflict
        is_conflict = any(c.severity == "HIGH" and (c.drone1 == s['id'] or c.drone2 == s['id']) for c in conflicts)
        is_warning = any(c.severity == "WARNING" and (c.drone1 == s['id'] or c.drone2 == s['id']) for c in conflicts)
        
        if is_conflict: colors.append('#ff3333')
        elif is_warning: colors.append('#ffff00')
        elif s.get('type') == 'unknown': colors.append('#ff9900')
        else: colors.append('#00ff00')
        
        symbols.append('diamond-wide' if s.get('type') == 'unknown' else 'circle')
        
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode='markers', 
        marker=dict(color=colors, size=8, symbol=symbols), 
        text=texts, hoverinfo='text', showlegend=False
    ))
    
    fig.update_layout(
        xaxis=dict(range=[-600, 600], showgrid=False, zeroline=True, zerolinecolor='#333', visible=False),
        yaxis=dict(range=[-600, 600], showgrid=False, zeroline=True, zerolinecolor='#333', visible=False),
        paper_bgcolor='#0e1117', plot_bgcolor='#0e1117',
        margin=dict(l=0, r=0, b=0, t=30), height=300,
        title=dict(text="Mini Radar (2D X-Y View)", font=dict(color='#fafafa', size=14))
    )
    return fig

# 3. Main Views
if st.session_state.workflow_step == "1. Select Scenario":
    st.header("Scenario Selection")
    scenarios = get_scenarios()
    selected = st.selectbox("Choose Scenario", list(scenarios.keys()), index=list(scenarios.keys()).index(st.session_state.scenario_name))
    if st.button("Load Scenario"):
        st.session_state.scenario_name = selected
        init_scenario(selected)
        st.rerun()
        
    st.plotly_chart(render_3d_plot(active_states), use_container_width=True)

elif st.session_state.workflow_step == "2. Preflight":
    st.header("Preflight Clearance")
    st.plotly_chart(render_3d_plot(active_states), use_container_width=True)
    
    st.subheader("Add New Mission (Flight Plans)")
    c1, c2, c3 = st.columns(3)
    start_x = c1.number_input("Start X", value=0)
    start_y = c2.number_input("Start Y", value=0)
    start_z = c3.number_input("Start Z", value=50)
    
    e1, e2, e3 = st.columns(3)
    end_x = e1.number_input("End X", value=100)
    end_y = e2.number_input("End Y", value=100)
    end_z = e3.number_input("End Z", value=50)
    
    v = st.number_input("Velocity", value=20.0)
    t = st.number_input("Start Time", value=st.session_state.current_time + 5.0)
    
    if st.button("Check Preflight"):
        new_d_id = f"New_Drone_{st.session_state.new_drone_counter}"
        waypoints = [(start_x, start_y, start_z), (end_x, end_y, end_z)]
        new_drone = Drone(new_d_id, waypoints, v, t)
        
        status, msg = check_preflight(new_drone, sim.trajectories, st.session_state.current_time)
        
        if status == "APPROVE":
            st.markdown(f"<div class='safe-alert'>🟢 APPROVE: {msg}</div>", unsafe_allow_html=True)
            if st.button("Add to Simulation"):
                sim.drones[new_d_id] = new_drone
                sim.trajectories[new_d_id] = TrajectoryService.calculate_segments(new_drone)
                sim.drone_time_offsets[new_d_id] = 0.0
                st.session_state.new_drone_counter += 1
                st.success("Added.")
        elif status == "DELAY":
            st.markdown(f"<div class='warning-alert'>🟡 DELAY: {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='conflict-alert'>🔴 REJECT: {msg}</div>", unsafe_allow_html=True)

elif "Monitor" in st.session_state.workflow_step:
    st.header("ATC Monitor Dashboard")
    
    top_col1, top_col2 = st.columns([2, 1])
    
    with top_col1:
        st.subheader("Airspace Visualization (3D)")
        # Performance limiting: Limit visualization to max 10 drones if Focus Mode is enabled.
        display_states = active_states
        focus_mode = st.toggle("Focus Mode (Limit visualization to 10 drones)", value=len(display_states) > 10)
        if focus_mode and len(display_states) > 10:
            # prioritize conflicts or unknowns, otherwise take first 10
            conflict_ids = {c.drone1 for c in conflicts}.union({c.drone2 for c in conflicts})
            focused = [s for s in display_states if s['id'] in conflict_ids]
            rem = 10 - len(focused)
            if rem > 0:
                focused += [s for s in display_states if s not in focused][:rem]
            display_states = focused
            
        st.plotly_chart(render_3d_plot(display_states, conflicts, focus_mode=True), use_container_width=True)
        
    with top_col2:
        st.subheader("📅 Conflict Timeline")
        if conflicts:
            # Sorted by time to impact
            for c in sorted(conflicts, key=lambda x: x.time_to_impact)[:8]:
                sym = "🔴" if c.severity == "HIGH" else "🟡"
                st.markdown(f"> {sym} **t +{c.time_to_impact:.1f}s** → `{c.drone1}` vs `{c.drone2}`")
        else:
            st.markdown("<div class='safe-alert'>🟢 Airspace is safe - No predictive conflicts</div>", unsafe_allow_html=True)
        
        st.divider()
        st.plotly_chart(render_mini_radar(all_active_states, conflicts), use_container_width=True)
            
    st.divider()
    
    bot_col1, bot_col2 = st.columns([1, 1])
    
    with bot_col1:
        st.subheader("📊 Performance Monitoring")
        # Record history (only while running)
        if st.session_state.running:
            st.session_state.drone_count_history.append(len(all_active_states))
            st.session_state.conflict_count_history.append(len(conflicts))
            # Keep max 60 data points
            if len(st.session_state.drone_count_history) > 60:
                st.session_state.drone_count_history.pop(0)
            if len(st.session_state.conflict_count_history) > 60:
                st.session_state.conflict_count_history.pop(0)
                
        if st.session_state.drone_count_history:
            df = pd.DataFrame({
                "Total Active Drones": st.session_state.drone_count_history,
                "Predicted Conflicts": st.session_state.conflict_count_history
            })
            st.line_chart(df, height=200)
            
        latency = (time.time() - st.session_state.last_time)*1000 if st.session_state.running else 0
        c1, c2 = st.columns(2)
        c1.metric("System Load", "HIGH" if len(all_active_states) > 20 else "NORMAL")
        c2.metric("Sim Latency", f"~{latency:.0f} ms")
        
    with bot_col2:
        st.subheader("Active Drones Control")
        # List a few drones to display/control (maximum 8 for clean UI)
        for state in display_states[:8]:
            c1, c2, c3 = st.columns([2, 1, 1])
            ctype = "🤖" if state.get('type') == 'controlled' else "❓"
            c1.markdown(f"{ctype} **{state['id']}** (Alt: {state['z']:.0f}m)")
            
            if state['status'] == "ACTIVE":
                if c2.button("Pause", key=f"pause_{state['id']}"):
                    sim.pause_drone(state['id'], st.session_state.current_time)
                    st.rerun()
            else:
                c1.markdown(f"<span style='color: yellow'>Paused {state['pause_duration']:.1f}s</span>", unsafe_allow_html=True)
                if c2.button("Resume", key=f"resume_{state['id']}"):
                    sim.resume_drone(state['id'], st.session_state.current_time)
                    st.rerun()
            
            if c3.button("Preview", key=f"preview_{state['id']}"):
                safe = not any(c.drone1 == state['id'] or c.drone2 == state['id'] for c in conflicts)
                if safe: st.toast(f"✅ {state['id']} clear to resume")
                else: st.toast(f"⚠️ {state['id']} conflicts predicted")

elif st.session_state.workflow_step == "4. Replay":
    st.header("Incident Replay Panel")
    st.session_state.running = False
    
    history = st.session_state.replay_buffer.get_replay()
    if not history:
        st.info("No history recorded yet. Start the simulation in the Monitor tab first.")
    else:
        frame_idx = st.slider("Select Timeline", 0, len(history)-1, len(history)-1)
        frame = history[frame_idx]
        st.write(f"Replay Time: **{frame['time']:.1f}s**")
        st.plotly_chart(render_3d_plot(frame['states']), use_container_width=True)

# Main Loop Execution for ~1Hz updates
if st.session_state.running and "Monitor" in st.session_state.workflow_step:
    st.session_state.replay_buffer.add_state(st.session_state.current_time, all_active_states)
    st.session_state.last_time = time.time()
    time.sleep(1.0)
    st.session_state.current_time += 1.0
    st.rerun()
