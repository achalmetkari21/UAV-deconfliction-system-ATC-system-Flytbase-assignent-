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
