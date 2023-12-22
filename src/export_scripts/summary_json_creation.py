import json
import os
import sys

# Relative imports with modules living within a package are a nightmare
SEPARATOR = 'ag2pi-2-ingest/'
CURRENT_PATH = os.getcwd()
SRC_PATH = CURRENT_PATH[:CURRENT_PATH.index(SEPARATOR) + len(SEPARATOR)]

sys.path.insert(0, SRC_PATH)

from src.utilities.ingest_api import ReadyIngestApi
from src.json_cleaner.json_cleaner import JsonCleaner

from collections import defaultdict
from itertools import product

from networkx import parse_adjlist


# Graph implementation for python from https://stackoverflow.com/questions/19472530/representing-graphs-data-structure-in-python
class Graph(object):
    """ Graph data structure, undirected by default. """

    def __init__(self, connections, directed=False):
        self._graph = defaultdict(set)
        self._directed = directed
        self.add_connections(connections)

    def add_connections(self, connections):
        """ Add connections (list of tuple pairs) to graph """

        for node1, node2 in connections:
            self.add(node1, node2)

    def add(self, node1, node2):
        """ Add connection between node1 and node2 """

        self._graph[node1].add(node2)
        if not self._directed:
            self._graph[node2].add(node1)

    def remove(self, node):
        """ Remove all references to node """

        for n, cxns in self._graph.items():  # python3: items(); python2: iteritems()
            try:
                cxns.remove(node)
            except KeyError:
                pass
        try:
            del self._graph[node]
        except KeyError:
            pass

    def is_connected(self, node1, node2):
        """ Is node1 directly connected to node2 """

        return node1 in self._graph and node2 in self._graph[node1]

    def find_path(self, node1, node2, path=[]):
        """ Find any path between node1 and node2 (may not be shortest) """

        path = path + [node1]
        if node1 == node2:
            return path
        if node1 not in self._graph:
            return None
        for node in self._graph[node1]:
            if node not in path:
                new_path = self.find_path(node, node2, path)
                if new_path:
                    return new_path
        return None

    def nodes(self):
        return set(*self._graph.values())

    def find_leaves(self):
        # There are no leaves in a non-directional graph
        if self._directed:
            return set().union(*self._graph.values()).difference(set().union(self._graph.keys()))
        return None

    def find_stems(self):
        # There are no stems in a non-directional graph
        if self._directed:
            return set().union(self._graph.keys()).difference(set().union(*self._graph.values()))
        return None

    def traverse_full_graph(self, nodes, path=[]):
        """
        Given a node, traverse and return the path until the leaves
        :param node:
        :return:
        """
        # Not implementing this now
        if not self._directed:
            return
        path += [nodes]
        for node in nodes:
            if node not in self._graph:
                return path
            path.append(self.traverse_full_graph(self._graph[node], path))
        return path

    def all_subgraphs(self, subgraph=[]):
        stem_nodes = self.find_stems()
        subgraphs = {}
        for node in stem_nodes:
            subgraphs[node]
            while node:
                current_subgraph.append(node)
                node = self._graph[node]
            subgraphs.append(current_subgraph)
        return subgraphs

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, dict(self._graph))


def translate_relationships_ids(relationship, mongo_uuid_map):
    for relation_direction, id_list in relationship.items():
        uuid_list = [mongo_uuid_map[mongo_id] for mongo_id in id_list]
        relationship[relation_direction] = uuid_list
    return relationship


def get_linking_map_with_uuids(linking_map, mongo_uuid_map):
    entity_uuid_linking = {}
    for domain_type, mongo_ids in linking_map.items():
        if domain_type == 'processes':
            continue
        for mongo_id, relationship in mongo_ids.items():
            uuid = mongo_uuid_map[mongo_id]
            entity_uuid_linking[uuid] = translate_relationships_ids(relationship, mongo_uuid_map)
    return entity_uuid_linking

