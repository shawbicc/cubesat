#include <WiFi.h>
#include <Adafruit_BME680.h>
#include <time.h>

// WiFi credentials
const char* ssid     = "Spothot";
const char* password = "hush1234";

// Server details
const char* host = "192.168.43.100";   // Change to your server IP
const uint16_t port = 5000;

// NTP server details
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 6 * 3600;  // GMT+6 in seconds
const int   daylightOffset_sec = 0;   // Adjust if needed

// BME688 sensor
Adafruit_BME680 bme; 

WiFiClient client;

void setup() {
  Serial.begin(115200);

  // Connect WiFi
  Serial.printf("Connecting to %s ", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" CONNECTED");

  // Init NTP
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

  // Init BME688
  if (!bme.begin(0x77)) {
    Serial.println("Could not find a valid BME688 sensor, check wiring!");
    while (1);
  }

  // Set up BME688
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms
}

time_t getTimeNow() {
  time_t now;
  time(&now);
  return now;
}

void loop() {
  if (!client.connected()) {
    Serial.println("Connecting to server...");
    if (!client.connect(host, port)) {
      Serial.println("Connection to server failed.");
      delay(2000);
      return;
    }
  }

  if (! bme.performReading()) {
    Serial.println("Failed to perform reading :(");
    return;
  }

  // Get UNIX timestamp
  time_t now = getTimeNow();

  // Format data: timestamp,temp,humidity,pressure
  String data = String((long)now) + "," +
                String(bme.temperature) + "," +
                String(bme.humidity) + "," +
                String(bme.pressure / 100.0F);

  // Send to server
  client.println(data);
  Serial.println("Sent: " + data);

  delay(5000); // every 5 seconds
}
