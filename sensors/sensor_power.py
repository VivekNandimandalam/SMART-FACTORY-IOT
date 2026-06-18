import argparse
import json
import random
import time
from datetime import datetime, timezone


def generate_power(anomaly=False):
    value = round(random.uniform(95.0, 150.0), 2) if anomaly else round(random.uniform(20.0, 75.0), 2)
    return {
        "sensor_id": "PWR_001",
        "sensor_type": "power",
        "value": value,
        "unit": "kW",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "machine_id": "MACHINE_A",
    }


def run(rate=5, anomaly_chance=0.05):
    print(f"[Power Sensor] Started. Sending every {rate}s")
    while True:
        data = generate_power(anomaly=random.random() < anomaly_chance)
        print(json.dumps(data))
        time.sleep(rate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=5)
    parser.add_argument("--anomaly-chance", type=float, default=0.05)
    arguments = parser.parse_args()
    run(rate=arguments.rate, anomaly_chance=arguments.anomaly_chance)
