# ESP32 BME688 TCP Sensor Logger

This project reads temperature, humidity, and pressure from a BME688 sensor and sends the data over TCP to a Python server. Each data point includes a UNIX timestamp synchronized via NTP.

Designed for untethered ESP32 units, scalable to multiple devices sending data to a central aggregator.

## Features

- Reads temperature, humidity, pressure from BME688 sensor.

- Sends timestamped data over Wi-Fi TCP.

- UNIX timestamps synced via NTP.

- Compatible with Nologo ESP32-C3 board.

- Simple CSV format: timestamp,temp,humidity,pressure.

## Hardware Required

- Nologo ESP32-C3 board

- Adafruit BME688 sensor

- Breadboard and jumper wires (for I2C connection)

- USB cable for initial programming

## Connections
| ESP32 Pin | BME688 Pin |
| --------- | ---------- |
| 3V3       | VIN        |
| GND       | GND        |
| SDA       | SDA        |
| SCL       | SCL        |


Ensure correct I2C voltage levels (3.3V) for ESP32.

## Arduino IDE Setup

- Install ESP32 board support

- Open Arduino IDE → Preferences → Additional Boards Manager URLs:

```
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```

- Open Tools → Board → Boards Manager, search for esp32, install.

- Select your board

Tools → Board → Nologo ESP32-C3

Tools → Port → select your ESP32 COM port.

- Install required libraries

Adafruit BME680 library (works for BME688)

Sketch → Include Library → Manage Libraries → Search "Adafruit BME680" → Install

## Usage

- Update the Wi-Fi credentials in the sketch:
```cpp
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
```

- Set the Python aggregator server IP and port:
```cpp
const char* host = "192.168.1.100";
const uint16_t port = 5000;
```

- Adjust GMT offset if needed:
```cpp
const long gmtOffset_sec = 6 * 3600;  // GMT+6
```

- Upload the sketch to ESP32.

- Open Serial Monitor (115200 baud) to see connection logs and sent data.

## Data Format

Each line sent to the server (CSV):

`timestamp,temp,humidity,pressure`


Example:

`1695456789,28.3,65.2,1012.5`

- timestamp → UNIX time (seconds since epoch, synced via NTP)

- temp → Temperature in °C

- humidity → Relative humidity in %

- pressure → Pressure in hPa

## Notes

- Multiple ESP32s can connect to the same server for scalable sensor logging.

- Recommended Python aggregator for collecting data and storing/plotting.

- Adjust `delay()` in `loop()` to change measurement interval.