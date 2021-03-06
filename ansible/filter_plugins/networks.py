# Copyright (c) 2017 StackHPC Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from ansible import errors
import jinja2
import netaddr


def _get_hostvar(context, var_name, inventory_hostname=None):
    if inventory_hostname is None:
        namespace = context
    else:
        if inventory_hostname not in context['hostvars']:
            raise errors.AnsibleFilterError(
                "Inventory hostname '%s' not in hostvars" % inventory_hostname)
        namespace = context["hostvars"][inventory_hostname]
    return namespace.get(var_name)


@jinja2.contextfilter
def net_attr(context, name, attr, inventory_hostname=None):
    var_name = "%s_%s" % (name, attr)
    return _get_hostvar(context, var_name, inventory_hostname)


def _make_attr_filter(attr):
    @jinja2.contextfilter
    def func(context, name, inventory_hostname=None):
        return net_attr(context, name, attr, inventory_hostname)
    return func


@jinja2.contextfilter
def net_vip_address(context, name, inventory_hostname=None):
    return net_attr(context, name, 'vip_address', inventory_hostname)


@jinja2.contextfilter
def net_ip(context, name, inventory_hostname=None):
    ips = net_attr(context, name, 'ips', inventory_hostname)
    if ips:
        if inventory_hostname is None:
            inventory_hostname = _get_hostvar(context, "inventory_hostname")
        return ips.get(inventory_hostname)


@jinja2.contextfilter
def net_interface(context, name, inventory_hostname=None):
    return net_attr(context, name, 'interface', inventory_hostname)


@jinja2.contextfilter
def net_cidr(context, name, inventory_hostname=None):
    return net_attr(context, name, 'cidr', inventory_hostname)


@jinja2.contextfilter
def net_mask(context, name, inventory_hostname=None):
    cidr = net_cidr(context, name, inventory_hostname)
    return str(netaddr.IPNetwork(cidr).netmask) if cidr is not None else None


@jinja2.contextfilter
def net_prefix(context, name, inventory_hostname=None):
    cidr = net_cidr(context, name, inventory_hostname)
    return str(netaddr.IPNetwork(cidr).prefixlen) if cidr is not None else None


@jinja2.contextfilter
def net_gateway(context, name, inventory_hostname=None):
    return net_attr(context, name, 'gateway', inventory_hostname)


@jinja2.contextfilter
def net_allocation_pool_start(context, name, inventory_hostname=None):
    return net_attr(context, name, 'allocation_pool_start', inventory_hostname)


@jinja2.contextfilter
def net_allocation_pool_end(context, name, inventory_hostname=None):
    return net_attr(context, name, 'allocation_pool_end', inventory_hostname)


@jinja2.contextfilter
def net_inspection_allocation_pool_start(context, name, inventory_hostname=None):
    return net_attr(context, name, 'inspection_allocation_pool_start', inventory_hostname)


@jinja2.contextfilter
def net_inspection_allocation_pool_end(context, name, inventory_hostname=None):
    return net_attr(context, name, 'inspection_allocation_pool_end', inventory_hostname)


@jinja2.contextfilter
def net_neutron_allocation_pool_start(context, name, inventory_hostname=None):
    return net_attr(context, name, 'neutron_allocation_pool_start', inventory_hostname)


@jinja2.contextfilter
def net_neutron_allocation_pool_end(context, name, inventory_hostname=None):
    return net_attr(context, name, 'neutron_allocation_pool_end', inventory_hostname)


@jinja2.contextfilter
def net_vlan(context, name, inventory_hostname=None):
    return net_attr(context, name, 'vlan', inventory_hostname)


net_mtu = _make_attr_filter('mtu')
net_routes = _make_attr_filter('routes')


@jinja2.contextfilter
def net_bridge_ports(context, name, inventory_hostname=None):
    return net_attr(context, name, 'bridge_ports', inventory_hostname)


def _route_obj(route):
    """Return a dict representation of an IP route.

    The returned dict is compatible with the route item of the
    interfaces_ether_interfaces and interfaces_bridge_interfaces variables in
    the MichaelRigaert.interfaces role.
    """
    net = netaddr.IPNetwork(route['cidr'])
    return {
        'network': str(net.network),
        'netmask': str(net.netmask),
        'gateway': route['gateway'],
    }


@jinja2.contextfilter
def net_interface_obj(context, name, inventory_hostname=None):
    """Return a dict representation of a network interface.

    The returned dict is compatible with the interfaces_ether_interfaces
    variable in the MichaelRigaert.interfaces role.
    """
    device = net_interface(context, name, inventory_hostname)
    if not device:
        raise errors.AnsibleFilterError(
            "Network interface for network '%s' on host '%s' not found" %
            (name, inventory_hostname))
    ip = net_ip(context, name, inventory_hostname)
    cidr = net_cidr(context, name, inventory_hostname)
    netmask = net_mask(context, name, inventory_hostname)
    gateway = net_gateway(context, name, inventory_hostname)
    vlan = net_vlan(context, name, inventory_hostname)
    mtu = net_mtu(context, name, inventory_hostname)
    routes = net_routes(context, name, inventory_hostname)
    if routes:
        routes = [_route_obj(route) for route in routes]
    interface = {
        'device': device,
        'address': ip,
        'netmask': netmask,
        'gateway': gateway,
        'vlan': vlan,
        'mtu': mtu,
        'route': routes,
        'bootproto': 'static',
        'onboot': 'yes',
    }
    interface = {k: v for k, v in interface.items() if v is not None}
    return interface


