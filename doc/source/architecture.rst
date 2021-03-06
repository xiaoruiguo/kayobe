============
Architecture
============

Hosts in the System
===================

In a system deployed by Kayobe we define a number of classes of hosts.

Control host
    The control host is the host on which kayobe, kolla and kolla-ansible will
    be installed, and is typically where the cloud will be managed from.
Seed host
    The seed host runs the bifrost deploy container and is used to provision
    the cloud hosts.  Typically the seed host is deployed as a VM but this is
    not mandatory.
Cloud hosts
    The cloud hosts run the OpenStack control plane, storage, and virtualised
    compute services.  Typically the cloud hosts run on bare metal but this is
    not mandatory.
Bare metal compute hosts:
    In a cloud providing bare metal compute services to tenants via ironic,
    these hosts will run the bare metal tenant workloads.  In a cloud with only
    virtualised compute this category of hosts does not exist.

.. note::

   In many cases the control and seed host will be the same, although this is
   not mandatory.

Networks
========

Kayobe's network configuration is very flexible but does define a few default
classes of networks.  These are logical networks and may map to one or more
physical networks in the system.

Overcloud provisioning network
    The overcloud provisioning network is used by the seed host to provision
    the cloud hosts.
Workload provisioning network
    The workload provisioning network is used by the cloud hosts to provision
    the bare metal compute hosts.
Internal network
    The internal network hosts the internal and admin OpenStack API endpoints.
External network
    The external network hosts the public OpenStack API endpoints and provides
    external network access for the hosts in the system.
