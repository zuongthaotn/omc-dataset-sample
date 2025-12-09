import random
import itertools
from core.catalog.product import BaseProductGenerator


class ConfigurableProductGenerator(BaseProductGenerator):
    """Generator for configurable products with variants"""
    
    def __init__(self, config):
        super().__init__(config)
        self.configurable_config = config.get('catalog', {}).get('product', {}).get('configurable', {})
    
    def generate_variants(self, rule_config):
        """Generate all possible variants based on rule configuration"""
        attributes = {}
        variant_counts = {}
        
        for attr_name, attr_config in rule_config.items():
            fixture_path = attr_config['fixture']
            variants_count = attr_config.get('varriants', 0)
            
            values = self.extract_fixture_values(fixture_path)
            attributes[attr_name] = values
            variant_counts[attr_name] = variants_count
        
        return attributes, variant_counts
    
    def get_variant_combinations(self, attributes, variant_counts):
        """Get all possible combinations of variants"""
        # Prepare variant lists for each attribute
        variant_lists = {}
        
        for attr_name, all_values in attributes.items():
            variant_count = variant_counts.get(attr_name, 0)
            
            if variant_count == 0:
                # Single value - pick one random value for all combinations
                variant_lists[attr_name] = [random.choice(all_values)]
            else:
                # Multiple values - select random subset
                count = min(variant_count, len(all_values))
                variant_lists[attr_name] = random.sample(all_values, count)
        
        # Generate all combinations
        attr_names = list(variant_lists.keys())
        attr_values = [variant_lists[name] for name in attr_names]
        
        combinations = []
        for combo in itertools.product(*attr_values):
            combination_dict = dict(zip(attr_names, combo))
            combinations.append(combination_dict)
        
        return combinations
    
    def generate_product_name(self, rule_template, selected_values):
        """Generate a product name based on rule template with selected attribute values"""
        name = rule_template
        
        for attr_name, value in selected_values.items():
            name = name.replace(f'{{{{{attr_name}}}}}', str(value))
        
        return name.strip()
    
    def generate(self):
        """Generate configurable products with variants"""
        if not self.configurable_config.get('enable', False):
            print("Configurable products disabled in config")
            return []
        
        print("Generating configurable products...")
        all_products = []
        rules_list = self.configurable_config.get('rules', [])
        
        for rule_item in rules_list:
            rule_name = rule_item['name']
            rule_template = rule_item['rule']
            rule_configs = rule_item.get('rules', [{}])[0]  # Get first rule config
            limit = rule_item.get('limit', 100)
            
            # Generate variants configuration
            attributes, variant_counts = self.generate_variants(rule_configs)
            
            # Generate parent configurable products
            for i in range(limit):
                parent_sku = f"G2IL-{i+1:05d}"
                
                # Get all variant combinations for this parent
                combinations = self.get_variant_combinations(attributes, variant_counts)
                
                # Create parent configurable product
                # Use first combination to get brand for parent name
                first_combo = combinations[0] if combinations else {}
                parent_name = self.generate_product_name(rule_template, first_combo)
                parent_brand = first_combo.get('brand', '')
                
                all_products.append({
                    'sku': parent_sku,
                    'name': parent_name,
                    'brand': parent_brand,
                    'price': '',  # Parent products typically don't have price
                    'visibility': 1,
                    'status': 1,
                    'type': 'configurable',
                    'parent_sku': ''
                })
                
                # Generate child products for each combination
                for j, selected_values in enumerate(combinations, 1):
                    product_name = self.generate_product_name(rule_template, selected_values)
                    
                    child_sku = f"{parent_sku}-{j:03d}"
                    product_price = round(random.uniform(10, 500), 2)
                    brand = selected_values.get('brand', '')
                    
                    all_products.append({
                        'sku': child_sku,
                        'name': product_name,
                        'brand': brand,
                        'price': product_price,
                        'visibility': 0,  # Children are not visible
                        'status': 1,
                        'type': 'simple',
                        'parent_sku': parent_sku
                    })
        
        print(f"Generated {len(all_products)} configurable product variants")
        return all_products
