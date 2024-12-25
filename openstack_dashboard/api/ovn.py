"""
API module for interacting with OVN (Open Virtual Network).
This module provides the interface between Horizon and OVN operations.
"""

from oslo_log import log as logging
from openstack_dashboard.api import base
from openstack_dashboard.api import neutron

LOG = logging.getLogger(__name__)

class OVNNetwork(neutron.NeutronAPIDictWrapper):
    """Wrapper for OVN networks."""
    _attrs = ['id', 'name', 'logical_switch', 'network_type', 
              'port_security_enabled', 'dhcp_options']

def ovn_network_list(request, **params):
    """List OVN networks available to the tenant."""
    networks = neutron.network_list(request, **params)
    # Enhance network objects with OVN-specific information
    for network in networks:
        _add_ovn_info(request, network)
    return networks

def _add_ovn_info(request, network):
    """Add OVN-specific information to a network object."""
    try:
        # Get OVN logical switch information
        client = neutron.neutronclient(request)
        ovn_info = client.show_network_ovn_info(network.id)
        network.ovn_info = OVNNetwork(ovn_info)
    except Exception as e:
        LOG.error('Failed to get OVN info for network %s: %s', 
                 network.id, str(e))
        network.ovn_info = None

def create_logical_switch(request, name, **kwargs):
    """Create an OVN logical switch."""
    body = {'name': name}
    body.update(kwargs)
    return neutron.neutronclient(request).create_ovn_logical_switch(body=body)

def delete_logical_switch(request, switch_id):
    """Delete an OVN logical switch."""
    return neutron.neutronclient(request).delete_ovn_logical_switch(switch_id)

def get_logical_switch(request, switch_id):
    """Get details of an OVN logical switch."""
    return OVNNetwork(
        neutron.neutronclient(request).show_ovn_logical_switch(switch_id)
    )