@jinja2.contextfilter
def net_bridge_obj(context, name, inventory_hostname=None):
    """Return a dict representation of a network bridge interface.

    The returned dict is compatible with the interfaces_bridge_interfaces
    variable in the MichaelRigaert.interfaces role.
    """
    device = net_interface(context, name, inventory_hostname)
    if not device:
        raise errors.AnsibleFilterError(
            "Network interface for network '%s' on host '%s' not found" %
            (name, inventory_hostname))
    ip = net_ip(context, name, inventory_hostname)
    cidr = net_cidr(context, name, inventory_hostname)
    netmask = net_mask(context, name, inventory_hostname)
    gateway = net_gateway(context, name, inventory_hostname)
    vlan = net_vlan(context, name, inventory_hostname)
    mtu = net_mtu(context, name, inventory_hostname)
    ports = net_bridge_ports(context, name, inventory_hostname)
    routes = net_routes(context, name, inventory_hostname)
    if routes:
        routes = [_route_obj(route) for route in routes]
    interface = {
        'device': device,
        'address': ip,
        'netmask': netmask,
        'gateway': gateway,
        'vlan': vlan,
        'mtu': mtu,
        'ports': ports,
        'route': routes,
        'bootproto': 'static',
        'onboot': 'yes',
    }
    interface = {k: v for k, v in interface.items() if v is not None}
    return interface


@jinja2.contextfilter
def net_is_ether(context, name, inventory_hostname=None):
    return net_bridge_ports(context, name) is None


@jinja2.contextfilter
def net_is_bridge(context, name, inventory_hostname=None):
    return net_bridge_ports(context, name) is not None


@jinja2.contextfilter
def net_is_vlan(context, name, inventory_hostname=None):
    return net_vlan(context, name) is not None


@jinja2.contextfilter
def net_select_ethers(context, names):
    return [name for name in names if net_is_ether(context, name)]


@jinja2.contextfilter
def net_select_bridges(context, names):
    return [name for name in names if net_is_bridge(context, name)]


@jinja2.contextfilter
def net_select_vlans(context, names):
    return [name for name in names if net_is_vlan(context, name)]


@jinja2.contextfilter
def net_reject_vlans(context, names):
    return [name for name in names if not net_is_vlan(context, name)]


@jinja2.contextfilter
def net_configdrive_network_device(context, name, inventory_hostname=None):
    device = net_interface(context, name, inventory_hostname)
    if not device:
        raise errors.AnsibleFilterError(
            "Network interface for network '%s' on host '%s' not found" %
            (name, inventory_hostname))
    ip = net_ip(context, name, inventory_hostname)
    cidr = net_cidr(context, name, inventory_hostname)
    netmask = net_mask(context, name, inventory_hostname)
    gateway = net_gateway(context, name, inventory_hostname)
    bootproto = 'static' if ip is not None else 'dhcp'
    interface = {
        'device': device,
        'address': ip,
        'netmask': netmask,
        'gateway': gateway,
        'bootproto': bootproto,
    }
    interface = {k: v for k, v in interface.items() if v is not None}
    return interface


class FilterModule(object):
    """Networking filters."""

    def filters(self):
        return {
            'net_attr': net_attr,
            'net_vip_address': net_vip_address,
            'net_fqdn': _make_attr_filter('fqdn'),
            'net_ip': net_ip,
            'net_interface': net_interface,
            'net_cidr': net_cidr,
            'net_mask': net_mask,
            'net_prefix': net_prefix,
            'net_gateway': net_gateway,
            'net_allocation_pool_start': net_allocation_pool_start,
            'net_allocation_pool_end': net_allocation_pool_end,
            'net_inspection_allocation_pool_start': net_inspection_allocation_pool_start,
            'net_inspection_allocation_pool_end': net_inspection_allocation_pool_end,
            'net_neutron_allocation_pool_start': net_neutron_allocation_pool_start,
            'net_neutron_allocation_pool_end': net_neutron_allocation_pool_end,
            'net_vlan': net_vlan,
            'net_mtu': net_mtu,
            'net_routes': net_routes,
            'net_interface_obj': net_interface_obj,
            'net_bridge_obj': net_bridge_obj,
            'net_is_ether': net_is_ether,
            'net_is_bridge': net_is_bridge,
            'net_is_vlan': net_is_vlan,
            'net_select_ethers': net_select_ethers,
            'net_select_bridges': net_select_bridges,
            'net_select_vlans': net_select_vlans,
            'net_reject_vlans': net_reject_vlans,
            'net_configdrive_network_device': net_configdrive_network_device,
        }
