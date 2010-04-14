from threading import Thread

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from django.contrib.auth.models import User

from agon.models import award_points, points_awarded


def skipIf(cond):
    def inner(func):
        if not cond:
            return func
    return inner


class PointsTestCase(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user("user_%d" % i, "user_%d@example.com" % i, str(i))
            for i in xrange(1)
        ]
    
    def tearDown(self):
        if hasattr(settings, "AGON_POINT_VALUES"):
            del settings.AGON_POINT_VALUES
    
    def setup_points(self, value):
        settings.AGON_POINT_VALUES = value
    
    def test_improperly_configured(self):
        user = self.users[0]
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
        user = self.users[0]
        award_points(user, "JOINED_SITE")
        self.assertEqual(points_awarded(user), 1)
    
    @skipIf(settings.DATABASE_ENGINE == "sqlite3")
    def test_concurrent_award(self):
        user = self.users[0]
        self.setup_points({
            "INVITED_USER": 10,
        })
        def run():
            award_points(user, "INVITED_USER")
        threads = []
        for i in xrange(5):
            t = Thread(target=run)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(points_awarded(user), 50)
