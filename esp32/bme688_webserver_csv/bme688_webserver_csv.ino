#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <WebServer.h>

// // WiFi credentials
// const char* ssid = "Sabik";
// const char* password = "sabik2409";

const char* ssid = "Spothot";
const char* password = "hush1234";

// I2C BME688
Adafruit_BME680 bme;
WebServer server(80);

// Store sensor readings
float temperature = 0, pressure = 0, humidity = 0;

void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CubeSat Sensors</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Bootstrap 5 -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    canvas {
      max-width: 100%;
      height: 500px;
    }
  </style>
</head>
<body>

<div class="container mt-4">
  <h2 class="text-center mb-4">CubeSat Live Sensor Dashboard</h2>
  <div class="row">
    <div class="col-md-4 mb-4">
      <canvas id="tempChart"></canvas>
    </div>
    <div class="col-md-4 mb-4">
      <canvas id="pressureChart"></canvas>
    </div>
    <div class="col-md-4 mb-4">
      <canvas id="humidityChart"></canvas>
    </div>
  </div>
  <div class="text-center mt-3">
    <button id="downloadBtn" class="btn btn-primary">Download CSV</button>
  </div>
</div>

<script>
  const MAX_POINTS = 20;       // number of data points shown on graph
  const MAX_STORAGE = 100000;  // max stored rows
  const TRIM_BATCH = 100;      // delete this many when limit exceeded
  const TRIM_INTERVAL = 10;    // check trimming every 10 new points
  let newCount = 0;

  const ESP32_URL = "/data";

  // Initialize storage if empty
  if (!localStorage.getItem("sensorData")) {
    localStorage.setItem("sensorData", JSON.stringify([]));
  }

  const createChart = (ctx, label, borderColor, bgColor, yMin, yMax, yLabel) => {
    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: label,
          data: [],
          borderColor: borderColor,
          backgroundColor: bgColor,
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 500,
          easing: 'easeOutQuart'
        },
        scales: {
          x: {
            ticks: {
              maxTicksLimit: 5
            }
          },
          y: {
            min: yMin,
            max: yMax,
            title: {
              display: true,
              text: yLabel
            }
          }
        }
      }
    });
  };

  const tempChart = createChart(document.getElementById('tempChart'), 'Temperature (°C)', 'red', 'rgba(255,0,0,0.1)', 0, 100, '°C');
  const pressureChart = createChart(document.getElementById('pressureChart'), 'Pressure (hPa)', 'blue', 'rgba(0,0,255,0.1)', 900, 1100, 'hPa');
  const humidityChart = createChart(document.getElementById('humidityChart'), 'Humidity (%)', 'green', 'rgba(0,128,0,0.1)', 0, 100, '%RH');

  function updateChart(chart, value) {
    const now = new Date().toLocaleTimeString();
    chart.data.labels.push(now);
    chart.data.datasets[0].data.push(value);
    if (chart.data.labels.length > MAX_POINTS) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }
    chart.update();
  }

  function storeData(timestamp, temp, pres, hum) {
    let dataArr = JSON.parse(localStorage.getItem("sensorData"));
    dataArr.push({time: timestamp, t: temp, p: pres, h: hum});
    newCount++;

    if (dataArr.length > MAX_STORAGE && newCount >= TRIM_INTERVAL) {
      dataArr.splice(0, TRIM_BATCH); // remove oldest entries
      newCount = 0;
    }

    localStorage.setItem("sensorData", JSON.stringify(dataArr));
  }

  async function fetchData() {
    try {
      const response = await fetch(ESP32_URL);
      const data = await response.json();

      const now = new Date();
      const timestamp = Math.floor(Date.now() / 1000); // UNIX timestamp (seconds)


      updateChart(tempChart, data.temperature);
      updateChart(pressureChart, data.pressure);
      updateChart(humidityChart, data.humidity);

      storeData(timestamp, data.temperature, data.pressure, data.humidity);
    } catch (err) {
      console.error("Failed to fetch ESP32 data:", err);
    }
  }

  // Download CSV button
  document.getElementById("downloadBtn").addEventListener("click", () => {
    let dataArr = JSON.parse(localStorage.getItem("sensorData"));
    let csv = "Date Time,Temperature,Pressure,Humidity\\n";
    dataArr.forEach(row => {
      csv += row.time + " " + row.t + " " + row.p + " " + row.h + "\\n";
    });
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.setAttribute("href", url);
    a.setAttribute("download", "sensors.csv");
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  });

  // Fetch data every 1 second
  setInterval(fetchData, 1000);
</script>

</body>
</html>
  )rawliteral";
  server.send(200, "text/html", html);
}

void handleData() {
  String json = "{";
  json += "\"temperature\":" + String(temperature, 2) + ",";
  json += "\"pressure\":" + String(pressure, 2) + ",";
  json += "\"humidity\":" + String(humidity, 2);
  json += "}";
  server.send(200, "application/json", json);
}

void setup() {
  Serial.begin(115200);
  Wire.begin(5, 4); // SDA = GPIO5, SCL = GPIO4

  if (!bme.begin(0x77)) {
    Serial.println("BME688 not found");
    while (1);
  }

  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(0, 0); // disable gas heater

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.begin();
}

void loop() {
  if (bme.performReading()) {
    temperature = bme.temperature;
    pressure = bme.pressure / 100.0; // hPa
    humidity = bme.humidity;
  }
  server.handleClient();
  delay(1000);
}
