#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
from dronekit import connect, VehicleMode
import socket
import time

# ==========================
# CONFIGURATION
# ==========================
# Pixhawk connection string
# For USB: '/dev/ttyUSB0'
# For SITL: 'udp:127.0.0.1:14550'
PIXHAWK_CONNECTION = '/dev/serial/by-id/usb-FTDI_FT231X_USB_UART_D30EZNO6-if00-port0'
# vehicle = connect(PIXHAWK_CONNECTION, baud=57600, wait_ready=True, timeout=120)

# Aggregator server (where ESP32 also sends data)
# SERVER_IP   = "192.168.43.100"   # change to your aggregator machine IP
SERVER_IP   = "192.168.0.113"   # change to your aggregator machine IP
SERVER_PORT = 5001

# Measurement rate (seconds)
SEND_INTERVAL = 2.0

# ==========================
# MAIN
# ==========================

def main():
    print("[INFO] Connecting to Pixhawk...")
    vehicle = connect(PIXHAWK_CONNECTION, baud=57600, wait_ready=False)
    print("[INFO] Connected.")
    vehicle.wait_ready('gps_0', timeout=120)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    print("[INFO] Connected to aggregator server at {}:{}".format(SERVER_IP, SERVER_PORT))

    try:
        while True:
            gps = vehicle.location.global_frame
            # Unix timestamp
            timestamp = int(time.time())
            # Latitude, Longitude, Altitude
            lat = gps.lat if gps.lat is not None else 0.0
            lon = gps.lon if gps.lon is not None else 0.0
            alt = gps.alt if gps.alt is not None else 0.0

            # CSV line
            line = "{},{},{},{}".format(timestamp, lat, lon, alt)
            sock.sendall(line + "\n")

            print("[SENT]", line)
            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")

    finally:
        sock.close()
        vehicle.close()
        print("[INFO] Closed connections.")


if __name__ == "__main__":
    main()
