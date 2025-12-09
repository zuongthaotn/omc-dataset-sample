import random
from core.catalog.product import BaseProductGenerator


class SimpleProductGenerator(BaseProductGenerator):
    """Generator for simple products from fixture files"""
    
    def __init__(self, config):
        super().__init__(config)
        self.simple_config = config.get('catalog', {}).get('product', {}).get('simple', {})
    
    def generate(self):
        """Generate simple products from fixture file"""
        if not self.simple_config.get('enable', False):
            print("Simple products disabled in config")
            return []
        
        fixture_path = self.simple_config.get('fixture', '')
        limit = self.simple_config.get('limit', 0)
        
        if not fixture_path:
            print("No fixture file specified for simple products")
            return []
        
        print("Generating simple products...")
        products_list = self.extract_fixture_values(fixture_path)
        
        # Apply limit if specified (0 means all)
        if limit > 0:
            products_list = products_list[:limit]
        
        products = []
        for i, product_name in enumerate(products_list, 1):
            product_sku = f"GIL-{i:05d}"
            product_price = round(random.uniform(10, 500), 2)
            
            products.append({
                'sku': product_sku,
                'name': product_name,
                'brand': '',
                'price': product_price,
                'visibility': 1,
                'status': 1,
                'type': 'simple',
                'parent_sku': ''
            })
        
        print(f"Generated {len(products)} simple products")
        return products