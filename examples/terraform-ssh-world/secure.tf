# Safe counterpart to vulnerable.tf.
# Administration is limited to the bastion security group.

resource "aws_security_group" "app" {
  name        = "app"
  description = "application"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "ssh from the bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }
}
