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
              'port_security_enabled', 'dhcp_options', 'acls',
              'load_balancers']

class OVNACL(neutron.NeutronAPIDictWrapper):
    """Wrapper for OVN Access Control Lists."""
    _attrs = ['id', 'direction', 'priority', 'match', 'action',
              'log', 'severity']

class OVNLoadBalancer(neutron.NeutronAPIDictWrapper):
    """Wrapper for OVN Load Balancers."""
    _attrs = ['id', 'name', 'protocol', 'vip', 'members',
              'admin_state_up', 'status']

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

# ACL Management
def create_acl(request, network_id, direction, priority, match, action,
               log=False, severity=None):
    """Create an ACL rule for an OVN logical switch.
    
    Args:
        request: The request object
        network_id: ID of the network/logical switch
        direction: 'to-lport' or 'from-lport'
        priority: Rule priority (0-32767, higher number = higher priority)
        match: OVN match expression
        action: 'allow', 'allow-related', 'drop', or 'reject'
        log: Whether to enable logging for this ACL
        severity: Log severity if logging is enabled
    """
    body = {
        'direction': direction,
        'priority': priority,
        'match': match,
        'action': action,
        'log': log
    }
    if severity:
        body['severity'] = severity
    
    return OVNACL(
        neutron.neutronclient(request).create_ovn_acl(
            network_id, body=body)
    )

def delete_acl(request, network_id, acl_id):
    """Delete an ACL rule."""
    return neutron.neutronclient(request).delete_ovn_acl(
        network_id, acl_id
    )

def list_acls(request, network_id):
    """List all ACLs for a network."""
    return [OVNACL(a) for a in 
            neutron.neutronclient(request).list_ovn_acls(network_id)['acls']]

# Load Balancer Management
def create_load_balancer(request, name, protocol, vip, members=None, **kwargs):
    """Create an OVN load balancer.
    
    Args:
        request: The request object
        name: Name of the load balancer
        protocol: Protocol (TCP, UDP)
        vip: Virtual IP address and port (e.g., "192.168.1.10:80")
        members: List of member IPs and ports (e.g., ["10.0.0.1:8080", "10.0.0.2:8080"])
        **kwargs: Additional parameters
    """
    body = {
        'name': name,
        'protocol': protocol,
        'vip': vip,
        'members': members or []
    }
    body.update(kwargs)
    
    return OVNLoadBalancer(
        neutron.neutronclient(request).create_ovn_load_balancer(body=body)
    )

def delete_load_balancer(request, lb_id):
    """Delete an OVN load balancer."""
    return neutron.neutronclient(request).delete_ovn_load_balancer(lb_id)

def get_load_balancer(request, lb_id):
    """Get details of an OVN load balancer."""
    return OVNLoadBalancer(
        neutron.neutronclient(request).show_ovn_load_balancer(lb_id)
    )

def list_load_balancers(request, network_id=None):
    """List OVN load balancers.
    
    Args:
        request: The request object
        network_id: Optional network ID to filter by
    """
    params = {'network_id': network_id} if network_id else {}
    return [OVNLoadBalancer(lb) for lb in 
            neutron.neutronclient(request).list_ovn_load_balancers(**params)['load_balancers']]

def add_lb_member(request, lb_id, member_address):
    """Add a member to an OVN load balancer.
    
    Args:
        request: The request object
        lb_id: Load balancer ID
        member_address: Member IP and port (e.g., "10.0.0.1:8080")
    """
    return neutron.neutronclient(request).add_ovn_load_balancer_member(
        lb_id, {'member': member_address}
    )

def remove_lb_member(request, lb_id, member_address):
    """Remove a member from an OVN load balancer."""
    return neutron.neutronclient(request).remove_ovn_load_balancer_member(
        lb_id, {'member': member_address}
    )
