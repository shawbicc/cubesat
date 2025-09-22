#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
GPS Aggregator Script (Laptop Side)
-----------------------------------
This script runs on your laptop (192.168.1.100) and listens for GPS data
sent from multiple ESP32C3 boards.
Each client sends messages over TCP to port 5000, and this server
logs and displays them.
"""

import socket
import threading
import time

# Server Config
HOST = "0.0.0.0"     # Listen on all interfaces (must be 192.168.0.118 in LAN)
PORT = 5000          # Must match ESP32 client port

# File for logging
LOG_FILE = "gps_aggregated.csv"

def handle_client(conn, addr):
    print("[INFO] New connection from: {}:{}".format(addr[0], addr[1]))
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break  # Client disconnected
                decoded = data.strip()
                timestamp = int(time.time())
                log_line = "{},{},{}\n".format(timestamp, addr[0], decoded)
                print("[DATA] {}".format(log_line.strip()))
                
                # Append to log file
                with open(LOG_FILE, "a") as f:
                    f.write(log_line)

            except Exception as e:
                print("[ERROR] Client {}:{} -> {}".format(addr[0], addr[1], e))
                break
    print("[INFO] Connection closed: {}:{}".format(addr[0], addr[1]))

def main():
    # Create TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print("[INFO] GPS Aggregator running on {}:{}".format(HOST, PORT))

    # Write CSV header if file is new
    try:
        open(LOG_FILE, "r")
    except:
        with open(LOG_FILE, "w") as f:
            f.write("unix_timestamp,client_ip,gps_data\n")

    # Accept clients
    while True:
        conn, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    main()
