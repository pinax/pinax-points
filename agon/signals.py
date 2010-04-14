import django.dispatch


points_awarded = django.dispatch.Signal(providing_args=["target", "key"])