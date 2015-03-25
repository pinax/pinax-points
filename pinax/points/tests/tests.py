from datetime import timedelta
# from threading import Thread

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase
# from django.test import TestCase, TransactionTestCase

from django.contrib.auth.models import User, Group

from pinax.points.models import TargetStat, PointValue, AwardedPointValue
from pinax.points.models import award_points, points_awarded


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
                "user_{0}".format(i), "user_{0}@example.com".format(i), str(i)
            ) for i in range(N)
        ]

    def setup_points(self, value):
        for key in value:
            PointValue.create(key=key, value=value[key])


class PointsTestCase(BasePointsTestCase, TestCase):

    def test_improperly_configured_point_value(self):
        self.setup_users(1)
        user = self.users[0]
        try:
            award_points(user, "JOINED_SITE")
        except ImproperlyConfigured as e:
            self.assertEqual(str(e), "PointValue for 'JOINED_SITE' does not exist")

    def test_improperly_configured(self):
        self.setup_users(1)
        user = self.users[0]
        try:
            award_points(user, True)
        except ImproperlyConfigured as e:
            self.assertEqual(
                str(e),
                "PointValue for 'True' does not exist"
            )

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

    def test_user_one_off_point_award(self):
        self.setup_users(1)
        user = self.users[0]
        award_points(user, 500)
        self.assertEqual(points_awarded(user), 500)

    def test_generic_one_off_point_award(self):
        group = Group.objects.create(name="Dwarfs")
        award_points(group, 500)
        self.assertEqual(points_awarded(group), 500)

    def test_user_one_off_point_award_value_is_null(self):
        self.setup_users(1)
        user = self.users[0]
        award_points(user, 500)
        apv = AwardedPointValue.objects.all()[0]
        self.assertTrue(apv.value is None)

    def test_generic_one_off_point_award_value_is_null(self):
        group = Group.objects.create(name="Dwarfs")
        award_points(group, 500)
        apv = AwardedPointValue.objects.all()[0]
        self.assertTrue(apv.value is None)

    def test_unicode_simple_user_point_award(self):
        self.setup_users(1)
        self.setup_points({
            "JOINED_SITE": 1,
        })
        user = self.users[0]
        award_points(user, "JOINED_SITE")
        apv = AwardedPointValue.objects.all()[0]
        self.assertEqual(
            str(apv),
            "{0} points for {1} awarded to {2}".format(1, "JOINED_SITE", str(user))
        )

    def test_unicode_simple_generic_point_award(self):
        self.setup_points({
            "ATE_SOMETHING": 5,
        })
        group = Group.objects.create(name="Dwarfs")
        award_points(group, "ATE_SOMETHING")
        apv = AwardedPointValue.objects.all()[0]
        self.assertEqual(
            str(apv),
            "{0} points for {1} awarded to {2}".format(5, "ATE_SOMETHING", str(group))
        )

    def test_unicode_user_one_off_point_award(self):
        self.setup_users(1)
        user = self.users[0]
        award_points(user, 500)
        apv = AwardedPointValue.objects.all()[0]
        self.assertEqual(
            str(apv),
            "{0} points awarded to {1}".format(500, str(user))
        )

    def test_unicode_generic_one_off_point_award(self):
        group = Group.objects.create(name="Dwarfs")
        award_points(group, 500)
        apv = AwardedPointValue.objects.all()[0]
        self.assertEqual(
            str(apv),
            "{0} points awarded to {1}".format(500, str(group))
        )


# class NegativePointsTestCase(BasePointsTestCase, TestCase):

#     def test_negative_totals_floored(self):
#         group = Group.objects.create(name="Dwarfs")
#         award_points(group, 500)
#         self.assertEqual(points_awarded(group), 500)
#         award_points(group, -700)
#         self.assertEqual(points_awarded(group), 0)

#     def test_negative_totals_unfloored(self):
#         group = Group.objects.create(name="Dwarfs")
#         award_points(group, 500)
#         self.assertEqual(points_awarded(group), 500)
#         award_points(group, -700)
#         self.assertEqual(points_awarded(group), -200)


# @@@ Determine how to get this executing again
# class PointsTransactionTestCase(BasePointsTestCase, TransactionTestCase):

#     def test_concurrent_award(self):
#         self.setup_users(1)
#         user = self.users[0]
#         self.setup_points({
#             "INVITED_USER": 10,
#         })

