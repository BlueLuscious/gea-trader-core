""" URL configuration for tenancy flows. """

from django.urls import path
from tenancy.views import SwitchActiveTenantView

urlpatterns = [
    path("tenancy/switch/<uuid:tenant_id>/", SwitchActiveTenantView.as_view(), name="switch-active-tenant"),
]
