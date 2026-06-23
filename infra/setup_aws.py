import os
import sys
from urllib.parse import urlparse

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from dotenv import load_dotenv


load_dotenv()


def _print_header(title):
    print(f"\n== {title} ==")


def _require_credentials(session):
    sts = session.client("sts")
    identity = sts.get_caller_identity()
    account = identity.get("Account", "unknown")
    arn = identity.get("Arn", "unknown")
    print(f"Credentials: OK ({account})")
    print(f"Caller ARN: {arn}")


def _check_sqs(session, region, queue_url):
    if not queue_url:
        print("SQS: skipped (SQS_QUEUE_URL not set)")
        return

    sqs = session.client("sqs", region_name=region)
    attrs = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=["QueueArn", "ApproximateNumberOfMessages"],
    )
    parsed = urlparse(queue_url)
    queue_name = parsed.path.rsplit("/", 1)[-1]
    print(f"SQS queue: {queue_name}")
    print(f"SQS ARN: {attrs['Attributes'].get('QueueArn', 'unknown')}")
    print(f"SQS approx messages: {attrs['Attributes'].get('ApproximateNumberOfMessages', 'unknown')}")


def _check_dynamodb(session, region, table_name):
    if not table_name:
        print("DynamoDB: skipped (DYNAMODB_TABLE not set)")
        return

    dynamodb = session.client("dynamodb", region_name=region)
    table = dynamodb.describe_table(TableName=table_name)
    status = table["Table"]["TableStatus"]
    arn = table["Table"].get("TableArn", "unknown")
    print(f"DynamoDB table: {table_name}")
    print(f"DynamoDB status: {status}")
    print(f"DynamoDB ARN: {arn}")


def _check_lambda(session, region, function_name):
    if not function_name:
        print("Lambda: skipped (LAMBDA_FUNCTION_NAME not set)")
        return

    client = session.client("lambda", region_name=region)
    function = client.get_function(FunctionName=function_name)
    config = function["Configuration"]
    print(f"Lambda function: {config['FunctionName']}")
    print(f"Lambda runtime: {config.get('Runtime', 'unknown')}")
    print(f"Lambda handler: {config.get('Handler', 'unknown')}")
    print(f"Lambda state: {config.get('State', 'unknown')}")


if __name__ == "__main__":
    region = os.getenv("AWS_REGION", "us-east-1")
    queue_url = os.getenv("SQS_QUEUE_URL")
    table_name = os.getenv("DYNAMODB_TABLE")
    function_name = os.getenv("LAMBDA_FUNCTION_NAME")

    print("Checking AWS resources...")
    print(f"Region: {region}")

    session = boto3.Session(region_name=region)

    try:
        _print_header("Credentials")
        _require_credentials(session)

        _print_header("SQS")
        _check_sqs(session, region, queue_url)

        _print_header("DynamoDB")
        _check_dynamodb(session, region, table_name)

        _print_header("Lambda")
        _check_lambda(session, region, function_name)

    except NoCredentialsError:
        print("AWS validation blocked: no credentials were found in this environment.")
        print("Add AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY or run this from a configured AWS CLI profile.")
        sys.exit(2)
    except (ClientError, BotoCoreError) as error:
        print(f"AWS validation failed: {error}")
        sys.exit(1)

    print("\nDone.")
