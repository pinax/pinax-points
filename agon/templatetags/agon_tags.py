import datetime

from django import template
from django.db.models.loading import cache as app_cache

from agon.models import points_awarded, get_top_objects


register = template.Library()


class TopObjectsNode(template.Node):
    
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        time_unit = None
        time_num = None
        limit = None
        
        if len(bits) not in [4, 6, 7, 9]:
            """
            4: No optional params
            6: limit N
            7: timeframe N UNITS
            9: limit N timeframe N UNITS --or-- timeframe N UNITS limit N
            """
            raise template.TemplateSyntaxError(
                "%r takes exactly three, five, six, or eight arguments (second"
                " argument must be 'as')" % str(bits[0])
            )
        
        if bits[2] != "as":
            raise template.TemplateSyntaxError(
                "Second argument to %r must be 'as'" % str(bits[0])
            )
        
        if len(bits) == 6 or len(bits) == 9:
            if "limit" != bits[4] and (len(bits) == 9 and "limit" == bits[7]):
                raise template.TemplateSyntaxError(
                    "4th or 7th argument to %r must be 'limit'" % bits[0]
                )
            if len(bits) == 6 or bits[4] == "limit":
                limit = bits[5]
            else:
                limit = bits[8]
        
        if len(bits) == 7 or len(bits) == 9:
            if "timeframe" not in [bits[4], bits[6]]:
                raise template.TemplateSyntaxError(
                    "4th or 6th argument to %r must be 'timeframe'" % bits[0]
                )
            if len(bits) == 7 or bits[4] == "timeframe":
                time_num, time_unit = bits[5], bits[6]
            else:
                time_num, time_unit = bits[7], bits[8]
        
        return cls(bits[1], bits[3], limit, time_num, time_unit)
    
    def __init__(self, model, context_var, limit, time_num, time_unit):
        self.model = template.Variable(model)
        self.context_var = context_var
        
        if limit is None:
            self.limit = None
        else:
            self.limit = template.Variable(limit)
        
        if time_num is None or time_unit is None:
            self.time_limit = None
        else:
            self.time_limit = datetime.timedelta(**{
                time_unit: int(time_num) # @@@ doing this means can't express "7 days" as variables
            })
    
    def render(self, context):
        limit = None
        model_lookup = self.model.resolve(context)
        incorrect_value = ValueError(
            "'%s' does not result in a model. Is it correct?" % model_lookup
        )
        
        try:
            model = app_cache.get_model(*model_lookup.split("."))
        except TypeError:
            raise incorrect_value
        else:
            if model is None:
                raise incorrect_value
        
        if self.limit is not None:
            limit = self.limit.resolve(context)
        
        context[self.context_var] = get_top_objects(
            model,
            limit,
            self.time_limit
        )
        
        return u""


@register.tag
def top_objects(parser, token):
    """
    Usage::
    
        {% top_objects "auth.User" as top_users limit 10 %}
    
    or::
    
        {% top_objects "auth.User" as top_users %}
    
    or::
    
         {% top_objects "auth.User" as top_users limit 10 timeframe 7 days %}
    
    All variations return a queryset of the model passed in with points annotated.
    """
    return TopObjectsNode.handle_token(parser, token)


class PointsForObjectNode(template.Node):
    
    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        if len(bits) == 2:
            return cls(bits[1])
        elif len(bits) == 4:
            # len(bits) == 7 will support interval timeframing
            if bits[2] != "as":
                raise template.TemplateSyntaxError("Second argument to '%s' "
                    "should be 'as'" % bits[0])
            return cls(bits[1], context_var=bits[3])
        elif len(bits) == 7:
            if bits[2] != "limit" and bits[5] != "as":
                raise template.TemplateSyntaxError("Second argument to '%s' "
                    "should be 'as' and fifth argument should be 'limit" % bits[0])
            return cls(
                bits[1],
                limit_num=bits[3],
                limit_unit=bits[4],
                context_var=bits[6]
            )
        raise template.TemplateSyntaxError("'%s' takes 1, 3, or 6 arguments." % bits[0])
    
    def __init__(self, obj, context_var=None, limit_num=None, limit_unit=None):
        self.obj = template.Variable(obj)
        self.context_var = context_var
        self.limit_num = limit_num
        self.limit_unit = limit_unit
    
    def render(self, context):
        obj = self.obj.resolve(context)
        
        since = None
        if self.limit_num is not None and self.limit_unit is not None:
            since = datetime.datetime.now() - datetime.timedelta(
                **{self.limit_unit: int(self.limit_num)}
            )
        
        points = points_awarded(obj, since=since)
        
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
    
    or
        
        {% points_for_object user limit 7 days as points %}
    """
    return PointsForObjectNode.handle_token(parser, token)
