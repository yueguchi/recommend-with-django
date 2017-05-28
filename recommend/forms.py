from django import forms
from recommend.models import Users

class UsersForm(forms.Form):
    users = forms.ChoiceField(label='購入者',widget=forms.Select,choices=Users.objects.all().values('name'))
