import os

from hca_ingest.api.ingestapi import IngestApi

INGEST_TOKEN = os.getenv('INGEST_TOKEN') or "Bearer <token>"

def set_ingestapi():
    api = IngestApi("https://api.ingest.staging.archive.data.humancellatlas.org/")
    api.set_token(INGEST_TOKEN)
    return api


def main(submission_uuid):
    api = set_ingestapi()
    biomaterials = list(api.get_entities(f"https://api.ingest.staging.archive.data.humancellatlas.org/submissionEnvelopes/63c56a0947199518779d4634", "biomaterials", "biomaterials"))
    files = list(api.get_entities(f"https://api.ingest.staging.archive.data.humancellatlas.org/submissionEnvelopes/63c56a0947199518779d4634", "files", "files"))
    for b in biomaterials:
        api.delete(b['_links']['self']['href'])
    for f in files:
        api.delete(f['_links']['self']['href'])


if __name__ == "__main__":
    main('e9d037d1-d759-4438-ba54-668ec2ec5495')