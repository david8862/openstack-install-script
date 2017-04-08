#!/usr/bin/python
# Filename: share_install.py
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


# This is an automation script for openstack share file system node installation
# on Ubuntu 16.04 or CentOS 7 host. Now it support Newton and Ocata release

# Python environment should be installed on your Ubuntu 16.04 host.
# If not, please use "apt-get install python" or "yum install python" to do that.


import os, sys, platform, getopt
import ConfigParser

ADMIN_PASS = 'cisco123'
DEMO_PASS = 'cisco123'
RABBIT_PASS = 'cisco123'
NOVA_PASS = 'cisco123'
NEUTRON_PASS = 'cisco123'
CINDER_PASS = 'cisco123'
MANILA_DBPASS = 'cisco123'
MANILA_PASS = 'cisco123'
CONTROLLER = 'controller'
CONTROLLER_IP = '10.74.130.52'

NTP_NAME = 'controller'
DB_NAME = 'controller'
MQ_NAME = 'controller'
MEMCACHE_NAME = 'controller'
KEYSTONE_NAME = 'controller'
GLANCE_NAME = 'controller'
NEUTRON_NAME = 'controller'

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
    os.system('sudo echo server '+NTP_NAME+' iburst >> /etc/chrony/chrony.conf')
    os.system('sudo echo generatecommandkey >> /etc/chrony/chrony.conf')
    os.system('sudo echo makestep 10 3 >> /etc/chrony/chrony.conf')
    os.system('sudo service chrony restart')


def ubuntu_client_install(release):
    ##################################################################### 
    # install & config Openstack client
    ##################################################################### 
    os.system('sudo apt-get install software-properties-common -y')
    if release == 'Newton' or release == 'newton':
        os.system('sudo add-apt-repository cloud-archive:newton -y')
    elif release == 'Ocata' or release == 'ocata':
        os.system('sudo add-apt-repository cloud-archive:ocata -y')
    os.system('sudo apt-get update && sudo apt-get dist-upgrade -y')
    os.system('sudo apt-get install python-openstackclient -y')
    os.system('sudo apt-get update && sudo apt-get dist-upgrade -y')


