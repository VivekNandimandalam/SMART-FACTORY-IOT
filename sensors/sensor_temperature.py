import argparse
import json
import random
import time
from datetime import datetime, timezone


def generate_temperature(anomaly=False):
    value = round(random.uniform(85.0, 105.0), 2) if anomaly else round(random.uniform(40.0, 75.0), 2)
    return {
        "sensor_id": "TEMP_001",
        "sensor_type": "temperature",
        "value": value,
        "unit": "celsius",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "machine_id": "MACHINE_A",
    }


def run(rate=5, anomaly_chance=0.05):
    print(f"[Temperature Sensor] Started. Sending every {rate}s")
    while True:
        data = generate_temperature(anomaly=random.random() < anomaly_chance)
        print(json.dumps(data))
        time.sleep(rate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    arguments = parser.parse_args()
    run(rate=arguments.rate, anomaly_chance=arguments.anomaly_chance)
