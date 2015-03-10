from django.test import TestCase
import yaml
import os
from smyt_models import utils
import json
import datetime

YAML_MODELS_PAHT = os.path.join(os.path.dirname(__file__), 'test_models.yaml')

# Create your tests here.
class YamlModelsTestCase(TestCase):

  def setUp(self):
    # Test definitions as before.
    pass

  def test_read_yaml(self):
    # test read yaml file
    name = os.path.join(os.path.dirname(__file__), 'test_models.yaml')
    f = open(os.path.join(name))
    stream = f.read()
    f.close()

    result = yaml.load(stream)
    self.assertEqual(set(result.keys()), set(['appusers', 'rooms']))
    print(result['appusers'])

  def test_generate_models(self):
    models = utils.generate_models(YAML_MODELS_PAHT, __name__)
    self.assertEqual(len(models), 2)
    self.assertEqual(models[0].__name__, 'appusers')
    self.assertEqual(models[1].__name__, 'rooms')

  def test_models(self):
    import smyt_models.models as app_models
    models_list = utils.generate_models(YAML_MODELS_PAHT, app_models.__name__)
    self.assertTrue(app_models.rooms)
    self.assertTrue(app_models.appusers)
    print YamlModelsTestCase.__module__

  def test_views(self):
    # genarate test models
    import smyt_models.models as app_models
    utils.generate_models(YAML_MODELS_PAHT, app_models.__name__)

    response = self.client.get('/smyt_models/')
    self.assertEqual(response.status_code, 200)

    # request without parameters
    response = self.client.post('/smyt_models/add/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, '{"error": "Invalid model name "}')

    #
    data = {
      'model': 'rooms',
    }
    response = self.client.post('/smyt_models/add/', data)
    self.assertEqual(response.status_code, 200)
    self.assertTrue('Field department has invalid value. This field is required.' in response.content)

    data = {
      'model': 'appusers',
      'name': 'user-1',
      'paycheck': 'invalid int',
    }

    response = self.client.post('/smyt_models/add/', data)
    self.assertEqual(response.status_code, 200)
    self.assertTrue('Field paycheck has invalid value. Enter a whole number.' in response.content)

    data = {
      'model': 'appusers',
      'name': 'user-1',
      'paycheck': '120000',
      'date_joined': 'invalid date'
    }

    response = self.client.post('/smyt_models/add/', data)
    self.assertEqual(response.status_code, 200)
    self.assertTrue('Field date_joined has invalid value. Enter a valid date.' in response.content)

    data = {
      'model': 'appusers',
      'name': 'user-1',
      'paycheck': '120000',
      'date_joined': '2015-20-20' # invalid date
    }

    response = self.client.post('/smyt_models/add/', data)
    self.assertEqual(response.status_code, 200)
    self.assertTrue('Field date_joined has invalid value. Enter a valid date.' in response.content)

    data = {
      'model': 'appusers',
      'name': 'user-1',
      'paycheck': '120000',
      'date_joined': '2015-03-15'
    }

    response = self.client.post('/smyt_models/add/', data)
    self.assertEqual(response.status_code, 200)
    result = json.loads(response.content)
    # check fields
    fields = result['fields']
    data = result['data']

    self.assertEqual(len(fields), 4)
    self.assertEqual(fields[0]['type'], u'int')
    self.assertEqual(fields[0]['name'], u'id')
    self.assertEqual(fields[1]['type'], u'char')
    self.assertEqual(fields[1]['name'], u'name')
    self.assertEqual(fields[2]['type'], u'int')
    self.assertEqual(fields[2]['name'], u'paycheck')
    self.assertEqual(fields[3]['type'], u'date')
    self.assertEqual(fields[3]['name'], u'date_joined')

    # check data
    self.assertEqual(len(data), 1)
    self.assertEqual(len(data[0]), 4)

    self.assertEqual(data[0][0]['name'], u'id')
    self.assertEqual(data[0][0]['value'], 1)
    self.assertEqual(data[0][1]['name'], u'name')
    self.assertEqual(data[0][1]['value'], u'user-1')
    self.assertEqual(data[0][2]['name'], u'paycheck')
    self.assertEqual(data[0][2]['value'], 120000)
    self.assertEqual(data[0][3]['name'], u'date_joined')
    self.assertEqual(data[0][3]['value'], '15/03/2015')

    # check invalid model
    response = self.client.post('/smyt_models/edit_cell/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, 'Model does not exist')

    # check invalid object
    data = {
      'model': 'appusers',
      'rowid': '10',
    }
    response = self.client.post('/smyt_models/edit_cell/', data)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, 'Invalid object id')

    # check invalid field name
    data = {
      'model': 'appusers',
      'rowid': '1',
      'colid': 'paycheck2',
    }

    response = self.client.post('/smyt_models/edit_cell/', data)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, 'Invalid field name')

    # check value
    data = {
      'model': 'appusers',
      'rowid': '1',
      'colid': 'paycheck',
    }

    response = self.client.post('/smyt_models/edit_cell/', data)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, 'Value is required')

    # check value
    data = {
      'model': 'appusers',
      'rowid': '1',
      'colid': 'paycheck',
      'value': 'invalid int',
    }

    response = self.client.post('/smyt_models/edit_cell/', data)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, 'Invalid value type. It should be integer.')

    # check value
    data = {
      'model': 'appusers',
      'rowid': '1',
      'colid': 'date_joined',
      'value': 'invalid date',
    }

    response = self.client.post('/smyt_models/edit_cell/', data)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, 'Invalid value type. Enter a valid date.')

    # check edit data
    data = {
      'model': 'appusers',
      'rowid': '1',
      'colid': 'paycheck',
      'value': '125000',
    }

    response = self.client.post('/smyt_models/edit_cell/', data)
    self.assertEqual(response.status_code, 200)

    user = app_models.appusers.objects.get(pk=1)
    self.assertEqual(user.paycheck, 125000)

    # check edit data
    data = {
      'model': 'appusers',
      'rowid': '1',
      'colid': 'date_joined',
      'value': '21/03/2015',
    }

    response = self.client.post('/smyt_models/edit_cell/', data)
    self.assertEqual(response.status_code, 200)

    user = app_models.appusers.objects.get(pk=1)
    self.assertEqual(user.date_joined, datetime.date(2015, 3, 21))