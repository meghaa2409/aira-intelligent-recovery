# AIRA
## AI-Driven Intelligent Recovery and Deployment Orchestrator for AWS

### Project Overview
AIRA is an AI-assisted system designed to detect application incidents,
analyse their causes, recommend controlled recovery actions and verify
application health after recovery.

### Project Objectives
- Deploy a sample application on AWS.
- Monitor application health and performance.
- Detect incidents using AWS monitoring services.
- Analyse incidents using Amazon Bedrock when available.
- Validate AI recommendations using predefined safety policies.
- Execute approved recovery actions.
- Verify and record recovery results.

### Technology Stack
- Python and FastAPI
- Docker
- Amazon ECR
- Amazon ECS with AWS Fargate
- Amazon CloudWatch
- AWS Lambda
- Amazon Bedrock (subject to access)
- Terraform
- GitHub

### Team Responsibilities
- Member 1: AWS Infrastructure and Terraform
- Member 2: Application Development and AI Analysis
- Member 3: Docker, Container Deployment and CI/CD
- Member 4: Monitoring and Automated Recovery

### Project Status
Development and integration preparation.

### Safety
AI-generated recommendations must be validated against
predefined policies. Arbitrary AI-generated commands must never
be executed directly.
