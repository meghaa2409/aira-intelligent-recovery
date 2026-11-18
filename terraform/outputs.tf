output "vpc_id" {
  value = aws_vpc.aira_vpc.id
}

output "ecr_repository_url" {
  value = aws_ecr_repository.aira_repo.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.aira_cluster.name
}

output "alb_dns_name" {
  value = aws_lb.aira_alb.dns_name
}