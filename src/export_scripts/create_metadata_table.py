"""
This script is intended to create the metadata tables for terra, based on the metadata available for ingest.

Each of the metadata tables is separated by schema type (Biomaterial, file) and stored as a separate csv

A separate experimental graph table will be generated
"""

import json
import sys
import os
import itertools



def create_uuid_metadata_map(files_path):
    return {filename.strip('.json'): json.load(open(f"{files_path}/{filename}", 'r')) for filename in os.listdir(files_path)}

def add_links(uuid_metadata_map, summary):
    map_with_links = {}
    for uuid, value in uuid_metadata_map.items():
        if value['schema_type'] == 'process' or value['schema_type'] == 'project':
            continue
        value.update({'uuid': uuid})
        relationships = summary[uuid]
        value.update(relationships)
        map_with_links[uuid] = value
    return map_with_links


def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten a nested dictionary to a flat list.

    Args:
        d (dict): A nested dictionary to be flattened.
        parent_key (str): A string representing the parent key, used for recursive calls.
        sep (str): A separator string used to separate keys in the flattened list.

    Returns:
        A list of tuples, where each tuple represents a key-value pair from the original dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

def ensure_same_length_values(dictionary: dict):
    max_length = max(len(sublist) for sublist in list(dictionary.values()))
    for key, value in dictionary.items():
        if (max_length - len(value)) != 0:
            dictionary[key].extend(['||'] * (max_length - len(value)))
    return dictionary

def preemptively_fill_fields(dictionary: dict, keys: list):
    if not dictionary:
        return dictionary
    max_length = max(len(sublist) for sublist in list(dictionary.values()))
    for key in dictionary.keys():
        if key not in keys:
            dictionary[key].append('||')
    for key in keys:
        if key not in dictionary.keys():
            dictionary[key] = ["||"] * max_length
    return dictionary


def flatten_map_to_csv(json_contents: dict):
    csv_maps = {}
    for uuid, content in json_contents.items():
        entity_type = content['describedBy'].split('/')[-1]
        if not entity_type in csv_maps:
            csv_maps[content['describedBy'].split('/')[-1]] = {}
        flattened_dict = flatten_dict(content, sep='.')
        for key, value in flattened_dict.items():
            if key not in csv_maps[content['describedBy'].split('/')[-1]]:
                csv_maps[content['describedBy'].split('/')[-1]][key] = []
            if not value:
                csv_maps[content['describedBy'].split('/')[-1]][key].append('||')
                continue
            else:
                csv_maps[content['describedBy'].split('/')[-1]][key].append(value)
        csv_maps[entity_type] = preemptively_fill_fields(csv_maps[entity_type], list(flattened_dict.keys()))
        csv_maps[entity_type] = ensure_same_length_values(csv_maps[entity_type])

    return csv_maps


def transpose_list(lst):
    """
    Transpose a list of lists.

    Args:
        lst (list): A list of lists to be transposed.

    Returns:
        A list of lists, where each sublist represents a column from the original list of lists.
    """
    return list(map(list, itertools.zip_longest(*lst, fillvalue="||")))

def csv_from_flattened_dict(flattened_dict: dict):
    headers = list(flattened_dict.keys())
    csv_matrix = transpose_list(list(flattened_dict.values()))
    return headers, csv_matrix


def save_csv(output_path, headers, csv_matrix):
    with open(output_path, 'w') as f:
        f.write(','.join(headers))
        f.write('\n')
        for row in csv_matrix:
            row = [f'"{str(r)}"' for r in row]
            f.write(f"{','.join(row).replace('||','')}\n")

def main(export_path):
    uuid_metadata_map = create_uuid_metadata_map(f"{export_path}/metadata")
    summary = json.load(open(f"{export_path}/summary.json"))
    map_with_links = add_links(uuid_metadata_map, summary)
    flattened_dict = flatten_map_to_csv(map_with_links)
    for table in flattened_dict:
        headers, csv_matrix = csv_from_flattened_dict(flattened_dict[table])
        save_csv(f"{export_path}/terra_metadata/{table}.csv", headers, csv_matrix)



if __name__ == '__main__':
    main(sys.argv[1])
