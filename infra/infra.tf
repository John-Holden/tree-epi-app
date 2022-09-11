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


resource "aws_vpc" "main" {
  cidr_block = "172.16.0.0/16"
}


resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "subnet" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "172.16.10.0/24"
}

resource "aws_network_interface" "web_interface" {
  subnet_id   = aws_subnet.subnet.id
}

# TODO make me bigger!!
resource "aws_instance" "webserver" {
ami           = "ami-0da3823b95bf63c23" //Ubuntu AMI
instance_type = "t2.large"
subnet_id     = aws_subnet.subnet.id
key_name      =  aws_key_pair.ssh_key.key_name
tags          = {
  Name        = "My EC2 instance",
  }

root_block_device {
    volume_size = 20
  }
}

resource "aws_eip" "lb" {
 instance = aws_instance.webserver.id
 vpc      = true
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "ssh-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC4D5SASj9GvEJyfEjGZkHLaPgqvab+IZ8BnXjUsA8iC2ZejnF+KiSwIhw1Xx9OqbTsyNJKStn8XPJ9U1+uJf9jUSKgvv5M9zaqB1QexNAarWzNDb08yLx8QLmaZzKeUw80/gv6y1HuZp5dqiauRNI4B+tKjnLDqTJWK2CltBg7puAcpP3E1ooi1E2vH4S1ZPbm3pka7ZFfXzr0zniw2K+MfO/Uc9HHvvXOq1rAvZCHS0XmVvUjVnf86QP4KMxtUxqhb7Cv6Z9GzZofWkq6cNHxjTEkD+K5EuOj+TaCWcXMsW7AX4Uitf/niWSiDQ2NSIW9n+CZja4sD9ZZBS8AjPzt4OIaVFUMICMnXMpUiY9fWsQkj0MhLcOWz6eoygdPZNm4w8vKilAHcjJ5C0Hve5Wis20dWzNvdh7AeouVuDH00cQmI68rFjVCccugqraOZzM67DkGjOVykuET9Mlnf5bNFx0jYyHz44awXurjzIinczAs+k5Xhyp3nel+kVvbKCk= john@john-XPS-15-9500"
  }

//security.tf
resource "aws_security_group" "ingress-all-test" {
name = "allow-all-sg"
vpc_id = aws_vpc.main.id
ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
  ingress {
    from_port = 3000
    to_port   = 3000
    protocol  = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }
egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_network_interface_sg_attachment" "sg_attachment" {
  security_group_id    = aws_security_group.ingress-all-test.id
  network_interface_id = "${aws_instance.webserver.primary_network_interface_id}"
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


resource "aws_route_table_association" "subnet-rta" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.allow.id
}