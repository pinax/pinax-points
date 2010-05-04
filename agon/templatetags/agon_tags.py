from django import template
from django.db.models.loading import cache as app_cache

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from agon.models import TargetStat, points_awarded


register = template.Library()


class TopObjectsNode(template.Node):
    
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        
        if len(bits) != 4 and len(bits) != 6:
            raise template.TemplateSyntaxError("%r takes exactly three or six "
                "arguments (second argument must be 'as')" % str(bits[0]))
        if bits[2] != "as":
            raise template.TemplateSyntaxError("Second argument to %r must be "
                "'as'" % str(bits[0]))
        if len(bits) == 6:
            if bits[4] != "limit":
                raise template.TemplateSyntaxError("Fourth argument to %r must be "
                    "'limit'" % bits[0])
            limit = bits[5]
        else:
            limit = None
        return cls(bits[1], bits[3], limit)
    
    def __init__(self, model, context_var, limit):
        self.model = template.Variable(model)
        self.context_var = context_var
        if limit is None:
            self.limit = None
        else:
            self.limit = template.Variable(limit)
    
    def render(self, context):
        limit = None
        model_lookup = self.model.resolve(context)
        incorrect_value = ValueError("'%s' does not result in a model. Is it "
            "correct?" % model_lookup)
        try:
            model = app_cache.get_model(*model_lookup.split("."))
        except TypeError:
            raise incorrect_value
        else:
            if model is None:
                raise incorrect_value
        queryset = TargetStat.objects.order_by("position")
        if issubclass(model, User):
            queryset = queryset.exclude(target_user=None)
            queryset = queryset.select_related("target_user")
        else:
            # @@@ currently when user code using this template tag needs to
            # call target it will perform a query (we could be slightly
            # smarter and when a limit is given we could pre-populate the
            # underlying cache with a single query using __in)
            ct = ContentType.objects.get_for_model(model)
            queryset.filter(target_content_type=ct)
        
        if self.limit is not None:
            limit = self.limit.resolve(context)
            queryset = queryset[:limit]
        context[self.context_var] = queryset
        return u""


@register.tag
def top_objects(parser, token):
    """
    Usage::
    
        {% top_objects "auth.User" as top_users limit 10 %}
    
    or::
    
        {% top_objects "auth.User" as top_users %}
    """
    return TopObjectsNode.handle_token(parser, token)


class PointsForObjectNode(template.Node):
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        if len(bits) == 2:
            return cls(bits[1])
        elif len(bits) == 4:
            if bits[2] != "as":
                raise template.TemplateSyntaxError("Second argument to %r "
                    "should be 'as'" % bits[0])
            return cls(bits[1], bits[3])
        raise template.TemplateSyntaxError("%r takes 1 or 3 arguments." % bits[0])
    
    def __init__(self, obj, context_var=None):
        self.obj = template.Variable(obj)
        self.context_var = context_var
    
    def render(self, context):
        obj = self.obj.resolve(context)
        points = points_awarded(obj)
        if self.context_var is not None:
            context[self.context_var] = points
            return ""
        return unicode(points)

@register.tag
def points_for_object(parser, token):
    """
    Gets the current points for an object, usage:
        
        {% points_for_object user %}
    
    or
        
        {% points_for_object user as points %}
    """
    return PointsForObjectNode.handle_token(parser, token)
