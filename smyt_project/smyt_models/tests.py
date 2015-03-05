from django.test import TestCase
import yaml
import os
from smyt_models import utils

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
    self.assertEqual(set(result.keys()), set(['app_users', 'rooms']))
    print(result['app_users'])

  def test_generate_models(self):
    models = utils.generate_models(YAML_MODELS_PAHT, __name__)
    self.assertEqual(len(models), 2)
    self.assertEqual(models[0].__name__, 'app_users')
    self.assertEqual(models[1].__name__, 'rooms')

  def test_models(self):
    from smyt_models import models
    self.assertTrue(models.rooms)
    print YamlModelsTestCase.__module__
