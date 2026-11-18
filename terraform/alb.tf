resource "aws_lb" "aira_alb" {
  name               = "aira-alb"
  internal           = false
  load_balancer_type = "application"

  security_groups = [
    aws_security_group.alb_sg.id
  ]

  subnets = [
    aws_subnet.public_1.id,
    aws_subnet.public_2.id
  ]

  tags = {
    Project = "AIRA"
  }
}

resource "aws_lb_target_group" "aira_tg" {
  name        = "aira-targets"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.aira_vpc.id
  target_type = "ip"

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.aira_alb.arn

  port     = 80
  protocol = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.aira_tg.arn
  }
}

