resource "aws_ecr_repository" "aira_repo" {
  name                 = "aira-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name    = "aira-api"
    Project = "AIRA"
  }
}

