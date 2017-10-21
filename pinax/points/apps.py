from django.apps import AppConfig as BaseAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(BaseAppConfig):

    name = "pinax.points"
    label = "pinax_points"
    verbose_name = _("Pinax Points")
