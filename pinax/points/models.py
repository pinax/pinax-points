import datetime
import itertools

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction, IntegrityError
from django.utils.encoding import python_2_unicode_compatible

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from . import signals
from .compat import GenericForeignKey


ALLOW_NEGATIVE_TOTALS = getattr(settings, "PINAX_POINTS_ALLOW_NEGATIVE_TOTALS", True)


@python_2_unicode_compatible
class PointValue(models.Model):
    """
    Stores a key and its point value. Simple.
    """

    key = models.CharField(max_length=255)
    value = models.IntegerField()

    @classmethod
    def create(cls, key, value):
        # simple wrapper in-case creation needs to be wrapped
        cls._default_manager.create(key=key, value=value)

    def __str__(self):
        return "{0} points for {1}".format(self.value, self.key)


@python_2_unicode_compatible
class AwardedPointValue(models.Model):
    """
    Stores a single row for each time a point value is awarded. Can be used
    as an audit trail of when point values were awarded to targets.
    """

    # object association (User is special-cased as it's a common case)
    target_user = models.ForeignKey(User, null=True, related_name="awardedpointvalue_targets")
    target_content_type = models.ForeignKey(ContentType, null=True, related_name="awardedpointvalue_targets")  # noqa
    target_object_id = models.IntegerField(null=True)
    target_object = GenericForeignKey("target_content_type", "target_object_id")

    value = models.ForeignKey(PointValue, null=True)

    reason = models.CharField(max_length=140)
    points = models.IntegerField()

    # object association (User is special-cased as it's a common case)
    source_user = models.ForeignKey(User, null=True, related_name="awardedpointvalue_sources")
    source_content_type = models.ForeignKey(ContentType, null=True, related_name="awardedpointvalue_sources")  # noqa
    source_object_id = models.IntegerField(null=True)
    source_object = GenericForeignKey("source_content_type", "source_object_id")

    timestamp = models.DateTimeField(default=datetime.datetime.now)

    @classmethod
    def points_awarded(cls, **lookup_params):
        qs = cls._default_manager.filter(**lookup_params)
        p = qs.aggregate(models.Sum("points")).get("points__sum", 0)
        return 0 if p is None else p

    @property
    def target(self):
        return self.target_user or self.target_object

    @property
    def source(self):
        return self.source_user or self.source_object

    def __str__(self):
        val = self.value
        if self.value is None:
            val = "{0} points".format(self.points)
        return "{0} awarded to {1}".format(val, self.target)


class TargetStat(models.Model):
    """
    Stores a single row for each target and their stats (points, position and
    level).
    """

    # object association (User is special-cased as it's a common case)
    target_user = models.OneToOneField(User, null=True, related_name="targetstat_targets")
    target_content_type = models.ForeignKey(ContentType, null=True, related_name="targetstat_targets")  # noqa
    target_object_id = models.IntegerField(null=True)
    target_object = GenericForeignKey("target_content_type", "target_object_id")

    points = models.IntegerField(default=0)
    position = models.PositiveIntegerField(null=True)
    level = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [(
            "target_content_type",
            "target_object_id",
        )]

    @classmethod
    def update_points(cls, given, lookup_params):
        return cls._default_manager.filter(**lookup_params).update(
            points=models.F("points") + given,
        )

    @classmethod
    def update_positions(cls, point_range=None):
        queryset = cls._default_manager.order_by("-points")

        if point_range is not None:
            # ensure point_range is always [0] < [1]
            if point_range[0] > point_range[1]:
                point_range = (point_range[1], point_range[0])
            all_target_stats = queryset.filter(points__range=point_range)
            position = queryset.filter(points__gt=point_range[1]).count()
        else:
            all_target_stats = queryset
            position = 0

        grouped_target_stats = itertools.groupby(all_target_stats, lambda x: x.points)
        prev_group_len = 0

        for points, target_stats in grouped_target_stats:
            position += prev_group_len + 1
            target_stats = list(target_stats)
            prev_group_len = len(target_stats) - 1
            pks = []
            for target_stat in target_stats:
                pks.append(target_stat.pk)
            cls._default_manager.filter(pk__in=pks).update(position=position)

    @property
    def target(self):
        """
        Abstraction to getting the target object of this stat object.
        """
        if self.target_user_id:
            return self.target_user
        else:
            return self.target_object

    @property
    def source(self):
        """
        Match the ``target`` abstraction so the interface is consistent.
        """
        return self.source_object


