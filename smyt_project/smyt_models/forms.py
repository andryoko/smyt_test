from django import forms
from django.forms.models import fields_for_model
from django.contrib.admin import widgets
from django.forms.extras.widgets import SelectDateWidget

def generate_form_model(model):
  fields = fields_for_model(model)

  for name, field in fields.items():
    if isinstance(field, forms.DateField):
      field.widget.attrs['class'] = 'datepicker'

  form = type('%sForm' % model.__name__, (forms.Form,), fields)
  return form