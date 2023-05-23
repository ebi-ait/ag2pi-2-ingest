import os

from hca_ingest.api.ingestapi import IngestApi

INGEST_TOKEN = os.getenv('INGEST_TOKEN') or "Bearer <token>"

def set_ingestapi():
    api = IngestApi("https://api.ingest.staging.archive.data.humancellatlas.org/")
    print(api.set_token(INGEST_TOKEN))
    return api


def main(submission_uuid):
    api = set_ingestapi()
    submission = api.get_submission_by_uuid(submission_uuid)
    processes = api.get_entities(submission['_links']['self']['href'], 'processes', 'processes')
    for p in processes:
        api.delete(p['_links']['self']['href'])


if __name__ == "__main__":
    main('731983aa-19ef-405a-8233-db9cd31eb2fd')