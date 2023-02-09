import os
import json


class fileReader:
    def __init__(self):
        pass

    @staticmethod
    def read_files(path):
        files = os.listdir(path)
        json_content = []
        for file in files:
            json_content.append(fileReader.read_file(f"{path}/{file}"))
        return json_content

    @staticmethod
    def read_file(path):
        with open(path, 'r') as f:
            json_content = json.load(f)
        return json_content

    @staticmethod
    def save_file(file, output_path):
        with open(output_path, 'w') as f:
            json.dump(file, f, indent=4, separators=(", ", ": "))