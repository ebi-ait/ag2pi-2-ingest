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


def link_biomat_with_files(api: IngestApi, processes, biomaterials):
    for p in processes:
        if "process_" not in p['content']['process_core']['process_id']:
            for biomaterial in biomaterials:
                if biomaterial['content'].get('custom').get('sample_descriptor', {}).get('value') == p['content']['process_core']['process_id']:
                    api.link_entity(from_entity=biomaterial, to_entity=p, relationship='inputToProcesses')



def main(submission_uuid):
    api = set_ingestapi()
    submission = api.get_submission_by_uuid(submission_uuid)
    submission_url = submission['_links']['self']['href']
    processes = list(api.get_entities(submission_url, 'processes', 'processes'))
    biomaterials = list(api.get_entities(submission_url, 'biomaterials', 'biomaterials'))
    link_biomat_with_files(api, processes, biomaterials)

if __name__ == '__main__':
    main(sys.argv[1])