def get_points(key):
    point_value = None
    if isinstance(key, int) and not isinstance(key, bool):
        points = key
    else:
        try:
            point_value = PointValue.objects.get(key=key)
            points = point_value.value
        except PointValue.DoesNotExist:
            raise ImproperlyConfigured("PointValue for '{0}' does not exist".format(key))
    return point_value, points


def award_points(target, key, reason="", source=None):
    """
    Awards target the point value for key.  If key is an integer then it's a
    one off assignment and should be interpreted as the actual point value.
    """
    point_value, points = get_points(key)

    if not ALLOW_NEGATIVE_TOTALS:
        total = points_awarded(target)
        if total + points < 0:
            reason = reason + "(floored from {0} to 0)".format(points)
            points = -total

    apv = AwardedPointValue(points=points, value=point_value, reason=reason)
    if isinstance(target, User):
        apv.target_user = target
        lookup_params = {
            "target_user": target
        }
    else:
        apv.target_object = target
        lookup_params = {
            "target_content_type": apv.target_content_type,
            "target_object_id": apv.target_object_id,
        }

    if source is not None:
        if isinstance(source, User):
            apv.source_user = source
        else:
            apv.source_object = source

    apv.save()

    if not TargetStat.update_points(points, lookup_params):
        try:
            sid = transaction.savepoint()
            TargetStat._default_manager.create(
                **dict(lookup_params, points=points)
            )
            transaction.savepoint_commit(sid)
        except IntegrityError:
            transaction.savepoint_rollback(sid)
            TargetStat.update_points(points, lookup_params)

    signals.points_awarded.send(
        sender=target.__class__,
        target=target,
        key=key,
        points=points,
        source=source
    )

    new_points = points_awarded(target)
    old_points = new_points - points

    TargetStat.update_positions((old_points, new_points))

    return apv


def points_awarded(target=None, source=None, since=None):
    """
    Determine out how many points the given target has recieved.
    """

    lookup_params = {}

    if target is not None:
        if isinstance(target, User):
            lookup_params["target_user"] = target
        else:
            lookup_params.update({
                "target_content_type": ContentType.objects.get_for_model(target),
                "target_object_id": target.pk,
            })
    if source is not None:
        if isinstance(source, User):
            lookup_params["source_user"] = source
        else:
            lookup_params.update({
                "source_content_type": ContentType.objects.get_for_model(source),
                "source_object_id": source.pk,
            })

    if since is None:
        if target is not None and source is None:
            try:
                return TargetStat.objects.get(**lookup_params).points
            except TargetStat.DoesNotExist:
                return 0
        else:
            return AwardedPointValue.points_awarded(**lookup_params)
    else:
        lookup_params["timestamp__gte"] = since
        return AwardedPointValue.points_awarded(**lookup_params)


def fetch_top_objects(model, time_limit):
    queryset = model.objects.all()

    if time_limit is None:
        if issubclass(model, User):
            queryset = queryset.annotate(
                num_points=models.Sum("targetstat_targets__points")
            )
        else:
            raise NotImplementedError("Only auth.User is supported at this time.")
    else:
        since = datetime.datetime.now() - time_limit
        if issubclass(model, User):
            queryset = queryset.filter(
                awardedpointvalue_targets__timestamp__gte=since
            ).annotate(
                num_points=models.Sum("awardedpointvalue_targets__points")
            )
        else:
            raise NotImplementedError("Only auth.User is supported at this time.")

    queryset = queryset.filter(num_points__isnull=False).order_by("-num_points")

    return queryset


class VoteError(Exception):
    pass


def record_vote(user, target, vote):
    # @@@ WARNING: this code is not safe concurrently

    # fetch the current vote for user on target (vote should only ever be -1, 0 or 1)
    existing = points_awarded(source=user, target=target)

    # ensure we have valid data
    if existing not in (-1, 0, 1):
        raise ValueError("something has gone wrong with voting")
    if vote not in (-1, 0, 1):
        raise ValueError("invalid vote value")

    # ensure we won't do something dumb
    if existing == -1 and vote == -1:
        raise VoteError("cannot downvote when already downvoted")
    if existing == 1 and vote == 1:
        raise VoteError("cannot upvote when already upvoted")

    points = {
        (1, 0): -1,
        (1, -1): -2,
        (0, 1): 1,
        (0, 0): 0,
        (0, -1): -1,
        (-1, 1): 2,
        (-1, 0): 1,
    }[(existing, vote)]

    if points:
        award_points(target, points, source=user)
        return points_awarded(target=target)