def get_mongo_uuid_map(api: ReadyIngestApi, submission):
    submission_url = submission['_links']['self']['href']
    mongo_uuid_map = {}
    for entity_type in ['biomaterials', 'projects', 'files', 'protocols', 'processes']:
        entities = api.get_entities(submission_url, entity_type, entity_type)
        for entity in entities:
            mongo_id = entity['_links']['self']['href'].split('/')[-1]
            uuid = entity['uuid']['uuid']
            mongo_uuid_map[mongo_id] = uuid
    return mongo_uuid_map


def generate_process_entities_map(entity_uuid_linking: dict, relation: str) -> dict:
    """
    Given a relation (derivedByProcesses, inputToProcesses) generate a {process_uuid: [entities_uuid]} map
    :param entity_uuid_linking:
    :param relation:
    :return:
    """
    process_entities_map = {}
    for entity, relations in entity_uuid_linking.items():
        for derivedBy in relations[relation]:
            if derivedBy not in process_entities_map.keys():
                process_entities_map[derivedBy] = []
            process_entities_map[derivedBy].append(entity)
    return process_entities_map

def generate_relation_pairs(entities_output_map, entities_input_map):
    relation_pairs_all = []
    for process_uuid, input_entities in entities_input_map.items():
        output_entities = entities_output_map.get(process_uuid)
        if output_entities:
            relation_pairs_sub = product(output_entities, input_entities)
            relation_pairs_all.extend(relation_pairs_sub)

    return relation_pairs_all

def skip_processes_in_map(entity_uuid_linking: dict):
    """
    Create a graph based solely on the entities populating it, skipping the processes (Not valuable for AG2PI purposes).

    The algorithm for this is:
        - Get a dictionary that has a process_uuid: [entities_output] structure
        - Get a dictionary that has a process_uuid: [entities_input] structure
        - Get a list of [ [ [entities_input], [entities_derived_from] ] ]
        - Demultiplex that list, creating a "simple" [[ entity_input, entity_output ]] list
        - Generate a graph with the class above


    :param entity_uuid_linking:
    :return:
    """

    entities_output_map = generate_process_entities_map(entity_uuid_linking, 'derivedByProcesses')
    entities_input_map = generate_process_entities_map(entity_uuid_linking, 'inputToProcesses')
    relation_pairs = generate_relation_pairs(entities_output_map, entities_input_map)
    graph = Graph(relation_pairs)




    keys = list(entity_uuid_linking.keys())



def replace_processes_with_entities(entity_process_map: dict, input_maps: dict, derived_maps: dict):
    final_map = {}
    for entity_uuid, relations in entity_process_map.items():
        if entity_uuid not in final_map:
            final_map[entity_uuid] = {'derivedInto': [], 'derivedFrom': []}

        for input_relation in relations['derivedByProcesses']:
            input_r = input_maps.get(input_relation, [])
            final_map[entity_uuid]['derivedFrom'].extend(input_r)

        for output_relation in relations['inputToProcesses']:
            output_r = derived_maps.get(output_relation, [])
            final_map[entity_uuid]['derivedInto'].extend(output_r)

    return final_map



def main(submission_uuid, terra_staging_path):
    api = ReadyIngestApi()
    # API object needs an extra header: 'accept'. Linking map will not return in json unless it's specified.
    # There is no function to set headers with this parameter.
    api.headers['accept'] = 'application/hal+json'
    submission = api.get_submission_by_uuid(submission_uuid)
    linking_map = api.get(submission['_links']['linkingMap']['href']).json()
    mongo_uuid_map = get_mongo_uuid_map(api, submission)
    entity_uuid_linking = get_linking_map_with_uuids(linking_map, mongo_uuid_map)
    derived_by = generate_process_entities_map(entity_uuid_linking, 'derivedByProcesses')
    input_to = generate_process_entities_map(entity_uuid_linking, 'inputToProcesses')
    entity_uuid_linking = replace_processes_with_entities(entity_uuid_linking, input_to, derived_by)
    cleaner = JsonCleaner(entity_uuid_linking)
    cleaner.save(f"{terra_staging_path}/summary.json")




if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])