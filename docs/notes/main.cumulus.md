---
id: ifujhetbiuz44o790amuwy2
title: Cumulus
desc: ''
updated: 1672875026787
created: 1672869663107
---

You need to do associate IP to get it to login via ssh
If you rebuild your known hosts file will compplain and you need to delete the offending line and the 3 lines above

### Setup

Ubuntu 18 seems to work. Some kind of security error on ubuntu 20+ not worth worrying about
sudo apt update && sudo apt -y upgrade
cd /tmp && curl https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh --output anaconda.sh // # accept agreement and type yes to init
- Run anaconda and click yes
- Run ssh-keygen to make ssh key and add to Github
- sudo apt install make && make condainit
- sudo ufw allow 80/tcp
- sudo apt-get install iptables-persistent
- sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

### To get app to run
https://serverfault.com/questions/112795/how-to-run-a-server-on-port-80-as-a-normal-user-on-linux
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080