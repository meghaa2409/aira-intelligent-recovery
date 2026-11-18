# AIRA - CloudWatch Monitoring

## Purpose
Monitor the health and performance of the AIRA ECS application.

## AWS Resources
- Region: ap-south-1
- ECS Cluster: aira-cluster
- ECS Service: aira-service
- Application: aira-api
- CloudWatch Log Group: /ecs/aira-api

## Monitoring Metrics
1. ECS CPU Utilization
2. ECS Memory Utilization
3. ALB HTTP 5xx Errors
4. ALB Unhealthy Targets
5. Application Logs

## Planned Alarms
- High CPU: Greater than 80%
- High Memory: Greater than 80%
- Application errors: Elevated HTTP 5xx responses
- Unhealthy targets: At least 1 unhealthy target

## Purpose of Alerts
CloudWatch alarms will detect application incidents and
initiate the AIRA incident-handling workflow through
EventBridge.