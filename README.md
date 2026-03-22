# Drone Traffic Management System (ATC Simulation)

A configurable and scalable drone traffic simulation platform for real-time multi-agent coordination.
Inspired by Air Traffic Control (ATC), this system manages multiple drones in shared airspace by detecting conflicts and dynamically adjusting trajectories.

---

## Overview

With the rapid growth of drone applications in logistics, surveillance, and smart cities, managing multiple drones safely has become a critical challenge.
This project simulates a drone traffic management system that ensures safe and efficient operation through real-time monitoring, conflict detection, and trajectory planning.

---

## Features

* Multi-drone simulation (supports 30+ drones)
* Real-time conflict detection and resolution
* Trajectory planning and deconfliction
* Interactive dashboard for visualization
* Scenario-based simulation testing

---

## User Configuration

The system allows users to customize simulation parameters to test different conditions:

### Drone Configuration

* Modify number of drones in the simulation
* Adjust initial positions and waypoints
* Define custom trajectories

### Safety Parameters

* Set minimum safe distance between drones
* Adjust conflict detection thresholds

### Simulation Control

* Change simulation speed
* Run predefined or custom scenarios
* Replay simulations for analysis

---

## Scalability

The system is designed to handle increasing complexity:

* Supports 30+ drones simultaneously
* Extendable to larger drone fleets
* Modular architecture for easy expansion

---

## Tech Stack

* Python
* Streamlit (dashboard visualization)
* NumPy
* Matplotlib

---

## How to Run

### Install Dependencies

pip install -r requirements.txt

### Run the Dashboard

streamlit run infrared-station/atc_dashboard/dashboard.py

---
## How to Use

1. Run the application using Streamlit:
   streamlit run infrared-station/atc_dashboard/dashboard.py

2. Once executed, the application will automatically open in your default browser.
   If it does not open, check the terminal for a message like:

   Local URL: http://localhost:8501

   Copy and paste this URL into your browser.

---

### Dashboard Interaction

After opening the dashboard:

1. Locate the control panel (usually on the left sidebar).

2. Start the simulation:

   * Click on the **Start / Run Simulation** button (if available)
   * This initializes multiple drones in the airspace

3. Observe the visualization:

   * Drones will appear moving along predefined or generated paths
   * Each drone represents an independent agent in the system

4. Monitor conflict detection:

   * The system continuously checks for path overlaps
   * Potential conflicts (collisions) are identified in real time

5. Analyze system behavior:

   * Observe how trajectories are adjusted to avoid collisions
   * Watch how the system maintains safe distance between drones

---

### Experiment with Scenarios

You can test different conditions to evaluate performance:

* Increase the number of drones (if configurable in UI or code)
* Modify paths or scenarios from the configuration files
* Run dense traffic scenarios to observe system limits

---

### What to Look For

While running the simulation, focus on:

* Smooth drone movement and trajectory visualization
* Detection of potential collision points
* System response in avoiding conflicts
* Overall stability with multiple drones

---

### Notes

* Ensure all dependencies are installed before running the project
* For better performance, run on a system with sufficient resources when simulating many drones


## System Architecture

### silent-stellar (Core Module)

* Drone data models
* Trajectory generation
* Conflict detection and resolution

### infrared-station (Visualization Module)

* Simulation engine
* Dashboard interface
* Scenario management

---

## How It Works

* Multiple drones are initialized with predefined or random paths
* The system continuously monitors their positions
* Potential conflicts are detected based on trajectory overlap
* Deconfliction strategies are applied to avoid collisions
* Results are visualized in real-time through the dashboard

---

## Engineering Highlights

* Modular design separating core logic and visualization
* Real-time monitoring and dynamic conflict resolution
* Configurable simulation parameters for experimentation
* Designed with scalability and extensibility in mind

---

## Applications

* Drone traffic management systems
* Smart city airspace coordination
* Autonomous robotics and multi-agent systems

---

## Future Scope

* AI-based predictive conflict detection
* Radar-based real-time monitoring system
* Integration with real-world drone hardware
* Cloud-based simulation environment

---

## Project Structure

AS/
├── silent-stellar/        # Core logic and services
├── infrared-station/      # Dashboard and simulation
├── requirements.txt       # Dependencies
└── README.md              # Documentation

---

## Author

Achal Metkari
