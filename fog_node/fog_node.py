import os
import queue
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

import requests
from dotenv import load_dotenv


sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sensors"))

from processor import process_reading
from sensor_humidity import generate_humidity
from sensor_power import generate_power
from sensor_pressure import generate_pressure
from sensor_temperature import generate_temperature
from sensor_vibration import generate_vibration


load_dotenv()

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:5000/ingest")
DISPATCH_INTERVAL = int(os.getenv("DISPATCH_INTERVAL", 10))

data_queue = queue.Queue()
batch_buffer = []
buffer_lock = threading.Lock()


def receive_sensor_data(data):
    data_queue.put(data)


def process_and_batch():
    while True:
        try:
            raw = data_queue.get(timeout=1)
        except queue.Empty:
            continue

        processed = process_reading(raw)
        if processed.get("anomaly"):
            print(
                f"[FOG ALERT] {processed['alert']} | Sensor: {processed['sensor_id']} | "
                f"Value: {processed['value']} {processed['unit']}"
            )

        with buffer_lock:
            batch_buffer.append(processed)


def dispatch_to_cloud():
    while True:
        time.sleep(DISPATCH_INTERVAL)
        with buffer_lock:
            if not batch_buffer:
                continue
            payload = {
                "fog_node_id": "FOG_NODE_001",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reading_count": len(batch_buffer),
                "readings": batch_buffer.copy(),
            }
            batch_buffer.clear()

        try:
            response = requests.post(API_ENDPOINT, json=payload, timeout=5)
            print(f"[FOG] Dispatched {payload['reading_count']} readings -> Status: {response.status_code}")
        except requests.RequestException as error:
            print(f"[FOG] Dispatch failed: {error} - will retry next interval")


def simulate_sensors():
    generators = [
        generate_vibration,
        generate_temperature,
        generate_pressure,
        generate_humidity,
        generate_power,
    ]

    print("[FOG] Sensor simulation started")
    while True:
        for generator in generators:
            data = generator(anomaly=False)
            receive_sensor_data(data)
        time.sleep(2)


def main():
    print("=" * 50)
    print("FOG NODE STARTED")
    print(f"Dispatching to: {API_ENDPOINT}")
    print(f"Batch interval: {DISPATCH_INTERVAL}s")
    print("=" * 50)

    threading.Thread(target=process_and_batch, daemon=True).start()
    threading.Thread(target=dispatch_to_cloud, daemon=True).start()
    simulate_sensors()


if __name__ == "__main__":
    main()
