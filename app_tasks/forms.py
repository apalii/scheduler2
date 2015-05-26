__author__ = 'apalii'
from app_tasks.models import Task, Comment
import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget

# forms.Form  /  forms.ModelForm
class CommentForm(forms.Form):
    comment = forms.CharField(max_length=800, widget=forms.TextInput(attrs={'class': 'form-control'}))
    """class Meta:
        model = Comment
        fields = ['comment']
        exclude = ['some_filed']
        """
'''
    Absentee_Owned = forms.CharField(required=False,
                                     max_length=5,
                                     widget=forms.Select(attrs={'class': 'form-control'},
                                     choices=(('done', ''),('yes', 'Yes'),('no', 'No'),)))
'''
class StatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']

'''
class TaskForm(forms.Form):
    ticket = forms.IntegerField(max_length=6, widget=forms.TextInput(attrs={'class': 'form-control'}))
    #date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today())
    task = forms.CharField(max_length=200,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer = forms.CharField(max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    executor = forms.CharField(required=False, initial='Nobody', max_length=20,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
'''