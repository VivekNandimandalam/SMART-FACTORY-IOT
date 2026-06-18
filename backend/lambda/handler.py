import json
import os
from datetime import datetime, timezone

import boto3


TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "SensorReadings")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    processed = 0
    errors = 0

    for record in event.get("Records", []):
        try:
            body = json.loads(record["body"])
            readings = body.get("readings", [])

            for reading in readings:
                table.put_item(
                    Item={
                        "sensor_id": reading.get("sensor_id", "UNKNOWN"),
                        "timestamp": reading.get("timestamp", datetime.now(timezone.utc).isoformat()),
                        "sensor_type": reading.get("sensor_type"),
                        "value": str(reading.get("value")),
                        "unit": reading.get("unit"),
                        "machine_id": reading.get("machine_id"),
                        "anomaly": reading.get("anomaly", False),
                        "alert": reading.get("alert"),
                        "fog_node_id": body.get("fog_node_id"),
                    }
                )
                processed += 1
        except Exception as error:
            print(f"Error processing record: {error}")
            errors += 1

    print(f"Processed: {processed} readings, Errors: {errors}")
    return {"statusCode": 200, "processed": processed, "errors": errors}
