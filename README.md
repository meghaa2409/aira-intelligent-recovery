# AIRA – AI-Driven Intelligent Recovery and Deployment Orchestrator for AWS

## 1. Project Overview

AIRA (AI-Driven Intelligent Recovery and Deployment Orchestrator for AWS) is a cloud-based project designed to monitor application health, analyze incidents, and support recovery operations in AWS environments.

It integrates application development, AI-based incident analysis, Docker containerization, AWS infrastructure, monitoring, and CI/CD automation into one solution.

## 2. Project Objectives

- Deploy applications reliably on AWS.
- Monitor application health and identify incidents.
- Analyze incident information using an AI-based incident analyzer.
- Support recovery workflows with human approval.
- Automate application builds and deployments using GitHub Actions.
- Improve application reliability through cloud monitoring and recovery integration.

## 3. Key Features

- FastAPI-based backend application.
- AI-based incident analysis.
- Live incident analysis using application monitoring data.
- Docker-based application containerization.
- Amazon ECR for Docker image storage.
- Amazon ECS with AWS Fargate for deployment.
- Application Load Balancer for application access.
- Amazon CloudWatch monitoring.
- EventBridge and Lambda-based incident handling.
- Recovery approval and rejection API endpoints.
- GitHub Actions CI/CD automation.
- Terraform-based infrastructure configuration.

## 4. Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| AI / Analysis | Python Incident Analyzer |
| Containerization | Docker |
| Container Registry | Amazon ECR |
| Container Deployment | Amazon ECS, AWS Fargate |
| Load Balancing | AWS Application Load Balancer |
| Monitoring | Amazon CloudWatch |
| Event Handling | Amazon EventBridge |
| Serverless Processing | AWS Lambda |
| CI/CD | GitHub Actions |
| Infrastructure as Code | Terraform |
| Cloud Platform | Amazon Web Services |

## 5. Project Structure

```text
AIRA/
├── README.md
├── Dockerfile
├── .dockerignore
├── .gitignore
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── application/
│   └── backend/
│
├── ai-engine/
│   └── incident-analyzer/
│
├── monitoring/
│
├── recovery-workflow/
│
├── recovery/
│   └── lambda/
│
└── terraform/
```


## 6. API Endpoints

The FastAPI application exposes the following endpoints through Swagger UI.

**Swagger Documentation:**

http://aira-alb-879435582.ap-south-1.elb.amazonaws.com/docs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application welcome page |
| GET | `/health` | Checks application health |
| GET | `/version` | Returns application version |
| GET | `/api/orders` | Retrieves order information |
| GET | `/simulate/error` | Simulates an application error |
| GET | `/simulate/slow` | Simulates a slow response |
| POST | `/analyze-incident` | Analyzes supplied incident information |
| GET | `/analyze-live-incident` | Analyzes live incident information |
| POST | `/recovery/approve` | Handles recovery approval |
| POST | `/recovery/reject` | Handles recovery rejection |

## 7. AWS Architecture and Deployment

The application uses the following AWS services:

1. **Amazon VPC:** Provides the cloud network environment.
2. **Amazon ECS with Fargate:** Runs the containerized application.
3. **Amazon ECR:** Stores Docker images.
4. **Application Load Balancer:** Routes incoming application traffic.
5. **Amazon CloudWatch:** Supports application monitoring.
6. **Amazon EventBridge:** Supports event-driven incident handling.
7. **AWS Lambda:** Processes incident-handling events.

## 8. Docker Containerization

Docker packages the FastAPI application and its dependencies into a portable container image.

Build the Docker image:

```bash
docker build -t aira-api .
```

Run the container:

```bash
docker run -d -p 8000:8000 --name aira-api-test aira-api
```

Verify the application:

```text
http://localhost:8000/health
```

Open Swagger UI:

```text
http://localhost:8000/docs
```

## 9. CI/CD Pipeline

A GitHub Actions workflow automates the application deployment process.

Workflow file:

`.github/workflows/deploy.yml`

The pipeline performs these steps:

1. Checks out the source code.
2. Configures AWS credentials using OpenID Connect (OIDC).
3. Logs in to Amazon ECR.
4. Builds and pushes the Docker image.
5. Retrieves the current ECS task definition.
6. Updates the container image.
7. Registers a new ECS task definition.
8. Deploys the updated task definition to ECS.
9. Waits for the ECS service to become stable.

This reduces manual deployment steps and supports consistent application updates.

## 10. Monitoring and Incident Analysis

AIRA integrates monitoring and incident analysis components.

- CloudWatch supports application metric monitoring.
- EventBridge supports event-driven incident handling.
- Lambda processes monitoring events.
- The incident analyzer evaluates incident information.
- The live incident analysis endpoint provides an interface for analyzing current application metrics.

## 11. Recovery Workflow

AIRA includes recovery workflow components that support human-approved recovery operations.

The application provides:

- Recovery approval endpoint.
- Recovery rejection endpoint.
- Monitoring and incident-handling integration.
- Recovery-related Lambda components.

**Implementation status:** Monitoring, incident analysis, and recovery infrastructure have been integrated. Complete human-approved automated recovery execution and end-to-end ECS scaling still require validation.

## 12. Running the Application Locally

### Prerequisites

- Python 3.12 or compatible version.
- Docker Desktop.
- Git.

### Clone the repository

```bash
git clone https://github.com/meghaa2409/aira-intelligent-recovery.git
cd aira-intelligent-recovery
```

### Build the Docker image

```bash
docker build -t aira-api .
```

### Start the container

```bash
docker run -d -p 8000:8000 --name aira-api-test aira-api
```

### Verify application health

Open:

```text
http://localhost:8000/health
```

### Access API documentation

Open:

```text
http://localhost:8000/docs
```

## 13. Team Contributions

The project is developed collaboratively by four team members.

| Member | Responsibility |
|---|---|
| Member 1 | AWS infrastructure and Terraform |
| Member 2 | FastAPI backend and AI incident analysis |
| Member 3 | Docker, Amazon ECR, ECS deployment, and CI/CD |
| Member 4 | Monitoring, incident handling, and recovery workflow |

## 14. Project Outcome

AIRA demonstrates the integration of application deployment, cloud infrastructure, monitoring, AI-based incident analysis, and recovery workflow capabilities using AWS services.

The project provides a foundation for improving application deployment reliability and supporting intelligent incident handling in cloud environments.

