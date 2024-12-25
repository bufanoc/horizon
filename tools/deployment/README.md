# OpenStack Deployment Script

This script installs and configures OpenStack Keystone and Horizon with OVN support on Ubuntu 22.04.

## Prerequisites

- Ubuntu Server 22.04 LTS
- Minimum 4GB RAM
- 20GB free disk space
- Root or sudo access

## Installation

1. Make the script executable:
```bash
chmod +x install_openstack.sh
```

2. Run the script:
```bash
sudo ./install_openstack.sh
```

## Configuration Details

### Default Settings

- Admin Password: openstack123
- Keystone Database Password: keystone123
- Horizon Database Password: horizon123
- Region: RegionOne
- Services:
  - Keystone: http://localhost:5000
  - Horizon: http://localhost/horizon

### Security Notes

- Change the default passwords in the script before running
- Configure firewall rules as needed
- Update SSL certificates for production use

## Post-Installation

1. Access Horizon:
   - URL: http://localhost/horizon
   - Username: admin
   - Password: openstack123

2. Verify Keystone:
```bash
source /etc/profile.d/openstack.sh
openstack token issue
```

## Troubleshooting

1. Check service status:
```bash
systemctl status apache2
systemctl status mysql
```

2. View logs:
```bash
tail -f /var/log/apache2/keystone.log
tail -f /var/log/apache2/horizon_error.log
```

3. Common issues:
   - Database connection errors: Check MySQL service and credentials
   - 500 errors: Check Apache logs
   - Authentication failures: Verify Keystone service status

## Production Considerations

1. Security:
   - Change all default passwords
   - Configure SSL/TLS
   - Set up proper firewall rules

2. Performance:
   - Adjust MySQL settings based on hardware
   - Configure Apache worker processes
   - Enable caching

3. Monitoring:
   - Set up logging
   - Configure monitoring tools
   - Regular backup schedule
