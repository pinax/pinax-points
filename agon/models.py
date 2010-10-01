import datetime
import itertools

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction, IntegrityError

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from agon import signals


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
    
    def __unicode__(self):
        return u"%s points for %s" % (self.value, self.key)


class AwardedPointValue(models.Model):
    """
    Stores a single row for each time a point value is awarded. Can be used
    as an audit trail of when point values were awarded to targets.
    """
    
    # object association (User is special-cased as it's a common case)
    target_user = models.ForeignKey(User, null=True)
    target_content_type = models.ForeignKey(ContentType, null=True)
    target_object_id = models.IntegerField(null=True)
    target_object = generic.GenericForeignKey("target_content_type", "target_object_id")
    
    value = models.ForeignKey(PointValue)
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    
    @property
    def target(self):
        return self.target_user or self.target_object
                
    def __unicode__(self):
        return u"%s awarded to %s" % (self.value, self.target)


class TargetStat(models.Model):
    """
    Stores a single row for each target and their stats (points, position and
    level).
    """
    
    # object association (User is special-cased as it's a common case)
    target_user = models.OneToOneField(User, null=True)
    target_content_type = models.ForeignKey(ContentType, null=True)
    target_object_id = models.IntegerField(null=True)
    target_object = generic.GenericForeignKey("target_content_type", "target_object_id")
    
    points = models.IntegerField(default=0)
    position = models.PositiveIntegerField(null=True)
    level = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = [("target_content_type", "target_object_id")]
    
    @classmethod
    def update_points(cls, given, lookup_params):
        return cls._default_manager.filter(**lookup_params).update(
            points = models.F("points") + given,
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


def award_points(target, key):
    """
    Awards target the point value for key
    """
    try:
        point_value = PointValue.objects.get(key=key)
    except PointValue.DoesNotExist:
        raise ImproperlyConfigured("PointValue for '%s' does not exist" % key)
    else:
        points_given = point_value.value
    
    apv = AwardedPointValue(value=point_value)
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
    apv.save()
    
    if not TargetStat.update_points(points_given, lookup_params):
        try:
            sid = transaction.savepoint()
            TargetStat._default_manager.create(
                **dict(lookup_params, points=points_given)
            )
            transaction.savepoint_commit(sid)
        except IntegrityError, e:
            transaction.savepoint_rollback(sid)
            TargetStat.update_points(points_given, lookup_params)
    
    signals.points_awarded.send(sender=target.__class__, target=target, key=key)
    
    new_points = points_awarded(target)
    old_points = new_points - points_given
    
    TargetStat.update_positions((old_points, new_points))


def points_awarded(target):
    if isinstance(target, User):
        lookup_params = {
            "target_user": target,
        }
    else:
        lookup_params = {
            "target_content_type": ContentType.objects.get_for_model(target),
            "target_object_id": target.pk,
        }
    try:
        return TargetStat.objects.get(**lookup_params).points
    except TargetStat.DoesNotExist:
        return 0
