#####################################################
# Define providers
#####################################################

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}


# Configure the AWS Provider
provider "aws" {
  region = "eu-west-1"
}

# #####################################################
# # Define base networking, vpc & subnets
# #####################################################

resource "aws_vpc" "main" {
  cidr_block = "172.16.0.0/16"
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "sb_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "172.16.10.0/24"
  availability_zone = "eu-west-1a"
}

resource "aws_subnet" "sb_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "172.16.11.0/24"
  availability_zone = "eu-west-1b"
}

resource "aws_route_table" "allow" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "allow-all"
  }
}

resource "aws_route_table_association" "sb_a_rta" {
  subnet_id      = aws_subnet.sb_a.id
  route_table_id = aws_route_table.allow.id
}


resource "aws_route_table_association" "sb_b_rta" {
  subnet_id      = aws_subnet.sb_b.id
  route_table_id = aws_route_table.allow.id
}

#####################################################
# Security groups
#####################################################

resource "aws_security_group" "tree_epi_app" {
name = "allow-all-sg"
vpc_id = aws_vpc.main.id
# Allow SSH 
ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
# Allow ALB to FE docker
ingress {
    from_port   = 80
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

# Allow FE docker to BE docker 
ingress {
    from_port   = 3000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_network_interface_sg_attachment" "sg_attachment" {
  security_group_id    = aws_security_group.tree_epi_app.id
  network_interface_id = "${aws_instance.webserver.primary_network_interface_id}"
}

resource "aws_security_group" "tree_epi_alb" {
  name        = "lb_security_group"
  description = "SG from NLB to ALB"
  vpc_id      = "${aws_vpc.main.id}"

  # All inbound trafic
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow FE docker to BE docker 
ingress {
    from_port   = 3000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow FE docker to BE docker 
ingress {
    from_port   = 80
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#####################################################
# NLB to recive incoming traffic
#####################################################

resource "aws_eip" "lb_ip" {
 vpc      = true
}

resource "aws_lb" "nlb" {
  name               = "tree-epi-nlb"
  load_balancer_type = "network"
  subnet_mapping {
    subnet_id     = aws_subnet.sb_a.id
    allocation_id = aws_eip.lb_ip.id
  }
}


resource "aws_lb_listener" "network_listener" {
  load_balancer_arn = "${aws_lb.nlb.arn}"
  port = "80"
  protocol = "TCP"
  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.tree_epi_nlb.arn
  }
}


resource "aws_lb_target_group" "tree_epi_nlb" {
  name = "tree-epi-nlb-target-group"
  target_type = "alb"
  port = "80"
  protocol = "TCP"
  vpc_id = aws_vpc.main.id
}


resource "aws_alb_target_group_attachment" "nlb_to_alb" {
  target_group_arn = aws_lb_target_group.tree_epi_nlb.arn
  target_id        = aws_alb.tree_epi_alb.arn
  port             = aws_lb_listener.network_listener.port
}


#####################################################
# ALB to recive incoming traffic from NLB
#####################################################

resource "aws_alb" "tree_epi_alb" {
    name = "tree-epi-alb"
    security_groups = [ aws_security_group.tree_epi_alb.id ]
    subnets = ["${aws_subnet.sb_a.id}" , "${aws_subnet.sb_b.id}"]
    tags = {
      Name = "tree-epidemics-alb"
      }
}


resource "aws_alb_listener" "tree_epi_app_listener" {
  load_balancer_arn = "${aws_alb.tree_epi_alb.arn}"
  port = "80"
  protocol = "HTTP"
  default_action {
    type = "forward"
    target_group_arn = aws_alb_target_group.tree_epi_app.arn
  }
}


resource "aws_alb_target_group" "tree_epi_app" {
  name = "tree-epi-target-group"
  port = 3000
  protocol = "HTTP"
  vpc_id = aws_vpc.main.id
}


resource "aws_alb_target_group_attachment" "tgattachment" {
  target_group_arn = aws_alb_target_group.tree_epi_app.arn
  target_id        = aws_instance.webserver.id
}

#####################################################
# ALB routes incoming traffic to EC2
#####################################################

resource "aws_instance" "webserver" {
ami           = "ami-0aca9de1791dcec2a" // Deb-11
instance_type = "t2.medium"
subnet_id     = aws_subnet.sb_a.id
key_name      =  aws_key_pair.ssh_key.key_name
tags          = {
  Name        = "My EC2 instance",
  }
root_block_device {
    volume_size = 20
  }
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "ssh-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC4D5SASj9GvEJyfEjGZkHLaPgqvab+IZ8BnXjUsA8iC2ZejnF+KiSwIhw1Xx9OqbTsyNJKStn8XPJ9U1+uJf9jUSKgvv5M9zaqB1QexNAarWzNDb08yLx8QLmaZzKeUw80/gv6y1HuZp5dqiauRNI4B+tKjnLDqTJWK2CltBg7puAcpP3E1ooi1E2vH4S1ZPbm3pka7ZFfXzr0zniw2K+MfO/Uc9HHvvXOq1rAvZCHS0XmVvUjVnf86QP4KMxtUxqhb7Cv6Z9GzZofWkq6cNHxjTEkD+K5EuOj+TaCWcXMsW7AX4Uitf/niWSiDQ2NSIW9n+CZja4sD9ZZBS8AjPzt4OIaVFUMICMnXMpUiY9fWsQkj0MhLcOWz6eoygdPZNm4w8vKilAHcjJ5C0Hve5Wis20dWzNvdh7AeouVuDH00cQmI68rFjVCccugqraOZzM67DkGjOVykuET9Mlnf5bNFx0jYyHz44awXurjzIinczAs+k5Xhyp3nel+kVvbKCk= john@john-XPS-15-9500"
  }

resource "aws_network_interface" "web_interface" {
  subnet_id   = aws_subnet.sb_a.id
}

resource "aws_eip" "ssh_ip" {
 vpc      = true
 instance = aws_instance.webserver.id
}
