from pathlib import Path
import os
import json
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import BotoCoreError, NoCredentialsError, ClientError
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
LOCAL_DATA_FILE = BACKEND_DIR / "data" / "local_readings.json"
load_dotenv(PROJECT_ROOT / ".env")

app = Flask(
    __name__,
    template_folder=str(BACKEND_DIR / "dashboard" / "templates"),
    static_folder=str(BACKEND_DIR / "dashboard" / "static"),
)

AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "SensorReadings")
SENSOR_IDS = ["VIB_001", "TEMP_001", "PRES_001", "HUM_001", "PWR_001"]
USE_AWS = os.getenv("USE_AWS", "true").lower() == "true"

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)


def _empty_latest():
    return {sensor_id: None for sensor_id in SENSOR_IDS}


def _ensure_local_data_file():
    LOCAL_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOCAL_DATA_FILE.exists():
        LOCAL_DATA_FILE.write_text("[]", encoding="utf-8")


def _load_local_readings():
    _ensure_local_data_file()
    try:
        return json.loads(LOCAL_DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save_local_reading(payload):
    readings = _load_local_readings()
    for reading in payload.get("readings", []):
        readings.append({
            **reading,
            "fog_node_id": payload.get("fog_node_id"),
            "timestamp": reading.get("timestamp", datetime.now(timezone.utc).isoformat()),
        })
    LOCAL_DATA_FILE.write_text(json.dumps(readings, indent=2), encoding="utf-8")


def _latest_from_local_store():
    readings = _load_local_readings()
    results = _empty_latest()
    for sensor_id in SENSOR_IDS:
        sensor_readings = [item for item in readings if item.get("sensor_id") == sensor_id]
        if sensor_readings:
            results[sensor_id] = sensor_readings[-1]
    return results


def _history_from_local_store(sensor_id):
    readings = _load_local_readings()
    return [item for item in readings if item.get("sensor_id") == sensor_id][-20:]


def _alerts_from_local_store():
    readings = _load_local_readings()
    return [item for item in readings if item.get("anomaly") is True][-50:]


def _aws_available():
    if not USE_AWS:
        return False
    try:
        table = dynamodb.Table(TABLE_NAME)
        table.table_status
        return True
    except (NoCredentialsError, ClientError, BotoCoreError):
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/latest")
def get_latest():
    if not _aws_available():
        return jsonify(_latest_from_local_store())

    results = {}
    try:
        for sensor_id in SENSOR_IDS:
            response = table.query(
                KeyConditionExpression=Key("sensor_id").eq(sensor_id),
                ScanIndexForward=False,
                Limit=1,
            )
            items = response.get("Items", [])
            if items:
                results[sensor_id] = items[0]
    except Exception as error:
        return jsonify({"error": str(error), "data": _empty_latest()}), 503

    return jsonify(results)


@app.route("/api/history/<sensor_id>")
def get_history(sensor_id):
    if not _aws_available():
        return jsonify(_history_from_local_store(sensor_id))

    try:
        response = table.query(
            KeyConditionExpression=Key("sensor_id").eq(sensor_id),
            ScanIndexForward=False,
            Limit=20,
        )
        items = response.get("Items", [])
        items.reverse()
        return jsonify(items)
    except Exception as error:
        return jsonify({"error": str(error), "items": []}), 503


@app.route("/api/alerts")
def get_alerts():
    if not _aws_available():
        return jsonify(_alerts_from_local_store())

    try:
        response = table.scan(
            FilterExpression=Attr("anomaly").eq(True),
            Limit=50,
        )
        return jsonify(response.get("Items", []))
    except Exception as error:
        return jsonify({"error": str(error), "items": []}), 503


@app.route("/ingest", methods=["POST"])
def ingest():
    payload = request.get_json(force=True, silent=False)

    if not _aws_available():
        _save_local_reading(payload)
        return jsonify({"status": "saved_locally"}), 200

    sqs = boto3.client("sqs", region_name=AWS_REGION)
    queue_url = os.getenv("SQS_QUEUE_URL")
    if not queue_url:
        return jsonify({"error": "SQS_QUEUE_URL is not configured"}), 500

    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(payload))
    return jsonify({"status": "queued"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
