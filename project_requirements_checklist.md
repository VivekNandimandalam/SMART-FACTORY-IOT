# Project Requirements Checklist

This file maps the college brief to the current implementation and shows what still depends on college-managed AWS resources.

## Core architecture
- [x] Sensors -> Fog node -> Cloud -> Dashboard
- [x] Five sensor streams: vibration, temperature, pressure, humidity, power
- [x] Fog-side anomaly detection in `fog_node/processor.py`

## Sensors
- [x] Separate simulators for each sensor
- [x] Configurable dispatch rate via `--rate`
- [x] Anomaly generation via `--anomaly-chance`

## Fog node
- [x] Local processing and alerting
- [x] Batch dispatch to the cloud endpoint
- [x] Simulated sensor input for local development

## AWS integration
- [x] SQS integration path defined
- [x] DynamoDB storage path defined
- [x] Lambda handler implemented
- [x] API route for ingestion implemented
- [ ] Real AWS deployment depends on college console permissions and pre-provisioned resources

## Dashboard
- [x] Live charts for all five sensors
- [x] Recent alerts panel
- [x] Local fallback storage when AWS is unavailable

## Testing
- [x] Sensor tests
- [x] Fog processor tests

## CI/CD
- [x] GitHub Actions workflow included

## Reporting and submission support
- [ ] IEEE report still needs to be written separately
- [ ] Presentation slides still need to be created separately
