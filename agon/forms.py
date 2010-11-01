from django import forms

from django.contrib.auth.models import User

from agon.models import award_points


class OneOffPointAwardForm(forms.Form):
    user = forms.ModelChoiceField(User.objects.filter(is_active=True))
    points = forms.IntegerField()
    
    def award(self):
        award_points(self.cleaned_data["user"], self.cleaned_data["points"])
