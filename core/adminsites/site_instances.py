""" Shared admin site instances. """

from core.adminsites.sites.master_admin_site import MasterAdminSite
from core.adminsites.sites.owner_admin_site import OwnerAdminSite


master_admin_site = MasterAdminSite(name="master_admin")
owner_admin_site = OwnerAdminSite(name="owner_admin")
