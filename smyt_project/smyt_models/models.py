import os
import utils

YAML_MODELS_PAHT = os.path.join(os.path.dirname(__file__), 'models.yaml')
yaml_models = utils.generate_models(YAML_MODELS_PAHT, __name__)
