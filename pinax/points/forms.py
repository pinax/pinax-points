from django import forms

from django.contrib.auth.models import User

from .models import award_points


class OneOffPointAwardForm(forms.Form):
    user = forms.ModelChoiceField(User.objects.filter(is_active=True))
    points = forms.IntegerField()
    reason = forms.CharField(max_length=140)

    def award(self):
        user = self.cleaned_data["user"]
        points = self.cleaned_data["points"]
        reason = self.cleaned_data["reason"]
        award_points(user, points, reason=reason)
