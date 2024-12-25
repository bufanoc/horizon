"""
Views for handling OVN network operations.
"""
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.networks import tables as project_tables
from openstack_dashboard.dashboards.project.networks.ovn_forms import CreateOVNNetworkForm
from openstack_dashboard.dashboards.project.networks.ovn_forms import UpdateOVNNetworkForm
from openstack_dashboard.dashboards.project.networks.ovn_acl_forms import CreateACLForm
from openstack_dashboard.dashboards.project.networks.ovn_lb_forms import CreateLoadBalancerForm
from openstack_dashboard.dashboards.project.networks.ovn_lb_forms import AddMemberForm


class CreateOVNNetworkView(forms.ModalFormView):
    form_class = CreateOVNNetworkForm
    template_name = 'project/networks/create_ovn_network.html'
    success_url = reverse_lazy('horizon:project:networks:index')
    page_title = _("Create OVN Network")
    submit_label = _("Create Network")


class UpdateOVNNetworkView(forms.ModalFormView):
    form_class = UpdateOVNNetworkForm
    template_name = 'project/networks/update_ovn_network.html'
    success_url = reverse_lazy('horizon:project:networks:index')
    page_title = _("Update OVN Network")
    submit_label = _("Update Network")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["network_id"] = self.kwargs['network_id']
        return context

    def get_initial(self):
        network_id = self.kwargs['network_id']
        try:
            network = api.neutron.network_get(self.request, network_id)
        except Exception:
            exceptions.handle(self.request,
                            _('Unable to retrieve network details.'),
                            redirect=self.success_url)
        return {'network_id': network_id,
                'name': network.name,
                'admin_state': network.admin_state_up,
                'shared': network.shared}


class CreateACLView(forms.ModalFormView):
    form_class = CreateACLForm
    template_name = 'project/networks/create_acl.html'
    page_title = _("Create ACL Rule")
    submit_label = _("Create Rule")

    def get_success_url(self):
        return reverse('horizon:project:networks:detail',
                      args=(self.kwargs['network_id'],))

    def get_initial(self):
        return {'network_id': self.kwargs['network_id']}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["network_id"] = self.kwargs['network_id']
        return context


class CreateLoadBalancerView(forms.ModalFormView):
    form_class = CreateLoadBalancerForm
    template_name = 'project/networks/create_lb.html'
    page_title = _("Create Load Balancer")
    submit_label = _("Create Load Balancer")

    def get_success_url(self):
        return reverse('horizon:project:networks:detail',
                      args=(self.kwargs['network_id'],))

    def get_initial(self):
        return {'network_id': self.kwargs['network_id']}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["network_id"] = self.kwargs['network_id']
        return context


class AddLBMemberView(forms.ModalFormView):
    form_class = AddMemberForm
    template_name = 'project/networks/add_lb_member.html'
    page_title = _("Add Load Balancer Member")
    submit_label = _("Add Member")

    def get_success_url(self):
        return reverse('horizon:project:networks:detail',
                      args=(self.kwargs['network_id'],))

    def get_initial(self):
        return {
            'network_id': self.kwargs['network_id'],
            'lb_id': self.kwargs['lb_id']
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "network_id": self.kwargs['network_id'],
            "lb_id": self.kwargs['lb_id']
        })
        return context
