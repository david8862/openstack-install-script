#! /bin/bash
#
# Copyright (C) 2016 Free Software Foundation,
# Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#
# main()
#
if [ $# -ne 5 ] ; then
    echo "Openstack newton installation script on Ubuntu16.04 or CentOS7"
	echo Usage: "`basename $0` [ Ubuntu | CentOS ] [ Provider | Self-service ] HOSTNAME IPADDRESS INTERFACE"
	echo "HOSTNAME     host name"
	echo "IPADDRESS    host IP address"
	echo "             for Self-service network, it should be"
	echo "             the management network IP address"
	echo "INTERFACE    ethernet device name, e.g. eth0"
	echo "             which connect to the public network"
	exit 1
fi

PLATFORM=$1
NETWORK=$2
HOSTNAME=$3
IPADDR=$4
INTERFACE=$5


if [ $(id -un) != "root" ]; then
    echo "Please use root account."
    exit 1
fi

if [ $PLATFORM == "Ubuntu" ]; then
    apt update && apt full-upgrade -y
    apt install python python-mysqldb -y
else
    yum upgrade -y
    yum install python MySQL-python -y
fi

python control_install.py -p $PLATFORM -n $NETWORK -m $HOSTNAME -i $IPADDR -f $INTERFACE


