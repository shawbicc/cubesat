from dronekit import connect, VehicleMode
import time
import socket

# --- Config ---
PIXHAWK_CONNECTION = "/dev/serial/by-id/usb-FTDI_FT231X_USB_UART_D30EZNO6-if00-port0"
BAUD_RATE = 57600
SERVER_IP = "192.168.43.100"   # same IP as aggregator
SERVER_PORT = 5001

def arm_and_takeoff(vehicle, target_altitude=0.4):
    """
    Arms the vehicle and takes off to a target altitude (meters).
    """
    print("[INFO] Arming drone...")

    while not vehicle.is_armable:
        print("[INFO] Waiting for vehicle to become armable...")
        time.sleep(1)

    # vehicle.mode = VehicleMode("GUIDED")
    # while vehicle.mode.name != "GUIDED":
    #     print("[INFO] Waiting for GUIDED mode...")
    #     time.sleep(1)

    vehicle.armed = True
    while not vehicle.armed:
        print("[INFO] Waiting for arming...")
        time.sleep(1)

    # print("[INFO] Drone armed, taking off...")
    # vehicle.simple_takeoff(target_altitude)

    # # wait until target altitude is reached
    # while True:
    #     altitude = vehicle.location.global_relative_frame.alt
    #     print("[INFO] Altitude: %.2f m" % altitude)
    #     if altitude >= target_altitude * 0.95:
    #         print("[INFO] Target altitude reached.")
    #         break
    #     time.sleep(1)

def main():
    print("[INFO] Connecting to Pixhawk...")
    vehicle = connect(PIXHAWK_CONNECTION, baud=BAUD_RATE, wait_ready=True)
    print("[INFO] Connected.")

    # Arm and takeoff
    arm_and_takeoff(vehicle, target_altitude=2)

    # Setup TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    print("[INFO] Connected to aggregator at {}:{}".format(SERVER_IP, SERVER_PORT))

    try:
        while True:
            loc = vehicle.location.global_frame
            timestamp = int(time.time())
            latitude = loc.lat
            longitude = loc.lon
            altitude = loc.alt

            # Format: timestamp,lat,lon,alt
            data = "{},{},{},{}\n".format(timestamp, latitude, longitude, altitude)
            sock.sendall(data.encode("utf-8"))
            print("[TX] " + data.strip())

            time.sleep(1)  # send every 1s

    except KeyboardInterrupt:
        print("[INFO] Interrupted. Landing drone...")
        vehicle.mode = VehicleMode("LAND")
        sock.close()
        vehicle.close()

if __name__ == "__main__":
    main()
