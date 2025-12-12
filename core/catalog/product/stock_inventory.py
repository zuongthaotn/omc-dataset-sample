import json
import csv
import os
import random
import xml.etree.ElementTree as ET
from core.base_generator import BaseGenerator


class StockInventoryGenerator(BaseGenerator):
    """Generator for product stock inventory from schema"""
    
    def __init__(self, config):
        self.config = config
        self.fixture_cache = {}
        self.stock_config = config.get('catalog', {}).get('stock_inventory', {})
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
    
    def generate_warehouse_name(self, warehouse_id):
        """Generate warehouse name based on ID"""
        warehouse_names = [
            'Main Warehouse',
            'East Coast Distribution Center',
            'West Coast Distribution Center',
            'Midwest Fulfillment Center',
            'Southern Regional Warehouse',
            'Northern Distribution Hub',
            'Central Logistics Center',
            'International Warehouse'
        ]
        
        if warehouse_id <= len(warehouse_names):
            return warehouse_names[warehouse_id - 1]
        else:
            return f'Warehouse {warehouse_id}'
    
    def generate(self, products):
        """Generate stock inventory for products"""
        if not self.stock_config.get('enable', False):
            print("Stock inventory generation disabled in config")
            return []
        
        print("Generating stock inventory...")
        
        # Get schema columns
        columns = self.get_schema_columns('stock_inventory')
        if not columns:
            print("No schema found for 'stock_inventory' table")
            return []
        
        if not products:
            print("No products available")
            return []
        
        # Get number of warehouses
        num_warehouses = self.stock_config.get('warehouses', 3)
        
        # Generate stock records
        stock_records = []
        stock_id = 1
        
        for product in products:
            # Each product exists in 1 to num_warehouses
            num_locations = random.randint(1, num_warehouses)
            selected_warehouses = random.sample(range(1, num_warehouses + 1), num_locations)
            
            for warehouse_id in selected_warehouses:
                stock_record = {}
                
                for col in columns:
                    col_name = col['name']
                    col_type = col['type']
                    
                    if col_name == 'id':
                        stock_record[col_name] = stock_id
                    elif col_name == 'product_id':
                        stock_record[col_name] = product.get('id', 0)
                    elif col_name == 'warehouse_id':
                        stock_record[col_name] = warehouse_id
                    elif col_name == 'warehouse_name':
                        stock_record[col_name] = self.generate_warehouse_name(warehouse_id)
                    elif col_name == 'stock_status':
                        # Random stock status
                        stock_record[col_name] = random.choice(['In Stock', 'Low Stock', 'Out of Stock'])
                    elif col_name == 'stock_quantity':
                        # Random quantity based on status
                        status = stock_record.get('stock_status', 'In Stock')
                        if status == 'Out of Stock':
                            stock_record[col_name] = 0
                        elif status == 'Low Stock':
                            stock_record[col_name] = random.randint(1, 10)
                        else:  # In Stock
                            stock_record[col_name] = random.randint(50, 1000)
                    else:
                        stock_record[col_name] = ''
                
                stock_records.append(stock_record)
                stock_id += 1
        
        print(f"Generated {len(stock_records)} stock inventory records")
        
        # Export to CSV
        self.export_to_csv(stock_records, 'outputs/stock_inventory.csv')
        
        return stock_records
    
    def export_to_csv(self, stock_records, output_file):
        """Export stock records to CSV file"""
        if not stock_records:
            print("No stock records to export")
            return
        
        os.makedirs('outputs', exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(stock_records[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(stock_records)
        
        print(f"Exported {len(stock_records)} stock records to: {output_file}")
