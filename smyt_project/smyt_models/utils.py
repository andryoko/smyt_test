__author__ = 'okoneshnikov'

import os
import sys
import yaml
import logging
from django.db import models


# Generate yaml models.

class YamlParseError(Exception):
  pass

def read_yaml(filename):
  assert filename
  f = open(filename)
  stream = f.read()
  f.close()
  return yaml.load(stream)

def generate_models(filename, module_name=__name__):
  classes = read_yaml(filename)
  created_models = []

  for class_name, description in classes.items():
    fields = {'__module__': module_name}

    for field_dict in description['fields']:
      if field_dict.get('id') and field_dict.get('title') and field_dict.get('type'):
        field = None
        if field_dict['type'] == 'char':
          field = models.CharField(field_dict['title'], max_length=100)
        elif field_dict['type'] == 'int':
          field = models.IntegerField(field_dict['title'], default=0)
        elif field_dict['type'] == 'date':
          field = models.DateField(field_dict['title'])

        if field:
          fields[field_dict['id']] = field
        else:
          logging.warning('Unknown field type:%r', field_dict)
      else:
        message = 'Invalid field description: %r' % field_dict
        logging.error(message)
        raise YamlParseError(message)

    cls = type(class_name, (models.Model,), fields)

    if description.get('title'):
      cls._meta.verbose_name_plural = description['title']

    # register model in module
    module = sys.modules[module_name]
    setattr(module, cls.__name__, cls)

    created_models.append(cls)

  return created_models
