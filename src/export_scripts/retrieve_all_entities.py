import sys
import os

from hca_ingest.downloader.schema_url import SchemaUrl

# Relative imports with modules living within a package are a nightmare
SEPARATOR = 'ag2pi-2-ingest/'
CURRENT_PATH = os.getcwd()
SRC_PATH = CURRENT_PATH[:CURRENT_PATH.index(SEPARATOR) + len(SEPARATOR)]

sys.path.insert(0, SRC_PATH)

from src.utilities.ingest_api import ReadyIngestApi
from src.json_cleaner.json_cleaner import JsonCleaner

ACCEPTED_DOMAINS = ["biomaterials", "protocols", "processes", "files", "projects"]


def get_entities_from_submission(api: ReadyIngestApi, submission: dict):
    entities = []
    for domain in ACCEPTED_DOMAINS:
        entities.extend(list(api.get_entities(submission['_links']['self']['href'], domain, domain)))

    return entities


def write_entities_in_terra_format(entities, output_path):
    for entity in entities:
        full_output_path = os.path.join(output_path, 'metadata')
        if not os.path.exists(full_output_path):
            os.mkdir(full_output_path)
        entity_name = f"{entity['uuid']['uuid']}.json"
        JsonCleaner(entity['content']).save(os.path.join(full_output_path, entity_name))


def write_mongodb_id_to_uuid_map(entities, output_path):
    id_uuid_map = {}
    for entity in entities:
        mongo_id = entity['_links']['self']['href'].split('/')[-1]
        id_uuid_map[mongo_id] = entity['uuid']['uuid']
    JsonCleaner(id_uuid_map).save(os.path.join(output_path, "mongodb_map.json"))

def main(submission_uuid, output_path):
    api = ReadyIngestApi()
    submission = api.get_submission_by_uuid(submission_uuid)
    entities = get_entities_from_submission(api, submission)
    write_entities_in_terra_format(entities, output_path)
    write_mongodb_id_to_uuid_map(entities, output_path)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
