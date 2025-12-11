import json
from core.autogen import AutoGen


def main():
    # Load configuration
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    
    auto_gen = AutoGen(config)
    auto_gen.generate_products()
    auto_gen.generate_customers()
    auto_gen.generate_orders()


if __name__ == "__main__":
    main()
