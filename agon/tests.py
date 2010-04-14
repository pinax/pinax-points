from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from django.contrib.auth.models import User

from agon.models import award_points, points_awarded


class PointsTestCase(TestCase):
    
    def setup_points(self, value):
        settings.AGON_POINT_VALUES = value
    
    def test_improperly_configured(self):
        user = User.objects.create_user("brian", "someone@example.com", "abc123")
        try:
            award_points(user, "JOINED_SITE")
        except ImproperlyConfigured, e:
            self.assertEqual(str(e), "You must define 'AGON_POINT_VALUES' in settings")
        self.setup_points({})
        try:
            award_points(user, "JOINED_SITE")
        except ImproperlyConfigured, e:
            self.assertEqual(str(e), "You must define a point value for 'JOINED_SITE'")
    
    def test_simple_user_point_award(self):
        self.setup_points({
            "JOINED_SITE": 1,
        })
        user = User.objects.create_user("brian", "someone@example.com", "abc123")
        award_points(user, "JOINED_SITE")
        self.assertEqual(points_awarded(user), 1)
