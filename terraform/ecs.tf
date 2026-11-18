resource "aws_ecs_cluster" "aira_cluster" {
  name = "aira-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Project = "AIRA"
  }
}

resource "aws_cloudwatch_log_group" "aira_logs" {
  name              = "/ecs/aira-api"
  retention_in_days = 7
}