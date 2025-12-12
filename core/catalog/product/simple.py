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
        
        # Get schema columns
        schema_columns = self.get_schema_columns('product')
        
        products = []
        for i, product_name in enumerate(products_list, 1):
            product_sku = f"GIL-{i:05d}"
            product_price = round(random.uniform(10, 500), 2)
            
            # Build product based on schema
            product = {}
            for col in schema_columns:
                if col == 'id':
                    product[col] = i
                elif col == 'sku':
                    product[col] = product_sku
                elif col == 'name':
                    product[col] = product_name
                elif col == 'price':
                    product[col] = product_price
                elif col == 'brand':
                    product[col] = ''
                elif col == 'category_id':
                    product[col] = random.randint(1, 10)
                elif col == 'tax_percent':
                    product[col] = 10
                elif col == 'status':
                    product[col] = 'Enabled'
                elif col == 'visibility':
                    product[col] = 'Catalog, Search'
                elif col == 'product_type':
                    product[col] = 'simple'
                elif col == 'created_at':
                    product[col] = '2024-01-01 00:00:00'
                else:
                    product[col] = ''
            
            products.append(product)
        
        print(f"Generated {len(products)} simple products")
        
        return products