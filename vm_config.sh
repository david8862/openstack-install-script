#!/bin/sh

# PLATFORM: CentOS, Ubuntu
PLATFORM=$(lsb_release -is 2>/dev/null)

echo "root:cisco123" | sudo chpasswd
sudo sed -i '/PermitRootLogin /c PermitRootLogin yes' /etc/ssh/sshd_config
sudo sed -i '/PasswordAuthentication /c PasswordAuthentication yes' /etc/ssh/sshd_config

if [ $PLATFORM == "Ubuntu" ]; then
    #echo "on Ubuntu platform"
    sudo service ssh restart
    sudo apt install -y rar p7zip vim git telnet
elif [ $PLATFORM == "CentOS" ]; then
    #echo "on CentOS platform"
    sudo systemctl restart sshd
    sudo yum -y install bzip2 vim git telnet
else
    sudo service ssh restart
    echo "Unsupport host platform!"
fi

