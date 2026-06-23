# Smart Factory Predictive Maintenance — Complete Project Guide
### NCI MSc Cloud Computing | Fog & Edge Computing (H9FECC) | Due: 27 July 2026

---

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Prerequisites & Setup](#2-prerequisites--setup)
3. [Project Folder Structure](#3-project-folder-structure)
4. [Step 1 — Sensor Simulators](#4-step-1--sensor-simulators)
5. [Step 2 — Fog Node](#5-step-2--fog-node)
6. [Step 3 — AWS Setup](#6-step-3--aws-setup)
7. [Step 4 — Lambda Function](#7-step-4--lambda-function)
8. [Step 5 — Dashboard](#8-step-5--dashboard)
9. [Step 6 — GitHub & CI/CD](#9-step-6--github--cicd)
10. [Step 7 — Testing](#10-step-7--testing)
11. [Step 8 — Report](#11-step-8--report)
12. [Step 9 — Presentation](#12-step-9--presentation)
13. [Checklist Before Submission](#13-checklist-before-submission)

---

## 1. Project Overview

### What You Are Building
A **Smart Factory Predictive Maintenance** IoT system with three layers:

```
[5 Sensors] → [Fog Node] → [AWS Cloud] → [Dashboard]
```

### Your 5 Sensors
| Sensor | What it measures | Anomaly |
|---|---|---|
| Vibration | Machine shake (mm/s) | > 15 mm/s = bearing failure |
| Temperature | Motor heat (°C) | > 85°C = overheating |
| Pressure | Hydraulic pressure (bar) | < 20 bar = leak |
| Humidity | Environment (%) | > 80% = corrosion risk |
| Power | Energy draw (kW) | Sudden spike = fault |

### AWS Services You Will Use
| Service | Purpose |
|---|---|
| API Gateway | Receives data from fog node |
| SQS | Queues incoming messages |
| Lambda | Processes queue messages |
| DynamoDB | Stores all sensor readings |
| EC2 / Elastic Beanstalk | Hosts the dashboard |

---

## 2. Prerequisites & Setup

### 2.1 Install These on Your Laptop

```bash
# Python 3.10+
python --version

# pip packages
pip install paho-mqtt boto3 flask requests python-dotenv pytest

# AWS CLI
# Download from: https://aws.amazon.com/cli/
aws --version

# Git
git --version
```

### 2.2 Create AWS Account
1. Go to https://aws.amazon.com
2. Create a free tier account
3. Go to **IAM → Users → Create User**
4. Attach policies: `AmazonSQSFullAccess`, `AmazonDynamoDBFullAccess`, `AWSLambda_FullAccess`, `AmazonAPIGatewayAdministrator`
5. Create **Access Key** → save `Access Key ID` and `Secret Access Key`

### 2.3 Configure AWS CLI
```bash
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Region: eu-west-1  (Ireland — closest to you)
# Output format: json
```

### 2.4 Create GitHub Repository
1. Go to https://github.com → New Repository
2. Name it: `smart-factory-iot`
3. Set to **Private**
4. Clone it locally:
```bash
git clone https://github.com/YOUR_USERNAME/smart-factory-iot.git
cd smart-factory-iot
```

---

## 3. Project Folder Structure

Create this exact structure:

```
smart-factory-iot/
├── sensors/
│   ├── sensor_vibration.py
│   ├── sensor_temperature.py
│   ├── sensor_pressure.py
│   ├── sensor_humidity.py
│   ├── sensor_power.py
│   └── run_all_sensors.py
├── fog_node/
│   ├── fog_node.py
│   └── processor.py
├── backend/
│   ├── lambda/
│   │   └── handler.py
│   ├── api/
│   │   └── app.py
│   └── dashboard/
│       ├── templates/
│       │   └── index.html
│       └── static/
│           └── charts.js
├── infra/
│   └── setup_aws.py
├── tests/
│   ├── test_sensors.py
│   └── test_fog_node.py
├── .github/
│   └── workflows/
│       └── deploy.yml
├── .env
├── requirements.txt
└── readme.txt
```

Create all folders now:
```bash
mkdir -p sensors fog_node backend/lambda backend/api backend/dashboard/templates backend/dashboard/static infra tests .github/workflows
```

---

## 4. Step 1 — Sensor Simulators

### What to build
5 Python scripts that generate realistic fake sensor data with configurable dispatch rates.

### 4.1 Create `sensors/sensor_vibration.py`

```python
import time
import random
import json
import argparse
from datetime import datetime

def generate_vibration(anomaly=False):
    """Generate vibration sensor reading in mm/s"""
    if anomaly:
        value = round(random.uniform(15.0, 25.0), 2)  # fault range
    else:
        value = round(random.uniform(0.5, 10.0), 2)   # normal range
    return {
        "sensor_id": "VIB_001",
        "sensor_type": "vibration",
        "value": value,
        "unit": "mm/s",
        "timestamp": datetime.utcnow().isoformat(),
        "machine_id": "MACHINE_A"
    }

def run(rate=5, anomaly_chance=0.05):
    """Run sensor at configurable rate (seconds between readings)"""
    print(f"[Vibration Sensor] Started. Sending every {rate}s")
    while True:
        anomaly = random.random() < anomaly_chance
        data = generate_vibration(anomaly=anomaly)
        print(json.dumps(data))
        time.sleep(rate)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5, help="Seconds between readings")
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    args = parser.parse_args()
    run(rate=args.rate, anomaly_chance=args.anomaly_chance)
```

### 4.2 Create `sensors/sensor_temperature.py`

```python
import time
import random
import json
import argparse
from datetime import datetime

def generate_temperature(anomaly=False):
    if anomaly:
        value = round(random.uniform(85.0, 105.0), 2)
    else:
        value = round(random.uniform(40.0, 75.0), 2)
    return {
        "sensor_id": "TEMP_001",
        "sensor_type": "temperature",
        "value": value,
        "unit": "celsius",
        "timestamp": datetime.utcnow().isoformat(),
        "machine_id": "MACHINE_A"
    }

def run(rate=5, anomaly_chance=0.05):
    print(f"[Temperature Sensor] Started. Sending every {rate}s")
    while True:
        anomaly = random.random() < anomaly_chance
        data = generate_temperature(anomaly=anomaly)
        print(json.dumps(data))
        time.sleep(rate)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    args = parser.parse_args()
    run(rate=args.rate, anomaly_chance=args.anomaly_chance)
```

### 4.3 Create `sensors/sensor_pressure.py`

```python
import time
import random
import json
import argparse
from datetime import datetime

def generate_pressure(anomaly=False):
    if anomaly:
        value = round(random.uniform(5.0, 18.0), 2)   # low pressure = leak
    else:
        value = round(random.uniform(25.0, 60.0), 2)  # normal range
    return {
        "sensor_id": "PRES_001",
        "sensor_type": "pressure",
        "value": value,
        "unit": "bar",
        "timestamp": datetime.utcnow().isoformat(),
        "machine_id": "MACHINE_A"
    }

def run(rate=5, anomaly_chance=0.05):
    print(f"[Pressure Sensor] Started. Sending every {rate}s")
    while True:
        anomaly = random.random() < anomaly_chance
        data = generate_pressure(anomaly=anomaly)
        print(json.dumps(data))
        time.sleep(rate)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    args = parser.parse_args()
    run(rate=args.rate, anomaly_chance=args.anomaly_chance)
```

### 4.4 Create `sensors/sensor_humidity.py`

```python
import time
import random
import json
import argparse
from datetime import datetime

def generate_humidity(anomaly=False):
    if anomaly:
        value = round(random.uniform(80.0, 98.0), 2)
    else:
        value = round(random.uniform(30.0, 65.0), 2)
    return {
        "sensor_id": "HUM_001",
        "sensor_type": "humidity",
        "value": value,
        "unit": "percent",
        "timestamp": datetime.utcnow().isoformat(),
        "machine_id": "MACHINE_A"
    }

def run(rate=5, anomaly_chance=0.05):
    print(f"[Humidity Sensor] Started. Sending every {rate}s")
    while True:
        anomaly = random.random() < anomaly_chance
        data = generate_humidity(anomaly=anomaly)
        print(json.dumps(data))
        time.sleep(rate)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    args = parser.parse_args()
    run(rate=args.rate, anomaly_chance=args.anomaly_chance)
```

### 4.5 Create `sensors/sensor_power.py`

```python
import time
import random
import json
import argparse
from datetime import datetime

def generate_power(anomaly=False):
    if anomaly:
        value = round(random.uniform(95.0, 150.0), 2)
    else:
        value = round(random.uniform(20.0, 75.0), 2)
    return {
        "sensor_id": "PWR_001",
        "sensor_type": "power",
        "value": value,
        "unit": "kW",
        "timestamp": datetime.utcnow().isoformat(),
        "machine_id": "MACHINE_A"
    }

def run(rate=5, anomaly_chance=0.05):
    print(f"[Power Sensor] Started. Sending every {rate}s")
    while True:
        anomaly = random.random() < anomaly_chance
        data = generate_power(anomaly=anomaly)
        print(json.dumps(data))
        time.sleep(rate)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    args = parser.parse_args()
    run(rate=args.rate, anomaly_chance=args.anomaly_chance)
```

### 4.6 Create `sensors/run_all_sensors.py`
This starts all 5 sensors at once in separate threads:

```python
import threading
import argparse
import sys
sys.path.insert(0, '.')

from sensor_vibration import run as run_vibration
from sensor_temperature import run as run_temperature
from sensor_pressure import run as run_pressure
from sensor_humidity import run as run_humidity
from sensor_power import run as run_power

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    args = parser.parse_args()

    sensors = [
        threading.Thread(target=run_vibration, args=(args.rate, args.anomaly_chance)),
        threading.Thread(target=run_temperature, args=(args.rate, args.anomaly_chance)),
        threading.Thread(target=run_pressure, args=(args.rate, args.anomaly_chance)),
        threading.Thread(target=run_humidity, args=(args.rate, args.anomaly_chance)),
        threading.Thread(target=run_power, args=(args.rate, args.anomaly_chance)),
    ]

    for s in sensors:
        s.daemon = True
        s.start()

    print("All 5 sensors running. Press Ctrl+C to stop.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Sensors stopped.")

if __name__ == "__main__":
    main()
```

### 4.7 Test Sensors Locally
```bash
cd sensors
python sensor_vibration.py --rate 2
# You should see JSON output every 2 seconds
# Press Ctrl+C to stop

# Run all sensors together
python run_all_sensors.py --rate 3 --anomaly-chance 0.1
```

---

## 5. Step 2 — Fog Node

### What to build
A Python service that receives sensor data, processes it locally, detects anomalies, and dispatches to AWS.

### 5.1 Create `fog_node/processor.py`

```python
# Anomaly thresholds for each sensor type
THRESHOLDS = {
    "vibration":   {"max": 15.0,  "unit": "mm/s",   "alert": "Bearing failure risk"},
    "temperature": {"max": 85.0,  "unit": "celsius", "alert": "Motor overheating"},
    "pressure":    {"min": 20.0,  "unit": "bar",     "alert": "Hydraulic leak detected"},
    "humidity":    {"max": 80.0,  "unit": "percent", "alert": "Corrosion risk"},
    "power":       {"max": 90.0,  "unit": "kW",      "alert": "Power spike - possible fault"},
}

# Rolling window for trend detection
reading_history = {}

def process_reading(data):
    """
    Process a single sensor reading.
    Returns enriched data with anomaly flag and alert message.
    """
    sensor_type = data.get("sensor_type")
    value = data.get("value")
    result = data.copy()
    result["anomaly"] = False
    result["alert"] = None
    result["processed_by"] = "fog_node"

    if sensor_type not in THRESHOLDS:
        return result

    threshold = THRESHOLDS[sensor_type]

    # Check max threshold
    if "max" in threshold and value > threshold["max"]:
        result["anomaly"] = True
        result["alert"] = threshold["alert"]
        result["severity"] = "HIGH"

    # Check min threshold
    if "min" in threshold and value < threshold["min"]:
        result["anomaly"] = True
        result["alert"] = threshold["alert"]
        result["severity"] = "HIGH"

    # Trend detection — is value rising consistently?
    sensor_id = data.get("sensor_id")
    if sensor_id not in reading_history:
        reading_history[sensor_id] = []

    reading_history[sensor_id].append(value)

    # Keep last 5 readings
    if len(reading_history[sensor_id]) > 5:
        reading_history[sensor_id].pop(0)

    # If last 3 readings all increasing AND approaching threshold
    history = reading_history[sensor_id]
    if len(history) >= 3:
        if history[-1] > history[-2] > history[-3]:
            if "max" in threshold and value > threshold["max"] * 0.85:
                result["trend"] = "RISING"
                if not result["anomaly"]:
                    result["alert"] = f"Warning: {sensor_type} trending toward threshold"
                    result["severity"] = "MEDIUM"

    return result
```

### 5.2 Create `fog_node/fog_node.py`

```python
import json
import time
import queue
import threading
import requests
import os
from datetime import datetime
from processor import process_reading
from dotenv import load_dotenv

load_dotenv()

# Config
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:5000/ingest")
DISPATCH_INTERVAL = int(os.getenv("DISPATCH_INTERVAL", 10))  # seconds

# Internal queue to buffer sensor data
data_queue = queue.Queue()
batch_buffer = []

def receive_sensor_data(data):
    """Called when sensor data arrives"""
    data_queue.put(data)

def process_and_batch():
    """Continuously process incoming sensor data"""
    global batch_buffer
    while True:
        try:
            raw = data_queue.get(timeout=1)
            processed = process_reading(raw)

            # Log anomalies immediately
            if processed.get("anomaly"):
                print(f"[FOG ALERT] {processed['alert']} | "
                      f"Sensor: {processed['sensor_id']} | "
                      f"Value: {processed['value']} {processed['unit']}")

            batch_buffer.append(processed)
        except queue.Empty:
            pass

def dispatch_to_cloud():
    """Every DISPATCH_INTERVAL seconds, send batch to AWS"""
    global batch_buffer
    while True:
        time.sleep(DISPATCH_INTERVAL)
        if batch_buffer:
            payload = {
                "fog_node_id": "FOG_NODE_001",
                "timestamp": datetime.utcnow().isoformat(),
                "reading_count": len(batch_buffer),
                "readings": batch_buffer.copy()
            }
            batch_buffer = []

            try:
                response = requests.post(API_ENDPOINT, json=payload, timeout=5)
                print(f"[FOG] Dispatched {payload['reading_count']} readings → "
                      f"Status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"[FOG] Dispatch failed: {e} — will retry next interval")

def simulate_sensors():
    """
    Simulate sensors sending data directly to fog node.
    In production, sensors would send over MQTT or HTTP.
    """
    import sys
    sys.path.insert(0, '../sensors')
    from sensor_vibration import generate_vibration
    from sensor_temperature import generate_temperature
    from sensor_pressure import generate_pressure
    from sensor_humidity import generate_humidity
    from sensor_power import generate_power

    import random

    generators = [
        generate_vibration,
        generate_temperature,
        generate_pressure,
        generate_humidity,
        generate_power
    ]

    print("[FOG] Sensor simulation started")
    while True:
        for gen in generators:
            anomaly = random.random() < 0.08
            data = gen(anomaly=anomaly)
            receive_sensor_data(data)
        time.sleep(2)

def main():
    print("=" * 50)
    print("FOG NODE STARTED")
    print(f"Dispatching to: {API_ENDPOINT}")
    print(f"Batch interval: {DISPATCH_INTERVAL}s")
    print("=" * 50)

    # Start processing thread
    t1 = threading.Thread(target=process_and_batch, daemon=True)
    t1.start()

    # Start dispatch thread
    t2 = threading.Thread(target=dispatch_to_cloud, daemon=True)
    t2.start()

    # Start sensor simulation
    simulate_sensors()

if __name__ == "__main__":
    main()
```

### 5.3 Test Fog Node Locally
```bash
cd fog_node
python fog_node.py
# You should see sensor readings being processed
# Anomalies will be flagged in red in the console
# Every 10 seconds it will try to dispatch to AWS
```

---

## 6. Step 3 — AWS Setup

### 6.1 Create SQS Queue
```bash
aws sqs create-queue \
  --queue-name smart-factory-queue \
  --region eu-west-1

# Save the Queue URL from the output — you'll need it
# Looks like: https://sqs.eu-west-1.amazonaws.com/123456789/smart-factory-queue
```

### 6.2 Create DynamoDB Table
```bash
aws dynamodb create-table \
  --table-name SensorReadings \
  --attribute-definitions AttributeName=sensor_id,AttributeType=S AttributeName=timestamp,AttributeType=S \
  --key-schema AttributeName=sensor_id,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 6.3 Create `.env` File
```bash
# In your project root, create .env:
AWS_REGION=us-east-1
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT_ID/smart-factory-queue
DYNAMODB_TABLE=SensorReadings
API_ENDPOINT=https://YOUR_API_GATEWAY_URL/ingest
DISPATCH_INTERVAL=10
```

### 6.4 Create `infra/setup_aws.py`
Run this script once to verify all AWS resources exist:

```python
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

region = os.getenv("AWS_REGION", "us-east-1")

def check_sqs():
    sqs = boto3.client("sqs", region_name=region)
    queues = sqs.list_queues(QueueNamePrefix="smart-factory")
    print(f"SQS Queues: {queues.get('QueueUrls', [])}")

def check_dynamodb():
    dynamodb = boto3.client("dynamodb", region_name=region)
    tables = dynamodb.list_tables()
    print(f"DynamoDB Tables: {tables['TableNames']}")

if __name__ == "__main__":
    print("Checking AWS resources...")
    check_sqs()
    check_dynamodb()
    print("Done.")
```

---

## 7. Step 4 — Lambda Function

### 7.1 Create `backend/lambda/handler.py`

```python
import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "SensorReadings"))

def lambda_handler(event, context):
    """
    Triggered by SQS. Processes each message and stores in DynamoDB.
    """
    processed = 0
    errors = 0

    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
            readings = body.get("readings", [])

            for reading in readings:
                table.put_item(Item={
                    "sensor_id":   reading.get("sensor_id", "UNKNOWN"),
                    "timestamp":   reading.get("timestamp", datetime.utcnow().isoformat()),
                    "sensor_type": reading.get("sensor_type"),
                    "value":       str(reading.get("value")),
                    "unit":        reading.get("unit"),
                    "machine_id":  reading.get("machine_id"),
                    "anomaly":     reading.get("anomaly", False),
                    "alert":       reading.get("alert"),
                    "fog_node_id": body.get("fog_node_id"),
                })
                processed += 1

        except Exception as e:
            print(f"Error processing record: {e}")
            errors += 1

    print(f"Processed: {processed} readings, Errors: {errors}")
    return {"statusCode": 200, "processed": processed}
```

### 7.2 Deploy Lambda to AWS

```bash
# Zip the lambda
cd backend/lambda
zip function.zip handler.py lambda_function.py

# Create Lambda function
aws lambda create-function \
  --function-name smart-factory-processor \
  --runtime python3.14 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-role \
    --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --environment Variables="{DYNAMODB_TABLE=SensorReadings}" \
    --region us-east-1

# Connect Lambda to SQS trigger
aws lambda create-event-source-mapping \
  --function-name smart-factory-processor \
    --event-source-arn arn:aws:sqs:us-east-1:YOUR_ACCOUNT_ID:smart-factory-queue \
  --batch-size 10 \
    --region us-east-1
```

---

## 8. Step 5 — Dashboard

### 8.1 Create `backend/api/app.py`

```python
from flask import Flask, jsonify, render_template
import boto3
import os
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Key

load_dotenv()

app = Flask(__name__, template_folder="../dashboard/templates",
            static_folder="../dashboard/static")

dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "eu-west-1"))
table = dynamodb.Table(os.getenv("DYNAMODB_TABLE", "SensorReadings"))

SENSOR_IDS = ["VIB_001", "TEMP_001", "PRES_001", "HUM_001", "PWR_001"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/latest")
def get_latest():
    """Get latest reading for each sensor"""
    results = {}
    for sensor_id in SENSOR_IDS:
        response = table.query(
            KeyConditionExpression=Key("sensor_id").eq(sensor_id),
            ScanIndexForward=False,
            Limit=1
        )
        items = response.get("Items", [])
        if items:
            results[sensor_id] = items[0]
    return jsonify(results)

@app.route("/api/history/<sensor_id>")
def get_history(sensor_id):
    """Get last 20 readings for a sensor"""
    response = table.query(
        KeyConditionExpression=Key("sensor_id").eq(sensor_id),
        ScanIndexForward=False,
        Limit=20
    )
    items = response.get("Items", [])
    items.reverse()
    return jsonify(items)

@app.route("/api/alerts")
def get_alerts():
    """Get recent anomalies"""
    response = table.scan(
        FilterExpression="anomaly = :val",
        ExpressionAttributeValues={":val": True},
        Limit=50
    )
    return jsonify(response.get("Items", []))

@app.route("/ingest", methods=["POST"])
def ingest():
    """Receives data from fog node and pushes to SQS"""
    from flask import request
    import boto3, json
    sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION"))
    sqs.send_message(
        QueueUrl=os.getenv("SQS_QUEUE_URL"),
        MessageBody=json.dumps(request.json)
    )
    return jsonify({"status": "queued"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

### 8.2 Create `backend/dashboard/templates/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Factory Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        h1 { color: #00d4ff; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .card { background: #16213e; border-radius: 10px; padding: 20px; }
        .card h3 { color: #00d4ff; margin-top: 0; }
        .alert { background: #ff4444; padding: 10px; border-radius: 5px; margin: 5px 0; }
        .value { font-size: 2em; font-weight: bold; color: #00ff88; }
        canvas { max-height: 200px; }
    </style>
</head>
<body>
    <h1>🏭 Smart Factory — Predictive Maintenance Dashboard</h1>

    <div class="grid">
        <div class="card">
            <h3>⚡ Vibration (mm/s)</h3>
            <div class="value" id="vib-value">--</div>
            <canvas id="vib-chart"></canvas>
        </div>
        <div class="card">
            <h3>🌡️ Temperature (°C)</h3>
            <div class="value" id="temp-value">--</div>
            <canvas id="temp-chart"></canvas>
        </div>
        <div class="card">
            <h3>💧 Pressure (bar)</h3>
            <div class="value" id="pres-value">--</div>
            <canvas id="pres-chart"></canvas>
        </div>
        <div class="card">
            <h3>💦 Humidity (%)</h3>
            <div class="value" id="hum-value">--</div>
            <canvas id="hum-chart"></canvas>
        </div>
        <div class="card">
            <h3>⚡ Power (kW)</h3>
            <div class="value" id="pwr-value">--</div>
            <canvas id="pwr-chart"></canvas>
        </div>
        <div class="card">
            <h3>🚨 Recent Alerts</h3>
            <div id="alerts-list">Loading...</div>
        </div>
    </div>

    <script src="/static/charts.js"></script>
</body>
</html>
```

### 8.3 Test Dashboard Locally
```bash
cd backend/api
python app.py
# Open http://localhost:5000 in your browser
```

---

## 9. Step 6 — GitHub & CI/CD

### 9.1 Create `requirements.txt`
```
boto3==1.34.0
flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
paho-mqtt==1.6.1
pytest==7.4.0
```

### 9.2 Create `.github/workflows/deploy.yml`

```yaml
name: Deploy Smart Factory IoT

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v

  deploy-lambda:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Deploy Lambda
        run: |
          cd backend/lambda
          zip function.zip handler.py lambda_function.py
          aws lambda update-function-code \
            --function-name smart-factory-processor \
            --zip-file fileb://function.zip
```

### 9.3 Add Secrets to GitHub
1. Go to your GitHub repo → **Settings → Secrets → Actions**
2. Add: `AWS_ACCESS_KEY_ID`
3. Add: `AWS_SECRET_ACCESS_KEY`

### 9.4 Push Everything to GitHub
```bash
git add .
git commit -m "Initial project setup"
git push origin main
```

---

## 10. Step 7 — Testing

### 10.1 Create `tests/test_sensors.py`

```python
import sys
sys.path.insert(0, './sensors')
from sensor_vibration import generate_vibration
from sensor_temperature import generate_temperature
from sensor_pressure import generate_pressure

def test_vibration_normal():
    data = generate_vibration(anomaly=False)
    assert data["sensor_type"] == "vibration"
    assert 0.5 <= data["value"] <= 10.0
    assert data["unit"] == "mm/s"

def test_vibration_anomaly():
    data = generate_vibration(anomaly=True)
    assert data["value"] >= 15.0

def test_temperature_normal():
    data = generate_temperature(anomaly=False)
    assert 40.0 <= data["value"] <= 75.0

def test_pressure_anomaly():
    data = generate_pressure(anomaly=True)
    assert data["value"] < 20.0
```

### 10.2 Create `tests/test_fog_node.py`

```python
import sys
sys.path.insert(0, './fog_node')
from processor import process_reading

def test_vibration_anomaly_detected():
    data = {"sensor_id": "VIB_001", "sensor_type": "vibration", "value": 20.0, "unit": "mm/s"}
    result = process_reading(data)
    assert result["anomaly"] == True
    assert result["alert"] is not None

def test_normal_reading_no_anomaly():
    data = {"sensor_id": "TEMP_001", "sensor_type": "temperature", "value": 55.0, "unit": "celsius"}
    result = process_reading(data)
    assert result["anomaly"] == False

def test_processed_by_fog():
    data = {"sensor_id": "HUM_001", "sensor_type": "humidity", "value": 40.0, "unit": "percent"}
    result = process_reading(data)
    assert result["processed_by"] == "fog_node"
```

### 10.3 Run Tests
```bash
pytest tests/ -v
# All tests should pass
```

---

## 11. Step 8 — Report

### Structure (6–8 pages, IEEE 2-column)

Download the IEEE template from:
https://www.ieee.org/conferences/publishing/templates.html

### Section by Section Guide

#### Abstract (100 words)
> Summarise: what you built, what sensors, what cloud services, key result (e.g. sub-10ms fog detection).

#### Introduction (half page)
- Problem: factory downtime costs $50,000/hour
- Why fog: cloud too slow for real-time fault detection
- Objectives: build 3-layer IoT system on AWS
- Structure of the paper

#### Architecture (1.5 pages)
- Include a diagram showing all three layers
- Justify each AWS service choice:
  - **Why SQS?** Decouples fog node from backend, handles traffic spikes
  - **Why Lambda?** Auto-scales with queue depth, no idle server costs
  - **Why DynamoDB?** Scales to millions of readings, pay-per-use
- Critically compare alternatives (e.g. Kinesis vs SQS, RDS vs DynamoDB)

#### Implementation (2 pages)
- Languages/libraries: Python, boto3, Flask, Chart.js
- Fog node processing logic
- Lambda trigger mechanism
- Dashboard architecture
- CI/CD pipeline with GitHub Actions
- Link to GitHub repo

#### Conclusions (half page)
- What worked well
- What was difficult (e.g. Lambda IAM permissions)
- What you would do differently
- Reflection on fog vs cloud-only approach

#### References (IEEE style)
Minimum 6–8 references. Include:
- Academic papers on fog computing / IIoT
- AWS documentation
- IoT architecture papers from IEEE Xplore

---

## 12. Step 9 — Presentation

### 4-Minute Script

| Time | Content |
|---|---|
| 0:00–0:30 | Problem — factory downtime costs money, cloud too slow |
| 0:30–1:00 | Solution — 3-layer architecture overview (show diagram) |
| 1:00–2:30 | Live demo — show dashboard with live sensor data flowing |
| 2:30–3:15 | Fog node — show anomaly being detected locally before cloud |
| 3:15–3:45 | Hardest part — explain what broke and how you fixed it |
| 3:45–4:00 | Summary and questions |

### Demo Tips
- Run the fog node with `--anomaly-chance 0.3` during demo (more alerts = better demo)
- Have the dashboard open on a second screen
- Test everything the night before
- Have a screen recording as backup in case live demo fails

---

## 13. Checklist Before Submission

### Code ✅
- [ ] 5 sensor simulators with configurable `--rate` argument
- [ ] Fog node processes and detects anomalies
- [ ] Fog node dispatches to AWS every N seconds
- [ ] SQS queue receiving messages
- [ ] Lambda function processing queue
- [ ] DynamoDB storing all readings
- [ ] Dashboard showing live charts for all 5 sensors
- [ ] Tests written and passing
- [ ] CI/CD pipeline in GitHub Actions
- [ ] All code commented
- [ ] `readme.txt` with installation instructions

### Report ✅
- [ ] IEEE 2-column format
- [ ] 6–8 pages (not more!)
- [ ] Student name, ID, course on page 1
- [ ] Abstract written
- [ ] Architecture diagram included
- [ ] GitHub link included
- [ ] Minimum 6 IEEE-style references
- [ ] No plagiarism

### Submission ✅
- [ ] ZIP file contains all source code
- [ ] ZIP file contains `readme.txt`
- [ ] PDF report ready
- [ ] Both uploaded to Moodle before 27 July 2026

### Presentation ✅
- [ ] Slides prepared (5–7 slides max)
- [ ] Demo tested and working
- [ ] Screen recording backup ready
- [ ] Under 4 minutes when rehearsed

---

## 🆘 If You Get Stuck

| Problem | Solution |
|---|---|
| AWS permissions error | Check IAM user has all required policies |
| Lambda not triggering | Check SQS event source mapping is enabled |
| DynamoDB empty | Check Lambda logs in CloudWatch |
| Dashboard not loading | Check Flask is running and API routes work |
| Tests failing | Check file paths and imports |

---

*Good luck! Build it step by step and you will have a working H1 project.*
