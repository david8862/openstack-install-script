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
	echo Usage: "`basename $0` [ Provider | Self-service ] RELEASE HOSTNAME IPADDRESS INTERFACE"
	echo "Currently only support Ubuntu16.04 and CentOS7"
	echo "RELEASE      Openstack release. Now support Newton and Ocata"
	echo "HOSTNAME     host name"
	echo "IPADDRESS    host IP address"
	echo "             for Self-service network, it should be"
	echo "             the management network IP address"
	echo "INTERFACE    ethernet device name, e.g. eth0"
	echo "             which connect to the public network"
	exit 1
fi

PLATFORM=$(lsb_release -is 2>/dev/null)
VERSION=$(lsb_release -rs 2>/dev/null)
NETWORK=$1
RELEASE=$2
HOSTNAME=$3
IPADDR=$4
INTERFACE=$5


if [ $(id -un) != "root" ]; then
    echo "Please use root account."
    exit 1
fi

if [ $PLATFORM == "Ubuntu" ] && [ $VERSION == "16.04" ]; then
    #echo "on Ubuntu platform"
    apt update && apt full-upgrade -y
    apt install wget vim python python-mysqldb -y
    python control_install.py -n $NETWORK -r $RELEASE -m $HOSTNAME -i $IPADDR -f $INTERFACE
elif [ $PLATFORM == "CentOS" ] && [ ${VERSION:0:2} == "7." ]; then
    #echo "on CentOS platform"
    yum upgrade -y
    yum install wget vim python MySQL-python -y
    python control_install.py -n $NETWORK -r $RELEASE -m $HOSTNAME -i $IPADDR -f $INTERFACE
else
    echo "Unsupport host platform!"
fi



