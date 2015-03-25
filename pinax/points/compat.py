try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey  # noqa

try:
    from django.apps import apps as app_cache
except ImportError:
    from django.db.models.loading import cache as app_cache  # noqa
