from django.contrib import admin
import models
import sys

# Register your models here.

def generate_admin_models():
  for model in models.yaml_models:
    class_name = "%sAdmin" % (model.__name__)
    fields = [f.name for f in model._meta.fields if f.name != 'id']
    admin_model = type(class_name, (admin.ModelAdmin,), dict(list_display=fields,
                                                             __module__=__name__))
    setattr(sys.modules[__name__], class_name, admin_model)
    admin.site.register(model, admin_model)

generate_admin_models()