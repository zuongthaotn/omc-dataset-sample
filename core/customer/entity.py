import json
import csv
import os
import random
import string
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from core.base_generator import BaseGenerator


class CustomerGenerator(BaseGenerator):
    """Generator for customer entities from schema and fixtures"""
    
    def __init__(self, config):
        self.config = config
        self.fixture_cache = {}
        self.customer_config = config.get('customer', {}).get('entity', {})
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
        if 'first_names' in data:
            return data['first_names']
        elif 'last_names' in data:
            return data['last_names']
        elif 'emails' in data:
            return data['emails']
        elif 'email_domains' in data:
            return data['email_domains']
        elif 'genders' in data:
            return data['genders']
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
                    col_type = column.get('{http://www.w3.org/2001/XMLSchema-instance}type')
                    columns.append({'name': col_name, 'type': col_type})
                break
        
        return columns
    
    def generate_random_phone(self):
        """Generate random US phone number"""
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        return f"+1-{area_code}-{exchange}-{number}"
    
    def generate_random_date(self, start_year=1950, end_year=2005):
        """Generate random date of birth"""
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        random_date = start_date + timedelta(days=random_days)
        return random_date.strftime('%Y-%m-%d')
    
    def generate_random_value(self, column_name, column_type):
        """Generate random value based on column name and type"""
        if column_name == 'id':
            return None  # Will be auto-incremented
        elif column_name == 'phone':
            return self.generate_random_phone()
        elif column_name == 'dob':
            return self.generate_random_date()
        elif column_name == 'default_billing' or column_name == 'default_shipping':
            return random.randint(1, 5)  # Random address ID
        elif column_name == 'group':
            return random.choice(['General', 'Wholesale', 'Retailer', 'VIP'])
        elif column_name == 'gender':
            return random.choice(['Male', 'Female', 'Other'])
        elif column_name == 'status':
            return random.choice(['Active', 'Inactive'])
        elif column_name == 'created_at':
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif column_type == 'int':
            return random.randint(0, 100)
        elif column_type == 'varchar':
            return ''.join(random.choices(string.ascii_letters, k=10))
        else:
            return ''
    
    def generate(self):
        """Generate customer entities from schema and fixtures"""
        if not self.customer_config.get('enable', False):
            print("Customer generation disabled in config")
            return []
        
        print("Generating customers...")
        
        # Get schema columns
        columns = self.get_schema_columns('customers')
        if not columns:
            print("No schema found for 'customers' table")
            return []
        
        # Load fixtures
        fixtures_config = self.customer_config.get('fixture', {})
        fixtures_data = {}
        
        for field_name, fixture_path in fixtures_config.items():
            if fixture_path:
                fixtures_data[field_name] = self.extract_fixture_values(fixture_path)
        
        # Get email domains if available
        email_domains = fixtures_data.get('email', [])
        if not email_domains:
            # Fallback to default domains if not in fixture
            email_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'example.com']
        
        # Get limit
        limit = self.customer_config.get('limit', 100)
        
        # Generate customers
        customers = []
        for i in range(1, limit + 1):
            customer = {}
            
            # Generate first_name and last_name first (needed for email)
            first_name = random.choice(fixtures_data.get('first_name', ['John'])) if 'first_name' in fixtures_data else f'FirstName{i}'
            last_name_and_gender = random.choice(fixtures_data.get('last_name', ['Doe'])) if 'last_name' in fixtures_data else f'LastName{i}'
            last_name = last_name_and_gender['last_name']
            gender = last_name_and_gender['gender']
            
            for col in columns:
                col_name = col['name']
                col_type = col['type']
                
                if col_name == 'id':
                    customer[col_name] = i
                elif col_name == 'first_name':
                    customer[col_name] = first_name
                elif col_name == 'last_name':
                    customer[col_name] = last_name
                elif col_name == 'email':
                    # Generate email using domains from fixture
                    customer[col_name] = self.generate_email_with_domains(first_name, last_name, email_domains)
                elif col_name in fixtures_data and fixtures_data[col_name]:
                    customer[col_name] = random.choice(fixtures_data[col_name])
                else:
                    customer[col_name] = self.generate_random_value(col_name, col_type)
            
            customers.append(customer)
        
        print(f"Generated {len(customers)} customers")
        
        # Export to CSV
        self.export_to_csv(customers, 'outputs/customers.csv')
        
        return customers
    
    def generate_email_with_domains(self, first_name, last_name, domains):
        """Generate email using provided domain list"""
        patterns = [
            f"{first_name.lower()}.{last_name.lower()}",
            f"{first_name.lower()}{last_name.lower()}",
            f"{first_name[0].lower()}{last_name.lower()}",
            f"{first_name.lower()}{random.randint(1, 999)}"
        ]
        username = random.choice(patterns)
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def export_to_csv(self, customers, output_file):
        """Export customers to CSV file"""
        if not customers:
            print("No customers to export")
            return
        
        os.makedirs('outputs', exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(customers[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(customers)
        
        print(f"Exported {len(customers)} customers to: {output_file}")