""" Owner-admin URL builder for quotation runtime flows. """

from urllib.parse import urljoin
from django.conf import settings
from django.urls import reverse
from quotation.models import QuoteModel


class QuoteAdminUrlBuilder:
    """ Build owner-admin URLs for persisted quotes. """

    @staticmethod
    def build(*, quote: QuoteModel) -> str:
        """ Build one owner-admin URL for the provided quote.

        Args:
            quote: Persisted quote root.

        Returns:
            str: Absolute owner-admin URL when one base URL exists, otherwise one relative path.
        """
        admin_path = reverse("owner_admin:quotation_quotemodel_change", args=[quote.id])
        base_url_setting = str(getattr(settings, "BASE_URL", "") or "").strip()
        website_url = str(getattr(quote.tenant, "website_url", "") or "").strip()
        base_url = base_url_setting or website_url
        if not base_url:
            return admin_path

        return urljoin(f"{base_url.rstrip('/')}/", admin_path.lstrip("/"))