def ubuntu_manila_install(volume, option, ipaddr):
    ##################################################################### 
    # install & config manila share node
    ##################################################################### 
    os.system('sudo apt-get install manila-share python-pymysql -y')


    default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'default_share_type':'default_share_type', 'rootwrap_config':'/etc/manila/rootwrap.conf'}

    keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_id':'default', 'user_domain_id': 'default', 'project_name':'service', 'username':'manila', 'password':MANILA_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/manila/manila.conf /etc/manila/manila.conf.bak')
    print "cp /etc/manila/manila.conf done!"
    with open('/etc/manila/manila.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://manila:'+MANILA_DBPASS+'@'+DB_NAME+'/manila')
        for (k,v) in default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/manila/tmp')

        config.write(open('/etc/manila/manila.conf', 'w'))
        #cfgfile.close()

    if option == 'No-Driver' or option == 'no-driver':
        os.system('sudo apt-get install lvm2 nfs-kernel-server -y')
        os.system('systemctl enable lvm2-lvmetad.service')
        os.system('systemctl enable lvm2-lvmetad.socket')
        os.system('systemctl start lvm2-lvmetad.service')
        os.system('systemctl start lvm2-lvmetad.socket')

        os.system('pvcreate /dev/'+volume)
        os.system('vgcreate manila-volumes /dev/'+volume)
        ################################################################################
        # TODO: here we insert the filter right after the header "device {". Not sure if
        #       it works. May need to verify. Refer to:
        #       http://docs.openstack.org/newton/zh_CN/install-guide-ubuntu/cinder-storage-install.html
        ################################################################################
        os.system('sed -i \'/devices {/a\ \tfilter = [ "a|'+volume+'|","r|.*|" ]\' /etc/lvm/lvm.conf')

        lvm = {'share_backend_name':'LVM', 'share_driver':'manila.share.drivers.lvm.LVMShareDriver', 'driver_handles_share_servers':'False', 'lvm_share_volume_group':'manila-volumes', 'lvm_share_export_ip':ipaddr}

        config = ConfigParser.ConfigParser()
        with open('/etc/manila/manila.conf', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            config.set('DEFAULT', 'enabled_share_backends', 'lvm')
            config.set('DEFAULT', 'enabled_share_protocols', 'NFS')
            if 'lvm' not in sections:
                config.add_section('lvm')
            for (k,v) in lvm.iteritems():
                config.set('lvm', k, v)
            config.write(open('/etc/manila/manila.conf', 'w'))
            #cfgfile.close()
    else : #Driver support for share server management
        os.system('sudo apt-get install neutron-plugin-linuxbridge-agent -y')

        neutron = {'url':'http://'+NEUTRON_NAME+':9696', 'auth_uri':'http://'+KEYSTONE_NAME+':5000', 'auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS}

        nova = {'auth_uri':'http://'+KEYSTONE_NAME+':5000', 'auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'nova', 'password':NOVA_PASS}

        cinder = {'auth_uri':'http://'+KEYSTONE_NAME+':5000', 'auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'cinder', 'password':CINDER_PASS}

        generic = {'share_backend_name':'GENERIC', 'share_driver':'manila.share.drivers.generic.GenericShareDriver', 'driver_handles_share_servers':'True', 'service_instance_flavor_id':'100', 'service_image_name':'manila-service-image', 'service_instance_user': 'manila', 'service_instance_password': 'manila', 'interface_driver':'manila.network.linux.interface.BridgeInterfaceDriver'}

        config = ConfigParser.ConfigParser()
        with open('/etc/manila/manila.conf', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            config.set('DEFAULT', 'enabled_share_backends', 'generic')
            config.set('DEFAULT', 'enabled_share_protocols', 'NFS')
            if 'neutron' not in sections:
                config.add_section('neutron')
            for (k,v) in neutron.iteritems():
                config.set('neutron', k, v)
            if 'nova' not in sections:
                config.add_section('nova')
            for (k,v) in nova.iteritems():
                config.set('nova', k, v)
            if 'cinder' not in sections:
                config.add_section('cinder')
            for (k,v) in cinder.iteritems():
                config.set('cinder', k, v)
            if 'generic' not in sections:
                config.add_section('generic')
            for (k,v) in generic.iteritems():
                config.set('generic', k, v)
            config.write(open('/etc/manila/manila.conf', 'w'))
            #cfgfile.close()

    os.system('service manila-share restart')
    os.system('rm -f /var/lib/manila/manila.sqlite')





def ubuntu_install(volume, option, ipaddr, hostname, release):
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
    ubuntu_client_install(release)
    ubuntu_manila_install(volume, option, ipaddr)




def centos_ntp_install():
    ##################################################################### 
    # install & config NTP service
    ##################################################################### 
    os.system('yum install chrony -y')
    os.system('cp /etc/chrony.conf /etc/chrony.conf.bak')
    os.system('echo server '+NTP_NAME+' iburst >> /etc/chrony.conf')
    os.system('sudo echo generatecommandkey >> /etc/chrony.conf')
    os.system('sudo echo makestep 10 3 >> /etc/chrony.conf')
    os.system('systemctl enable chronyd.service')
    os.system('systemctl start chronyd.service')


def centos_client_install(release):
    ##################################################################### 
    # install & config Openstack client
    ##################################################################### 
    if release == 'Newton' or release == 'newton':
        os.system('yum install centos-release-openstack-newton -y')
    elif release == 'Ocata' or release == 'ocata':
        os.system('yum install centos-release-openstack-ocata -y')
    os.system('yum upgrade -y')
    os.system('yum install python-openstackclient -y')
    os.system('yum install openstack-selinux -y')
    os.system('yum upgrade -y')


def centos_manila_install(volume, option, ipaddr):
    ##################################################################### 
    # install & config manila share node
    ##################################################################### 
    os.system('yum install openstack-manila-share python2-PyMySQL -y')


    default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'default_share_type':'default_share_type', 'rootwrap_config':'/etc/manila/rootwrap.conf'}

    keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_id':'default', 'user_domain_id': 'default', 'project_name':'service', 'username':'manila', 'password':MANILA_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/manila/manila.conf /etc/manila/manila.conf.bak')
    print "cp /etc/manila/manila.conf done!"
    with open('/etc/manila/manila.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://manila:'+MANILA_DBPASS+'@'+DB_NAME+'/manila')
        for (k,v) in default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/manila/tmp')

        config.write(open('/etc/manila/manila.conf', 'w'))
        #cfgfile.close()

    if option == 'No-Driver' or option == 'no-driver':
        os.system('yum install lvm2 nfs-utils nfs4-acl-tools portmap -y')
        os.system('systemctl enable lvm2-lvmetad.service')
        os.system('systemctl start lvm2-lvmetad.service')

        os.system('pvcreate /dev/'+volume)
        os.system('vgcreate manila-volumes /dev/'+volume)
        ################################################################################
        # TODO: here we insert the filter right after the header "device {". Not sure if
        #       it works. May need to verify. Refer to:
        #       http://docs.openstack.org/newton/zh_CN/install-guide-ubuntu/cinder-storage-install.html
        ################################################################################
        os.system('sed -i \'/devices {/a\ \tfilter = [ "a|'+volume+'|","r|.*|" ]\' /etc/lvm/lvm.conf')

        lvm = {'share_backend_name':'LVM', 'share_driver':'manila.share.drivers.lvm.LVMShareDriver', 'driver_handles_share_servers':'False', 'lvm_share_volume_group':'manila-volumes', 'lvm_share_export_ip':ipaddr}

        config = ConfigParser.ConfigParser()
        with open('/etc/manila/manila.conf', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            config.set('DEFAULT', 'enabled_share_backends', 'lvm')
            config.set('DEFAULT', 'enabled_share_protocols', 'NFS')
            if 'lvm' not in sections:
                config.add_section('lvm')
            for (k,v) in lvm.iteritems():
                config.set('lvm', k, v)
            config.write(open('/etc/manila/manila.conf', 'w'))
            #cfgfile.close()
    else : #Driver support for share server management
        os.system('yum install openstack-neutron openstack-neutron-linuxbridge ebtables -y')

        neutron = {'url':'http://'+NEUTRON_NAME+':9696', 'auth_uri':'http://'+KEYSTONE_NAME+':5000', 'auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS}

        nova = {'auth_uri':'http://'+KEYSTONE_NAME+':5000', 'auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'nova', 'password':NOVA_PASS}

        cinder = {'auth_uri':'http://'+KEYSTONE_NAME+':5000', 'auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'cinder', 'password':CINDER_PASS}

        generic = {'share_backend_name':'GENERIC', 'share_driver':'manila.share.drivers.generic.GenericShareDriver', 'driver_handles_share_servers':'True', 'service_instance_flavor_id':'100', 'service_image_name':'manila-service-image', 'service_instance_user': 'manila', 'service_instance_password': 'manila', 'interface_driver':'manila.network.linux.interface.BridgeInterfaceDriver'}

        config = ConfigParser.ConfigParser()
        with open('/etc/manila/manila.conf', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            config.set('DEFAULT', 'enabled_share_backends', 'generic')
            config.set('DEFAULT', 'enabled_share_protocols', 'NFS')
            if 'neutron' not in sections:
                config.add_section('neutron')
            for (k,v) in neutron.iteritems():
                config.set('neutron', k, v)
            if 'nova' not in sections:
                config.add_section('nova')
            for (k,v) in nova.iteritems():
                config.set('nova', k, v)
            if 'cinder' not in sections:
                config.add_section('cinder')
            for (k,v) in cinder.iteritems():
                config.set('cinder', k, v)
            if 'generic' not in sections:
                config.add_section('generic')
            for (k,v) in generic.iteritems():
                config.set('generic', k, v)
            config.write(open('/etc/manila/manila.conf', 'w'))
            #cfgfile.close()

    os.system('systemctl enable openstack-manila-share.service target.service')
    os.system('systemctl start openstack-manila-share.service target.service')




def centos_install(volume, option, ipaddr, hostname, release):
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
    centos_client_install(release)
    centos_manila_install(volume, option, ipaddr)





def usage():
    print 'share_install.py [options]'
    print 'now only support Ubuntu16.04 and CentOS7'
    print 'Options:'
    print '-r, --release=<Release>       openstack release (Newton or Ocata)'
    print '-v, --volume=<VolumeName>     Physical volume device name for manila'
    print '                              service. e.g. sdb(not /dev/sdb!)'
    print '-o, --option=<DriverMode>     share server management mode (Driver or'
    print '                              No-Driver)'
    print '-m, --hostname=<HostName>     host name'
    print '-i, --ipaddr=<IPAddress>      host IP address'
    print '                              for Self-service network, it should be'
    print '                              the management network IP address'


def main(argv):
    platform = ''
    release = ''
    volume = ''
    option = ''
    ipaddr = ''
    hostname = ''
    try:
        opts, args = getopt.getopt(argv,"hr:v:o:i:m:",["release=","volume=","option=","ipaddr=","hostname="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
           usage()
           sys.exit()
        elif opt in ("-r", "--release"):
           release = arg
        elif opt in ("-v", "--volume"):
           volume = arg
        elif opt in ("-o", "--option"):
           option = arg
        elif opt in ("-i", "--ipaddr"):
           ipaddr = arg
        elif opt in ("-m", "--hostname"):
           hostname = arg

    # check param integrity
    if release == '' or volume == '' or option == '' or ipaddr == '' or hostname == '':
        usage()
        sys.exit()

    if release != 'Newton' and release != 'Ocata':
        usage()
        sys.exit()

    platform = get_distribution()

    if platform == 'Ubuntu':
        ubuntu_install(volume, option, ipaddr, hostname, release)
    elif platform == 'CentOS':
        centos_install(volume, option, ipaddr, hostname, release)
    else :
        print 'Unsupported host platform!'
        usage()


if __name__ == "__main__":
    main(sys.argv[1:])

