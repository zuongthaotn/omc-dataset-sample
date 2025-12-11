import json
import csv
import os
from core.base_generator import BaseGenerator


CSV_STRUCTURE = {
    "sku": "sku",
    "name": "name",
    "brand": "brand",
    "price": "price",
    "visibility": 0,
    "status": 1,
    "type": "simple",
    "parent_sku": "parent_sku"
}



class BaseProductGenerator(BaseGenerator):
    """Base class for product generators"""
    
    def __init__(self, config):
        self.config = config
        self.fixture_cache = {}
        
    def load_fixture(self, fixture_path):
        """Load fixture data from JSON file with caching"""
        if fixture_path in self.fixture_cache:
            return self.fixture_cache[fixture_path]
        
        full_path = f'fixtures/{fixture_path}'
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.fixture_cache[fixture_path] = data
            return data
    
    def extract_fixture_values(self, fixture_path):
        """Extract values from fixture file based on its structure"""
        data = self.load_fixture(fixture_path)
        
        # Handle different fixture structures
        if 'brands' in data:
            return [item['brand'] for item in data['brands']]
        elif 'materials' in data:
            return [item['Material'] for item in data['materials']]
        elif 'gender' in data:
            return data['gender']
        elif 'EU_size' in data:
            return data['EU_size']
        elif 'UK_size' in data:
            return data['UK_size']
        elif 'styles' in data:
            return data['styles']
        elif 'products' in data:
            return data['products']
        else:
            # Return first array found
            for key, value in data.items():
                if isinstance(value, list):
                    return value
            return []
    
    def generate(self):
        """Generate products - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement generate()")
    
    def export_to_csv(self, products, output_file):
        """Export products to CSV file"""
        os.makedirs('outputs', exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(CSV_STRUCTURE.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        
        print(f"Exported {len(products)} products to: {output_file}")


class CategoryGenerator(BaseGenerator):
    def __init__(self, config):
        self.config = config
        self.fixture_cache = {}
    
    def generate(self):
        pass
    

class CategoryProductGenerator(BaseGenerator):
    def __init__(self, config):
        self.config = config
        self.fixture_cache = {}