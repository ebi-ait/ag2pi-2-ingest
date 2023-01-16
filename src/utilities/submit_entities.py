import json
import os
import sys

from hca_ingest.api.ingestapi import IngestApi

INGEST_TOKEN = os.getenv('INGEST_TOKEN') or "Bearer <token>"

def set_ingestapi():
    api = IngestApi("https://api.ingest.staging.archive.data.humancellatlas.org/")
    api.set_token(INGEST_TOKEN)
    return api

def submit_entity(api: IngestApi, content, entity_type, submission):
    api.create_entity(submission['_links']['self']['href'], content, entity_type)

def read_files(path):
    files = os.listdir(path)

    json_content = []
    for file in files:
        with open(f"{path}/{file}", 'r') as f:
            json_content.append(json.load(f))
    return json_content


def main(path, submission_uuid):
    json_content = read_files(path)
    ingest_api = set_ingestapi()
    submission = ingest_api.get_submission_by_uuid(submission_uuid)
    for entity in json_content:
        if "analyses" in entity['describedBy']:
            ingest_api.create_file(submission['_links']['self']['href'], entity['analysis_file_name']['value'], entity)
        else:
            ingest_api.create_biomaterial(submission['_links']['self']['href'], entity)


if __name__ == "__main__":
    main(sys.argv[1], 'a57eaa06-a212-4993-93c8-df3293a1fd42')