# Kafka Uber Simulation

This project simulates a simplified ride-hailing workflow using event-driven patterns similar to what you would see in a Kafka-based microservices system. It models rider requests, driver assignment, trip progress, cancellations, and payment events.

## What the project does

The simulation generates events through the lifecycle of a ride:

1. A rider creates a ride request.
2. A ride is assigned to an available driver in the same city.
3. The driver starts the trip.
4. The driver moves toward the pickup point.
5. The driver reaches the drop-off location.
6. The ride is marked complete and a payment event is generated.
7. Some rides may be cancelled randomly during the lifecycle.

Each stage is represented as a structured event payload, which makes the project useful for experimenting with event streaming, event processing, and message flow design.

## Why this project exists

The goal is to model a basic Kafka-style event pipeline in Python without depending on a full production infrastructure stack. It is designed to help understand:

- event generation
- state transitions in a ride lifecycle
- driver and rider availability logic
- event payload structure
- how streaming systems process real-world business events

## High-level flow

The application simulates an end-to-end ride journey like this:

- rider requests a trip
- system finds a suitable driver
- driver is assigned
- driver travels to pickup
- ride starts
- driver travels to drop-off
- ride completes
- payment event is emitted

This mirrors the flow described in the project architecture notes.

## Project structure

```text
kafka-simulation-project/
├── main.py
├── pyproject.toml
├── README.md
├── architecture/
│   └── ride-sim.md
├── py-simulator/
│   ├── driver_simulator.py
│   ├── ride_events_generator.py
│   ├── ride_simulator.py
│   └── ...
├── utilities/
│   ├── __init__.py
│   └── utils.py
└── .venv/
```

## Main components

### 1. Ride generator
The ride event generator creates ride requests and advances active rides through the lifecycle. It writes event payloads to files while simulating real-time progress.

### 2. Driver simulator
This module simulates driver locations and movement across the city. It tracks status values such as:

- available
- en_route
- on_trip
- offline

### 3. Ride simulator
This file defines the event-building functions for ride lifecycle events, including:

- ride_requested
- driver_assigned
- ride_started
- ride_completed
- ride_cancelled
- payment_event

### 4. Utility functions
The utility module contains helper methods for:

- UUID generation
- UTC timestamps
- distance calculations
- location generation
- coordinate generation

## Example event flow

A typical ride may progress like this:

```python
ride_requested
driver_assigned
ride_started
ride_completed
payment_event
```

If the ride is cancelled before completion, the flow may instead emit:

```python
ride_cancelled
```

## Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -e .
```

You can also use the project lock file if your environment supports it:

```bash
uv sync
```

## Running the simulation

From the project root, you can run the simulator scripts such as:

```bash
python py-simulator/ride_events_generator.py
python py-simulator/driver_simulator.py
```

These scripts are meant to simulate the event flow continuously over time.

## Notes

- This project is a learning and simulation project rather than a production Kafka deployment.
- The runtime behavior is intentionally simplified to model how event-driven ride systems evolve over time.
- The data and event payloads are designed to be easy to inspect and extend.

## Future improvements

Possible next steps for the project include:

- connecting the events to a real Kafka broker
- adding structured producers and consumers
- persisting events to JSON or database storage
- adding rider and driver analytics dashboards
- introducing city-specific routing and ETA logic

## Architecture reference

The project architecture notes describe the intended ride lifecycle and event flow in more detail in [architecture/ride-sim.md](architecture/ride-sim.md).
