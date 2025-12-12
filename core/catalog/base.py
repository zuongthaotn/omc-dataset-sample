import json
import csv
import os
import xml.etree.ElementTree as ET
from core.base_generator import BaseGenerator


class BaseProductGenerator(BaseGenerator):
    """Base class for product generators"""
    
    def __init__(self, config):
        self.config = config
        self.fixture_cache = {}
        self.schema_path = config.get('schema', 'schema/full_schema.xml')
        
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
        
        # If data is already a list, return it directly
        if isinstance(data, list):
            return data
        
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
    
    def get_schema_columns(self, table_name):
        """Parse XML schema to get column names for a table"""
        tree = ET.parse(self.schema_path)
        root = tree.getroot()
        
        columns = []
        for table in root.findall('table'):
            if table.get('name') == table_name:
                for column in table.findall('column'):
                    col_name = column.get('name')
                    columns.append(col_name)
                break
        
        return columns
    
    def generate(self):
        """Generate products - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement generate()")
    
    def export_to_csv(self, products, output_file):
        """Export products to CSV file"""
        if not products:
            print("No products to export")
            return
            
        os.makedirs('outputs', exist_ok=True)
        
        # Get schema columns for product table
        schema_columns = self.get_schema_columns('product')
        
        # If schema not found, use product keys
        if not schema_columns:
            fieldnames = list(products[0].keys())
        else:
            # Use schema columns, but only include those present in products
            fieldnames = [col for col in schema_columns if col in products[0]]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
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