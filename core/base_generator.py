
class BaseGenerator:
    def __init__(self, config, fixture_path, output_folder):
        self.config = config
        self.fixture_path = fixture_path
        self.output_folder = output_folder
        self.fixture_cache = {}
    
    def load_fixture(self, fixture_path):
        pass
    
    def extract_fixture_values(self):
        pass
    
    def generate(self):
        pass
    
    def export_to_csv(self, data):
        pass