from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from smyt_models.models import yaml_models
from django.forms.models import model_to_dict, save_instance
import forms
import datetime
from django.db import models
from django.http import Http404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect

def prepare_context(model_name):
  current_model = None
  models_list = []
  for model in yaml_models:

    models_list.append({
      'name': model.__name__,
      'title': model._meta.verbose_name_plural,
    })

    if model.__name__ == model_name:
      current_model = model

  context = {'models': models_list}

  if current_model:
    fields = [field for field in current_model._meta.fields]

    objects = []
    for obj in current_model.objects.all():
      dct = model_to_dict(obj)
      row = []
      for fld in fields:
        value = dct.get(fld.name)
        field_type = 'char'
        if isinstance(value, datetime.date):
          value = '%02d/%02d/%d' % (value.day, value.month, value.year)
          field_type = 'date'
        elif isinstance(value, int):
          field_type = 'int'

        row.append({'id':fld.name, 'value':value, 'type': field_type})
      objects.append(row)

    context['objects'] = objects
    context['current_model'] = current_model.__name__
    context['current_model_class'] = current_model
    context['fields'] = fields

  return context

def index(request):
  model_name = request.GET.get('model') or request.POST.get('model')
  context = prepare_context(model_name)
  current_model = context.get('current_model_class')
  form_model = forms.generate_form_model(current_model) if current_model else None

  if request.method == 'GET' and current_model:
    context['form'] = form_model() if form_model else None
  elif request.method == 'POST':
    assert current_model and form_model
    # create a form instance and populate it with data from the request:
    form = form_model(request.POST)
    # check whether it's valid:
    if form.is_valid():
      # save new instance
      instance = current_model()
      save_instance(form, instance)
      # refresh page
      return HttpResponseRedirect('/?model=%s' % model_name)
    else:
      context['form'] = form

  template = loader.get_template('smyt_models/index.html')
  context = RequestContext(request, context)
  return HttpResponse(template.render(context))

@csrf_protect
def edit_cell(request):
  if request.method == 'POST':
    model_name = request.POST.get('model')
    rowid = request.POST.get('rowid')
    colid = request.POST.get('colid')
    value = request.POST.get('value')
    model = None

    for cls in yaml_models:
      if cls.__name__ == model_name:
        model = cls
        break

    try:
      object = model.objects.get(pk=rowid)
    except model.DoesNotExist:
      Http404("Object does not exist")

    field = model._meta.get_field_by_name(colid)[0]
    if isinstance(field, models.IntegerField):
      value = int(value)
    elif isinstance(field, models.DateField):
      sd, sm, sy = value.split('/')
      value = datetime.date(int(sy), int(sm), int(sd))

    setattr(object, colid, value)
    object.save(update_fields=[colid])
    return HttpResponse('success')
  else:
    Http404("Method does not exist")