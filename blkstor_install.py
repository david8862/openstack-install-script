#!/usr/bin/python
# Filename: blkstor_install.py
#
# Copyright (C) 2017  Xiaobin Zhang (david8862@gmail.com)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


# This is an automation script for openstack Newton block storage node installation
# on Ubuntu 16.04 or CentOS 7 host

# Python environment should be installed on your Ubuntu 16.04 host.
# If not, please use "apt-get install python" or "yum install python" to do that.


import os, sys, platform, getopt
import ConfigParser

ADMIN_PASS = 'cisco123'
DEMO_PASS = 'cisco123'
RABBIT_PASS = 'cisco123'
CINDER_DBPASS = 'cisco123'
CINDER_PASS = 'cisco123'
CONTROLLER = 'controller'
CONTROLLER_IP = '10.74.130.52'

NTP_NAME = 'controller'
DB_NAME = 'controller'
MQ_NAME = 'controller'
MEMCACHE_NAME = 'controller'
KEYSTONE_NAME = 'controller'
GLANCE_NAME = 'controller'

def create_env_script():
    # create admin & demo client env script
    admin_openrc = open('admin-openrc', 'w+')
    admin_openrc.write('export OS_PROJECT_DOMAIN_NAME=default\n')
    admin_openrc.write('export OS_USER_DOMAIN_NAME=default\n')
    admin_openrc.write('export OS_PROJECT_NAME=admin\n')
    admin_openrc.write('export OS_USERNAME=admin\n')
    admin_openrc.write('export OS_PASSWORD='+ADMIN_PASS+'\n')
    admin_openrc.write('export OS_AUTH_URL=http://'+KEYSTONE_NAME+':35357/v3\n')
    admin_openrc.write('export OS_IDENTITY_API_VERSION=3\n')
    admin_openrc.write('export OS_IMAGE_API_VERSION=2\n')
    admin_openrc.close()

    demo_openrc = open('demo-openrc', 'w+')
    demo_openrc.write('export OS_PROJECT_DOMAIN_NAME=default\n')
    demo_openrc.write('export OS_USER_DOMAIN_NAME=default\n')
    demo_openrc.write('export OS_PROJECT_NAME=demo\n')
    demo_openrc.write('export OS_USERNAME=demo\n')
    demo_openrc.write('export OS_PASSWORD='+DEMO_PASS+'\n')
    demo_openrc.write('export OS_AUTH_URL=http://'+KEYSTONE_NAME+':5000/v3\n')
    demo_openrc.write('export OS_IDENTITY_API_VERSION=3\n')
    demo_openrc.write('export OS_IMAGE_API_VERSION=2\n')
    demo_openrc.close()


def get_distribution():
    ######################################################################
    # get host distribution info, now only support Ubuntu16.04 and CentOS7
    ######################################################################
    if platform.system() == 'Linux':
        try:
            distribution = platform.linux_distribution()[0].capitalize()
            version = platform.linux_distribution()[1].capitalize()
            if 'Ubuntu' in distribution and version == '16.04':
                distribution = 'Ubuntu'
            elif 'Centos' in distribution and version.startswith('7.'):
                distribution = 'CentOS'
            else:
                distribution = 'OtherLinux'
        except:
            distribution = platform.dist()[0].capitalize()
    else:
        distribution = None
    return distribution


def ubuntu_ntp_install():
    ##################################################################### 
    # install & config NTP service
    ##################################################################### 
    os.system('sudo apt-get install chrony -y')
    os.system('sudo cp /etc/chrony/chrony.conf /etc/chrony/chrony.conf.bak')
    os.system('sudo echo server '+NTP_NAME+' iburst > /etc/chrony/chrony.conf')
    os.system('sudo echo generatecommandkey >> /etc/chrony/chrony.conf')
    os.system('sudo echo makestep 10 3 >> /etc/chrony/chrony.conf')
    os.system('sudo service chrony restart')


def ubuntu_client_install():
    ##################################################################### 
    # install & config Openstack client
    ##################################################################### 
    os.system('sudo apt-get install software-properties-common -y')
    os.system('sudo add-apt-repository cloud-archive:newton -y')
    os.system('sudo apt-get update & sudo apt-get dist-upgrade -y')
    os.system('sudo apt-get install python-openstackclient -y')
    os.system('sudo apt-get update & sudo apt-get dist-upgrade -y')


