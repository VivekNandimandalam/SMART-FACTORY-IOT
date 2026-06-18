import os

import boto3
from dotenv import load_dotenv


load_dotenv()


def check_sqs(region):
    sqs = boto3.client("sqs", region_name=region)
    queues = sqs.list_queues(QueueNamePrefix="smart-factory")
    print(f"SQS Queues: {queues.get('QueueUrls', [])}")


def check_dynamodb(region):
    dynamodb = boto3.client("dynamodb", region_name=region)
    tables = dynamodb.list_tables()
    print(f"DynamoDB Tables: {tables.get('TableNames', [])}")


if __name__ == "__main__":
    region = os.getenv("AWS_REGION", "eu-west-1")
    print("Checking AWS resources...")
    check_sqs(region)
    check_dynamodb(region)
    print("Done.")
