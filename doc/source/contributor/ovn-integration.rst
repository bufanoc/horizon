======================
OVN Network Integration
======================

Overview
--------
The OVN (Open Virtual Network) integration in OpenStack Horizon provides advanced networking capabilities through a user-friendly interface. This document describes the implementation details, usage examples, and best practices.

Features
--------
* Logical Switch Management
* Access Control Lists (ACLs)
* Load Balancing
* DHCP Configuration

ACL Management
-------------
ACLs provide fine-grained traffic control for OVN networks.

Match Expression Examples
~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: none

    # Allow HTTP traffic from specific subnet
    ip4.src==10.0.0.0/24 && tcp.dst==80

    # Allow SSH access from management network
    ip4.src==192.168.1.0/24 && tcp.dst==22

    # Block outgoing SMTP traffic
    ip4.dst==0.0.0.0/0 && tcp.dst==25

    # Allow DNS queries to specific server
    ip4.dst==10.0.0.53 && udp.dst==53

    # Match all IPv6 traffic
    ip6

    # Match traffic by MAC address
    eth.src==00:00:00:00:00:01

Priority Guidelines
~~~~~~~~~~~~~~~~~
* Priority range: 0-32767 (higher number = higher priority)
* Recommended ranges:
    * 32000-32767: Emergency rules
    * 31000-31999: Security group rules
    * 25000-30999: User-defined rules
    * 0-24999: Default rules

Actions
~~~~~~~
* ``allow``: Permit matching traffic
* ``allow-related``: Permit traffic and related connections
* ``drop``: Silently discard matching traffic
* ``reject``: Discard and send rejection notification

Load Balancer Configuration
-------------------------
Load balancers distribute traffic across multiple instances.

Example Configurations
~~~~~~~~~~~~~~~~~~~~
1. Web Server Load Balancer:

   .. code-block:: none

       Name: web-lb
       Protocol: TCP
       VIP: 192.168.1.100:80
       Members:
         - 10.0.0.10:8080
         - 10.0.0.11:8080
         - 10.0.0.12:8080

2. DNS Load Balancer:

   .. code-block:: none

       Name: dns-lb
       Protocol: UDP
       VIP: 192.168.1.53:53
       Members:
         - 10.0.0.53:53
         - 10.0.0.54:53

Best Practices
-------------
1. ACL Management:
   * Start with permissive rules and gradually restrict
   * Use logging for troubleshooting
   * Document match expressions
   * Regular review and cleanup of rules

2. Load Balancer:
   * Ensure member health checks
   * Monitor member performance
   * Plan for maintenance windows
   * Consider session persistence needs

Troubleshooting
--------------
Common Issues and Solutions:

1. ACL Not Working:
   * Verify priority order
   * Check match expression syntax
   * Enable logging for debugging
   * Confirm direction setting

2. Load Balancer Issues:
   * Verify member health status
   * Check network connectivity
   * Validate port configurations
   * Review protocol settings

API Reference
------------
.. code-block:: python

    # Create ACL
    ovn.create_acl(request,
                   network_id='uuid',
                   direction='to-lport',
                   priority=1000,
                   match='ip4.src==10.0.0.0/24',
                   action='allow')

    # Create Load Balancer
    ovn.create_load_balancer(request,
                            name='web-lb',
                            protocol='tcp',
                            vip='192.168.1.100:80',
                            members=['10.0.0.10:8080'])

Development
----------
Adding New Features:

1. API Layer (``ovn.py``):
   * Add new methods for OVN operations
   * Implement error handling
   * Add docstrings and type hints

2. Forms (``ovn_forms.py``):
   * Create form classes for new features
   * Add validation logic
   * Include help text

3. Views (``ovn_views.py``):
   * Implement view classes
   * Handle form processing
   * Add success/error messages

4. Templates:
   * Create/update HTML templates
   * Add necessary JavaScript
   * Follow Horizon UI guidelines
