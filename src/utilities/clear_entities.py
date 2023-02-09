import os

from hca_ingest.api.ingestapi import IngestApi

INGEST_TOKEN = os.getenv('INGEST_TOKEN') or "Bearer <token>"

def set_ingestapi():
    api = IngestApi("https://api.ingest.staging.archive.data.humancellatlas.org/")
    print(api.set_token(INGEST_TOKEN))
    return api


def main(submission_uuid):
    api = set_ingestapi()
    project = api.get_project_by_uuid('114d1511-0e8c-4d04-a932-bf45b63b283f')
    #submission = api.get_submission_by_uuid(submission_uuid)
    #api.delete(submission['_links']['self']['href'])
    new_submission = api.create_submission()
    new_submission['uuid']['uuid'] = submission_uuid
    submission = api.put(new_submission['_links']['self']['href'], json=new_submission).json()
    api.link_entity(from_entity=project, to_entity=submission, relationship='submissionEnvelopes')


if __name__ == "__main__":
    main('a57eaa06-a212-4993-93c8-df3293a1fd42')