import json
import csv
import os
import random
import xml.etree.ElementTree as ET
from core.base_generator import BaseGenerator


class CustomerAddressGenerator(BaseGenerator):
    """Generator for customer addresses from schema and fixtures"""
    
    def __init__(self, config):
        self.config = config
        self.fixture_cache = {}
        self.address_config = config.get('customer', {}).get('address', {})
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
    
    def generate_random_street(self):
        """Generate random street address"""
        street_numbers = random.randint(1, 9999)
        street_names = ['Main St', 'Oak Ave', 'Maple Dr', 'Park Blvd', 'Cedar Ln', 
                       'Elm St', 'Washington Ave', 'Lake Dr', 'Hill Rd', 'Forest Ave']
        return f"{street_numbers} {random.choice(street_names)}"
    
    def generate_random_zipcode(self):
        """Generate random US zipcode"""
        return f"{random.randint(10000, 99999)}"
    
    def generate_random_value(self, column_name, column_type):
        """Generate random value based on column name and type"""
        if column_name == 'id':
            return None  # Will be auto-incremented
        elif column_name == 'street':
            return self.generate_random_street()
        elif column_name == 'zipcode':
            return self.generate_random_zipcode()
        elif column_name == 'city':
            return random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
                                 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'])
        elif column_name == 'region':
            return random.choice(['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'FL', 'OH', 'MI', 'WA'])
        elif column_name == 'country':
            return 'US'
        elif column_type == 'int':
            return random.randint(0, 100)
        elif column_type == 'varchar':
            return ''
        else:
            return ''
    
    def generate(self, customer_count=100):
        """Generate customer addresses from schema and fixtures"""
        if not self.address_config.get('enable', False):
            print("Customer address generation disabled in config")
            return []
        
        print("Generating customer addresses...")
        
        # Get schema columns
        columns = self.get_schema_columns('customer_address')
        if not columns:
            print("No schema found for 'customer_address' table")
            return []
        
        # Load fixture if configured
        fixture_path = self.address_config.get('fixture', '')
        address_fixtures = []
        
        if fixture_path:
            address_fixtures = self.extract_fixture_values(fixture_path)
        
        # Get max addresses per customer
        max_addresses_per_customer = self.address_config.get('max_address_per_customer', 2)
        
        # Generate addresses
        addresses = []
        address_id = 1
        
        for customer_id in range(1, customer_count + 1):
            # Random number of addresses per customer (1 to max)
            num_addresses = random.randint(1, max_addresses_per_customer)
            
            for addr_num in range(num_addresses):
                address = {}
                
                # If we have fixture data, use it
                if address_fixtures:
                    fixture_address = random.choice(address_fixtures)
                    
                    # Map fixture fields to schema fields
                    field_mapping = {
                        'street': 'address',  # fixture 'address' -> schema 'street'
                        'region': 'state',    # fixture 'state' -> schema 'region'
                        'zipcode': 'zip',     # fixture 'zip' -> schema 'zipcode'
                        'city': 'city',       # same name
                        'country': None       # not in fixture, will use default
                    }
                    
                    for col in columns:
                        col_name = col['name']
                        col_type = col['type']
                        
                        if col_name == 'id':
                            address[col_name] = address_id
                        elif col_name == 'customer_id':
                            address[col_name] = customer_id
                        elif col_name == 'country':
                            # Default country to US
                            address[col_name] = 'US'
                        elif col_name in field_mapping and field_mapping[col_name]:
                            # Map schema field to fixture field
                            fixture_field = field_mapping[col_name]
                            if fixture_field in fixture_address:
                                address[col_name] = fixture_address[fixture_field]
                            else:
                                address[col_name] = self.generate_random_value(col_name, col_type)
                        else:
                            address[col_name] = self.generate_random_value(col_name, col_type)
                else:
                    # No fixture, generate random data
                    for col in columns:
                        col_name = col['name']
                        col_type = col['type']
                        
                        if col_name == 'id':
                            address[col_name] = address_id
                        elif col_name == 'customer_id':
                            address[col_name] = customer_id
                        else:
                            address[col_name] = self.generate_random_value(col_name, col_type)
                
                addresses.append(address)
                address_id += 1
        
        print(f"Generated {len(addresses)} customer addresses")
        
        # Export to CSV
        self.export_to_csv(addresses, 'outputs/customer_address.csv')
        
        return addresses
    
    def export_to_csv(self, addresses, output_file):
        """Export addresses to CSV file"""
        if not addresses:
            print("No addresses to export")
            return
        
        os.makedirs('outputs', exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(addresses[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(addresses)
        
        print(f"Exported {len(addresses)} addresses to: {output_file}")
