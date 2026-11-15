# INTENTIONALLY VULNERABLE — teaching fixture for security-audit-skills.
# Do not apply this configuration.

resource "aws_security_group" "app" {
  name        = "app"
  description = "application"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "ssh from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
