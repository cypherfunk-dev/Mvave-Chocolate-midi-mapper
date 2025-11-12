import json
import os
from models.configuration import AppConfiguration

class FileManager:
    @staticmethod
    def save_configuration(config, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def load_configuration(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return None