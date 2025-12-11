from core.catalog.product.simple import SimpleProductGenerator
from core.catalog.product.configurable import ConfigurableProductGenerator


class AutoGen:
    def __init__(self, config):
        self.config = config

    def generate_products(self):
        # Generate simple products
        simple_generator = SimpleProductGenerator(self.config)
        simple_generator.generate()
        
        # Generate configurable products
        configurable_generator = ConfigurableProductGenerator(self.config)
        configurable_generator.generate()

    def generate_customers(self):
        pass

    def generate_orders(self):
        pass