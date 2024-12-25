#!/bin/bash

set -e # Exit on error
set -x # Print commands

# Configuration variables
ADMIN_PASS="openstack123"
KEYSTONE_DBPASS="keystone123"
HORIZON_DBPASS="horizon123"
CONTROLLER_HOST="controller"
REGION="RegionOne"

# Update system
sudo apt update && sudo apt upgrade -y

# Install MySQL
sudo apt install -y mysql-server python3-pymysql

# Configure MySQL
sudo tee /etc/mysql/mysql.conf.d/openstack.cnf << EOF
[mysqld]
bind-address = 0.0.0.0
default-storage-engine = innodb
innodb_file_per_table = on
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8
EOF

# Restart MySQL
sudo systemctl restart mysql

# Secure MySQL installation
sudo mysql_secure_installation << EOF

y
$ADMIN_PASS
$ADMIN_PASS
y
y
y
y
EOF

# Create databases
sudo mysql -u root -p$ADMIN_PASS << EOF
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '$KEYSTONE_DBPASS';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '$KEYSTONE_DBPASS';
CREATE DATABASE horizon;
GRANT ALL PRIVILEGES ON horizon.* TO 'horizon'@'localhost' IDENTIFIED BY '$HORIZON_DBPASS';
GRANT ALL PRIVILEGES ON horizon.* TO 'horizon'@'%' IDENTIFIED BY '$HORIZON_DBPASS';
FLUSH PRIVILEGES;
EOF

# Install Keystone
sudo apt install -y keystone python3-openstackclient apache2 libapache2-mod-wsgi-py3

# Configure Keystone
sudo cp /etc/keystone/keystone.conf /etc/keystone/keystone.conf.bak
sudo tee /etc/keystone/keystone.conf << EOF
[DEFAULT]
log_dir = /var/log/keystone

[database]
connection = mysql+pymysql://keystone:$KEYSTONE_DBPASS@localhost/keystone

[token]
provider = fernet

[cache]
backend = oslo_cache.memcache_pool
enabled = true

[oslo_middleware]
enable_proxy_headers_parsing = true
EOF

# Initialize Keystone DB
sudo su -s /bin/bash keystone -c "keystone-manage db_sync"

# Initialize Fernet key repositories
sudo keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
sudo keystone-manage credential_setup --keystone-user keystone --keystone-group keystone

# Bootstrap Keystone
sudo keystone-manage bootstrap --bootstrap-password $ADMIN_PASS \
  --bootstrap-admin-url http://localhost:5000/v3/ \
  --bootstrap-internal-url http://localhost:5000/v3/ \
  --bootstrap-public-url http://localhost:5000/v3/ \
  --bootstrap-region-id $REGION

# Configure Apache for Keystone
sudo tee /etc/apache2/sites-available/keystone.conf << EOF
Listen 5000
<VirtualHost *:5000>
    WSGIDaemonProcess keystone-public processes=5 threads=1 user=keystone group=keystone display-name=%{GROUP}
    WSGIProcessGroup keystone-public
    WSGIScriptAlias / /usr/bin/keystone-wsgi-public
    WSGIApplicationGroup %{GLOBAL}
    WSGIPassAuthorization On
    ErrorLogFormat "%{cu}t %M"
    ErrorLog /var/log/apache2/keystone.log
    CustomLog /var/log/apache2/keystone_access.log combined

    <Directory /usr/bin>
        Require all granted
    </Directory>
</VirtualHost>
EOF

sudo ln -s /etc/apache2/sites-available/keystone.conf /etc/apache2/sites-enabled/
sudo systemctl restart apache2

# Set environment variables
cat << EOF | sudo tee /etc/profile.d/openstack.sh
export OS_USERNAME=admin
export OS_PASSWORD=$ADMIN_PASS
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://localhost:5000/v3
export OS_IDENTITY_API_VERSION=3
EOF

source /etc/profile.d/openstack.sh

# Create service project
openstack project create --domain default --description "Service Project" service

# Install Horizon dependencies
sudo apt install -y python3-pip git

# Clone and install Horizon
cd /opt
sudo git clone https://github.com/openstack/horizon.git
cd horizon
sudo pip3 install -e .

# Install additional requirements
sudo pip3 install -r requirements.txt

# Configure Horizon
sudo cp openstack_dashboard/local/local_settings.py.example openstack_dashboard/local/local_settings.py
sudo sed -i "s/OPENSTACK_HOST = \"127.0.0.1\"/OPENSTACK_HOST = \"localhost\"/" openstack_dashboard/local/local_settings.py
sudo sed -i "s/'enable_router': True,/'enable_router': True,\n    'enable_distributed_router': True,\n    'enable_ha_router': True,\n    'enable_lb': True,\n    'enable_firewall': True,\n    'enable_vpn': True,\n    'enable_fip_topology_check': True,/" openstack_dashboard/local/local_settings.py

# Configure Apache for Horizon
sudo tee /etc/apache2/conf-available/openstack-dashboard.conf << EOF
WSGIScriptAlias /horizon /opt/horizon/openstack_dashboard/wsgi/django.wsgi process-group=horizon
WSGIDaemonProcess horizon user=www-data group=www-data processes=3 threads=10 python-path=/opt/horizon
WSGIProcessGroup horizon
Alias /static /opt/horizon/static
<Directory /opt/horizon/openstack_dashboard/wsgi>
  Require all granted
</Directory>
<Directory /opt/horizon/static>
  Require all granted
</Directory>
EOF

sudo ln -s /etc/apache2/conf-available/openstack-dashboard.conf /etc/apache2/conf-enabled/
sudo a2enmod rewrite
sudo systemctl restart apache2

# Create Horizon database tables
cd /opt/horizon
python3 manage.py migrate --settings=openstack_dashboard.settings

# Collect static files
python3 manage.py collectstatic --noinput --settings=openstack_dashboard.settings

# Set permissions
sudo chown -R www-data:www-data /opt/horizon

# Final restart of services
sudo systemctl restart apache2

echo "Installation completed!"
echo "Access Horizon at: http://localhost/horizon"
echo "Default credentials:"
echo "Username: admin"
echo "Password: $ADMIN_PASS"
