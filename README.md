# SDN Traffic Monitoring and Stats

This project demonstrates a simple Software Defined Networking (SDN) setup using Mininet, a Ryu controller, and a Flask dashboard.

## Project Overview

- `custom_topology.py` creates a small Mininet topology with 3 OpenFlow 1.3 switches and 6 hosts.
- `traffic_monitor.py` runs a Ryu controller app that learns MAC addresses, installs forwarding rules, and periodically collects flow and port statistics.
- `dashboard.py` serves a Flask web app that reads the latest report and shows live traffic data, flow tables, port counters, and history.
- `dashboard.html` contains the dashboard UI used by the Flask app.
- `traffic_report.json` stores the latest generated report from the controller.

## How It Works

1. Mininet starts the network topology.
2. The Ryu controller connects to the switches and handles packet-in events.
3. The controller writes periodic statistics into `traffic_report.json`.
4. The Flask dashboard reads that file and exposes API endpoints for the browser UI.

## Requirements

- Linux environment is recommended for Mininet and Ryu.
- Python 3.
- Mininet.
- Ryu.
- Flask.
- A browser for the dashboard UI.

## Suggested Setup

1. Install Mininet and Ryu on your Linux system or in a Linux VM/WSL environment.
2. Install Python dependencies for the dashboard, including Flask.
3. Keep the project files in the same folder so the dashboard can load `dashboard.html`.

## Run Order

1. Start the Ryu controller with `traffic_monitor.py`.
2. Start the Mininet topology with `custom_topology.py`.
3. Start the dashboard with `dashboard.py`.
4. Open the dashboard in a browser at `http://127.0.0.1:8080`.

## Dashboard Endpoints

- `GET /` returns the HTML dashboard.
- `GET /api/live` returns the latest traffic report.
- `GET /api/history` returns saved report snapshots.

## Important Notes

- The current code uses hardcoded Linux file paths for `traffic_report.json` and `traffic_history.json` inside `traffic_monitor.py` and `dashboard.py`. If you run the project from a different folder or on Windows, update those paths before starting the apps.
- The project expects the controller and dashboard to be able to read and write the same report file.
- If the dashboard shows no data, check that the Ryu controller is running and that the Mininet switches are connected.

## File Structure

- `custom_topology.py` - Mininet topology and test traffic.
- `traffic_monitor.py` - Ryu controller and statistics collector.
- `dashboard.py` - Flask API and dashboard server.
- `dashboard.html` - frontend dashboard page.
- `traffic_report.json` - latest generated statistics.
- `sdn_project_new/` - additional project folder copy.

## Troubleshooting

- If you see no live data, confirm that `traffic_report.json` is being updated by the controller.
- If Mininet cannot connect to the controller, verify the controller IP and port in `custom_topology.py`.
- If the dashboard cannot start, make sure Flask is installed and that port 8080 is free.

This project is a compact SDN traffic monitoring demo and can be extended with alerts, richer graphs, or persistence for longer history.