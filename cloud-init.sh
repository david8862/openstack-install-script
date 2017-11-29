#cloud-config

package_update: true
package_upgrade: true

write_files:
- path: /etc/hosts
  permissions: '0644'
  content: |
    192.168.1.4 server2
    192.168.1.5 server3
    192.168.1.6 server4
    192.168.1.7 server5

apt_mirror: http://rtp-linux.cisco.com/ubuntu/

packages:
  - vim
  - tree
  - git
  - wget
  - curl
  - python
  - python-pip
  - telnet

bootcmd:
  - echo "root:cisco123" | chpasswd
  - rpm -ivh http://rtp-linux.cisco.com/misc/cisco-centos-config-7.0-1.noarch.rpm


runcmd:
  - sed -i '/PermitRootLogin /c PermitRootLogin yes' /etc/ssh/sshd_config
  - sed -i '/PasswordAuthentication /c PasswordAuthentication yes' /etc/ssh/sshd_config
  - systemctl restart sshd

