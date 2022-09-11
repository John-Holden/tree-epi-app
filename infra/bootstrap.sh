#!/bin/bash


apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install git make \
	apt-transport-https ca-certificates curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update && DEBIAN_FRONTEND=noninteractive apt -y install docker-ce docker-ce-cli containerd.io

DEBIAN_FRONTEND=noninteractive apt-get install -y docker-compose-plugin
echo "alias docker-compose='docker compose'" >> ~/.bashrc && . ~/.bashrc

cd /opt/ && git clone https://github.com/John-Holden/tree-epi-app.git


