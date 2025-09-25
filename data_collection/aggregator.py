#!/usr/bin/env python3
"""
Combined GPS + Sensor Aggregator (Python 3)
-------------------------------------------
Aggregates GPS data from Pixhawk (DroneKit) and sensor data from ESP32s,
then writes a single CSV file with the format:

timestamp(unix),latitude,longitude,altitude,temperature,pressure,humidity
"""

import socket
import threading
import time
import csv
from datetime import datetime

# Server Config
GPS_PORT = 5001      # Pixhawk / DroneKit data
SENSOR_PORT = 5000      # ESP32 sensor data
LOG_FILE = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

# Latest data storage
latest_data = {
    "timestamp_gps": "",
    "latitude": "",
    "longitude": "",
    "altitude": "",
    "timestamp_sensor": "",
    "temperature": "",
    "pressure": "",
    "humidity": ""
}

lock = threading.Lock()

# Helper to write a row
def write_row():
    with lock:
        timestamp = int(time.time())
        row = [
            latest_data["timestamp_gps"],
            latest_data["latitude"],
            latest_data["longitude"],
            latest_data["altitude"],
            latest_data["timestamp_sensor"],
            latest_data["temperature"],
            latest_data["pressure"],
            latest_data["humidity"]
        ]
        with open(LOG_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        print(f"[LOG] {row}")

# Handle GPS clients (Pixhawk)
def handle_gps(conn, addr):
    print(f"[INFO] GPS connection from {addr[0]}:{addr[1]}")
    with conn:
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                parts = data.decode().strip().split(",")
                if len(parts) >= 3:
                    with lock:
                        latest_data["timestamp_gps"] = parts[0]
                        latest_data["latitude"] = parts[1]
                        latest_data["longitude"] = parts[2]
                        latest_data["altitude"] = parts[3]
                write_row()
        except Exception as e:
            print(f"[ERROR] GPS client {addr[0]}:{addr[1]} -> {e}")
    print(f"[INFO] GPS connection closed: {addr[0]}:{addr[1]}")

# Handle sensor clients (ESP32)
def handle_sensor(conn, addr):
    print(f"[INFO] Sensor connection from {addr[0]}:{addr[1]}")
    with conn:
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                parts = data.decode().strip().split(",")
                if len(parts) >= 3:
                    with lock:
                        latest_data["timestamp_sensor"] = parts[0]
                        latest_data["temperature"] = parts[1]
                        latest_data["pressure"] = parts[2]
                        latest_data["humidity"] = parts[3]
                write_row()
        except Exception as e:
            print(f"[ERROR] Sensor client {addr[0]}:{addr[1]} -> {e}")
    print(f"[INFO] Sensor connection closed: {addr[0]}:{addr[1]}")

# Start server for a given port
def start_server(port, handler):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"[INFO] Listening on port {port}")
    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handler, args=(conn, addr))
        t.daemon = True
        t.start()

# Initialize CSV file with header
def init_csv():
    with open(LOG_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp(gps)", "latitude", "longitude", "altitude",
                         "timestamp(sensor)", "temperature", "pressure", "humidity"])

def main():
    init_csv()
    # Start GPS and sensor servers in separate threads
    threading.Thread(target=start_server, args=(GPS_PORT, handle_gps), daemon=True).start()
    threading.Thread(target=start_server, args=(SENSOR_PORT, handle_sensor), daemon=True).start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Aggregator stopped by user")

if __name__ == "__main__":
    main()
