from src.transformer.transformer import Transformer
from src.common import common
import pandas as pd

# Currently Copilot data does not need transformation from the dictionaries via which it is extracted
# Placeholder class
# More advanced metrics (efficience plutot que utilisation) will likely require tranformation
class CopilotTransformer(Transformer):
    def initialize_data(self, config):
        self.config = config

    def transform_data(self, adapted_data):
        return adapted_data