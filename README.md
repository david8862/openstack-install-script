Automation script for Openstack Newton version install & deployment
======================================================
## Guide
This project includes a set of automation scripts for following openstack service deployment and config. All these scripts support Ubuntu 16.04 and CentOS 7 host OS. Deploy & config process mainly follows Openstack online guide:
* https://docs.openstack.org/newton/install-guide-ubuntu/
* https://docs.openstack.org/newton/install-guide-rdo/


### 1. Controller Node
* host environment (DNS, NTP, DB, etc.) setup
* keystone
* glance
* nova
* neutron
* cinder
* heat
* manila
* trove
* horizon(dashboard)

### 2. Compute Node
* host environment (DNS, NTP, DB, etc.) setup
* nova-compute
* neutron

### 3. Block Storage Node
* host environment (DNS, NTP, DB, etc.) setup
* cinder volume
* lvm

### 4. Manila Share Storage Node 
* host environment (DNS, NTP, DB, etc.) setup
* manila share
* lvm/neutron linux bridge

## Config script
"demo-template.yml" is a template file for heat service. And "config.sh" is a pre-config script when launching a new Ubuntu 16.04 or CentOS 7 VM from Openstack to enable the ssh password login and install some needed software.