#         def run():
#             award_points(user, "INVITED_USER")
#         threads = []
#         for i in range(5):
#             t = Thread(target=run)
#             threads.append(t)
#             t.start()
#         for t in threads:
#             t.join()
#         self.assertEqual(points_awarded(user), 50)


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

    def test_no_args_with_target_objects(self):
        self.setup_points({
            "ATE_SOMETHING": 5,
            "DRANK_SOMETHING": 10,
            "WENT_TO_SLEEP": 4
        })
        points = PointValue.objects.all()

        TargetStat.objects.create(target_object=points[0], points=100)
        TargetStat.objects.create(target_object=points[1], points=90)
        TargetStat.objects.create(target_object=points[2], points=90)

        TargetStat.update_positions()

        self.assertEqual(
            [(p.position, p.points) for p in TargetStat.objects.order_by("position")],
            [(1, 100), (2, 90), (2, 90)]
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

    def test_up_range_with_target_objects(self):
        self.setup_points({
            "ATE_SOMETHING": 5,
            "DRANK_SOMETHING": 10,
            "WENT_TO_SLEEP": 4
        })
        points = PointValue.objects.all()

        TargetStat.objects.create(target_object=points[0], points=100, position=1)
        TargetStat.objects.create(target_object=points[1], points=90, position=2)
        TargetStat.objects.create(target_object=points[2], points=95, position=3)

        TargetStat.update_positions((90, 95))

        self.assertEqual(
            [(p.position, p.points) for p in TargetStat.objects.order_by("position")],
            [(1, 100), (2, 95), (3, 90)]
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

    def test_down_range_with_target_objects(self):
        self.setup_points({
            "ATE_SOMETHING": 5,
            "DRANK_SOMETHING": 10,
            "WENT_TO_SLEEP": 4
        })
        points = PointValue.objects.all()

        TargetStat.objects.create(target_object=points[0], points=100, position=1)
        TargetStat.objects.create(target_object=points[1], points=90, position=2)
        TargetStat.objects.create(target_object=points[2], points=95, position=3)

        TargetStat.update_positions((95, 90))

        self.assertEqual(
            [(p.position, p.points) for p in TargetStat.objects.order_by("position")],
            [(1, 100), (2, 95), (3, 90)]
        )


class TargetObjectsTestCase(BasePointsTestCase, TestCase):

    def test_exception_assiging_object_to_user(self):
        self.setup_points({
            "ATE_SOMETHING": 5,
            "DRANK_SOMETHING": 10
        })
        points = PointValue.objects.all()

        self.assertRaises(
            ValueError,
            lambda: TargetStat.objects.create(target_user=points[0], points=100)
        )


class TopObjectsTagTestCase(BasePointsTestCase, TestCase):

    def setUp(self):
        self.setup_users(5)
        self.setup_points({
            "TEST_THIS_TAG": 10,
        })
        group = Group.objects.create(name="Eldarion")
        user = self.users[0]
        # award 40 now and 10 set three weeks ago
        award_points(group, "TEST_THIS_TAG")
        apv = award_points(group, "TEST_THIS_TAG")
        apv.timestamp = apv.timestamp - timedelta(days=14)
        apv.save()
        award_points(user, "TEST_THIS_TAG")
        award_points(user, "TEST_THIS_TAG")
        award_points(user, "TEST_THIS_TAG")
        award_points(user, "TEST_THIS_TAG")
        apv = award_points(user, "TEST_THIS_TAG")
        apv.timestamp = apv.timestamp - timedelta(days=21)
        apv.save()

    def test_no_args(self):
        try:
            Template("{% load pinax_points_tags %}{% top_objects %}")
        except TemplateSyntaxError as e:
            self.assertEqual(
                str(e),
                "'top_objects' takes exactly three, five, six, or eight arguments (second argument must be 'as')"  # noqa
            )

    def test_typo_as(self):
        """
        The Alex test.
        """
        try:
            Template('{% load pinax_points_tags %}{% top_objects "auth.User" a top_users %}')
        except TemplateSyntaxError as e:
            self.assertEqual(str(e), "Second argument to 'top_objects' must be 'as'")

    # Exceptions will vary depending on Django version
    # def test_bad_model_arg(self):
    #     t = Template('{% load pinax_points_tags %}{% top_objects "auth" as top_users %}')
    #     try:
    #         t.render(Context({}))
    #     except ValueError as e:
    #         self.assertEqual(str(e), "need more than 1 value to unpack")

    #     t = Template('{% load pinax_points_tags %}{% top_objects "auth.U" as top_users %}')
    #     try:
    #         t.render(Context({}))
    #     except ValueError as e:
    #         self.assertEqual(str(e), "'auth.U' does not result in a model. Is it correct?")

    def test_should_return_annotated_queryset(self):
        t = Template("""{% load pinax_points_tags %}{% top_objects "auth.User" as top_users %}""")
        c = Context({})
        t.render(c)
        self.assertEquals(c["top_users"].model, User.objects.all().model)

    def test_should_return_annotated_queryset_with_limit(self):
        t = Template("""{% load pinax_points_tags %}{% top_objects "auth.User" as top_users limit 3 %}""")
        c = Context({})
        t.render(c)
        self.assertEquals(c["top_users"].model, User.objects.all().model)

    def test_should_return_annotated_queryset_non_user_model(self):
        t = Template("""{% load pinax_points_tags %}{% top_objects "auth.Group" as top_users %}""")
        c = Context({})
        try:
            t.render(c)
            self.fail("Should have raised a NotImplementedError!")
        except NotImplementedError:
            pass

    def test_should_return_annotated_queryset_has_points(self):
        t = Template("""{% load pinax_points_tags %}{% top_objects "auth.User" as top_users %}""")
        c = Context({})
        t.render(c)
        self.assertEquals(c["top_users"][0].num_points, 50)

    def test_should_return_annotated_queryset_has_points_with_limit(self):
        t = Template("""{% load pinax_points_tags %}{% top_objects "auth.User" as top_users limit 3 %}""")
        c = Context({})
        t.render(c)
        self.assertEquals(c["top_users"][0].num_points, 50)

    def test_should_return_annotated_queryset_non_user_model_has_points(self):
        t = Template("""{% load pinax_points_tags %}{% top_objects "auth.Group" as top_users %}""")
        c = Context({})
        try:
            t.render(c)
            self.fail("Should have raised a NotImplementedError!")
        except NotImplementedError:
            pass

    def test_should_return_annotated_queryset_with_timeframe_has_points(self):
        t = Template("""{% load pinax_points_tags %}{% top_objects "auth.User" as top_users timeframe 7 days %}""")  # noqa
        c = Context({})
        t.render(c)
        self.assertEquals(c["top_users"][0].num_points, 40)

    def test_should_return_annotated_queryset_with_timeframe_non_user_model_has_points(self):
        t = Template("""{% load pinax_points_tags %}{% top_objects "auth.Group" as top_users limit 10 timeframe 7 days %}""")  # noqa
        c = Context({})
        try:
            t.render(c)
            self.fail("Should have raised a NotImplementedError!")
        except NotImplementedError:
            pass


class PointsForObjectTagTestCase(BasePointsTestCase, TestCase):
    """
    points_for_object
    """

    def test_no_args(self):
        try:
            Template("{% load pinax_points_tags %}{% points_for_object %}")
        except TemplateSyntaxError as e:
            self.assertEqual(str(e), "'points_for_object' takes 1, 3, or 6 arguments.")

    def test_type_as(self):
        try:
            self.setup_users(1)
            t = Template('{% load pinax_points_tags %}{% points_for_object user a points %}')
            t.render(Context({"user": self.users[0]}))
        except TemplateSyntaxError as e:
            self.assertEqual(str(e), "Second argument to 'points_for_object' should be 'as'")

    def test_user_object_without_as(self):
        self.setup_users(1)
        award_points(self.users[0], 15)
        t = Template('{% load pinax_points_tags %}{% points_for_object user %} Points')
        self.assertEqual(t.render(Context({"user": self.users[0]})), "15 Points")

    def test_user_object_with_as(self):
        self.setup_users(1)
        award_points(self.users[0], 10)
        t = Template('{% load pinax_points_tags %}{% points_for_object user as points %}{{ points }} Points')  # noqa
        self.assertEqual(t.render(Context({"user": self.users[0]})), "10 Points")

    def test_user_object_with_limit(self):
        self.setup_users(1)
        ap = award_points(self.users[0], 10)
        ap.timestamp = ap.timestamp - timedelta(days=14)
        ap.save()
        award_points(self.users[0], 18)
        t = Template('{% load pinax_points_tags %}{% points_for_object user limit 7 days as points %}{{ points }} Points')  # noqa
        self.assertEqual(t.render(Context({"user": self.users[0]})), "18 Points")

    def test_user_object_with_limit_30_days(self):
        self.setup_users(1)
        ap = award_points(self.users[0], 10)
        ap.timestamp = ap.timestamp - timedelta(days=14)
        ap.save()
        award_points(self.users[0], 18)
        t = Template('{% load pinax_points_tags %}{% points_for_object user limit 30 days as points %}{{ points }} Points')  # noqa
        self.assertEqual(t.render(Context({"user": self.users[0]})), "28 Points")
