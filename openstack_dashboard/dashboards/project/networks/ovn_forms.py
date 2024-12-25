"""
Forms for handling OVN network operations.
"""
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard.api import neutron
from openstack_dashboard.api import ovn


class CreateOVNNetworkForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255,
                         label=_("Network Name"),
                         required=True)
    
    admin_state_up = forms.BooleanField(label=_("Enable Admin State"),
                                      initial=True,
                                      required=False)
    
    shared = forms.BooleanField(label=_("Shared"),
                              initial=False,
                              required=False)
    
    # OVN specific fields
    logical_switch_name = forms.CharField(
        max_length=255,
        label=_("Logical Switch Name"),
        required=False,
        help_text=_("Name for the OVN logical switch. If left empty, "
                   "the network name will be used."))
    
    port_security = forms.BooleanField(
        label=_("Port Security"),
        initial=True,
        required=False,
        help_text=_("Enable security groups and port security"))
    
    dhcp_options = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label=_("DHCP Options"),
        required=False,
        help_text=_("Enter DHCP options in key=value format, one per line. "
                   "Example: router=192.168.1.1"))
    
    def handle(self, request, data):
        try:
            params = {
                'name': data['name'],
                'admin_state_up': data['admin_state_up'],
                'shared': data['shared'],
                'port_security_enabled': data['port_security']
            }
            
            # Add OVN-specific parameters
            if data.get('logical_switch_name'):
                params['logical_switch'] = data['logical_switch_name']
            else:
                params['logical_switch'] = data['name']
                
            # Parse DHCP options
            if data.get('dhcp_options'):
                dhcp_opts = {}
                for line in data['dhcp_options'].split('\n'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        dhcp_opts[key.strip()] = value.strip()
                params['dhcp_options'] = dhcp_opts
            
            # Create the network with OVN parameters
            network = ovn.create_logical_switch(request, **params)
            
            messages.success(request,
                           _('Network %s was successfully created.') %
                           data['name'])
            return network
        except Exception as e:
            exceptions.handle(request,
                           _('Unable to create network: %s') % str(e))
            return False


class UpdateOVNNetworkForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255,
                         label=_("Name"),
                         required=False)
    
    admin_state = forms.BooleanField(label=_("Enable Admin State"),
                                   required=False)
    
    shared = forms.BooleanField(label=_("Shared"),
                              required=False)
    
    port_security = forms.BooleanField(
        label=_("Port Security"),
        required=False,
        help_text=_("Enable security groups and port security"))
    
    dhcp_options = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label=_("DHCP Options"),
        required=False,
        help_text=_("Enter DHCP options in key=value format, one per line. "
                   "Example: router=192.168.1.1"))
    
    failure_url = 'horizon:project:networks:index'

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        network_id = kwargs.get('initial', {}).get('network_id')
        if network_id:
            try:
                network = neutron.network_get(request, network_id)
                self.fields['name'].initial = network.name
                self.fields['admin_state'].initial = network.admin_state_up
                self.fields['shared'].initial = network.shared
                
                # Set OVN-specific initial values
                if hasattr(network, 'ovn_info'):
                    self.fields['port_security'].initial = (
                        network.ovn_info.port_security_enabled)
                    if network.ovn_info.dhcp_options:
                        dhcp_opts = []
                        for key, value in network.ovn_info.dhcp_options.items():
                            dhcp_opts.append(f"{key}={value}")
                        self.fields['dhcp_options'].initial = '\n'.join(dhcp_opts)
            except Exception:
                exceptions.handle(request,
                               _('Unable to retrieve network details.'))
    
    def handle(self, request, data):
        try:
            params = {
                'name': data['name'],
                'admin_state_up': data['admin_state'],
                'shared': data['shared'],
                'port_security_enabled': data['port_security']
            }
            
            # Parse DHCP options
            if data.get('dhcp_options'):
                dhcp_opts = {}
                for line in data['dhcp_options'].split('\n'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        dhcp_opts[key.strip()] = value.strip()
                params['dhcp_options'] = dhcp_opts
            
            network_id = self.initial['network_id']
            network = neutron.network_update(request, network_id, **params)
            msg = _('Network %s was successfully updated.') % data['name']
            messages.success(request, msg)
            return network
        except Exception as e:
            exceptions.handle(request,
                           _('Unable to update network: %s') % str(e))
            return False
