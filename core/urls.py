""" URL configuration for core project. """

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.urls import path, include
from core.adminsites.site_instances import master_admin_site, owner_admin_site

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("django_components.urls")),
]

urlpatterns += i18n_patterns(
    path("admin/", master_admin_site.urls),
    path("owner-admin/", owner_admin_site.urls),
    prefix_default_language=False,
)

if settings.DEBUG and settings.MEDIA_URL.startswith("/"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
