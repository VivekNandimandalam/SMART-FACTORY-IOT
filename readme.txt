Smart Factory Predictive Maintenance

Setup:
1. Install Python 3.10+.
2. Run pip install -r requirements.txt.
3. Configure .env with your college AWS values or set USE_AWS=false for local development.
4. Use `infra/setup_aws.py` to validate AWS credentials and resources once your college account is available.

College AWS restrictions:
- Use only pre-created AWS console resources if your account cannot change IAM.
- You should not need to create new IAM roles yourself if the college provides the Lambda role.
- If AWS resources are not yet available, the dashboard stores readings locally in backend/data/local_readings.json.

Run sensors:
cd sensors
python run_all_sensors.py --rate 3 --anomaly-chance 0.1

Run fog node:
cd fog_node
python fog_node.py

Run dashboard:
cd backend/api
python app.py
Open http://localhost:5000

Production dashboard hosting:
- Use the root `Procfile` with `gunicorn backend.api.app:app`
- Make sure the hosting platform provides AWS credentials through an instance role or equivalent secret store
- Set `AWS_REGION`, `DYNAMODB_TABLE`, `SQS_QUEUE_URL`, `USE_AWS=true`, and `API_ENDPOINT` in the host environment
- For AWS App Runner, use the root `Dockerfile` and health check path `/health`

If you are using AWS:
- SQS_QUEUE_URL must point to the existing queue.
- DYNAMODB_TABLE must match the existing DynamoDB table.
- API_ENDPOINT should point to the existing API Gateway or to the local Flask ingest route during development.
- Optional: set LAMBDA_FUNCTION_NAME if you want `infra/setup_aws.py` to validate the Lambda function too.

Run tests:
pytest tests -v
