import argparse
import json
import random
import time
from datetime import datetime, timezone


def generate_humidity(anomaly=False):
    value = round(random.uniform(80.0, 98.0), 2) if anomaly else round(random.uniform(30.0, 65.0), 2)
    return {
        "sensor_id": "HUM_001",
        "sensor_type": "humidity",
        "value": value,
        "unit": "percent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "machine_id": "MACHINE_A",
    }


def run(rate=5, anomaly_chance=0.05):
    print(f"[Humidity Sensor] Started. Sending every {rate}s")
    while True:
        data = generate_humidity(anomaly=random.random() < anomaly_chance)
        print(json.dumps(data))
        time.sleep(rate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    arguments = parser.parse_args()
    run(rate=arguments.rate, anomaly_chance=arguments.anomaly_chance)
