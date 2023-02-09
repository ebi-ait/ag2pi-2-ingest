import json

from copy import deepcopy

class JsonCleaner:
    content: dict

    def __init__(self, content: dict):
        self.content = content


    def create_exec_statement(self, pre, fqk, post):
        fqk_to_str = "".join([str([int(v) if v.isdigit() else v]) for v in fqk.split('.')])
        statement = f"{pre}self.content{fqk_to_str} {post}"
        return statement

    def delete_field(self, fqk):
        delete_statement = self.create_exec_statement("del ", fqk, "")
        exec(delete_statement)

    def replace_value(self, value, fqk):
        value = f"'{value}'" if not value.isnumeric() else value
        replace_statement = self.create_exec_statement("", fqk, f"= {value}")
        exec(replace_statement)

    def add_field(self, value, fqk):
        value = f"'{value}'" if self.is_string(value) else value
        add_statement = self.create_exec_statement("", fqk, f"= {value}")
        exec(add_statement)

    def is_string(self, value: str):
        if value.startswith("[") or value.startswith('{') or value.isnumeric():
            return False
        return True

    def return_content_on_fqk(self, fqk: str):
        content = self.content
        for key in fqk.split('.'):
            if key.isdigit():
                key = int(key)
            content = content[key]
        return content

    def clean_null_values(self):
        # Dictionaries cannot be updated while traversed
        content_copy = deepcopy(self.content)
        for full_qualified_key in self.search_value(content_copy, None):
            full_qualified_key = ".".join(full_qualified_key.split(".")[:-1])
            if full_qualified_key.split(".")[-1].isdigit():
                full_qualified_key = ".".join(full_qualified_key.split(".")[:-1])
            try:
                self.delete_field(full_qualified_key)
            except KeyError:
                # Sometimes there's more than 1 null value
                continue
            except IndexError:
                continue

    def replace_all_values(self, old, new):
        for full_qualified_key in self.search_value(self.content, old):
            self.replace_value(new, full_qualified_key)


    def search_value(self, content, value_to_check, fq_key=""):
        if isinstance(content, list):
            for i, element in enumerate(content):
                yield from self.search_value(element, value_to_check, f"{fq_key}{'.' if fq_key else ''}{i}")
        elif isinstance(content, dict):
            for key in content.keys():
                yield from self.search_value(content[key], value_to_check, f"{fq_key}{'.' if fq_key else ''}{key}")
        elif content == value_to_check:
            yield fq_key
        else:
            pass


    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.content, f, indent=4, separators=(", ", ": "))



if __name__ == '__main__':
    with open("/Users/enrique/HumanCellAtlas/ag2pi-2-ingest/examples/input/datasets/SAMEA8050953_scrna.json", 'r') as f:
        contents = json.load(f)

    cleaner = JsonCleaner(contents)
    cleaner.clean_null_values()
