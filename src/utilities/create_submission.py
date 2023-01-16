import sys
import os

from hca_ingest.api.ingestapi import IngestApi

INGEST_TOKEN = os.getenv('INGEST_TOKEN') or "Bearer <token>"

def main():
    uuid = sys.argv[1]
    api = IngestApi(url="https://api.ingest.staging.archive.data.humancellatlas.org/")
    api.set_token(INGEST_TOKEN)
    submission = api.create_submission()
    project = api.get_project_by_uuid(uuid)
    api.link_entity(project, submission, "submissionEnvelopes")
    print(submission['_links']['self']['href'])



if __name__ == '__main__':
    main()