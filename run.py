import json
from core.catalog.product.simple import SimpleProductGenerator
from core.catalog.product.configurable import ConfigurableProductGenerator


def main():
    # Load configuration
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    all_products = []
    
    # Generate simple products
    simple_generator = SimpleProductGenerator(config)
    simple_products = simple_generator.generate()
    all_products.extend(simple_products)
    
    # Generate configurable products
    configurable_generator = ConfigurableProductGenerator(config)
    configurable_products = configurable_generator.generate()
    all_products.extend(configurable_products)
    
    # Export all products to CSV
    if all_products:
        print(f"\nExporting {len(all_products)} total products...")
        simple_generator.export_to_csv(all_products, 'outputs/products.csv')
        print("Done!")
    else:
        print("No products generated")


if __name__ == "__main__":
    main()
