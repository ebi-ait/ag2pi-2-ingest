import sys
import os

from hca_ingest.api.ingestapi import IngestApi

sys.path.insert(0, '/Users/enrique/HumanCellAtlas/ag2pi-2-ingest/src')
from utilities.file_reader import fileReader

INGEST_TOKEN = os.getenv('INGEST_TOKEN') or "Bearer <token>"

def set_ingestapi():
    api = IngestApi("https://api.ingest.staging.archive.data.humancellatlas.org/")
    api.set_token(INGEST_TOKEN)
    return api

def get_all_biomaterials_from_submission(api: IngestApi, submission_url):
    biomaterials = api.get_entities(submission_url, 'biomaterials', 'biomaterials')

    return list(biomaterials)


def discard_primary_entities(entity_list):
    return [e for e in entity_list if e.get('content').get('derived_from')]

def map_from_entities(derived_entities, biomaterial_uuid_map):
    process_map = {}
    for e in derived_entities:

        process_map[biomaterial_uuid_map[e['content']['custom']['sample_name']['value']]] = {'derived_from': biomaterial_uuid_map[e['content']['derived_from']['value']],
                                                            'process': ''}
    return process_map


def create_processes_from_map(api: IngestApi, process_mapping, submission_url, examples_path):
    base_process = fileReader.read_file(os.path.join(examples_path, "base_process/base_process.json"))
    for i, link in enumerate(process_mapping.keys()):
        base_process['process_core']['process_id'] = f"process_id_{i}"
        proc = api.create_process(submission_url, base_process)
        process_mapping[link]['process'] = proc
    return process_mapping


def construct_biomaterial_uuid_mapping(biomaterial_list):
    biomaterial_uuid_map = {}
    for b in biomaterial_list:
        if b['content']['custom'].get('sample_name'):
            biomaterial_uuid_map[b['content']['custom']['sample_name']['value']] = b['uuid']['uuid']
        else:
            biomaterial_uuid_map[b['content']['custom']['sample_descriptor']['value']] = b['uuid']['uuid']
    return biomaterial_uuid_map


def link_entities_with_process(process_mapping, api: IngestApi):
    for from_entity_uuid, link_params in process_mapping.items():
        from_entity = api.get_entity_by_uuid('biomaterials', from_entity_uuid)
        process = link_params['process']
        to_entity = api.get_entity_by_uuid('biomaterials', link_params['derived_from'])
        api.link_entity(from_entity=to_entity, to_entity=process, relationship='derivedByProcesses')
        api.link_entity(from_entity=from_entity, to_entity=process, relationship='inputToProcesses')


def main(submission_uuid, examples_path):
    api = set_ingestapi()
    submission_url = api.get_submission_by_uuid(submission_uuid)['_links']['self']['href']
    json_entities = get_all_biomaterials_from_submission(api, submission_url)
    biomaterial_uuid_map = construct_biomaterial_uuid_mapping(json_entities)
    derived_entities = discard_primary_entities(json_entities)
    process_mapping = map_from_entities(derived_entities, biomaterial_uuid_map)
    process_mapping_with_processes = create_processes_from_map(api, process_mapping, submission_url, examples_path)
    link_entities_with_process(process_mapping, api)

    fileReader.save_file(process_mapping_with_processes, 'test_map.json')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])


