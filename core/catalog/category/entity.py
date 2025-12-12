import json
import csv
import os
import random
import xml.etree.ElementTree as ET
from core.base_generator import BaseGenerator


class CategoryGenerator(BaseGenerator):
    """Generator for product categories from schema and fixtures"""
    
    def __init__(self, config):
        self.config = config
        self.fixture_cache = {}
        self.category_config = config.get('catalog', {}).get('category', {})
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
                    col_type = column.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                    columns.append({'name': col_name, 'type': col_type})
                break
        
        return columns
    
    def generate_slug(self, name):
        """Generate URL-friendly slug from category name"""
        return name.lower().replace(' ', '-').replace('&', 'and')
    
    def generate(self):
        """Generate product categories from schema and fixtures"""
        if not self.category_config.get('enable', False):
            print("Category generation disabled in config")
            return []
        
        print("Generating categories...")
        
        # Get schema columns
        columns = self.get_schema_columns('category')
        if not columns:
            print("No schema found for 'category' table")
            return []
        
        # Load fixture if configured
        fixture_path = self.category_config.get('fixture', '')
        
        if fixture_path:
            # Load hierarchical category structure
            data = self.load_fixture(fixture_path)
            categories = self.parse_hierarchical_categories(data, columns)
        else:
            # Default flat categories if no fixture
            category_names = [
                'Electronics', 'Clothing', 'Home & Garden', 'Sports & Outdoors',
                'Books', 'Toys & Games', 'Health & Beauty', 'Automotive',
                'Food & Beverage', 'Office Supplies'
            ]
            categories = self.create_flat_categories(category_names, columns)
        
        # Apply limit if specified (0 means all)
        limit = self.category_config.get('limit', 0)
        if limit > 0:
            categories = categories[:limit]
        
        print(f"Generated {len(categories)} categories")
        
        # Export to CSV
        self.export_to_csv(categories, 'outputs/category.csv')
        
        return categories
    
    def parse_hierarchical_categories(self, data, columns):
        """Parse hierarchical category structure from fixture (3 levels)"""
        categories = []
        category_id = 1
        
        # Check if data has 'categories' key
        if 'categories' in data:
            category_data = data['categories']
        else:
            category_data = data
        
        # Process 3-level hierarchy: Parent → Subcategory → Items
        for parent_name, subcategories in category_data.items():
            # Level 1: Create parent category (e.g., "Apparel")
            parent_category = self.create_category(category_id, parent_name, 0, columns)
            categories.append(parent_category)
            parent_id = category_id
            category_id += 1
            
            # Level 2: Create subcategories (e.g., "Tops", "Bottoms")
            if isinstance(subcategories, dict):
                for subcat_name, items in subcategories.items():
                    subcat_category = self.create_category(
                        category_id, 
                        subcat_name, 
                        parent_id, 
                        columns
                    )
                    categories.append(subcat_category)
                    subcat_id = category_id
                    category_id += 1
                    
                    # Level 3: Create leaf items (e.g., "Blouse", "Sweater")
                    if isinstance(items, list):
                        for item_name in items:
                            item_category = self.create_category(
                                category_id,
                                item_name,
                                subcat_id,
                                columns
                            )
                            categories.append(item_category)
                            category_id += 1
        
        return categories
    
    def create_flat_categories(self, category_names, columns):
        """Create flat category list without hierarchy"""
        categories = []
        for i, name in enumerate(category_names, 1):
            category = self.create_category(i, name, 0, columns)
            categories.append(category)
        return categories
    
    def create_category(self, cat_id, name, parent_id, columns):
        """Create a single category record"""
        category = {}
        
        for col in columns:
            col_name = col['name']
            col_type = col['type']
            
            if col_name == 'id':
                category[col_name] = cat_id
            elif col_name == 'name':
                category[col_name] = name
            elif col_name == 'parent_id':
                category[col_name] = parent_id
            elif col_name == 'slug':
                category[col_name] = self.generate_slug(name)
            elif col_name == 'status':
                category[col_name] = 'Enabled'
            elif col_name == 'created_at':
                category[col_name] = '2024-01-01 00:00:00'
            else:
                category[col_name] = ''
        
        return category
    
    def export_to_csv(self, categories, output_file):
        """Export categories to CSV file"""
        if not categories:
            print("No categories to export")
            return
        
        os.makedirs('outputs', exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(categories[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(categories)
        
        print(f"Exported {len(categories)} categories to: {output_file}")
