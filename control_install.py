#!/usr/bin/python
# Filename: control_install.py
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


# This is an automation script for openstack Newton controller node installation
# on Ubuntu 16.04 or CentOS 7 host

# Python environment and MySQLdb package should be installed on your Ubuntu 16.04
# or CentOS 7 host. If not, please use "apt-get install python python-mysqldb"
# or "yum install python python-mysqldb" to do that.


import os, sys, platform, time, getopt
from termios import tcflush, TCIFLUSH
import MySQLdb
import ConfigParser

MYSQL_PASS = 'cisco123'
RABBIT_PASS = 'cisco123'
KEYSTONE_DBPASS = 'cisco123'
GLANCE_DBPASS = 'cisco123'
GLANCE_PASS = 'cisco123'
ADMIN_PASS = 'cisco123'
DEMO_PASS = 'cisco123'
NOVA_DBPASS = 'cisco123'
NOVA_PASS = 'cisco123'
NEUTRON_DBPASS = 'cisco123'
NEUTRON_PASS = 'cisco123'
METADATA_SECRET = 'cisco123'
CINDER_DBPASS = 'cisco123'
CINDER_PASS = 'cisco123'
HEAT_DBPASS = 'cisco123'
HEAT_PASS = 'cisco123'
HEAT_DOMAIN_PASS = 'cisco123'
MANILA_DBPASS = 'cisco123'
MANILA_PASS = 'cisco123'
TROVE_DBPASS = 'cisco123'
TROVE_PASS = 'cisco123'

DB_NAME = 'controller'
MQ_NAME = 'controller'
MEMCACHE_NAME = 'controller'
KEYSTONE_NAME = 'controller'
GLANCE_NAME = 'controller'
NOVA_NAME = 'controller'
NEUTRON_NAME = 'controller'
CINDER_NAME = 'controller'
HEAT_NAME = 'controller'
MANILA_NAME = 'controller'
TROVE_NAME = 'controller'
SWIFT_NAME = 'controller'



def export_admin():
    os.putenv('OS_PROJECT_DOMAIN_NAME', 'default')
    os.putenv('OS_USER_DOMAIN_NAME', 'default')
    os.putenv('OS_PROJECT_NAME', 'admin')
    os.putenv('OS_USERNAME', 'admin')
    os.putenv('OS_PASSWORD', ADMIN_PASS)
    os.putenv('OS_AUTH_URL', 'http://'+KEYSTONE_NAME+':35357/v3')
    os.putenv('OS_IDENTITY_API_VERSION', '3')
    os.putenv('OS_IMAGE_API_VERSION', '2')


def export_demo():
    os.putenv('OS_PROJECT_DOMAIN_NAME', 'default')
    os.putenv('OS_USER_DOMAIN_NAME', 'default')
    os.putenv('OS_PROJECT_NAME', 'demo')
    os.putenv('OS_USERNAME', 'demo')
    os.putenv('OS_PASSWORD', DEMO_PASS)
    os.putenv('OS_AUTH_URL', 'http://'+KEYSTONE_NAME+':5000/v3')
    os.putenv('OS_IDENTITY_API_VERSION', '3')
    os.putenv('OS_IMAGE_API_VERSION', '2')


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


def openstack_config(network):
    export_admin()
    os.system('openstack network create --share --provider-physical-network provider --provider-network-type flat provider')
    if network == 'Self-service' or network == 'self-service':
        os.system('neutron net-update provider --router:external')
        export_demo()
        os.system('openstack network create selfservice')
        os.system('openstack router create router')
        #os.system('neutron router-interface-add router selfservice')
        #os.system('neutron router-gateway-set router provider')

    export_admin()
    os.system('openstack flavor create --id 0 --vcpus 1 --ram 64 --disk 1 m1.nano')
    os.system('openstack security group rule create --proto icmp default')
    os.system('openstack security group rule create --proto tcp --dst-port 22 default')
    export_demo()
    os.system('ssh-keygen -f /root/.ssh/id_rsa -q -N ""')
    os.system('openstack keypair create --public-key /root/.ssh/id_rsa.pub mykey')
    os.system('openstack security group rule create --proto icmp default')
    os.system('openstack security group rule create --proto tcp --dst-port 22 default')




def ubuntu_ntp_install():
    ##################################################################### 
    # install & config NTP service
    ##################################################################### 
    os.system('sudo apt-get install chrony -y')
    os.system('sudo cp /etc/chrony/chrony.conf /etc/chrony/chrony.conf.bak')
    os.system('sudo echo server ntp.ubuntu.com iburst >> /etc/chrony/chrony.conf')
    os.system('sudo echo allow 0/0 >> /etc/chrony/chrony.conf')
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