def ubuntu_cinder_install(volume, ipaddr):
    ##################################################################### 
    # install & config lvm & cinder volume
    ##################################################################### 
    os.system('sudo apt-get install lvm2 thin-provisioning-tools -y')
    os.system('systemctl enable lvm2-lvmetad.service')
    os.system('systemctl enable lvm2-lvmetad.socket')
    os.system('systemctl start lvm2-lvmetad.service')
    os.system('systemctl start lvm2-lvmetad.socket')


    os.system('pvcreate /dev/'+volume)
    os.system('vgcreate cinder-volumes /dev/'+volume)
    ################################################################################
    # TODO: here we insert the filter right after the header "device {". Not sure if
    #       it works. May need to verify. Refer to:
    #       http://docs.openstack.org/newton/zh_CN/install-guide-ubuntu/cinder-storage-install.html
    ################################################################################
    os.system('sed -i \'/devices {/a\ \tfilter = [ "a|'+volume+'|","r|.*|" ]\' /etc/lvm/lvm.conf')

    os.system('sudo apt-get install cinder-volume -y')

    default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'enabled_backends':'lvm', 'glance_api_servers':'http://'+GLANCE_NAME+':9292'}

    keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'cinder', 'password':CINDER_PASS}

    lvm = {'volume_driver':'cinder.volume.drivers.lvm.LVMVolumeDriver', 'volume_group':'cinder-volumes', 'iscsi_protocol':'iscsi', 'iscsi_helper':'tgtadm', 'lvm_type':'auto'}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/cinder/cinder.conf /etc/cinder/cinder.conf.bak')
    print "cp /etc/cinder/cinder.conf done!"
    with open('/etc/cinder/cinder.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://cinder:'+CINDER_DBPASS+'@'+DB_NAME+'/cinder')
        for (k,v) in default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'lvm' not in sections:
            config.add_section('lvm')
        for (k,v) in lvm.iteritems():
            config.set('lvm', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/cinder/tmp')

        config.write(open('/etc/cinder/cinder.conf', 'w'))
        #cfgfile.close()

    ################################################################################
    # TODO: here is some hack code change for the cinder-volume service. Refer to:
    #       https://ask.openstack.org/en/question/100163/cinder-volume-cappedversionunknown/
    #       it should be able to be removed after Ubuntu package fix them.
    ################################################################################
#    os.system('sed -i "/OBJ_VERSIONS.add(\'1.3\'/a\OBJ_VERSIONS.add(\'1.11\', {\'GroupSnapshot\': \'1.0\', \'GroupSnapshotList\': \'1.0\',\'Group\': \'1.1\'})" /usr/lib/python2.7/dist-packages/cinder/objects/base.py')
#    os.system('sed -i "/OBJ_VERSIONS.add(\'1.3\'/a\# Hacked by messeiry error in version 1.11, this will add version 1.11 to the supported versions, the code on Githib is uch uipdated than this one" /usr/lib/python2.7/dist-packages/cinder/objects/base.py')

#    os.system('sed -i "/ ctxt = self.serializer.serialize_context/a\        self.version_cap = 3.0" /usr/lib/python2.7/dist-packages/oslo_messaging/rpc/client.py')
#    os.system('sed -i "/ ctxt = self.serializer.serialize_context/a\        self.version = 3.0" /usr/lib/python2.7/dist-packages/oslo_messaging/rpc/client.py')
#    os.system('sed -i "/ ctxt = self.serializer.serialize_context/a\        # ERROR  oslo_service.service Requested message version, 3.0 is incompatible" /usr/lib/python2.7/dist-packages/oslo_messaging/rpc/client.py')
#    os.system('sed -i "/ ctxt = self.serializer.serialize_context/a\        # Hacked by Messeiry: this is to force the application to state same versions, by this we should fix error" /usr/lib/python2.7/dist-packages/oslo_messaging/rpc/client.py')

#    os.system('sed -i "/version_parts = version/i\    # Hacked by Messeiry as temp fix, the log was showing an error that version dont have a function called split probably a data tytpe error" /usr/lib/python2.7/dist-packages/oslo_messaging/_utils.py')
#    os.system('sed -i "/version_parts = version/i\    return True" /usr/lib/python2.7/dist-packages/oslo_messaging/_utils.py')


    os.system('service tgt restart')
    os.system('service cinder-volume restart')
    # here we clean the cinder-volumes-pool logical volume to make sure
    # cinder-scheduler service can get correct logical volume info
    # os.system('lvremove /dev/cinder-volumes/cinder-volumes-pool')
    # os.system('service tgt restart')
    # os.system('service cinder-volume restart')



def ubuntu_install(volume, ipaddr, hostname):
    print "Start installation on Ubuntu host"

    ##################################################################### 
    # config network
    ##################################################################### 
    os.system('hostname ' + hostname)
    os.system('cp /etc/hostname /etc/hostname.bak')
    print "cp /etc/hostname done!"
    os.system('echo '+hostname+' > /etc/hostname')

    os.system('cp /etc/hosts /etc/hosts.bak')
    print "cp /etc/hosts done!"
    os.system('sed -i \'/127.0.0.1/c 127.0.0.1 localhost '+hostname+'\' /etc/hosts')
    os.system('sed -i \'/127.0.1.1/d\' /etc/hosts')
    os.system('echo '+CONTROLLER_IP+'  '+CONTROLLER+' >> /etc/hosts')
    os.system('echo '+ipaddr+'  '+hostname+' >> /etc/hosts')

    create_env_script()
    ubuntu_ntp_install()
    ubuntu_client_install()
    ubuntu_cinder_install(volume, ipaddr)




def centos_ntp_install():
    ##################################################################### 
    # install & config NTP service
    ##################################################################### 
    os.system('yum install chrony -y')
    os.system('cp /etc/chrony.conf /etc/chrony.conf.bak')
    os.system('echo server '+NTP_NAME+' iburst > /etc/chrony.conf')
    os.system('sudo echo generatecommandkey >> /etc/chrony.conf')
    os.system('sudo echo makestep 10 3 >> /etc/chrony.conf')
    os.system('systemctl enable chronyd.service')
    os.system('systemctl start chronyd.service')


def centos_client_install():
    ##################################################################### 
    # install & config Openstack client
    ##################################################################### 
    os.system('yum install centos-release-openstack-newton -y')
    os.system('yum upgrade -y')
    os.system('yum install python-openstackclient -y')
    os.system('yum install openstack-selinux -y')
    os.system('yum upgrade -y')


def centos_cinder_install(volume, ipaddr):
    ##################################################################### 
    # install & config lvm & cinder volume
    ##################################################################### 
    os.system('yum install lvm2 -y')
    os.system('systemctl enable lvm2-lvmetad.service')
    os.system('systemctl start lvm2-lvmetad.service')
    os.system('pvcreate /dev/'+volume)
    os.system('vgcreate cinder-volumes /dev/'+volume)
    ################################################################################
    # TODO: here we insert the filter right after the header "device {". Not sure if
    #       it works. May need to verify. Refer to:
    #       http://docs.openstack.org/newton/zh_CN/install-guide-ubuntu/cinder-storage-install.html
    ################################################################################
    os.system('sed -i \'/devices {/a\ \tfilter = [ "a|'+volume+'|","r|.*|" ]\' /etc/lvm/lvm.conf')

    os.system('yum install openstack-cinder targetcli python-keystone -y')

    default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'enabled_backends':'lvm', 'glance_api_servers':'http://'+GLANCE_NAME+':9292'}

    keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'cinder', 'password':CINDER_PASS}

    lvm = {'volume_driver':'cinder.volume.drivers.lvm.LVMVolumeDriver', 'volume_group':'cinder-volumes', 'iscsi_protocol':'iscsi', 'iscsi_helper':'lioadm', 'lvm_type':'auto'}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/cinder/cinder.conf /etc/cinder/cinder.conf.bak')
    print "cp /etc/cinder/cinder.conf done!"
    with open('/etc/cinder/cinder.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://cinder:'+CINDER_DBPASS+'@'+DB_NAME+'/cinder')
        for (k,v) in default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'lvm' not in sections:
            config.add_section('lvm')
        for (k,v) in lvm.iteritems():
            config.set('lvm', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/cinder/tmp')

        config.write(open('/etc/cinder/cinder.conf', 'w'))
        #cfgfile.close()

    os.system('systemctl enable openstack-cinder-volume.service target.service')
    os.system('systemctl start openstack-cinder-volume.service target.service')
    # here we clean the cinder-volumes-pool logical volume to make sure
    # cinder-scheduler service can get correct logical volume info
    os.system('systemctl stop openstack-cinder-volume.service target.service')
    os.system('lvremove /dev/cinder-volumes/cinder-volumes-pool')
    os.system('systemctl start openstack-cinder-volume.service target.service')



def centos_install(volume, ipaddr, hostname):
    print "Start installation on CentOS host"

    ##################################################################### 
    # config network
    ##################################################################### 
    os.system('hostname ' + hostname)
    os.system('cp /etc/hostname /etc/hostname.bak')
    print "cp /etc/hostname done!"
    os.system('echo '+hostname+' > /etc/hostname')

    os.system('cp /etc/sysconfig/network /etc/sysconfig/network.bak')
    print "cp /etc/sysconfig/network done!"
    os.system('echo HOSTNAME='+hostname+' >> /etc/sysconfig/network')
    os.system('sed -i \'/HOSTNAME=/c HOSTNAME='+hostname+'\' /etc/sysconfig/network')

    os.system('cp /etc/hosts /etc/hosts.bak')
    print "cp /etc/hosts done!"
    os.system('sed -i \'/127.0.0.1/c 127.0.0.1 localhost '+hostname+'\' /etc/hosts')
    os.system('sed -i \'/127.0.1.1/d\' /etc/hosts')
    os.system('echo '+CONTROLLER_IP+'  '+CONTROLLER+' >> /etc/hosts')
    os.system('echo '+ipaddr+'  '+hostname+' >> /etc/hosts')

    ##################################################################### 
    # disable IPv6
    ##################################################################### 
    os.system('cp /etc/sysctl.conf /etc/sysctl.conf.bak')
    print "cp /etc/sysctl.conf done!"
    os.system('echo net.ipv6.conf.all.disable_ipv6 = 1 >> /etc/sysctl.conf')
    os.system('echo net.ipv6.conf.default.disable_ipv6 = 1 >> /etc/sysctl.conf')
    os.system('echo net.ipv6.conf.lo.disable_ipv6 = 1 >> /etc/sysctl.conf')
    os.system('sysctl -p')

    ##################################################################### 
    # disable firewall
    ##################################################################### 
    os.system('systemctl stop firewalld.service')
    os.system('systemctl disable firewalld.service')

    create_env_script()
    centos_ntp_install()
    centos_client_install()
    centos_cinder_install(volume, ipaddr)





def usage():
    print 'blkstor_install.py [options]'
    print 'now only support Ubuntu16.04 and CentOS7'
    print 'Options:'
    print '-v, --volume=<VolumeName>     Physical volume device name for cinder'
    print '                              service. e.g. sdb(not /dev/sdb!)'
    print '-m, --hostname=<HostName>     host name'
    print '-i, --ipaddr=<IPAddress>      host IP address'
    print '                              for Self-service network, it should be'
    print '                              the management network IP address'


def main(argv):
    platform = ''
    volume = ''
    ipaddr = ''
    hostname = ''
    try:
        opts, args = getopt.getopt(argv,"hv:i:m:",["volume=","ipaddr=","hostname="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
           usage()
           sys.exit()
        elif opt in ("-v", "--volume"):
           volume = arg
        elif opt in ("-i", "--ipaddr"):
           ipaddr = arg
        elif opt in ("-m", "--hostname"):
           hostname = arg

    # check param integrity
    if volume == '' or ipaddr == '' or hostname == '':
        usage()
        sys.exit()

    platform = get_distribution()

    if platform == 'Ubuntu':
        ubuntu_install(volume, ipaddr, hostname)
    elif platform == 'CentOS':
        centos_install(volume, ipaddr, hostname)
    else :
        print 'Unsupported host platform!'
        usage()


if __name__ == "__main__":
    main(sys.argv[1:])

