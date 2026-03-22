# Drone Traffic Management System (ATC Simulation)

A simulation-based drone traffic management system inspired by Air Traffic Control (ATC). This project enables safe coordination of multiple drones in a shared airspace by detecting conflicts and dynamically adjusting trajectories.

---

## ✅ Features

* Multi-drone simulation (supports 30+ drones)
* Real-time conflict detection between drone paths
* Trajectory planning and deconfliction strategies
* Interactive dashboard for visualization
* Scenario-based simulation for testing different conditions

---

## 🛠️ Tech Stack

* Python
* Streamlit (for dashboard visualization)
* NumPy (for computations)
* Matplotlib (for plotting and visualization)

---

## 🚀 How to Run

### ⚙️ Install Requirements

```bash
pip install -r requirements.txt
```

---

### 📊 Run Dashboard

```bash
streamlit run infrared-station/atc_dashboard/dashboard.py
```

---

## 🧠 System Modules

### 🔹 silent-stellar (Core Module)

* Drone data models
* Trajectory generation
* Conflict detection and resolution

### 🔹 infrared-station (Visualization Module)

* Simulation engine
* Dashboard interface
* Scenario management

---

## 🧪 How It Works

* Multiple drones are initialized with predefined or random paths
* The system continuously monitors their positions
* Potential conflicts are detected based on trajectory overlap
* Deconfliction strategies are applied to avoid collisions
* Results are visualized in real-time through the dashboard

---

## 🔧 Proposed Enhancements

* Radar-based monitoring for real-time airspace scanning
* AI-based prediction for future conflict detection
* Integration with real-world drone systems

---

## 📁 Project Structure

```bash
AS/
├── silent-stellar/        # Core logic and services
├── infrared-station/      # Dashboard and simulation
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

---

## 🔑 Applications

* Drone traffic management systems
* Smart city airspace coordination
* Autonomous robotics simulations

---

## 🚧 Notes

* Ensure all dependencies are installed before running
* Use proper system resources for smooth simulation with multiple drones

---

## 👨‍💻 Author

Achal Metkari