def ubuntu_db_install(ipaddr, hostname):
    ##################################################################### 
    # install & config MariaDB database
    ##################################################################### 
    global DB_NAME
    DB_NAME = hostname
    os.system('sudo apt-get install mariadb-server python-pymysql -y')

    mysqld = {'bind-address':ipaddr, 'default-storage-engine':'innodb', 'max_connections':'4096', 'collation-server':'utf8_general_ci', 'character-set-server':'utf8'}

    config = ConfigParser.ConfigParser()
    with open('/etc/mysql/mariadb.conf.d/99-openstack.cnf', 'w+') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'mysqld' not in sections:
            config.add_section('mysqld')
        for (k,v) in mysqld.iteritems():
            config.set('mysqld', k, v)

        config.write(open('/etc/mysql/mariadb.conf.d/99-openstack.cnf', 'w'))

    os.system('sed -i "/default-storage-engine/a\innodb_file_per_table" /etc/mysql/mariadb.conf.d/99-openstack.cnf')

    os.system('service mysql restart')
    ##################################################################### 
    # NOTE: For Ubuntu, we should set root passwd and choose other option
    #       as "n" here to make sure the MariaDB could be access
    ##################################################################### 
    time.sleep(2)
    tcflush(sys.stdin, TCIFLUSH)
    print "Will set MariaDB. Please set a root passwd and choose 'n' for all other options"
    raw_input("Press enter to continue: ")
    os.system('mysql_secure_installation')

    ##################################################################### 
    # allow remote access to MariaDB database
    ##################################################################### 
    con = MySQLdb.connect('localhost', 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('GRANT ALL PRIVILEGES ON *.* TO \'root\'@\'%\' IDENTIFIED BY \''+MYSQL_PASS+'\' WITH GRANT OPTION;')
    cursor.execute('FLUSH PRIVILEGES;')
    cursor.close()



def ubuntu_mq_install(hostname):
    ##################################################################### 
    # install & config Rabbitmq
    ##################################################################### 
    global MQ_NAME
    MQ_NAME = hostname
    os.system('sudo apt-get install rabbitmq-server -y')
    os.system('rabbitmqctl add_user openstack ' + RABBIT_PASS)
    os.system('rabbitmqctl set_permissions openstack ".*" ".*" ".*"')


def ubuntu_memcache_install(hostname):
    ##################################################################### 
    # install & config Memcached
    ##################################################################### 
    global MEMCACHE_NAME
    MEMCACHE_NAME = hostname
    os.system('sudo apt-get install memcached python-memcache -y')
    os.system('service memcached restart')


def ubuntu_keystone_install(hostname):
    ##################################################################### 
    # install & config Keystone
    ##################################################################### 
    global KEYSTONE_NAME
    KEYSTONE_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS keystone;')
    cursor.execute('CREATE DATABASE keystone;')
    cursor.execute('GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'localhost\' IDENTIFIED BY \''+KEYSTONE_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'%\' IDENTIFIED BY \''+KEYSTONE_DBPASS+'\';')
    cursor.close()

    os.system('sudo apt-get install keystone -y')
    config = ConfigParser.ConfigParser()
    os.system('cp /etc/keystone/keystone.conf /etc/keystone/keystone.conf.bak')
    print "cp /etc/keystone/keystone.conf done!"
    with open('/etc/keystone/keystone.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://keystone:'+KEYSTONE_DBPASS+'@'+DB_NAME+'/keystone')
        if 'token' not in sections:
            config.add_section('token')
        config.set('token', 'provider', 'fernet')

        config.write(open('/etc/keystone/keystone.conf', 'w'))

    os.system('su -s /bin/sh -c "keystone-manage db_sync" keystone')
    os.system('keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone')
    os.system('keystone-manage credential_setup --keystone-user keystone --keystone-group keystone')
    os.system('keystone-manage bootstrap --bootstrap-password '+ADMIN_PASS+' --bootstrap-admin-url http://'+KEYSTONE_NAME+':35357/v3/ --bootstrap-internal-url http://'+KEYSTONE_NAME+':35357/v3/ --bootstrap-public-url http://'+KEYSTONE_NAME+':5000/v3/ --bootstrap-region-id RegionOne')

    os.system('echo ServerName '+KEYSTONE_NAME+' >> /etc/apache2/apache2.conf')
    os.system('service apache2 restart')
    os.system('rm -f /var/lib/keystone/keystone.db')


    export_admin()
    os.system('openstack project create --domain default --description "Service Project" service')
    os.system('openstack project create --domain default --description "Demo Project" demo')
    os.system('openstack user create --domain default --password '+DEMO_PASS+' demo')
    os.system('openstack role create user')
    os.system('openstack role add --project demo --user demo user')

    ################################################################################################# 
    # TODO: not sure if remove "admin_token_auth" from /etc/keystone/keystone-paste.ini is necessary.
    #       may need to add this part here if this script failed. Refer to:
    #       http://docs.openstack.org/newton/zh_CN/install-guide-ubuntu/keystone-verify.html
    ################################################################################################# 


def ubuntu_glance_install(hostname):
    ##################################################################### 
    # install & config Glance
    ##################################################################### 
    global GLANCE_NAME
    GLANCE_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS glance;')
    cursor.execute('CREATE DATABASE glance;')
    cursor.execute('GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'localhost\' IDENTIFIED BY \''+GLANCE_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'%\' IDENTIFIED BY \''+GLANCE_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+GLANCE_PASS+' glance')
    os.system('openstack role add --project service --user glance admin')
    os.system('openstack service create --name glance --description "OpenStack Image" image')
    os.system('openstack endpoint create --region RegionOne image public http://'+GLANCE_NAME+':9292')
    os.system('openstack endpoint create --region RegionOne image internal http://'+GLANCE_NAME+':9292')
    os.system('openstack endpoint create --region RegionOne image admin http://'+GLANCE_NAME+':9292')

    os.system('sudo apt-get install glance -y')

    glance_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'glance', 'password':GLANCE_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/glance/glance-api.conf /etc/glance/glance-api.conf.bak')
    print "cp /etc/glance/glance-api.conf done!"
    with open('/etc/glance/glance-api.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://glance:'+GLANCE_DBPASS+'@'+DB_NAME+'/glance')
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in glance_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'paste_deploy' not in sections:
            config.add_section('paste_deploy')
        config.set('paste_deploy', 'flavor', 'keystone')

        if 'glance_store' not in sections:
            config.add_section('glance_store')
        config.set('glance_store', 'stores', 'file,http')
        config.set('glance_store', 'default_store', 'file')
        config.set('glance_store', 'filesystem_store_datadir', '/var/lib/glance/images/')
        config.write(open('/etc/glance/glance-api.conf', 'w'))
        #cfgfile.close()

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/glance/glance-registry.conf /etc/glance/glance-registry.conf.bak')
    print "cp /etc/glance/glance-registry.conf done!"
    with open('/etc/glance/glance-registry.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://glance:'+GLANCE_DBPASS+'@'+DB_NAME+'/glance')
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in glance_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'paste_deploy' not in sections:
            config.add_section('paste_deploy')
        config.set('paste_deploy', 'flavor', 'keystone')
        config.write(open('/etc/glance/glance-registry.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "glance-manage db_sync" glance')
    os.system('service glance-registry restart')
    os.system('service glance-api restart')

    # verify Glance
    export_admin()
    os.system('wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img')
    os.system('openstack image create "cirros" --file cirros-0.3.4-x86_64-disk.img --disk-format qcow2 --container-format bare --public')


def ubuntu_nova_install(ipaddr, hostname):
    ##################################################################### 
    # install & config nova
    ##################################################################### 
    global NOVA_NAME
    NOVA_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS nova_api;')
    cursor.execute('DROP DATABASE IF EXISTS nova;')
    cursor.execute('CREATE DATABASE nova_api;')
    cursor.execute('CREATE DATABASE nova;')
    cursor.execute('GRANT ALL PRIVILEGES ON nova_api.* TO \'nova\'@\'localhost\' IDENTIFIED BY \''+NOVA_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON nova_api.* TO \'nova\'@\'%\' IDENTIFIED BY \''+NOVA_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'localhost\' IDENTIFIED BY \''+NOVA_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'%\' IDENTIFIED BY \''+NOVA_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+NOVA_PASS+' nova')
    os.system('openstack role add --project service --user nova admin')
    os.system('openstack service create --name nova --description "OpenStack Compute" compute')
    os.system('openstack endpoint create --region RegionOne compute public http://'+NOVA_NAME+':8774/v2.1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne compute internal http://'+NOVA_NAME+':8774/v2.1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne compute admin http://'+NOVA_NAME+':8774/v2.1/%\(tenant_id\)s')

    os.system('sudo apt-get install nova-api nova-conductor nova-consoleauth nova-novncproxy nova-scheduler -y')


    default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'use_neutron':'True', 'firewall_driver':'nova.virt.firewall.NoopFirewallDriver', 'vif_plugging_is_fatal':'False', 'vif_plugging_timeout':'0'}

    nova_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'nova', 'password':NOVA_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/nova/nova.conf /etc/nova/nova.conf.bak')
    print "cp /etc/nova/nova.conf done!"
    with open('/etc/nova/nova.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'api_database' not in sections:
            config.add_section('api_database')
        config.set('api_database', 'connection', 'mysql+pymysql://nova:'+NOVA_DBPASS+'@'+DB_NAME+'/nova_api')
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://nova:'+NOVA_DBPASS+'@'+DB_NAME+'/nova')
        for (k,v) in default.iteritems():
            config.set('DEFAULT', k, v)
        config.remove_option("DEFAULT","log-dir")
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in nova_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'vnc' not in sections:
            config.add_section('vnc')
        config.set('vnc', 'vncserver_listen', '$my_ip')
        config.set('vnc', 'vncserver_proxyclient_address', '$my_ip')
        if 'glance' not in sections:
            config.add_section('glance')
        config.set('glance', 'api_servers', 'http://'+GLANCE_NAME+':9292')
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/nova/tmp')

        config.write(open('/etc/nova/nova.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "nova-manage api_db sync" nova')
    os.system('su -s /bin/sh -c "nova-manage db sync" nova')
    os.system('service nova-api restart')
    os.system('service nova-consoleauth restart')
    os.system('service nova-scheduler restart')
    os.system('service nova-conductor restart')
    os.system('service nova-novncproxy restart')


def ubuntu_neutron_install(ipaddr, hostname, interface, network):
    ##################################################################### 
    # install & config neutron
    ##################################################################### 
    global NEUTRON_NAME
    NEUTRON_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS neutron;')
    cursor.execute('CREATE DATABASE neutron;')
    cursor.execute('GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'localhost\' IDENTIFIED BY \''+NEUTRON_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'%\' IDENTIFIED BY \''+NEUTRON_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+NEUTRON_PASS+' neutron')
    os.system('openstack role add --project service --user neutron admin')
    os.system('openstack service create --name neutron --description "OpenStack Networking" network')
    os.system('openstack endpoint create --region RegionOne network public http://'+NEUTRON_NAME+':9696')
    os.system('openstack endpoint create --region RegionOne network internal http://'+NEUTRON_NAME+':9696')
    os.system('openstack endpoint create --region RegionOne network admin http://'+NEUTRON_NAME+':9696')

    os.system('sudo apt-get install neutron-server neutron-plugin-ml2 neutron-linuxbridge-agent neutron-dhcp-agent neutron-metadata-agent -y')

    neutron_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS}

    neutron_nova = {'auth_url':'http://'+KEYSTONE_NAME+':35357', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'nova', 'password':NOVA_PASS}


    if network == 'Self-service' or network == 'self-service':
        os.system('sudo apt-get install neutron-l3-agent -y')

        config = ConfigParser.ConfigParser()
        os.system('cp /etc/neutron/l3_agent.ini /etc/neutron/l3_agent.ini.bak')
        print "cp /etc/neutron/l3_agent.ini done!"
        with open('/etc/neutron/l3_agent.ini', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            config.set('DEFAULT', 'interface_driver', 'neutron.agent.linux.interface.BridgeInterfaceDriver')
            config.write(open('/etc/neutron/l3_agent.ini', 'w'))
        neutron_default = {'core_plugin':'ml2', 'service_plugins':'router', 'allow_overlapping_ips':'True', 'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'notify_nova_on_port_status_changes':'True', 'notify_nova_on_port_data_changes':'True'}
    else:
        neutron_default = {'core_plugin':'ml2', 'service_plugins':'', 'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'notify_nova_on_port_status_changes':'True', 'notify_nova_on_port_data_changes':'True'}


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.bak')
    print "cp /etc/neutron/neutron.conf done!"
    with open('/etc/neutron/neutron.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://neutron:'+NEUTRON_DBPASS+'@'+DB_NAME+'/neutron')
        for (k,v) in neutron_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in neutron_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'nova' not in sections:
            config.add_section('nova')
        for (k,v) in neutron_nova.iteritems():
            config.set('nova', k, v)
        config.write(open('/etc/neutron/neutron.conf', 'w'))


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugins/ml2/ml2_conf.ini.bak')
    print "cp /etc/neutron/plugins/ml2/ml2_conf.ini done!"
    with open('/etc/neutron/plugins/ml2/ml2_conf.ini', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'ml2' not in sections:
            config.add_section('ml2')
        if network == 'Self-service' or network == 'self-service':
            config.set('ml2', 'type_drivers', 'flat,vlan,vxlan')
            config.set('ml2', 'tenant_network_types', 'vxlan')
            config.set('ml2', 'mechanism_drivers', 'linuxbridge,l2population')
            if 'ml2_type_vxlan' not in sections:
                config.add_section('ml2_type_vxlan')
            config.set('ml2_type_vxlan', 'vni_ranges', '1:1000')
        else:
            config.set('ml2', 'type_drivers', 'flat,vlan')
            config.set('ml2', 'tenant_network_types', '')
            config.set('ml2', 'mechanism_drivers', 'linuxbridge')
        config.set('ml2', 'extension_drivers', 'port_security')
        if 'ml2_type_flat' not in sections:
            config.add_section('ml2_type_flat')
        config.set('ml2_type_flat', 'flat_networks', 'provider')
        if 'securitygroup' not in sections:
            config.add_section('securitygroup')
        config.set('securitygroup', 'enable_ipset', 'True')
        config.write(open('/etc/neutron/plugins/ml2/ml2_conf.ini', 'w'))


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
            config.set('vxlan', 'enable_vxlan', 'True')
            config.set('vxlan', 'local_ip', ipaddr)
            config.set('vxlan', 'l2_population', 'True')
        else:
            config.set('vxlan', 'enable_vxlan','False')
        if 'securitygroup' not in sections:
            config.add_section('securitygroup')
        config.set('securitygroup', 'enable_security_group','True')
        config.set('securitygroup', 'firewall_driver','neutron.agent.linux.iptables_firewall.IptablesFirewallDriver')
        config.write(open('/etc/neutron/plugins/ml2/linuxbridge_agent.ini', 'w'))


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/dhcp_agent.ini /etc/neutron/dhcp_agent.ini.bak')
    print "cp /etc/neutron/dhcp_agent.ini done!"
    with open('/etc/neutron/dhcp_agent.ini', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('DEFAULT', 'interface_driver', 'neutron.agent.linux.interface.BridgeInterfaceDriver')
        config.set('DEFAULT', 'dhcp_driver', 'neutron.agent.linux.dhcp.Dnsmasq')
        config.set('DEFAULT', 'enable_isolated_metadata', 'True')
        config.write(open('/etc/neutron/dhcp_agent.ini', 'w'))


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/metadata_agent.ini /etc/neutron/metadata_agent.ini.bak')
    print "cp /etc/neutron/metadata_agent.ini done!"
    with open('/etc/neutron/metadata_agent.ini', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('DEFAULT', 'nova_metadata_ip', NOVA_NAME)
        config.set('DEFAULT', 'metadata_proxy_shared_secret', METADATA_SECRET)
        config.write(open('/etc/neutron/metadata_agent.ini', 'w'))


    neutron = {'url':'http://'+NEUTRON_NAME+':9696','auth_url':'http://'+KEYSTONE_NAME+':35357', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS, 'service_metadata_proxy':'True', 'metadata_proxy_shared_secret':METADATA_SECRET}

    if os.path.exists('/etc/nova/nova.conf'):
        config = ConfigParser.ConfigParser()
        with open('/etc/nova/nova.conf', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            if 'neutron' not in sections:
                config.add_section('neutron')
            for (k,v) in neutron.iteritems():
                config.set('neutron', k, v)
            config.write(open('/etc/nova/nova.conf', 'w'))
    else:
        print "Seems nova service not install on this host"
        print "Please edit /etc/nova/nova.conf on your nova service host for neutron"
        time.sleep(2)
        tcflush(sys.stdin, TCIFLUSH)
        raw_input("Press enter to continue: ")


    os.system('su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron')
    if os.path.exists('/etc/nova/nova.conf'):
        os.system('service nova-api restart')
    os.system('service neutron-server restart')
    os.system('service neutron-linuxbridge-agent restart')
    os.system('service neutron-dhcp-agent restart')
    os.system('service neutron-metadata-agent restart')
    if network == 'Self-service' or network == 'self-service':
        os.system('service neutron-l3-agent restart')


def ubuntu_redirect_page(hostname):
    index_html = open('/var/www/html/index.html', 'w+')
    index_html.write('<HTML>\n')
    index_html.write('<HEAD>\n')
    index_html.write('<meta http-equiv="refresh" content="0; url=http://'+hostname+'/horizon">\n')
    index_html.write('</HEAD>\n')
    index_html.write('<BODY> </BODY>\n')
    index_html.write('</HTML>\n')
    index_html.close()


def ubuntu_dashboard_install(hostname, network):
    ##################################################################### 
    # install & config dashboard
    ##################################################################### 
    os.system('sudo apt-get install openstack-dashboard -y')
    os.system('sed -i \'/OPENSTACK_HOST =/c OPENSTACK_HOST = "'+hostname+'"\' /etc/openstack-dashboard/local_settings.py')
    os.system('sed -i \'/OPENSTACK_KEYSTONE_URL =/c OPENSTACK_KEYSTONE_URL = "http://%s:5000/v3" % OPENSTACK_HOST\' /etc/openstack-dashboard/local_settings.py')

    os.system('sed -i "/CACHES = {/i\SESSION_ENGINE = \'django.contrib.sessions.backends.cache\'" /etc/openstack-dashboard/local_settings.py')
#    os.system('sed -i "/11211/c \'LOCATION\': \''+hostname+':11211\'," /etc/openstack-dashboard/local_settings.py')

    os.system('sed -i \'/OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT/c OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True\' /etc/openstack-dashboard/local_settings.py')
    os.system('sed -i \'/OPENSTACK_KEYSTONE_DEFAULT_DOMAIN/c OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = "default"\' /etc/openstack-dashboard/local_settings.py')
    os.system('sed -i \'/OPENSTACK_KEYSTONE_DEFAULT_ROLE/c OPENSTACK_KEYSTONE_DEFAULT_ROLE = "user"\' /etc/openstack-dashboard/local_settings.py')

    os.system('sed -i \'/OPENSTACK_API_VERSIONS/c OPENSTACK_API_VERSIONS = {\' /etc/openstack-dashboard/local_settings.py')
    os.system('sed -i \'/OPENSTACK_API_VERSIONS/a\}\' /etc/openstack-dashboard/local_settings.py')
    os.system('sed -i \'/OPENSTACK_API_VERSIONS/a\    "volume": 2,\' /etc/openstack-dashboard/local_settings.py')
    os.system('sed -i \'/OPENSTACK_API_VERSIONS/a\    "image": 2,\' /etc/openstack-dashboard/local_settings.py')
    os.system('sed -i \'/OPENSTACK_API_VERSIONS/a\    "identity": 3,\' /etc/openstack-dashboard/local_settings.py')

    if network == 'Provider' or network == 'provider':
        ################################################################################################# 
        # TODO: here we missed "'enable_quotas': False," since there's a same line in local_settings.py.
        #       may need a better way to do the search & replace.
        ################################################################################################# 
        os.system('sed -i "/enable_router/c      \'enable_router\': False," /etc/openstack-dashboard/local_settings.py')
        os.system('sed -i "/enable_ipv6/c      \'enable_ipv6\': False," /etc/openstack-dashboard/local_settings.py')
        os.system('sed -i "/enable_distributed_router/c      \'enable_distributed_router\': False," /etc/openstack-dashboard/local_settings.py')
        os.system('sed -i "/enable_ha_router/c      \'enable_ha_router\': False," /etc/openstack-dashboard/local_settings.py')
        os.system('sed -i "/enable_lb/c      \'enable_lb\': False," /etc/openstack-dashboard/local_settings.py')
        os.system('sed -i "/enable_firewall/c      \'enable_firewall\': False," /etc/openstack-dashboard/local_settings.py')
        os.system('sed -i "/enable_vpn/c      \'enable_vpn\': False," /etc/openstack-dashboard/local_settings.py')
        os.system('sed -i "/enable_fip_topology_check/c      \'enable_fip_topology_check\': False," /etc/openstack-dashboard/local_settings.py')


    os.system('sed -i \'/TIME_ZONE/c TIME_ZONE = "Asia/Shanghai"\' /etc/openstack-dashboard/local_settings.py')
    os.system('sed -i "/DEFAULT_THEME/c DEFAULT_THEME = \'default\'" /etc/openstack-dashboard/local_settings.py')

    os.system('sed -i "/Timeout 300/c Timeout 600" /etc/apache2/apache2.conf')
    os.system('sed -i "/WSGIProcessGroup horizon/a\WSGIApplicationGroup %{GLOBAL}" /etc/apache2/conf-available/openstack-dashboard.conf')
    ubuntu_redirect_page(hostname)

    os.system('service apache2 reload')




def ubuntu_cinder_install(ipaddr, hostname):
    ##################################################################### 
    # install & config Cinder
    ##################################################################### 
    global CINDER_NAME
    CINDER_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS cinder;')
    cursor.execute('CREATE DATABASE cinder;')
    cursor.execute('GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'localhost\' IDENTIFIED BY \''+CINDER_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'%\' IDENTIFIED BY \''+CINDER_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+CINDER_PASS+' cinder')
    os.system('openstack role add --project service --user cinder admin')
    os.system('openstack service create --name cinder --description "OpenStack Block Storage" volume')
    os.system('openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2')
    os.system('openstack endpoint create --region RegionOne volume public http://'+CINDER_NAME+':8776/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volume internal http://'+CINDER_NAME+':8776/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volume admin http://'+CINDER_NAME+':8776/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volumev2 public http://'+CINDER_NAME+':8776/v2/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volumev2 internal http://'+CINDER_NAME+':8776/v2/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volumev2 admin http://'+CINDER_NAME+':8776/v2/%\(tenant_id\)s')

    os.system('sudo apt-get install cinder-api cinder-scheduler -y')

    cinder_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'cinder', 'password':CINDER_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/cinder/cinder.conf /etc/cinder/cinder.conf.bak')
    print "cp /etc/cinder/cinder.conf done!"
    with open('/etc/cinder/cinder.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://cinder:'+CINDER_DBPASS+'@'+DB_NAME+'/cinder')
        config.set('DEFAULT', 'transport_url', 'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME)
        config.set('DEFAULT', 'auth_strategy', 'keystone')
        config.set('DEFAULT', 'my_ip', ipaddr)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in cinder_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/cinder/tmp')
        config.write(open('/etc/cinder/cinder.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "cinder-manage db sync" cinder')
    os.system('service nova-api restart')
    os.system('service cinder-scheduler restart')
    os.system('service cinder-api restart')

def ubuntu_heat_install(hostname):
    ##################################################################### 
    # install & config Cinder
    ##################################################################### 
    global HEAT_NAME
    HEAT_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS heat;')
    cursor.execute('CREATE DATABASE heat;')
    cursor.execute('GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'localhost\' IDENTIFIED BY \''+HEAT_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'%\' IDENTIFIED BY \''+HEAT_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+HEAT_PASS+' heat')
    os.system('openstack role add --project service --user heat admin')
    os.system('openstack service create --name heat --description "Orchestration" orchestration')
    os.system('openstack service create --name head-cfn --description "Orchestration" cloudformation')
    os.system('openstack endpoint create --region RegionOne orchestration public http://'+HEAT_NAME+':8004/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne orchestration internal http://'+HEAT_NAME+':8004/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne orchestration admin http://'+HEAT_NAME+':8004/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne cloudformation public http://'+HEAT_NAME+':8000/v1')
    os.system('openstack endpoint create --region RegionOne cloudformation internal http://'+HEAT_NAME+':8000/v1')
    os.system('openstack endpoint create --region RegionOne cloudformation admin http://'+HEAT_NAME+':8000/v1')

    os.system('openstack domain create --description "Stack projects and users" heat')
    os.system('openstack user create --domain heat --password '+HEAT_DOMAIN_PASS+' heat_domain_admin')
    os.system('openstack role add --domain heat --user-domain heat --user heat_domain_admin admin')
    os.system('openstack role create heat_stack_owner')
    os.system('openstack role add --project demo --user demo heat_stack_owner')
    os.system('openstack role create heat_stack_user')

    os.system('sudo apt-get install heat-api heat-api-cfn heat-engine -y')

    heat_default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'heat_metadata_server_url':'http://'+HEAT_NAME+':8000', 'heat_waitcondition_server_url':'http://'+HEAT_NAME+':8000/v1/waitcondition', 'stack_domain_admin':'heat_domain_admin', 'stack_domain_admin_password':HEAT_DOMAIN_PASS, 'stack_user_domain_name':'heat'}

    heat_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'heat', 'password':HEAT_PASS}

    heat_trustee = {'auth_type':'password', 'auth_url':'http://'+KEYSTONE_NAME+':35357', 'username':'heat', 'password':HEAT_PASS, 'user_domain_name': 'default'}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/heat/heat.conf /etc/heat/heat.conf.bak')
    print "cp /etc/heat/heat.conf done!"
    with open('/etc/heat/heat.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://heat:'+HEAT_DBPASS+'@'+DB_NAME+'/heat')
        for (k,v) in heat_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in heat_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'trustee' not in sections:
            config.add_section('trustee')
        for (k,v) in heat_trustee.iteritems():
            config.set('trustee', k, v)
        if 'clients_keystone' not in sections:
            config.add_section('clients_keystone')
        config.set('clients_keystone', 'auth_uri', 'http://'+KEYSTONE_NAME+':35357')
        if 'ec2authtoken' not in sections:
            config.add_section('ec2authtoken')
        config.set('ec2authtoken', 'auth_uri', 'http://'+KEYSTONE_NAME+':5000')
        config.write(open('/etc/heat/heat.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "heat-manage db_sync" heat')
    os.system('service heat-api restart')
    os.system('service heat-api-cfn restart')
    os.system('service heat-engine restart')


def ubuntu_manila_install(ipaddr, hostname):
    ##################################################################### 
    # install & config Manila
    ##################################################################### 
    global MANILA_NAME
    MANILA_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS manila;')
    cursor.execute('CREATE DATABASE manila;')
    cursor.execute('GRANT ALL PRIVILEGES ON manila.* TO \'manila\'@\'localhost\' IDENTIFIED BY \''+MANILA_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON manila.* TO \'manila\'@\'%\' IDENTIFIED BY \''+MANILA_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+MANILA_PASS+' manila')
    os.system('openstack role add --project service --user manila admin')
    os.system('openstack service create --name manila --description "OpenStack Shared File Systems" share')
    os.system('openstack service create --name manilav2 --description "OpenStack Shared File Systems" sharev2')
    os.system('openstack endpoint create --region RegionOne share public http://'+MANILA_NAME+':8786/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne share internal http://'+MANILA_NAME+':8786/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne share admin http://'+MANILA_NAME+':8786/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne sharev2 public http://'+MANILA_NAME+':8786/v2/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne sharev2 internal http://'+MANILA_NAME+':8786/v2/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne sharev2 admin http://'+MANILA_NAME+':8786/v2/%\(tenant_id\)s')

    ################################################################################################# 
    # TODO: currently manila ui plugin python-manila-ui have problem on Ubuntu 16.04 newton release.
    #       may need to wait for a suitable SW package.
    ################################################################################################# 
    #os.system('sudo apt-get install manila-api manila-scheduler python-manilaclient python-manila-ui -y')
    os.system('sudo apt-get install manila-api manila-scheduler python-manilaclient -y')

    manila_default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'default_share_type':'default_share_type', 'share_name_template':'share-%s', 'rootwrap_config':'/etc/manila/rootwrap.conf', 'api_paste_config':'/etc/manila/api-paste.ini'}

    manila_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_id':'default', 'user_domain_id': 'default', 'project_name':'service', 'username':'manila', 'password':MANILA_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/manila/manila.conf /etc/manila/manila.conf.bak')
    print "cp /etc/manila/manila.conf done!"
    with open('/etc/manila/manila.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://manila:'+MANILA_DBPASS+'@'+DB_NAME+'/manila')
        for (k,v) in manila_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in manila_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lock/manila')
        config.write(open('/etc/manila/manila.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "manila-manage db sync" manila')
    os.system('service manila-scheduler restart')
    os.system('service manila-api restart')
    #os.system('service apache2 restart')
    #os.system('service memcached restart')
    os.system('rm -rf /var/lib/manila/manila.sqlite')


def ubuntu_trove_install(hostname):
    ##################################################################### 
    # install & config Trove
    ##################################################################### 
    global TROVE_NAME
    TROVE_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS trove;')
    cursor.execute('CREATE DATABASE trove;')
    cursor.execute('GRANT ALL PRIVILEGES ON trove.* TO \'trove\'@\'localhost\' IDENTIFIED BY \''+TROVE_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON trove.* TO \'trove\'@\'%\' IDENTIFIED BY \''+TROVE_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+TROVE_PASS+' trove')
    os.system('openstack role add --project service --user trove admin')
    os.system('openstack service create --name trove --description "OpenStack Database" database')
    os.system('openstack endpoint create --region RegionOne database public http://'+TROVE_NAME+':8779/v1.0/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne database internal http://'+TROVE_NAME+':8779/v1.0/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne database admin http://'+TROVE_NAME+':8779/v1.0/%\(tenant_id\)s')

    os.system('sudo apt-get install python-trove python-troveclient python-glanceclient trove-common trove-api trove-taskmanager trove-conductor -y')


    ##################################################################### 
    # check and get /etc/trove/api-paste.ini
    ##################################################################### 
    if not os.path.exists('/etc/trove/api-paste.ini'):
        os.system('sudo curl -o /etc/trove/api-paste.ini http://git.openstack.org/cgit/openstack/trove/plain/etc/trove/api-paste.ini?h=stable/newton')
    ##################################################################### 
    # check and get /etc/trove/trove-guestagent.conf
    ##################################################################### 
    if not os.path.exists('/etc/trove/trove-guestagent.conf'):
        os.system('sudo curl -o /etc/trove/trove-guestagent.conf http://git.openstack.org/cgit/openstack/trove/plain/etc/trove/trove-guestagent.conf.sample?h=stable/newton')


    trove_all_default = {'log_dir':'/var/log/trove', 'trove_auth_url':'http://'+KEYSTONE_NAME+':5000/v2.0', 'nova_compute_url':'http://'+NOVA_NAME+':8774/v2', 'cinder_url':'http://'+CINDER_NAME+':8776/v1', 'swift_url':'http://'+SWIFT_NAME+':8080/v1/AUTH_', 'notifier_queue_hostname':MQ_NAME, 'rpc_backend':'rabbit'}

    trove_all_oslo_messaging_rabbit = {'rabbit_host':MQ_NAME, 'rabbit_userid':'openstack', 'rabbit_password':RABBIT_PASS}

    trove_default = {'auth_strategy':'keystone', 'add_addresses':'True', 'network_label_regex':'^NETWORK_LABEL$', 'api_paste_config':'/etc/trove/api-paste.ini'}

    trove_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'trove', 'password':TROVE_PASS}

    trove_taskmanager_default = {'nova_proxy_admin_user':'admin', 'nova_proxy_admin_pass':ADMIN_PASS, 'nova_proxy_admin_tenant_name':'service', 'taskmanager_manager':'trove.taskmanager.manager.Manager', 'use_nova_server_config_drive':'True', 'network_driver':'trove.network.neutron.NeutronDriver', 'network_label_regex':'.*'}

    trove_guestagent_default = {'rabbit_host':MQ_NAME, 'rabbit_password':RABBIT_PASS, 'nova_proxy_admin_user':'admin', 'nova_proxy_admin_pass':ADMIN_PASS, 'nova_proxy_admin_tenant_name':'service','trove_auth_url':'http://'+KEYSTONE_NAME+':35357/v2.0'}


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/trove/trove.conf /etc/trove/trove.conf.bak')
    print "cp /etc/trove/trove.conf done!"
    with open('/etc/trove/trove.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in trove_all_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://trove:'+TROVE_DBPASS+'@'+DB_NAME+'/trove')
        if 'oslo_messaging_rabbit' not in sections:
            config.add_section('oslo_messaging_rabbit')
        for (k,v) in trove_all_oslo_messaging_rabbit.iteritems():
            config.set('oslo_messaging_rabbit', k, v)
        for (k,v) in trove_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in trove_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        config.write(open('/etc/trove/trove.conf', 'w'))
        #cfgfile.close()

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/trove/trove-taskmanager.conf /etc/trove/trove-taskmanager.conf.bak')
    print "cp /etc/trove/trove-taskmanager.conf done!"
    with open('/etc/trove/trove-taskmanager.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in trove_all_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://trove:'+TROVE_DBPASS+'@'+DB_NAME+'/trove')
        if 'oslo_messaging_rabbit' not in sections:
            config.add_section('oslo_messaging_rabbit')
        for (k,v) in trove_all_oslo_messaging_rabbit.iteritems():
            config.set('oslo_messaging_rabbit', k, v)
        for (k,v) in trove_taskmanager_default.iteritems():
            config.set('DEFAULT', k, v)
        config.write(open('/etc/trove/trove-taskmanager.conf', 'w'))
        #cfgfile.close()

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/trove/trove-conductor.conf /etc/trove/trove-conductor.conf.bak')
    print "cp /etc/trove/trove-conductor.conf done!"
    with open('/etc/trove/trove-conductor.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in trove_all_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://trove:'+TROVE_DBPASS+'@'+DB_NAME+'/trove')
        if 'oslo_messaging_rabbit' not in sections:
            config.add_section('oslo_messaging_rabbit')
        for (k,v) in trove_all_oslo_messaging_rabbit.iteritems():
            config.set('oslo_messaging_rabbit', k, v)
        config.write(open('/etc/trove/trove-conductor.conf', 'w'))
        #cfgfile.close()

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/trove/trove-guestagent.conf /etc/trove/trove-guestagent.conf.bak')
    print "cp /etc/trove/trove-guestagent.conf done!"
    with open('/etc/trove/trove-guestagent.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in trove_guestagent_default.iteritems():
            config.set('DEFAULT', k, v)
        config.write(open('/etc/trove/trove-guestagent.conf', 'w'))
        #cfgfile.close()


    os.system('su -s /bin/sh -c "trove-manage db_sync" trove')
    os.system('service trove-api restart')
    os.system('service trove-taskmanager restart')
    os.system('service trove-conductor restart')
    ##################################################################### 
    # install Trove dashboard, use version 7.0.1 for newton
    ##################################################################### 
    os.system('sudo apt-get install python-pip -y')
    #os.system('sudo apt-get install python-trove-dashboard -y')
    os.system('pip install trove-dashboard==7.0.1')
    os.system('cp -rf /usr/local/lib/python2.7/dist-packages/trove_dashboard/enabled/* /usr/share/openstack-dashboard/openstack_dashboard/local/enabled/')
    os.system('service apache2 restart')




def ubuntu_install(ipaddr, hostname, interface, network):
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
    os.system('sed -i \'/127.0.0.1/c 127.0.0.1  localhost '+hostname+' \' /etc/hosts')
    os.system('sed -i \'/127.0.1.1/d\' /etc/hosts')
    os.system('echo '+ipaddr+'  '+hostname+' >> /etc/hosts')

    ubuntu_ntp_install()
    ubuntu_client_install()
    ubuntu_db_install(ipaddr, hostname)
    ubuntu_mq_install(hostname)
    ubuntu_memcache_install(hostname)
    ubuntu_keystone_install(hostname)
    create_env_script()
    ubuntu_glance_install(hostname)
    ubuntu_nova_install(ipaddr, hostname)
    ubuntu_neutron_install(ipaddr, hostname, interface, network)
    ubuntu_dashboard_install(hostname, network)
    ubuntu_cinder_install(ipaddr, hostname)
    ubuntu_heat_install(hostname)
    ubuntu_manila_install(ipaddr, hostname)
    ubuntu_trove_install(hostname)
    openstack_config(network)






def centos_ntp_install():
    ##################################################################### 
    # install & config NTP service
    ##################################################################### 
    os.system('yum install chrony -y')
    os.system('cp /etc/chrony.conf /etc/chrony.conf.bak')
    os.system('echo server ntp.ubuntu.com iburst >> /etc/chrony.conf')
    os.system('echo allow 0/0 >> /etc/chrony.conf')
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


def centos_db_install(ipaddr, hostname):
    ##################################################################### 
    # install & config MariaDB database
    ##################################################################### 
    global DB_NAME
    DB_NAME = hostname
    os.system('yum install mariadb mariadb-server python2-PyMySQL -y')

    mysqld = {'bind-address':ipaddr, 'default-storage-engine':'innodb', 'max_connections':'4096', 'collation-server':'utf8_general_ci', 'character-set-server':'utf8'}

    config = ConfigParser.ConfigParser()
    with open('/etc/my.cnf.d/openstack.cnf', 'w+') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'mysqld' not in sections:
            config.add_section('mysqld')
        for (k,v) in mysqld.iteritems():
            config.set('mysqld', k, v)

        config.write(open('/etc/my.cnf.d/openstack.cnf', 'w'))

    os.system('sed -i "/default-storage-engine/a\innodb_file_per_table" /etc/my.cnf.d/openstack.cnf')

    os.system('systemctl enable mariadb.service')
    os.system('systemctl start mariadb.service')
    ##################################################################### 
    # NOTE: For CentOS, we should set root passwd and choose other option
    #       as "Y" here to make sure the MariaDB could be access
    ##################################################################### 
    time.sleep(2)
    tcflush(sys.stdin, TCIFLUSH)
    print "Will set MariaDB. Please set a root passwd and choose 'Y' for all other options"
    raw_input("Press enter to continue: ")
    os.system('mysql_secure_installation')

    ##################################################################### 
    # allow remote access to MariaDB database
    ##################################################################### 
    con = MySQLdb.connect('localhost', 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('GRANT ALL PRIVILEGES ON *.* TO \'root\'@\'%\' IDENTIFIED BY \''+MYSQL_PASS+'\' WITH GRANT OPTION;')
    cursor.execute('FLUSH PRIVILEGES;')
    cursor.close()


def centos_mq_install(hostname):
    ##################################################################### 
    # install & config Rabbitmq
    ##################################################################### 
    global MQ_NAME
    MQ_NAME = hostname
    os.system('yum install rabbitmq-server -y')
    os.system('systemctl enable rabbitmq-server.service')
    os.system('systemctl start rabbitmq-server.service')
    os.system('rabbitmqctl add_user openstack ' + RABBIT_PASS)
    os.system('rabbitmqctl set_permissions openstack ".*" ".*" ".*"')


def centos_memcache_install(hostname):
    ##################################################################### 
    # install & config Memcached
    ##################################################################### 
    global MEMCACHE_NAME
    MEMCACHE_NAME = hostname
    os.system('yum install memcached python-memcached -y')
    os.system('systemctl enable memcached.service')
    os.system('systemctl start memcached.service')


def centos_keystone_install(hostname):
    ##################################################################### 
    # install & config Keystone
    ##################################################################### 
    global KEYSTONE_NAME
    KEYSTONE_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS keystone;')
    cursor.execute('CREATE DATABASE keystone;')
    cursor.execute('GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'localhost\' IDENTIFIED BY \''+KEYSTONE_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'%\' IDENTIFIED BY \''+KEYSTONE_DBPASS+'\';')
    cursor.close()

    os.system('yum install openstack-keystone httpd mod_wsgi -y')
    config = ConfigParser.ConfigParser()
    os.system('cp /etc/keystone/keystone.conf /etc/keystone/keystone.conf.bak')
    print "cp /etc/keystone/keystone.conf done!"
    with open('/etc/keystone/keystone.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('database', 'connection', 'mysql+pymysql://keystone:'+KEYSTONE_DBPASS+'@'+DB_NAME+'/keystone')
        config.set('token', 'provider', 'fernet')
        config.write(open('/etc/keystone/keystone.conf', 'w'))

    os.system('su -s /bin/sh -c "keystone-manage db_sync" keystone')
    os.system('keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone')
    os.system('keystone-manage credential_setup --keystone-user keystone --keystone-group keystone')
    os.system('keystone-manage bootstrap --bootstrap-password '+ADMIN_PASS+' --bootstrap-admin-url http://'+KEYSTONE_NAME+':35357/v3/ --bootstrap-internal-url http://'+KEYSTONE_NAME+':35357/v3/ --bootstrap-public-url http://'+KEYSTONE_NAME+':5000/v3/ --bootstrap-region-id RegionOne')

    os.system('echo ServerName '+KEYSTONE_NAME+' >> /etc/httpd/conf/httpd.conf')
    os.system('ln -s /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/')
    os.system('systemctl enable httpd.service')
    os.system('systemctl start httpd.service')


    export_admin()
    os.system('openstack project create --domain default --description "Service Project" service')
    os.system('openstack project create --domain default --description "Demo Project" demo')
    os.system('openstack user create --domain default --password '+DEMO_PASS+' demo')
    os.system('openstack role create user')
    os.system('openstack role add --project demo --user demo user')

    ################################################################################################# 
    # TODO: not sure if remove "admin_token_auth" from /etc/keystone/keystone-paste.ini is necessary.
    #       may need to add this part here if this script failed. Refer to:
    #       http://docs.openstack.org/newton/zh_CN/install-guide-ubuntu/keystone-verify.html
    ################################################################################################# 



def centos_glance_install(hostname):
    ##################################################################### 
    # install & config Glance
    ##################################################################### 
    global GLANCE_NAME
    GLANCE_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS glance;')
    cursor.execute('CREATE DATABASE glance;')
    cursor.execute('GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'localhost\' IDENTIFIED BY \''+GLANCE_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'%\' IDENTIFIED BY \''+GLANCE_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+GLANCE_PASS+' glance')
    os.system('openstack role add --project service --user glance admin')
    os.system('openstack service create --name glance --description "OpenStack Image" image')
    os.system('openstack endpoint create --region RegionOne image public http://'+GLANCE_NAME+':9292')
    os.system('openstack endpoint create --region RegionOne image internal http://'+GLANCE_NAME+':9292')
    os.system('openstack endpoint create --region RegionOne image admin http://'+GLANCE_NAME+':9292')

    os.system('yum install openstack-glance -y')

    glance_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'glance', 'password':GLANCE_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/glance/glance-api.conf /etc/glance/glance-api.conf.bak')
    print "cp /etc/glance/glance-api.conf done!"
    with open('/etc/glance/glance-api.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('database', 'connection', 'mysql+pymysql://glance:'+GLANCE_DBPASS+'@'+DB_NAME+'/glance')
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in glance_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'paste_deploy' not in sections:
            config.add_section('paste_deploy')
        config.set('paste_deploy', 'flavor', 'keystone')

        if 'glance_store' not in sections:
            config.add_section('glance_store')
        config.set('glance_store', 'stores', 'file,http')
        config.set('glance_store', 'default_store', 'file')
        config.set('glance_store', 'filesystem_store_datadir', '/var/lib/glance/images/')
        config.write(open('/etc/glance/glance-api.conf', 'w'))
        #cfgfile.close()

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/glance/glance-registry.conf /etc/glance/glance-registry.conf.bak')
    print "cp /etc/glance/glance-registry.conf done!"
    with open('/etc/glance/glance-registry.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('database', 'connection', 'mysql+pymysql://glance:'+GLANCE_DBPASS+'@'+DB_NAME+'/glance')
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in glance_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'paste_deploy' not in sections:
            config.add_section('paste_deploy')
        config.set('paste_deploy', 'flavor', 'keystone')
        config.write(open('/etc/glance/glance-registry.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "glance-manage db_sync" glance')
    os.system('systemctl enable openstack-glance-api.service openstack-glance-registry.service')
    os.system('systemctl start openstack-glance-api.service openstack-glance-registry.service')

    # verify Glance
    export_admin()
    os.system('wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img')
    os.system('openstack image create "cirros" --file cirros-0.3.4-x86_64-disk.img --disk-format qcow2 --container-format bare --public')


def centos_nova_install(ipaddr, hostname):
    ##################################################################### 
    # install & config nova
    ##################################################################### 
    global NOVA_NAME
    NOVA_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS nova_api;')
    cursor.execute('DROP DATABASE IF EXISTS nova;')
    cursor.execute('CREATE DATABASE nova_api;')
    cursor.execute('CREATE DATABASE nova;')
    cursor.execute('GRANT ALL PRIVILEGES ON nova_api.* TO \'nova\'@\'localhost\' IDENTIFIED BY \''+NOVA_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON nova_api.* TO \'nova\'@\'%\' IDENTIFIED BY \''+NOVA_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'localhost\' IDENTIFIED BY \''+NOVA_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'%\' IDENTIFIED BY \''+NOVA_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+NOVA_PASS+' nova')
    os.system('openstack role add --project service --user nova admin')
    os.system('openstack service create --name nova --description "OpenStack Compute" compute')
    os.system('openstack endpoint create --region RegionOne compute public http://'+NOVA_NAME+':8774/v2.1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne compute internal http://'+NOVA_NAME+':8774/v2.1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne compute admin http://'+NOVA_NAME+':8774/v2.1/%\(tenant_id\)s')

    os.system('yum install openstack-nova-api openstack-nova-conductor openstack-nova-console openstack-nova-novncproxy openstack-nova-scheduler -y')


    default = {'enabled_apis':'osapi_compute,metadata', 'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'use_neutron':'True', 'firewall_driver':'nova.virt.firewall.NoopFirewallDriver', 'vif_plugging_is_fatal':'False', 'vif_plugging_timeout':'0'}

    nova_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'nova', 'password':NOVA_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/nova/nova.conf /etc/nova/nova.conf.bak')
    print "cp /etc/nova/nova.conf done!"
    with open('/etc/nova/nova.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('api_database', 'connection', 'mysql+pymysql://nova:'+NOVA_DBPASS+'@'+DB_NAME+'/nova_api')
        config.set('database', 'connection', 'mysql+pymysql://nova:'+NOVA_DBPASS+'@'+DB_NAME+'/nova')
        for (k,v) in default.iteritems():
            config.set('DEFAULT', k, v)
        config.remove_option("DEFAULT","log-dir")
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in nova_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'vnc' not in sections:
            config.add_section('vnc')
        config.set('vnc', 'vncserver_listen', '$my_ip')
        config.set('vnc', 'vncserver_proxyclient_address', '$my_ip')
        if 'glance' not in sections:
            config.add_section('glance')
        config.set('glance', 'api_servers', 'http://'+GLANCE_NAME+':9292')
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/nova/tmp')

        config.write(open('/etc/nova/nova.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "nova-manage api_db sync" nova')
    os.system('su -s /bin/sh -c "nova-manage db sync" nova')
    os.system('systemctl enable openstack-nova-api.service openstack-nova-consoleauth.service openstack-nova-scheduler.service openstack-nova-conductor.service openstack-nova-novncproxy.service')
    os.system('systemctl start openstack-nova-api.service openstack-nova-consoleauth.service openstack-nova-scheduler.service openstack-nova-conductor.service openstack-nova-novncproxy.service')


def centos_neutron_install(ipaddr, hostname, interface, network):
    ##################################################################### 
    # install & config neutron
    ##################################################################### 
    global NEUTRON_NAME
    NEUTRON_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS neutron;')
    cursor.execute('CREATE DATABASE neutron;')
    cursor.execute('GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'localhost\' IDENTIFIED BY \''+NEUTRON_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'%\' IDENTIFIED BY \''+NEUTRON_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+NEUTRON_PASS+' neutron')
    os.system('openstack role add --project service --user neutron admin')
    os.system('openstack service create --name neutron --description "OpenStack Networking" network')
    os.system('openstack endpoint create --region RegionOne network public http://'+NEUTRON_NAME+':9696')
    os.system('openstack endpoint create --region RegionOne network internal http://'+NEUTRON_NAME+':9696')
    os.system('openstack endpoint create --region RegionOne network admin http://'+NEUTRON_NAME+':9696')


    os.system('yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-linuxbridge ebtables -y')

    neutron_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS}

    neutron_nova = {'auth_url':'http://'+KEYSTONE_NAME+':35357', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'nova', 'password':NOVA_PASS}


    if network == 'Self-service' or network == 'self-service':

        config = ConfigParser.ConfigParser()
        os.system('cp /etc/neutron/l3_agent.ini /etc/neutron/l3_agent.ini.bak')
        print "cp /etc/neutron/l3_agent.ini done!"
        with open('/etc/neutron/l3_agent.ini', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            config.set('DEFAULT', 'interface_driver', 'neutron.agent.linux.interface.BridgeInterfaceDriver')
            config.write(open('/etc/neutron/l3_agent.ini', 'w'))
        neutron_default = {'core_plugin':'ml2', 'service_plugins':'router', 'allow_overlapping_ips':'True', 'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'notify_nova_on_port_status_changes':'True', 'notify_nova_on_port_data_changes':'True'}
    else:
        neutron_default = {'core_plugin':'ml2', 'service_plugins':'', 'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'notify_nova_on_port_status_changes':'True', 'notify_nova_on_port_data_changes':'True'}


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/neutron.conf /etc/neutron/neutron.conf.bak')
    print "cp /etc/neutron/neutron.conf done!"
    with open('/etc/neutron/neutron.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('database', 'connection', 'mysql+pymysql://neutron:'+NEUTRON_DBPASS+'@'+DB_NAME+'/neutron')
        for (k,v) in neutron_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in neutron_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'nova' not in sections:
            config.add_section('nova')
        for (k,v) in neutron_nova.iteritems():
            config.set('nova', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/neutron/tmp')
        config.write(open('/etc/neutron/neutron.conf', 'w'))


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugins/ml2/ml2_conf.ini.bak')
    print "cp /etc/neutron/plugins/ml2/ml2_conf.ini done!"
    with open('/etc/neutron/plugins/ml2/ml2_conf.ini', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if network == 'Self-service' or network == 'self-service':
            config.set('ml2', 'type_drivers', 'flat,vlan,vxlan')
            config.set('ml2', 'tenant_network_types', 'vxlan')
            config.set('ml2', 'mechanism_drivers', 'linuxbridge,l2population')
            config.set('ml2_type_vxlan', 'vni_ranges', '1:1000')
        else:
            config.set('ml2', 'type_drivers', 'flat,vlan')
            config.set('ml2', 'tenant_network_types', '')
            config.set('ml2', 'mechanism_drivers', 'linuxbridge')
        config.set('ml2', 'extension_drivers', 'port_security')
        config.set('ml2_type_flat', 'flat_networks', 'provider')
        config.set('securitygroup', 'enable_ipset', 'True')
        config.write(open('/etc/neutron/plugins/ml2/ml2_conf.ini', 'w'))


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini /etc/neutron/plugins/ml2/linuxbridge_agent.ini.bak')
    print "cp /etc/neutron/plugins/ml2/linuxbridge_agent.ini done!"
    with open('/etc/neutron/plugins/ml2/linuxbridge_agent.ini', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('linux_bridge', 'physical_interface_mappings', 'provider:'+interface)
        if network == 'Self-service' or network == 'self-service':
            config.set('vxlan', 'enable_vxlan', 'True')
            config.set('vxlan', 'local_ip', ipaddr)
            config.set('vxlan', 'l2_population', 'True')
        else:
            config.set('vxlan', 'enable_vxlan','False')
        config.set('securitygroup', 'enable_security_group','True')
        config.set('securitygroup', 'firewall_driver','neutron.agent.linux.iptables_firewall.IptablesFirewallDriver')
        config.write(open('/etc/neutron/plugins/ml2/linuxbridge_agent.ini', 'w'))


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/dhcp_agent.ini /etc/neutron/dhcp_agent.ini.bak')
    print "cp /etc/neutron/dhcp_agent.ini done!"
    with open('/etc/neutron/dhcp_agent.ini', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('DEFAULT', 'interface_driver', 'neutron.agent.linux.interface.BridgeInterfaceDriver')
        config.set('DEFAULT', 'dhcp_driver', 'neutron.agent.linux.dhcp.Dnsmasq')
        config.set('DEFAULT', 'enable_isolated_metadata', 'True')
        config.write(open('/etc/neutron/dhcp_agent.ini', 'w'))


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/neutron/metadata_agent.ini /etc/neutron/metadata_agent.ini.bak')
    print "cp /etc/neutron/metadata_agent.ini done!"
    with open('/etc/neutron/metadata_agent.ini', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        config.set('DEFAULT', 'nova_metadata_ip', NOVA_NAME)
        config.set('DEFAULT', 'metadata_proxy_shared_secret', METADATA_SECRET)
        config.write(open('/etc/neutron/metadata_agent.ini', 'w'))


    neutron = {'url':'http://'+NEUTRON_NAME+':9696','auth_url':'http://'+KEYSTONE_NAME+':35357', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'region_name': 'RegionOne', 'project_name':'service', 'username':'neutron', 'password':NEUTRON_PASS, 'service_metadata_proxy':'True', 'metadata_proxy_shared_secret':METADATA_SECRET}

    if os.path.exists('/etc/nova/nova.conf'):
        config = ConfigParser.ConfigParser()
        with open('/etc/nova/nova.conf', 'rw') as cfgfile:
            config.readfp(cfgfile)
            sections = config.sections()
            if 'neutron' not in sections:
                config.add_section('neutron')
            for (k,v) in neutron.iteritems():
                config.set('neutron', k, v)
            config.write(open('/etc/nova/nova.conf', 'w'))
    else:
        print "Seems nova service not install on this host"
        print "Please edit /etc/nova/nova.conf on your nova service host for neutron"
        time.sleep(2)
        tcflush(sys.stdin, TCIFLUSH)
        raw_input("Press enter to continue: ")

    os.system('ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini')
    os.system('su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron')

    if os.path.exists('/etc/nova/nova.conf'):
        os.system('systemctl restart openstack-nova-api.service')
    os.system('systemctl enable neutron-server.service neutron-linuxbridge-agent.service neutron-dhcp-agent.service neutron-metadata-agent.service')
    os.system('systemctl start neutron-server.service neutron-linuxbridge-agent.service neutron-dhcp-agent.service neutron-metadata-agent.service')

    if network == 'Self-service' or network == 'self-service':
        os.system('systemctl enable neutron-l3-agent.service')
        os.system('systemctl start neutron-l3-agent.service')


def centos_redirect_page(hostname):
    index_html = open('/var/www/html/index.html', 'w+')
    index_html.write('<HTML>\n')
    index_html.write('<HEAD>\n')
    index_html.write('<meta http-equiv="refresh" content="0; url=http://'+hostname+'/dashboard">\n')
    index_html.write('</HEAD>\n')
    index_html.write('<BODY> </BODY>\n')
    index_html.write('</HTML>\n')
    index_html.close()

def centos_dashboard_install(hostname, network):
    ##################################################################### 
    # install & config dashboard
    ##################################################################### 
    os.system('yum install openstack-dashboard -y')
    os.system('sed -i \'/OPENSTACK_HOST =/c OPENSTACK_HOST = "'+hostname+'"\' /etc/openstack-dashboard/local_settings')
    os.system('sed -i "/ALLOWED_HOSTS/c ALLOWED_HOSTS = [\'*\', ]" /etc/openstack-dashboard/local_settings')
    os.system('sed -i \'/OPENSTACK_KEYSTONE_URL =/c OPENSTACK_KEYSTONE_URL = "http://%s:5000/v3" % OPENSTACK_HOST\' /etc/openstack-dashboard/local_settings')

    os.system('sed -i "/CACHES = {/i\SESSION_ENGINE = \'django.contrib.sessions.backends.cache\'" /etc/openstack-dashboard/local_settings')
#    os.system('sed -i "/11211/c \'LOCATION\': \''+hostname+':11211\'," /etc/openstack-dashboard/local_settings')

    os.system('sed -i \'/OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT/c OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True\' /etc/openstack-dashboard/local_settings')
    os.system('sed -i \'/OPENSTACK_KEYSTONE_DEFAULT_DOMAIN/c OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = "default"\' /etc/openstack-dashboard/local_settings')
    os.system('sed -i \'/OPENSTACK_KEYSTONE_DEFAULT_ROLE/c OPENSTACK_KEYSTONE_DEFAULT_ROLE = "user"\' /etc/openstack-dashboard/local_settings')

    os.system('sed -i \'/OPENSTACK_API_VERSIONS/c OPENSTACK_API_VERSIONS = {\' /etc/openstack-dashboard/local_settings')
    os.system('sed -i \'/OPENSTACK_API_VERSIONS/a\}\' /etc/openstack-dashboard/local_settings')
    os.system('sed -i \'/OPENSTACK_API_VERSIONS/a\    "volume": 2,\' /etc/openstack-dashboard/local_settings')
    os.system('sed -i \'/OPENSTACK_API_VERSIONS/a\    "image": 2,\' /etc/openstack-dashboard/local_settings')
    os.system('sed -i \'/OPENSTACK_API_VERSIONS/a\    "identity": 3,\' /etc/openstack-dashboard/local_settings')

    if network == 'Provider' or network == 'provider':
        ################################################################################################# 
        # TODO: here we missed "'enable_quotas': False," since there's a same line in local_settings.py.
        #       may need a better way to do the search & replace.
        ################################################################################################# 
        os.system('sed -i "/enable_router/c      \'enable_router\': False," /etc/openstack-dashboard/local_settings')
        os.system('sed -i "/enable_ipv6/c      \'enable_ipv6\': False," /etc/openstack-dashboard/local_settings')
        os.system('sed -i "/enable_distributed_router/c      \'enable_distributed_router\': False," /etc/openstack-dashboard/local_settings')
        os.system('sed -i "/enable_ha_router/c      \'enable_ha_router\': False," /etc/openstack-dashboard/local_settings')
        os.system('sed -i "/enable_lb/c      \'enable_lb\': False," /etc/openstack-dashboard/local_settings')
        os.system('sed -i "/enable_firewall/c      \'enable_firewall\': False," /etc/openstack-dashboard/local_settings')
        os.system('sed -i "/enable_vpn/c      \'enable_vpn\': False," /etc/openstack-dashboard/local_settings')
        os.system('sed -i "/enable_fip_topology_check/c      \'enable_fip_topology_check\': False," /etc/openstack-dashboard/local_settings')


    os.system('sed -i \'/TIME_ZONE/c TIME_ZONE = "Asia/Shanghai"\' /etc/openstack-dashboard/local_settings')
#    os.system('sed -i "/DEFAULT_THEME/c DEFAULT_THEME = \'default\'" /etc/openstack-dashboard/local_settings')

#    os.system('sed -i "/Timeout 300/c Timeout 600" /etc/apache2/apache2.conf')
#    os.system('sed -i "/WSGIProcessGroup horizon/a\WSGIApplicationGroup %{GLOBAL}" /etc/apache2/conf-available/openstack-dashboard.conf')
    centos_redirect_page(hostname)

    os.system('systemctl restart httpd.service memcached.service')


def centos_cinder_install(ipaddr, hostname):
    ##################################################################### 
    # install & config Cinder
    ##################################################################### 
    global CINDER_NAME
    CINDER_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS cinder;')
    cursor.execute('CREATE DATABASE cinder;')
    cursor.execute('GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'localhost\' IDENTIFIED BY \''+CINDER_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'%\' IDENTIFIED BY \''+CINDER_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+CINDER_PASS+' cinder')
    os.system('openstack role add --project service --user cinder admin')
    os.system('openstack service create --name cinder --description "OpenStack Block Storage" volume')
    os.system('openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2')
    os.system('openstack endpoint create --region RegionOne volume public http://'+CINDER_NAME+':8776/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volume internal http://'+CINDER_NAME+':8776/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volume admin http://'+CINDER_NAME+':8776/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volumev2 public http://'+CINDER_NAME+':8776/v2/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volumev2 internal http://'+CINDER_NAME+':8776/v2/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne volumev2 admin http://'+CINDER_NAME+':8776/v2/%\(tenant_id\)s')

    os.system('yum install openstack-cinder -y')

    cinder_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'cinder', 'password':CINDER_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/cinder/cinder.conf /etc/cinder/cinder.conf.bak')
    print "cp /etc/cinder/cinder.conf done!"
    with open('/etc/cinder/cinder.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://cinder:'+CINDER_DBPASS+'@'+DB_NAME+'/cinder')
        config.set('DEFAULT', 'transport_url', 'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME)
        config.set('DEFAULT', 'auth_strategy', 'keystone')
        config.set('DEFAULT', 'my_ip', ipaddr)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in cinder_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lib/cinder/tmp')
        config.write(open('/etc/cinder/cinder.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "cinder-manage db sync" cinder')
    os.system('systemctl restart openstack-nova-api.service')
    os.system('systemctl enable openstack-cinder-api.service openstack-cinder-scheduler.service')
    os.system('systemctl start openstack-cinder-api.service openstack-cinder-scheduler.service')

def centos_heat_install(hostname):
    ##################################################################### 
    # install & config Cinder
    ##################################################################### 
    global HEAT_NAME
    HEAT_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS heat;')
    cursor.execute('CREATE DATABASE heat;')
    cursor.execute('GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'localhost\' IDENTIFIED BY \''+HEAT_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'%\' IDENTIFIED BY \''+HEAT_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+HEAT_PASS+' heat')
    os.system('openstack role add --project service --user heat admin')
    os.system('openstack service create --name heat --description "Orchestration" orchestration')
    os.system('openstack service create --name head-cfn --description "Orchestration" cloudformation')
    os.system('openstack endpoint create --region RegionOne orchestration public http://'+HEAT_NAME+':8004/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne orchestration internal http://'+HEAT_NAME+':8004/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne orchestration admin http://'+HEAT_NAME+':8004/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne cloudformation public http://'+HEAT_NAME+':8000/v1')
    os.system('openstack endpoint create --region RegionOne cloudformation internal http://'+HEAT_NAME+':8000/v1')
    os.system('openstack endpoint create --region RegionOne cloudformation admin http://'+HEAT_NAME+':8000/v1')

    os.system('openstack domain create --description "Stack projects and users" heat')
    os.system('openstack user create --domain heat --password '+HEAT_DOMAIN_PASS+' heat_domain_admin')
    os.system('openstack role add --domain heat --user-domain heat --user heat_domain_admin admin')
    os.system('openstack role create heat_stack_owner')
    os.system('openstack role add --project demo --user demo heat_stack_owner')
    os.system('openstack role create heat_stack_user')

    os.system('yum install openstack-heat-api openstack-heat-api-cfn openstack-heat-engine -y')

    heat_default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'heat_metadata_server_url':'http://'+HEAT_NAME+':8000', 'heat_waitcondition_server_url':'http://'+HEAT_NAME+':8000/v1/waitcondition', 'stack_domain_admin':'heat_domain_admin', 'stack_domain_admin_password':HEAT_DOMAIN_PASS, 'stack_user_domain_name':'heat'}

    heat_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'heat', 'password':HEAT_PASS}

    heat_trustee = {'auth_type':'password', 'auth_url':'http://'+KEYSTONE_NAME+':35357', 'username':'heat', 'password':HEAT_PASS, 'user_domain_name': 'default'}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/heat/heat.conf /etc/heat/heat.conf.bak')
    print "cp /etc/heat/heat.conf done!"
    with open('/etc/heat/heat.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://heat:'+HEAT_DBPASS+'@'+DB_NAME+'/heat')
        for (k,v) in heat_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in heat_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'trustee' not in sections:
            config.add_section('trustee')
        for (k,v) in heat_trustee.iteritems():
            config.set('trustee', k, v)
        if 'clients_keystone' not in sections:
            config.add_section('clients_keystone')
        config.set('clients_keystone', 'auth_uri', 'http://'+KEYSTONE_NAME+':35357')
        if 'ec2authtoken' not in sections:
            config.add_section('ec2authtoken')
        config.set('ec2authtoken', 'auth_uri', 'http://'+KEYSTONE_NAME+':5000')
        config.write(open('/etc/heat/heat.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "heat-manage db_sync" heat')
    os.system('systemctl enable openstack-heat-api.service openstack-heat-api-cfn.service openstack-heat-engine.service')
    os.system('systemctl start openstack-heat-api.service openstack-heat-api-cfn.service openstack-heat-engine.service')



def centos_manila_install(ipaddr, hostname):
    ##################################################################### 
    # install & config Manila
    ##################################################################### 
    global MANILA_NAME
    MANILA_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS manila;')
    cursor.execute('CREATE DATABASE manila;')
    cursor.execute('GRANT ALL PRIVILEGES ON manila.* TO \'manila\'@\'localhost\' IDENTIFIED BY \''+MANILA_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON manila.* TO \'manila\'@\'%\' IDENTIFIED BY \''+MANILA_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+MANILA_PASS+' manila')
    os.system('openstack role add --project service --user manila admin')
    os.system('openstack service create --name manila --description "OpenStack Shared File Systems" share')
    os.system('openstack service create --name manilav2 --description "OpenStack Shared File Systems" sharev2')
    os.system('openstack endpoint create --region RegionOne share public http://'+MANILA_NAME+':8786/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne share internal http://'+MANILA_NAME+':8786/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne share admin http://'+MANILA_NAME+':8786/v1/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne sharev2 public http://'+MANILA_NAME+':8786/v2/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne sharev2 internal http://'+MANILA_NAME+':8786/v2/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne sharev2 admin http://'+MANILA_NAME+':8786/v2/%\(tenant_id\)s')

    os.system('yum install openstack-manila python-manilaclient openstack-manila-ui -y')

    manila_default = {'transport_url':'rabbit://openstack:'+RABBIT_PASS+'@'+MQ_NAME, 'auth_strategy':'keystone', 'my_ip':ipaddr, 'default_share_type':'default_share_type', 'share_name_template':'share-%s', 'rootwrap_config':'/etc/manila/rootwrap.conf', 'api_paste_config':'/etc/manila/api-paste.ini'}

    manila_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'memcached_servers':MEMCACHE_NAME+':11211', 'auth_type':'password', 'project_domain_id':'default', 'user_domain_id': 'default', 'project_name':'service', 'username':'manila', 'password':MANILA_PASS}

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/manila/manila.conf /etc/manila/manila.conf.bak')
    print "cp /etc/manila/manila.conf done!"
    with open('/etc/manila/manila.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://manila:'+MANILA_DBPASS+'@'+DB_NAME+'/manila')
        for (k,v) in manila_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in manila_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        if 'oslo_concurrency' not in sections:
            config.add_section('oslo_concurrency')
        config.set('oslo_concurrency', 'lock_path', '/var/lock/manila')
        config.write(open('/etc/manila/manila.conf', 'w'))
        #cfgfile.close()

    os.system('su -s /bin/sh -c "manila-manage db sync" manila')
    os.system('systemctl enable openstack-manila-api.service openstack-manila-scheduler.service')
    os.system('systemctl start openstack-manila-api.service openstack-manila-scheduler.service')
    os.system('systemctl restart httpd')
    os.system('systemctl restart memcached')


def centos_trove_install(hostname):
    ##################################################################### 
    # install & config Trove
    ##################################################################### 
    global TROVE_NAME
    TROVE_NAME = hostname
    con = MySQLdb.connect(DB_NAME, 'root', MYSQL_PASS)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS trove;')
    cursor.execute('CREATE DATABASE trove;')
    cursor.execute('GRANT ALL PRIVILEGES ON trove.* TO \'trove\'@\'localhost\' IDENTIFIED BY \''+TROVE_DBPASS+'\';')
    cursor.execute('GRANT ALL PRIVILEGES ON trove.* TO \'trove\'@\'%\' IDENTIFIED BY \''+TROVE_DBPASS+'\';')
    cursor.close()

    export_admin()
    os.system('openstack user create --domain default --password '+TROVE_PASS+' trove')
    os.system('openstack role add --project service --user trove admin')
    os.system('openstack service create --name trove --description "OpenStack Database" database')
    os.system('openstack endpoint create --region RegionOne database public http://'+TROVE_NAME+':8779/v1.0/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne database internal http://'+TROVE_NAME+':8779/v1.0/%\(tenant_id\)s')
    os.system('openstack endpoint create --region RegionOne database admin http://'+TROVE_NAME+':8779/v1.0/%\(tenant_id\)s')

    os.system('yum install openstack-trove python-troveclient -y')


    ##################################################################### 
    # check and get /etc/trove/api-paste.ini
    ##################################################################### 
    if not os.path.exists('/etc/trove/api-paste.ini'):
        os.system('sudo curl -o /etc/trove/api-paste.ini http://git.openstack.org/cgit/openstack/trove/plain/etc/trove/api-paste.ini?h=stable/newton')
    ##################################################################### 
    # check and get /etc/trove/trove-guestagent.conf
    ##################################################################### 
    if not os.path.exists('/etc/trove/trove-guestagent.conf'):
        os.system('sudo curl -o /etc/trove/trove-guestagent.conf http://git.openstack.org/cgit/openstack/trove/plain/etc/trove/trove-guestagent.conf.sample?h=stable/newton')


    trove_all_default = {'log_dir':'/var/log/trove', 'trove_auth_url':'http://'+KEYSTONE_NAME+':5000/v2.0', 'nova_compute_url':'http://'+NOVA_NAME+':8774/v2', 'cinder_url':'http://'+CINDER_NAME+':8776/v1', 'swift_url':'http://'+SWIFT_NAME+':8080/v1/AUTH_', 'notifier_queue_hostname':MQ_NAME, 'rpc_backend':'rabbit'}

    trove_all_oslo_messaging_rabbit = {'rabbit_host':MQ_NAME, 'rabbit_userid':'openstack', 'rabbit_password':RABBIT_PASS}

    trove_default = {'auth_strategy':'keystone', 'add_addresses':'True', 'network_label_regex':'^NETWORK_LABEL$', 'api_paste_config':'/etc/trove/api-paste.ini'}

    trove_keystone_authtoken = {'auth_uri':'http://'+KEYSTONE_NAME+':5000','auth_url':'http://'+KEYSTONE_NAME+':35357', 'auth_type':'password', 'project_domain_name':'default', 'user_domain_name': 'default', 'project_name':'service', 'username':'trove', 'password':TROVE_PASS}

    trove_taskmanager_default = {'nova_proxy_admin_user':'admin', 'nova_proxy_admin_pass':ADMIN_PASS, 'nova_proxy_admin_tenant_name':'service', 'taskmanager_manager':'trove.taskmanager.manager.Manager', 'use_nova_server_config_drive':'True', 'network_driver':'trove.network.neutron.NeutronDriver', 'network_label_regex':'.*'}

    trove_guestagent_default = {'rabbit_host':MQ_NAME, 'rabbit_password':RABBIT_PASS, 'nova_proxy_admin_user':'admin', 'nova_proxy_admin_pass':ADMIN_PASS, 'nova_proxy_admin_tenant_name':'service','trove_auth_url':'http://'+KEYSTONE_NAME+':35357/v2.0'}


    config = ConfigParser.ConfigParser()
    os.system('cp /etc/trove/trove.conf /etc/trove/trove.conf.bak')
    print "cp /etc/trove/trove.conf done!"
    with open('/etc/trove/trove.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in trove_all_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://trove:'+TROVE_DBPASS+'@'+DB_NAME+'/trove')
        if 'oslo_messaging_rabbit' not in sections:
            config.add_section('oslo_messaging_rabbit')
        for (k,v) in trove_all_oslo_messaging_rabbit.iteritems():
            config.set('oslo_messaging_rabbit', k, v)
        for (k,v) in trove_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'keystone_authtoken' not in sections:
            config.add_section('keystone_authtoken')
        for (k,v) in trove_keystone_authtoken.iteritems():
            config.set('keystone_authtoken', k, v)
        config.write(open('/etc/trove/trove.conf', 'w'))
        #cfgfile.close()

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/trove/trove-taskmanager.conf /etc/trove/trove-taskmanager.conf.bak')
    print "cp /etc/trove/trove-taskmanager.conf done!"
    with open('/etc/trove/trove-taskmanager.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in trove_all_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://trove:'+TROVE_DBPASS+'@'+DB_NAME+'/trove')
        if 'oslo_messaging_rabbit' not in sections:
            config.add_section('oslo_messaging_rabbit')
        for (k,v) in trove_all_oslo_messaging_rabbit.iteritems():
            config.set('oslo_messaging_rabbit', k, v)
        for (k,v) in trove_taskmanager_default.iteritems():
            config.set('DEFAULT', k, v)
        config.write(open('/etc/trove/trove-taskmanager.conf', 'w'))
        #cfgfile.close()

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/trove/trove-conductor.conf /etc/trove/trove-conductor.conf.bak')
    print "cp /etc/trove/trove-conductor.conf done!"
    with open('/etc/trove/trove-conductor.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in trove_all_default.iteritems():
            config.set('DEFAULT', k, v)
        if 'database' not in sections:
            config.add_section('database')
        config.set('database', 'connection', 'mysql+pymysql://trove:'+TROVE_DBPASS+'@'+DB_NAME+'/trove')
        if 'oslo_messaging_rabbit' not in sections:
            config.add_section('oslo_messaging_rabbit')
        for (k,v) in trove_all_oslo_messaging_rabbit.iteritems():
            config.set('oslo_messaging_rabbit', k, v)
        config.write(open('/etc/trove/trove-conductor.conf', 'w'))
        #cfgfile.close()

    config = ConfigParser.ConfigParser()
    os.system('cp /etc/trove/trove-guestagent.conf /etc/trove/trove-guestagent.conf.bak')
    print "cp /etc/trove/trove-guestagent.conf done!"
    with open('/etc/trove/trove-guestagent.conf', 'rw') as cfgfile:
        config.readfp(cfgfile)
        sections = config.sections()
        for (k,v) in trove_guestagent_default.iteritems():
            config.set('DEFAULT', k, v)
        config.write(open('/etc/trove/trove-guestagent.conf', 'w'))
        #cfgfile.close()


    os.system('su -s /bin/sh -c "trove-manage db_sync" trove')
    os.system('systemctl enable openstack-trove-api.service openstack-trove-taskmanager.service openstack-trove-conductor.service')
    os.system('systemctl start openstack-trove-api.service openstack-trove-taskmanager.service openstack-trove-conductor.service')
    ##################################################################### 
    # install Trove dashboard, use version 7.0.1 for newton
    ##################################################################### 
    os.system('yum install python-pip -y')
    os.system('pip install trove-dashboard==7.0.1')
    os.system('cp -rf /usr/lib/python2.7/site-packages/trove_dashboard/enabled/* /usr/share/openstack-dashboard/openstack_dashboard/local/enabled/')
    os.system('systemctl restart httpd.service memcached.service')




def centos_install(ipaddr, hostname, interface, network):
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
    os.system('sed -i \'/127.0.0.1/c 127.0.0.1  localhost '+hostname+' \' /etc/hosts')
    os.system('sed -i \'/127.0.1.1/d\' /etc/hosts')
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

    centos_ntp_install()
    centos_client_install()
    centos_db_install(ipaddr, hostname)
    centos_mq_install(hostname)
    centos_memcache_install(hostname)
    centos_keystone_install(hostname)
    create_env_script()
    centos_glance_install(hostname)
    centos_nova_install(ipaddr, hostname)
    centos_neutron_install(ipaddr, hostname, interface, network)
    centos_dashboard_install(hostname, network)
    centos_cinder_install(ipaddr, hostname)
    centos_heat_install(hostname)
    centos_manila_install(ipaddr, hostname)
    centos_trove_install(hostname)
    openstack_config(network)





def usage():
    print 'control_install.py [options]'
    print 'now only support Ubuntu16.04 and CentOS7'
    print 'Options:'
    print '-n, --network=<NetworkType>   network type (Provider or Self-service)'
    print '-m, --hostname=<HostName>     host name'
    print '-i, --ipaddr=<IPAddress>      host IP address'
    print '                              for Self-service network, it should be'
    print '                              the management network IP address'
    print '-f, --interface=<DeviceName>  ethernet device name, e.g. eth0'
    print '                              which connect to the public network'


def main(argv):
    platform = ''
    network = ''
    ipaddr = ''
    hostname = ''
    interface = ''
    try:
        opts, args = getopt.getopt(argv,"hn:i:m:f:",["network=","ipaddr=","hostname=","interface="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
           usage()
           sys.exit()
        elif opt in ("-n", "--network"):
           network = arg
        elif opt in ("-i", "--ipaddr"):
           ipaddr = arg
        elif opt in ("-m", "--hostname"):
           hostname = arg
        elif opt in ("-f", "--interface"):
           interface = arg

    # check param integrity
    if network == '' or ipaddr == '' or hostname == '' or interface == '':
        usage()
        sys.exit()

    platform = get_distribution()

    if platform == 'Ubuntu':
        ubuntu_install(ipaddr, hostname, interface, network)
    elif platform == 'CentOS':
        centos_install(ipaddr, hostname, interface, network)
    else :
        print 'Unsupported host platform!'
        usage()




if __name__ == "__main__":
    main(sys.argv[1:])

