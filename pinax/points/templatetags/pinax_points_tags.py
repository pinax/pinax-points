import datetime

from django import template

from ..compat import app_cache
from ..models import points_awarded, fetch_top_objects


register = template.Library()


def assert_arg_length(bits):
    if len(bits) not in [4, 6, 7, 9]:
        """
        4: No optional params
        6: limit N
        7: timeframe N UNITS
        9: limit N timeframe N UNITS --or-- timeframe N UNITS limit N
        """
        raise template.TemplateSyntaxError(
            "'{0}' takes exactly three, five, six, or eight arguments (second"
            " argument must be 'as')".format(bits[0])
        )


def assert_has_as(bits):
    if bits[2] != "as":
        raise template.TemplateSyntaxError(
            "Second argument to '{0}' must be 'as'".format(bits[0])
        )


def get_limit(bits):
    limit = None
    if len(bits) == 6 or len(bits) == 9:
        if "limit" != bits[4] and (len(bits) == 9 and "limit" == bits[7]):
            raise template.TemplateSyntaxError(
                "4th or 7th argument to {0} must be 'limit'".format(bits[0])
            )
        if len(bits) == 6 or bits[4] == "limit":
            limit = bits[5]
        else:
            limit = bits[8]
    return limit


def get_time_num_and_unit(bits):
    time_unit = None
    time_num = None
    if len(bits) == 7 or len(bits) == 9:
        if "timeframe" not in [bits[4], bits[6]]:
            raise template.TemplateSyntaxError(
                "4th or 6th argument to {0} must be 'timeframe'".format(bits[0])
            )
        if len(bits) == 7 or bits[4] == "timeframe":
            time_num, time_unit = bits[5], bits[6]
        else:
            time_num, time_unit = bits[7], bits[8]
    return time_unit, time_num


class TopObjectsNode(template.Node):

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()

        assert_arg_length(bits)
        assert_has_as(bits)

        limit = get_limit(bits)
        time_unit, time_num = get_time_num_and_unit(bits)

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
                time_unit: int(time_num)  # @@@ doing this means can't express "7 days" as variables
            })

    def render(self, context):
        limit = None
        model_lookup = self.model.resolve(context)
        incorrect_value = ValueError(
            "'{0}' does not result in a model. Is it correct?".format(model_lookup)
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

        objs = fetch_top_objects(model, self.time_limit)

        if limit is not None:
            objs = objs[:limit]

        context[self.context_var] = objs

        return ""


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
                raise template.TemplateSyntaxError(
                    "Second argument to '{0}' should be 'as'".format(bits[0])
                )
            return cls(bits[1], context_var=bits[3])
        elif len(bits) == 7:
            if bits[2] != "limit" and bits[5] != "as":
                raise template.TemplateSyntaxError(
                    "Second argument to '{0}' should be 'as' and fifth argument should be 'limit".format(bits[0])  # noqa
                )
            return cls(
                bits[1],
                limit_num=bits[3],
                limit_unit=bits[4],
                context_var=bits[6]
            )
        raise template.TemplateSyntaxError("'{0}' takes 1, 3, or 6 arguments.".format(bits[0]))

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
        return str(points)


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


class UserHasVotedNode(template.Node):

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        if len(bits) != 5:
            raise template.TemplateSyntaxError
        if bits[3] != "as":
            raise template.TemplateSyntaxError
        return cls(
            parser.compile_filter(bits[1]),
            parser.compile_filter(bits[2]),
            bits[4]
        )

    def __init__(self, user, obj, varname):
        self.user = user
        self.obj = obj
        self.varname = varname

    def render(self, context):
        user = self.user.resolve(context)
        obj = self.obj.resolve(context)

        vote = points_awarded(source=user, target=obj)

        context[self.varname] = {
            -1: "downvote",
            0: "novote",
            1: "upvote",
        }.get(vote, "badvote")

        return ""


@register.tag
def user_has_voted(parser, token):
    """
    Usage::
        {% user_has_voted user obj as var %}
    """
    return UserHasVotedNode.handle_token(parser, token)
