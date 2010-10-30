from django.dispatch import Signal


points_awarded = Signal(providing_args=["target", "key", "points", "source"])
