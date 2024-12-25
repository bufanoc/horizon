====================
OVN Network Guide
====================

This guide helps you manage OVN networks in OpenStack using the Horizon dashboard.

Creating an OVN Network
----------------------
1. Navigate to :menuselection:`Project --> Network --> Networks`
2. Click :guilabel:`Create OVN Network`
3. Fill in the following:
   * Network Name
   * Logical Switch Name (optional)
   * Enable/disable port security
   * DHCP options (optional)
4. Click :guilabel:`Create Network`

Managing ACL Rules
----------------
Access Control Lists (ACLs) control traffic flow in your network.

Creating ACL Rules
~~~~~~~~~~~~~~~~
1. Go to network details page
2. Click :guilabel:`Add Rule` in the ACLs section
3. Configure:
   * Direction (ingress/egress)
   * Priority (0-32767)
   * Match Expression
   * Action (allow/drop/reject)
   * Logging options

Common Match Expressions
~~~~~~~~~~~~~~~~~~~~~~
1. Allow HTTP traffic:
   ``ip4.src==10.0.0.0/24 && tcp.dst==80``

2. Allow SSH access:
   ``ip4.src==192.168.1.0/24 && tcp.dst==22``

3. Block outgoing SMTP:
   ``ip4.dst==0.0.0.0/0 && tcp.dst==25``

4. Allow specific MAC:
   ``eth.src==00:00:00:00:00:01``

Load Balancer Management
----------------------

Creating Load Balancers
~~~~~~~~~~~~~~~~~~~~~
1. Navigate to network details
2. Click :guilabel:`Create Load Balancer`
3. Configure:
   * Name
   * Protocol (TCP/UDP)
   * Virtual IP and Port
   * Initial Members (optional)

Adding Load Balancer Members
~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Open load balancer details
2. Click :guilabel:`Add Member`
3. Enter:
   * Member IP Address
   * Port Number

Example Configurations
--------------------

Web Server Load Balancing
~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: none

    Name: web-frontend
    Protocol: TCP
    VIP: 192.168.1.100:80
    Members:
      - 10.0.0.10:8080  # Web Server 1
      - 10.0.0.11:8080  # Web Server 2
      - 10.0.0.12:8080  # Web Server 3

    ACL Rules:
      1. Priority: 2000
         Match: ip4.dst==192.168.1.100 && tcp.dst==80
         Action: allow

      2. Priority: 1000
         Match: ip4.src==10.0.0.0/8
         Action: allow-related

Database Load Balancing
~~~~~~~~~~~~~~~~~~~~~
.. code-block:: none

    Name: db-cluster
    Protocol: TCP
    VIP: 192.168.1.200:5432
    Members:
      - 10.0.0.20:5432  # Primary DB
      - 10.0.0.21:5432  # Secondary DB

    ACL Rules:
      1. Priority: 3000
         Match: ip4.src==10.0.0.0/24 && tcp.dst==5432
         Action: allow

      2. Priority: 2000
         Match: tcp.dst==5432
         Action: drop

Troubleshooting
--------------

ACL Issues
~~~~~~~~~
1. Rule not working:
   * Check priority order
   * Verify match expression
   * Enable logging
   * Review direction setting

2. Connection problems:
   * Confirm IP addresses/subnets
   * Check for conflicting rules
   * Verify port numbers

Load Balancer Issues
~~~~~~~~~~~~~~~~~~
1. Members unreachable:
   * Verify member health status
   * Check network connectivity
   * Confirm port configurations

2. Performance issues:
   * Monitor member load
   * Check network latency
   * Review member distribution

Tips and Best Practices
---------------------
1. ACL Management:
   * Use descriptive names
   * Document rule purposes
   * Regular rule review
   * Test before production

2. Load Balancing:
   * Regular health checks
   * Monitor performance
   * Plan for scaling
   * Document configurations
