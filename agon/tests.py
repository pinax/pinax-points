from threading import Thread

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase, TransactionTestCase

from django.contrib.auth.models import User, Group

from agon.models import TargetStat, PointValue
from agon.models import award_points, points_awarded


def skipIf(cond):
    def inner(func):
        if not cond:
            return func
    return inner


class BasePointsTestCase(object):
    
    def tearDown(self):
        if hasattr(settings, "AGON_POINT_VALUES"):
            del settings.AGON_POINT_VALUES
    
    def setup_users(self, N):
        self.users = [
            User.objects.create_user(
                "user_%d" % i, "user_%d@example.com" % i, str(i)
            ) for i in xrange(N)
        ]
    
    def setup_points(self, value):
        for k, v in value.iteritems():
            PointValue.create(key=k, value=v)


class PointsTestCase(BasePointsTestCase, TestCase):
    
    def test_improperly_configured(self):
        self.setup_users(1)
        user = self.users[0]
        try:
            award_points(user, "JOINED_SITE")
        except ImproperlyConfigured, e:
            self.assertEqual(str(e), "PointValue for 'JOINED_SITE' does not exist")
    
    def test_simple_user_point_award(self):
        self.setup_users(1)
        self.setup_points({
            "JOINED_SITE": 1,
        })
        user = self.users[0]
        award_points(user, "JOINED_SITE")
        self.assertEqual(points_awarded(user), 1)
    
    def test_simple_generic_point_award(self):
        self.setup_points({
            "ATE_SOMETHING": 5,
        })
        group = Group.objects.create(name="Dwarfs")
        award_points(group, "ATE_SOMETHING")
        self.assertEqual(points_awarded(group), 5)


class PointsTransactionTestCase(BasePointsTestCase, TransactionTestCase):
    
    @skipIf(settings.DATABASE_ENGINE == "sqlite3")
    def test_concurrent_award(self):
        self.setup_users(1)
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


class PositionsTestCase(BasePointsTestCase, TestCase):
    
    def test_no_range(self):
        self.setup_users(9)
        
        TargetStat.objects.create(target_user=self.users[0], points=100)
        TargetStat.objects.create(target_user=self.users[1], points=90)
        TargetStat.objects.create(target_user=self.users[2], points=85)
        TargetStat.objects.create(target_user=self.users[3], points=70)
        TargetStat.objects.create(target_user=self.users[4], points=70)
        TargetStat.objects.create(target_user=self.users[5], points=60)
        TargetStat.objects.create(target_user=self.users[6], points=50)
        TargetStat.objects.create(target_user=self.users[7], points=10)
        TargetStat.objects.create(target_user=self.users[8], points=5)
        
        TargetStat.update_positions()
        
        self.assertEqual(
            [(p.position, p.points) for p in TargetStat.objects.order_by("position")],
            [(1, 100), (2, 90), (3, 85), (4, 70), (4, 70), (6, 60), (7, 50), (8, 10), (9, 5)]
        )
    
    def test_up_range(self):
        self.setup_users(9)
        
        TargetStat.objects.create(target_user=self.users[0], points=100, position=1)
        TargetStat.objects.create(target_user=self.users[1], points=90, position=2)
        TargetStat.objects.create(target_user=self.users[2], points=85, position=3)
        TargetStat.objects.create(target_user=self.users[3], points=70, position=4)
        TargetStat.objects.create(target_user=self.users[4], points=70, position=4)
        TargetStat.objects.create(target_user=self.users[5], points=60, position=6)
        TargetStat.objects.create(target_user=self.users[6], points=61, position=7)
        TargetStat.objects.create(target_user=self.users[7], points=10, position=8)
        TargetStat.objects.create(target_user=self.users[8], points=5, position=9)
        
        # user 6 scored 11 points
        TargetStat.update_positions((50, 61))
        
        self.assertEqual(
            [(p.position, p.points) for p in TargetStat.objects.order_by("position")],
            [(1, 100), (2, 90), (3, 85), (4, 70), (4, 70), (6, 61), (7, 60), (8, 10), (9, 5)]
        )
    
    def test_down_range(self):
        self.setup_users(9)
        
        TargetStat.objects.create(target_user=self.users[0], points=100, position=1)
        TargetStat.objects.create(target_user=self.users[1], points=90, position=2)
        TargetStat.objects.create(target_user=self.users[2], points=69, position=3)
        TargetStat.objects.create(target_user=self.users[3], points=70, position=4)
        TargetStat.objects.create(target_user=self.users[4], points=70, position=4)
        TargetStat.objects.create(target_user=self.users[5], points=60, position=6)
        TargetStat.objects.create(target_user=self.users[6], points=50, position=7)
        TargetStat.objects.create(target_user=self.users[7], points=10, position=8)
        TargetStat.objects.create(target_user=self.users[8], points=5, position=9)
        
        # user 6 scored 11 points
        TargetStat.update_positions((85, 69))
        
        self.assertEqual(
            [(p.position, p.points) for p in TargetStat.objects.order_by("position")],
            [(1, 100), (2, 90), (3, 70), (3, 70), (5, 69), (6, 60), (7, 50), (8, 10), (9, 5)]
        )


class TopObjectsTagTestCase(TestCase):
    
    def test_no_args(self):
        try:
            t = Template("{% load agon_tags %}{% top_objects %}")
        except TemplateSyntaxError, e:
            self.assertEqual(str(e), "'top_objects' takes exactly three or six arguments (second argument must be 'as')")
    
    def test_typo_as(self):
        """
        The Alex test.
        """
        try:
            t = Template('{% load agon_tags %}{% top_objects "auth.User" a top_users %}')
        except TemplateSyntaxError, e:
            self.assertEqual(str(e), "Second argument to 'top_objects' must be 'as'")
    
    def test_bad_model_arg(self):
        t = Template('{% load agon_tags %}{% top_objects "auth" as top_users %}')
        try:
            t.render(Context({}))
        except ValueError, e:
            self.assertEqual(str(e), "'auth' does not result in a model. Is it correct?")
        
        t = Template('{% load agon_tags %}{% top_objects "auth.U" as top_users %}')
        try:
            t.render(Context({}))
        except ValueError, e:
            self.assertEqual(str(e), "'auth.U' does not result in a model. Is it correct?")



