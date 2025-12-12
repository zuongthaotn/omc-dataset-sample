import pandas as pd
from core.catalog.product.simple import SimpleProductGenerator
from core.catalog.product.configurable import ConfigurableProductGenerator
from core.customer.entity import CustomerGenerator
from core.customer.address import CustomerAddressGenerator
from core.catalog.category.entity import CategoryGenerator
from core.catalog.category.product import CategoryProductGenerator
from core.catalog.product.stock_inventory import StockInventoryGenerator


class AutoGen:
    def __init__(self, config):
        self.config = config

    def generate_products(self):
        # Generate categories first
        category_generator = CategoryGenerator(self.config)
        categories = category_generator.generate()
        
        # Generate simple products
        simple_generator = SimpleProductGenerator(self.config)
        simple_products = simple_generator.generate()
        
        # Generate configurable products
        configurable_generator = ConfigurableProductGenerator(self.config)
        configurable_products = configurable_generator.generate()
        
        # Combine all products
        all_products = simple_products + configurable_products
        # Export to CSV
        file = 'outputs/product.csv'
        self.export_to_csv(all_products, file, 'product')
        print(f"Exported {len(all_products)} products to: {file}")
        
        # Generate category-product relationships
        category_product_generator = CategoryProductGenerator(self.config)
        category_product_generator.generate(all_products, categories)
        
        # Generate stock inventory
        stock_generator = StockInventoryGenerator(self.config)
        stock_generator.generate(all_products)

    def generate_customers(self):
        # Generate customer entities
        customer_generator = CustomerGenerator(self.config)
        customers = customer_generator.generate()
        
        # Generate customer addresses
        address_generator = CustomerAddressGenerator(self.config)
        customer_count = self.config.get('customer', {}).get('entity', {}).get('limit', 100)
        address_generator.generate(customer_count)

    def generate_orders(self):
        pass

    def get_schema_columns(self, table_name):
        """Parse XML schema to get column names for a table"""
        import xml.etree.ElementTree as ET
        
        schema_path = self.config.get('schema', 'schema/full_schema.xml')
        tree = ET.parse(schema_path)
        root = tree.getroot()
        
        columns = []
        for table in root.findall('table'):
            if table.get('name') == table_name:
                for column in table.findall('column'):
                    col_name = column.get('name')
                    columns.append(col_name)
                break
        
        return columns

    def export_to_csv(self, data, output_file, table_name):
        """Export data to CSV file using pandas"""
        if not data:
            print("No data to export")
            return
        
        import os
        os.makedirs('outputs', exist_ok=True)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Get schema columns for ordering
        schema_columns = self.get_schema_columns(table_name)
        
        if schema_columns:
            # Reorder columns based on schema, only include columns that exist in data
            existing_columns = [col for col in schema_columns if col in df.columns]
            df = df[existing_columns]
        
        # Export to CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Exported {len(df)} records to: {output_file}")