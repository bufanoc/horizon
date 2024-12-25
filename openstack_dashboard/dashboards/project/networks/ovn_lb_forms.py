"""
Forms for managing OVN Load Balancers.
"""
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard.api import ovn


class CreateLoadBalancerForm(forms.SelfHandlingForm):
    name = forms.CharField(
        max_length=255,
        label=_("Name"),
        required=True)
    
    protocol = forms.ChoiceField(
        label=_("Protocol"),
        choices=[
            ('tcp', _('TCP')),
            ('udp', _('UDP'))
        ])
    
    vip_address = forms.IPField(
        label=_("VIP Address"),
        required=True,
        help_text=_("Virtual IP address for the load balancer"))
    
    vip_port = forms.IntegerField(
        label=_("VIP Port"),
        min_value=1,
        max_value=65535,
        required=True,
        help_text=_("Port number for the virtual IP"))
    
    members = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label=_("Members"),
        required=False,
        help_text=_("One member per line in format: IP:PORT"))
    
    admin_state_up = forms.BooleanField(
        label=_("Admin State"),
        required=False,
        initial=True)
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.network_id = kwargs.get('initial', {}).get('network_id')
    
    def clean_members(self):
        members = self.cleaned_data.get('members', '')
        if not members:
            return []
        
        member_list = []
        for line in members.split('\n'):
            line = line.strip()
            if line:
                if ':' not in line:
                    raise forms.ValidationError(
                        _("Invalid member format. Use IP:PORT"))
                member_list.append(line)
        return member_list
    
    def handle(self, request, data):
        try:
            vip = f"{data['vip_address']}:{data['vip_port']}"
            lb = ovn.create_load_balancer(
                request,
                name=data['name'],
                protocol=data['protocol'],
                vip=vip,
                members=data['members'],
                admin_state_up=data['admin_state_up'],
                network_id=self.network_id
            )
            messages.success(
                request,
                _('Successfully created load balancer %s') % data['name'])
            return lb
        except Exception as e:
            exceptions.handle(
                request,
                _('Unable to create load balancer: %s') % str(e))
            return False


class AddMemberForm(forms.SelfHandlingForm):
    member_address = forms.IPField(
        label=_("Member IP"),
        required=True)
    
    member_port = forms.IntegerField(
        label=_("Member Port"),
        min_value=1,
        max_value=65535,
        required=True)
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.lb_id = kwargs.get('initial', {}).get('lb_id')
    
    def handle(self, request, data):
        try:
            member = f"{data['member_address']}:{data['member_port']}"
            ovn.add_lb_member(request, self.lb_id, member)
            messages.success(request,
                           _('Successfully added member %s') % member)
            return True
        except Exception as e:
            exceptions.handle(request,
                            _('Unable to add member: %s') % str(e))
            return False
