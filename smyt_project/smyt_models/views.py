from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from smyt_models.models import yaml_models
import smyt_models.models as app_models
from django.forms.models import model_to_dict, save_instance
import forms
import datetime
from django.db import models
from django.http import Http404
from django.views.decorators.csrf import csrf_protect
import json
from django.core.exceptions import ObjectDoesNotExist


def get_table_rows(model):
  """ Create list of the dictionary with field (id, value, type)."""
  assert model
  fields = [field for field in model._meta.fields]

  objects = []
  for obj in model.objects.all():
    dct = model_to_dict(obj)
    row = []
    for fld in fields:
      value = dct.get(fld.name)
      if isinstance(value, datetime.date):
        value = '%02d/%02d/%d' % (value.day, value.month, value.year)

      row.append({'name':fld.name, 'value':value})
    objects.append(row)
  return objects


def index(request):
  models_list = []
  for model in yaml_models:

    models_list.append({
      'name': model.__name__,
      'title': model._meta.verbose_name_plural,
    })

  context = {'models': models_list}
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

    if not model:
      raise Http404("Model does not exist")

    try:
      object = model.objects.get(pk=rowid)
    except ObjectDoesNotExist:
      raise Http404("Object does not exist")

    field = model._meta.get_field_by_name(colid)[0]
    if not value:
      return HttpResponse('Value is required')
    elif isinstance(field, models.IntegerField):
      try:
        value = int(value)
      except ValueError:
        return HttpResponse('Invalid value type. It should be integer')
    elif isinstance(field, models.DateField):
      sd, sm, sy = value.split('/')
      value = datetime.date(int(sy), int(sm), int(sd))

    setattr(object, colid, value)
    object.save(update_fields=[colid])
    return HttpResponse('success')
  else:
    raise Http404("Method does not exist")


def objects_to_dict(current_model):
  assert current_model

  # create fields description
  fields = []
  for field in current_model._meta.fields:
    field_dict = {
      'name': field.name,
      'title': field.verbose_name,
      'type': 'char'
    }
    if isinstance(field, models.IntegerField) or isinstance(field, models.AutoField):
      field_dict['type'] = 'int'
    elif isinstance(field, models.DateField):
      field_dict['type'] = 'date'

    fields.append(field_dict)

  return {
    'fields': fields,
    'data': get_table_rows(current_model)
  }


@csrf_protect
def get_table(request):
  if request.method == 'POST':
    model_name = request.POST['model']
    current_model = getattr(app_models, model_name, None)
    if current_model:
      # create fields description
      response_data = objects_to_dict(current_model)
    else:
      response_data = {'error':'Invalid model name'}

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")

@csrf_protect
def add_object(request):
  if request.method == 'POST':
    response_data = {}
    model_name = request.POST.get('model', '')
    current_model = getattr(app_models, model_name, None)
    if current_model:
      form_model = forms.generate_form_model(current_model)
      form = form_model(request.POST)
      # check whether it's valid:
      if form.is_valid():
        # save new instance
        instance = current_model()
        save_instance(form, instance)
        response_data = objects_to_dict(current_model)
      else:
        field, error = form.errors.items()[0]
        response_data = {
          'error': 'Field %s has invalid value. %s' % (field, error[0])
        }
    else:
      response_data = {'error': 'Invalid model name %s' % model_name}

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")