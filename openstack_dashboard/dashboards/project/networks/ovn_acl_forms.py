"""
Forms for managing OVN Access Control Lists.
"""
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard.api import ovn


class CreateACLForm(forms.SelfHandlingForm):
    direction = forms.ChoiceField(
        label=_("Direction"),
        choices=[
            ('to-lport', _('Ingress (to port)')),
            ('from-lport', _('Egress (from port)'))
        ],
        help_text=_("Direction of traffic flow"))
    
    priority = forms.IntegerField(
        label=_("Priority"),
        min_value=0,
        max_value=32767,
        initial=1000,
        help_text=_("Priority of the rule (0-32767, higher = more important)"))
    
    match = forms.CharField(
        label=_("Match Expression"),
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text=_("OVN match expression (e.g., 'ip4.src==10.0.0.0/24 && tcp.dst==80')"))
    
    action = forms.ChoiceField(
        label=_("Action"),
        choices=[
            ('allow', _('Allow')),
            ('allow-related', _('Allow Related')),
            ('drop', _('Drop')),
            ('reject', _('Reject'))
        ],
        help_text=_("Action to take when rule matches"))
    
    log = forms.BooleanField(
        label=_("Enable Logging"),
        required=False,
        help_text=_("Log matches to this rule"))
    
    severity = forms.ChoiceField(
        label=_("Log Severity"),
        required=False,
        choices=[
            ('alert', _('Alert')),
            ('warning', _('Warning')),
            ('notice', _('Notice')),
            ('info', _('Info')),
            ('debug', _('Debug'))
        ],
        help_text=_("Severity level for logging"))
    
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.network_id = kwargs.get('initial', {}).get('network_id')
    
    def handle(self, request, data):
        try:
            acl = ovn.create_acl(
                request,
                self.network_id,
                direction=data['direction'],
                priority=data['priority'],
                match=data['match'],
                action=data['action'],
                log=data['log'],
                severity=data['severity'] if data['log'] else None
            )
            messages.success(request,
                           _('Successfully created ACL rule.'))
            return acl
        except Exception as e:
            exceptions.handle(request,
                            _('Unable to create ACL rule: %s') % str(e))
            return False
