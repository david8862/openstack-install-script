#!/usr/bin/python
# Filename: compute_install.py
#
# Copyright (C) 2016  Xiaobin Zhang (david8862@gmail.com)
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


# This is an automation script for openstack compute node installation
# on Ubuntu 16.04 or CentOS 7 host. Now it support Newton and Ocata release

# Python environment should be installed on your Ubuntu 16.04 host.
# If not, please use "apt-get install python" or "yum install python" to do that.


import os, sys, platform, getopt
import ConfigParser

ADMIN_PASS = 'cisco123'
DEMO_PASS = 'cisco123'
RABBIT_PASS = 'cisco123'
NOVA_PASS = 'cisco123'
PLACEMENT_PASS = 'cisco123'
NEUTRON_PASS = 'cisco123'
CONTROLLER = 'controller'
CONTROLLER_IP = '10.74.130.52'


NTP_NAME = 'controller'
DB_NAME = 'controller'
MQ_NAME = 'controller'
MEMCACHE_NAME = 'controller'
KEYSTONE_NAME = 'controller'
GLANCE_NAME = 'controller'
NOVA_NAME = 'controller'
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


def ubuntu_nova_install(ipaddr, release):
    ##################################################################### 
    # install & config nova compute
    ##################################################################### 
    os.system('sudo apt-get install nova-compute -y')

    if release == 'Ocata' or release == 'ocata':
        default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'my_ip':ipaddr, 'use_neutron':'True', 'firewall_driver':'nova.virt.firewall.NoopFirewallDriver', 'vif_plugging_is_fatal':'False', 'vif_plugging_timeout':'0'}
        placement = {'os_region_name':'RegionOne', 'auth_url':'http://'+KEYSTONE_NAME+':35357/v3', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'placement', 'password':PLACEMENT_PASS}

    elif release == 'Newton' or release == 'newton':
        default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'use_neutron':'True', 'firewall_driver':'nova.virt.firewall.NoopFirewallDriver', 'vif_plugging_is_fatal':'False', 'vif_plugging_timeout':'0'}

    nova_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'nova', 'password':NOVA_PASS}

    vnc = {'enabled':'True', 'vncserver_listen':'0.0.0.0', 'vncserver_proxyclient_address':'$my_ip', 'novncproxy_base_url':'http://'+NOVA_NAME+':6080/vnc_auto.html'}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/nova/nova.conf /etc/nova/nova.conf.bak')
    print "cp /etc/nova/nova.conf done!"
    with open('/etc/nova/nova.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in default.iteritems():
            config.set('DEFAULT', k, v)
        config.remove_option("DEFAULT","log-dir")

        if release == 'Ocata' or release == 'ocata':
            if 'api' not in sections:
                config.add_section('api')
            config.set('api', 'auth_strategy', 'keystone')

        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in nova_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'vnc' not in sections:
            config.add_section('vnc')
        for (k,v) in vnc.iteritems():
            config.set('vnc', k, v)
        if 'glance' not in sections:
            config.add_section('glance')
        config.set('glance', 'api_servers', 'http://'+GLANCE_NAME+':9292')
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/nova/tmp')

        if release == 'Ocata' or release == 'ocata':
            if 'placement' not in sections:
                config.add_section('placement')
            for (k,v) in placement.iteritems():
                config.set('placement', k, v)

        config.write(open('/etc/nova/nova.conf', 'w'))
        #cfgfile.close()

    #####################################################################
    # here we don't follow the openstack official guide for the kvm
    # support check. "egrep -c '(vmx|svm)' /proc/cpuinfo" could only
    # reflect capability of CPU for HW accelerate, but not involving
    # BIOS setup. So we choose to check /dev/kvm to make sure the support
    # is fully enabled.
    #####################################################################
    #output = os.popen("egrep -c '(vmx|svm)' /proc/cpuinfo")  
    #out = output.readlines()  
    #acc_value = int(out[0].strip())
    #print "The acc_value is " + str(acc_value)

    #if (acc_value < 1):
    if not(os.path.exists('/dev/kvm')):
        config = ConfigParser.ConfigParser()
        os.system('cp /etc/nova/nova-compute.conf /etc/nova/nova-compute.conf.bak')
        with open('/etc/nova/nova-compute.conf', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            if 'libvirt' not in sections:
                config.add_section('libvirt')
            config.set('libvirt', 'virt_type', 'qemu')
            config.write(open('/etc/nova/nova-compute.conf', 'w'))

    os.system('service nova-compute restart')


def ubuntu_neutron_install(ipaddr, interface, network):
    ##################################################################### 
    # install & config neutron
    ##################################################################### 
    os.system('sudo apt-get install neutron-linuxbridge-agent -y')

    neutron_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.bak')
    print "cp /etc/neutron/neutron.conf done!"
    with open('/etc/neutron/neutron.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.remove_option("database","connection")
        config.set('DEFAULT', 'transport_url', 'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME)
        config.set('DEFAULT', 'auth_strategy','keystone')
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in neutron_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        config.write(open('/etc/neutron/neutron.conf', 'w'))

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini.bak')
    print "cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini done!"
    with open('/etc/neutron/plugins/ml2/linuxbridge_agent.ini', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'linux_bridge' not in sections:
            config.add_section('linux_bridge')
        config.set('linux_bridge', 'physical_interface_mappings', 'provider:'+interface)
        if 'vxlan' not in sections:
            config.add_section('vxlan')
        if network == 'Self-service' or network == 'self-service':
            config.set('vxlan', 'enable_vxlan','True')
            config.set('vxlan', 'local_ip',ipaddr)
            config.set('vxlan', 'l2_population','True')
        else:
            config.set('vxlan', 'enable_vxlan','False')
        if 'securitygroup' not in sections:
            config.add_section('securitygroup')
        config.set('securitygroup', 'enable_security_group','True')
        config.set('securitygroup', 'firewall_driver','neutron.agent.linux.iptables_firewall.IptablesFirewallDriver')
        config.write(open('/etc/neutron/plugins/ml2/linuxbridge_agent.ini', 'w'))


    neutron = {'url':'http://'+NEUTRON_NAME+':9696','auth_url':'http://'+KEYSTONE_NAME+':35357', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS}

    config = ConfigParser.ConfigParser()
    with open('/etc/nova/nova.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'neutron' not in sections:
            config.add_section('neutron')
        for (k,v) in neutron.iteritems():
            config.set('neutron', k, v)
        # config cinder service for nova-compute
        if 'cinder' not in sections:
            config.add_section('cinder')
        config.set('cinder', 'os_region_name','RegionOne')

        config.write(open('/etc/nova/nova.conf', 'w'))

    os.system('service nova-compute restart')
    os.system('service neutron-linuxbridge-agent restart')




def ubuntu_install(ipaddr, hostname, interface, network, release):
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
    ubuntu_nova_install(ipaddr, release)
    ubuntu_neutron_install(ipaddr, interface, network)



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


def centos_nova_install(ipaddr, release):
    ##################################################################### 
    # install & config nova compute
    ##################################################################### 
    os.system('yum install openstack-nova-compute -y')

    if release == 'Ocata' or release == 'ocata':
        default = {'enabled_apis':'osapi_compute,metadata', 'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'my_ip':ipaddr, 'use_neutron':'True', 'firewall_driver':'nova.virt.firewall.NoopFirewallDriver'}
        placement = {'os_region_name':'RegionOne', 'auth_url':'http://'+KEYSTONE_NAME+':35357/v3', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'placement', 'password':PLACEMENT_PASS}

    elif release == 'Newton' or release == 'newton':
        default = {'enabled_apis':'osapi_compute,metadata', 'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'use_neutron':'True', 'firewall_driver':'nova.virt.firewall.NoopFirewallDriver'}

    nova_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'nova', 'password':NOVA_PASS}

    vnc = {'enabled':'True', 'vncserver_listen':'0.0.0.0', 'vncserver_proxyclient_address':'$my_ip', 'novncproxy_base_url':'http://'+NOVA_NAME+':6080/vnc_auto.html'}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/nova/nova.conf /etc/nova/nova.conf.bak')
    print "cp /etc/nova/nova.conf done!"
    with open('/etc/nova/nova.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in default.iteritems():
            config.set('DEFAULT', k, v)
        config.remove_option("DEFAULT","log-dir")

        if release == 'Ocata' or release == 'ocata':
            if 'api' not in sections:
                config.add_section('api')
            config.set('api', 'auth_strategy', 'keystone')

        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in nova_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'vnc' not in sections:
            config.add_section('vnc')
        for (k,v) in vnc.iteritems():
            config.set('vnc', k, v)
        if 'glance' not in sections:
            config.add_section('glance')
        config.set('glance', 'api_servers', 'http://'+GLANCE_NAME+':9292')
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/nova/tmp')

        if release == 'Ocata' or release == 'ocata':
            if 'placement' not in sections:
                config.add_section('placement')
            for (k,v) in placement.iteritems():
                config.set('placement', k, v)

        config.write(open('/etc/nova/nova.conf', 'w'))
        #cfgfile.close()

    #####################################################################
    # here we don't follow the openstack official guide for the kvm
    # support check. "egrep -c '(vmx|svm)' /proc/cpuinfo" could only
    # reflect capability of CPU for HW accelerate, but not involving
    # BIOS setup. So we choose to check /dev/kvm to make sure the support
    # is fully enabled.
    #####################################################################
    #output = os.popen("egrep -c '(vmx|svm)' /proc/cpuinfo")  
    #out = output.readlines()  
    #acc_value = int(out[0].strip())
    #print "The acc_value is " + str(acc_value)

    #if (acc_value < 1):
    if not(os.path.exists('/dev/kvm')):
        config = ConfigParser.ConfigParser()
        with open('/etc/nova/nova.conf', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            if 'libvirt' not in sections:
                config.add_section('libvirt')
            config.set('libvirt', 'virt_type', 'qemu')
            config.write(open('/etc/nova/nova.conf', 'w'))

    os.system('systemctl enable libvirtd.service openstack-nova-compute.service')
    os.system('systemctl start libvirtd.service openstack-nova-compute.service')


def centos_neutron_install(ipaddr, interface, network):
    ##################################################################### 
    # install & config neutron
    ##################################################################### 
    os.system('yum install openstack-neutron-linuxbridge ebtables ipset -y')

    neutron_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.bak')
    print "cp /etc/neutron/neutron.conf done!"
    with open('/etc/neutron/neutron.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.remove_option("database","connection")
        config.set('DEFAULT', 'transport_url', 'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME)
        config.set('DEFAULT', 'auth_strategy','keystone')
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in neutron_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/neutron/tmp')
        config.write(open('/etc/neutron/neutron.conf', 'w'))

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini.bak')
    print "cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini done!"
    with open('/etc/neutron/plugins/ml2/linuxbridge_agent.ini', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'linux_bridge' not in sections:
            config.add_section('linux_bridge')
        config.set('linux_bridge', 'physical_interface_mappings', 'provider:'+interface)
        if 'vxlan' not in sections:
            config.add_section('vxlan')
        if network == 'Self-service' or network == 'self-service':
            config.set('vxlan', 'enable_vxlan','True')
            config.set('vxlan', 'local_ip',ipaddr)
            config.set('vxlan', 'l2_population','True')
        else:
            config.set('vxlan', 'enable_vxlan','False')
        if 'securitygroup' not in sections:
            config.add_section('securitygroup')
        config.set('securitygroup', 'enable_security_group','True')
        config.set('securitygroup', 'firewall_driver','neutron.agent.linux.iptables_firewall.IptablesFirewallDriver')
        config.write(open('/etc/neutron/plugins/ml2/linuxbridge_agent.ini', 'w'))


    neutron = {'url':'http://'+NEUTRON_NAME+':9696','auth_url':'http://'+KEYSTONE_NAME+':35357', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS}

    config = ConfigParser.ConfigParser()
    with open('/etc/nova/nova.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'neutron' not in sections:
            config.add_section('neutron')
        for (k,v) in neutron.iteritems():
            config.set('neutron', k, v)
        # config cinder service for nova-compute
        if 'cinder' not in sections:
            config.add_section('cinder')
        config.set('cinder', 'os_region_name','RegionOne')

        config.write(open('/etc/nova/nova.conf', 'w'))

    os.system('systemctl restart openstack-nova-compute.service')
    os.system('systemctl enable neutron-linuxbridge-agent.service')
    os.system('systemctl start neutron-linuxbridge-agent.service')




def centos_install(ipaddr, hostname, interface, network, release):
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
    centos_nova_install(ipaddr, release)
    centos_neutron_install(ipaddr, interface, network)




def usage():
    print 'compute_install.py [options]'
    print 'now only support Ubuntu16.04 and CentOS7'
    print 'Options:'
    print '-r, --release=<Release>       openstack release (Newton or Ocata)'
    print '-n, --network=<NetworkType>   network type (Provider or Self-service)'
    print '-m, --hostname=<HostName>     host name'
    print '-i, --ipaddr=<IPAddress>      host IP address'
    print '                              for Self-service network, it should be'
    print '                              the management network IP address'
    print '-f, --interface=<DeviceName>  ethernet device name, e.g. eth0'
    print '                              which connect to the public network'


def main(argv):
    platform = ''
    release = ''
    network = ''
    ipaddr = ''
    hostname = ''
    interface = ''
    try:
        opts, args = getopt.getopt(argv,"hr:n:i:m:f:",["release=","network=","ipaddr=","hostname=","interface="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
           usage()
           sys.exit()
        elif opt in ("-r", "--release"):
           release = arg
        elif opt in ("-n", "--network"):
           network = arg
        elif opt in ("-i", "--ipaddr"):
           ipaddr = arg
        elif opt in ("-m", "--hostname"):
           hostname = arg
        elif opt in ("-f", "--interface"):
           interface = arg

    # check param integrity
    if release == '' or network == '' or ipaddr == '' or hostname == '' or interface == '':
        usage()
        sys.exit()

    if release != 'Newton' and release != 'Ocata':
        usage()
        sys.exit()

    platform = get_distribution()

    if platform == 'Ubuntu':
        ubuntu_install(ipaddr, hostname, interface, network, release)
    elif platform == 'CentOS':
        centos_install(ipaddr, hostname, interface, network, release)
    else :
        print 'Unsupported host platform!'
        usage()


if __name__ == "__main__":
    main(sys.argv[1:])

