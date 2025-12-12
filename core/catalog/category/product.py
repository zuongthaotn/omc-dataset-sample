import json
import csv
import os
import random
import xml.etree.ElementTree as ET
from core.base_generator import BaseGenerator


class CategoryProductGenerator(BaseGenerator):
    """Generator for category-product relationships from schema"""
    
    def __init__(self, config):
        self.config = config
        self.fixture_cache = {}
        self.category_product_config = config.get('catalog', {}).get('category_product', {})
        self.schema_path = config.get('schema', 'schema/full_schema.xml')
        
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
    
    def generate(self, products, categories):
        """Generate category-product relationships"""
        if not self.category_product_config.get('enable', False):
            print("Category-product generation disabled in config")
            return []
        
        print("Generating category-product relationships...")
        
        # Get schema columns
        columns = self.get_schema_columns('category_product')
        if not columns:
            print("No schema found for 'category_product' table")
            return []
        
        if not products or not categories:
            print("No products or categories available")
            return []
        
        # Create a mapping of category name to category object
        category_map = {cat['name'].lower(): cat for cat in categories}
        
        # Generate relationships
        relationships = []
        relationship_id = 1
        
        for product in products:
            product_name = product.get('name', '')
            
            # Extract last word from product name
            words = product_name.strip().split()
            if not words:
                continue
            
            last_word = words[-1].lower()
            
            # Find matching category by last word
            matched_category = None
            if last_word in category_map:
                matched_category = category_map[last_word]
            
            # If no exact match, try to find partial match
            if not matched_category:
                for cat_name, cat in category_map.items():
                    if last_word in cat_name or cat_name in last_word:
                        matched_category = cat
                        break
            
            # If still no match, skip this product
            if not matched_category:
                continue
            
            # Create relationship
            relationship = {}
            
            for col in columns:
                col_name = col['name']
                col_type = col['type']
                
                if col_name == 'id':
                    relationship[col_name] = relationship_id
                elif col_name == 'category_id':
                    relationship[col_name] = matched_category.get('id', 0)
                elif col_name == 'product_id':
                    relationship[col_name] = product.get('id', 0)
                else:
                    relationship[col_name] = ''
            
            relationships.append(relationship)
            relationship_id += 1
        
        print(f"Generated {len(relationships)} category-product relationships")
        
        # Export to CSV
        self.export_to_csv(relationships, 'outputs/category_product.csv')
        
        return relationships
    
    def export_to_csv(self, relationships, output_file):
        """Export relationships to CSV file"""
        if not relationships:
            print("No relationships to export")
            return
        
        os.makedirs('outputs', exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(relationships[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(relationships)
        
        print(f"Exported {len(relationships)} relationships to: {output_file}")
