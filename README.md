# AIRA
## AI-Driven Intelligent Recovery and Deployment Orchestrator for AWS

### 1. Project Overview

AIRA is an AI-assisted incident detection, analysis and recovery orchestration project built on AWS.

The system is designed to monitor application health, detect incidents, analyse their causes, recommend controlled recovery actions and verify application health.

### 2. Project Objectives

- Deploy a sample application on AWS.
- Monitor application health and performance.
- Detect incidents using AWS monitoring services.
- Analyse incidents and recommend recovery actions.
- Validate recommendations using predefined safety policies.
- Support human approval before recovery actions.
- Verify and record recovery results.

### 3. Key Features

- FastAPI-based application backend.
- Docker containerization.
- Container image storage in Amazon ECR.
- Application deployment using Amazon ECS with AWS Fargate.
- Public application access through an Application Load Balancer.
- Automated build and deployment using GitHub Actions.
- Application health checks.
- Incident monitoring using CloudWatch.
- Event-driven incident handling using EventBridge and AWS Lambda.
- Human-approval gate for recovery actions.

### 4. Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Containerization | Docker |
| Container Registry | Amazon ECR |
| Deployment | Amazon ECS, AWS Fargate |
| Load Balancing | Application Load Balancer |
| Monitoring | Amazon CloudWatch |
| Event Handling | Amazon EventBridge, AWS Lambda |
| Infrastructure | Terraform |
| CI/CD | GitHub Actions |
| Version Control | Git, GitHub |
| AI Analysis | Python-based incident analyzer |
| Potential AI Integration | Amazon Bedrock, subject to availability and access |

### 5. System Architecture

The project brings together application deployment, monitoring, incident analysis and controlled recovery.

1. The FastAPI application runs in a Docker container.
2. The Docker image is stored in Amazon ECR.
3. Amazon ECS with AWS Fargate runs the application.
4. An Application Load Balancer provides access to the application.
5. CloudWatch monitors application and infrastructure signals.
6. EventBridge routes configured incident events to an AWS Lambda handler.
7. The incident handler processes incidents and applies an approval gate.
8. Recovery actions require appropriate approval and controlled execution.
9. Application health can be checked through the health endpoint.

### 6. Repository Structure

```text
AIRA/
├── README.md
├── Dockerfile
├── .dockerignore
├── .github/
│   └── workflows/
│       └── deploy.yml
├── application/
│   └── backend/
└── ai-engine/
    └── incident-analyzer/
```

### 7. Application API Endpoints

The FastAPI backend provides the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application welcome response |
| GET | `/health` | Application health check |
| GET | `/version` | Application version |
| GET | `/docs` | Interactive Swagger API documentation |
| GET | `/api/orders` | Sample orders endpoint |
| GET | `/simulate/error` | Simulate an application error |
| GET | `/simulate/slow` | Simulate a delayed response |
| POST | `/analyze-incident` | Analyse an incident |

### 8. AI Incident Analysis

The incident analyzer is implemented in Python.

It is designed to process incident information, identify possible causes and provide recovery recommendations.

Recovery recommendations must be checked against predefined policies before any action is considered for execution.

Amazon Bedrock is a potential integration and should not be considered an active dependency unless it is configured and verified.

### 9. Docker and CI/CD

The application is containerized using Docker.

The deployment workflow is maintained at:

`.github/workflows/deploy.yml`

The GitHub Actions workflow:

1. Builds the Docker image.
2. Authenticates with Amazon ECR using GitHub OIDC.
3. Pushes the image to Amazon ECR.
4. Registers an updated ECS task definition.
5. Updates the ECS service.
6. Waits for the ECS service to become stable.

The workflow supports deployment when changes are pushed to the `develop` branch and can also be started manually.

### 10. AWS Deployment

The application has been deployed using:

- Amazon ECR for container image storage.
- Amazon ECS with AWS Fargate for container execution.
- An Application Load Balancer for application access.
- Amazon CloudWatch for monitoring.
- AWS IAM roles for controlled access.

The deployed application exposes its API and health-check endpoints through the load balancer.

### 11. Monitoring and Recovery

The monitoring workflow uses:

- Amazon CloudWatch for monitoring and alarms.
- Amazon EventBridge for event routing.
- AWS Lambda for incident handling.
- A human-approval gate before recovery execution.

The CloudWatch-to-EventBridge-to-Lambda incident-handling flow has been demonstrated.

The approval gate can return an `awaiting_human_approval` status without executing recovery.

The approval-to-ECS recovery execution path must be verified before it is presented as a completed end-to-end automated recovery feature.

### 12. Running the Application Locally

Make sure Docker Desktop is running.

Build the Docker image:

```powershell
docker build -t aira-api:latest .
```

Run the container:

```powershell
docker run --rm --name aira-api-local -p 8000:8000 aira-api:latest
```

Open the following URLs:

- Application: http://localhost:8000/
- Health check: http://localhost:8000/health
- API documentation: http://localhost:8000/docs

### 13. Deployment Verification

The following checks can be used to verify the deployed application:

- Application welcome endpoint responds successfully.
- Health endpoint reports a healthy status.
- Version endpoint returns the application version.
- Swagger documentation is accessible.
- ECS service reports a running task.
- Load balancer target health reports healthy.
- GitHub Actions deployment workflow completes successfully.

### 14. Team Responsibilities

| Team Member | Responsibility |
|---|---|
| Member 1 | AWS Infrastructure and Terraform |
| Member 2 | Application Development and AI Analysis |
| Member 3 | Docker, Container Deployment and CI/CD |
| Member 4 | Monitoring and Automated Recovery |

### 15. Project Status

The application containerization, AWS application deployment and GitHub Actions CI/CD workflow have been demonstrated successfully.

The monitoring and incident-handling flow using CloudWatch, EventBridge and Lambda has also been demonstrated.

The human-approval gate is implemented in the incident-handling flow. The complete approval-triggered recovery execution and post-recovery verification should be treated as pending until tested end to end.

### 16. Safety and Security

- AI-generated recommendations must be validated against predefined policies.
- Arbitrary AI-generated commands must never be executed directly.
- Recovery actions should require appropriate authorization and approval.
- AWS access should follow the principle of least privilege.
- GitHub Actions should use OIDC-based authentication rather than storing long-lived AWS access keys.
- Secrets and sensitive configuration files must not be committed to the repository.

### 17. Future Enhancements

- Complete and test the human-approval-to-ECS recovery integration.
- Verify post-recovery application health automatically.
- Improve incident analysis and recovery recommendations.
- Integrate Amazon Bedrock if access and project requirements permit.
- Expand monitoring, logging and incident reporting.
- Add automated tests for application and recovery components.

