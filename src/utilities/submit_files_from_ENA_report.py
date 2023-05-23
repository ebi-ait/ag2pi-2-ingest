import sys
import os
import requests

from copy import deepcopy

sys.path.insert(0, '/Users/enrique/HumanCellAtlas/ag2pi-2-ingest/src')
from utilities.file_reader import fileReader
from hca_ingest.api.ingestapi import IngestApi

INGEST_TOKEN = os.getenv('INGEST_TOKEN') or "Bearer <token>"

def set_ingestapi():
    api = IngestApi("https://api.ingest.staging.archive.data.humancellatlas.org/")
    api.set_token(INGEST_TOKEN)
    return api

def read_ena_json_report(project_accession):
    r = requests.get(f" https://www.ebi.ac.uk/ena/portal/api/filereport?accession={project_accession}&result=read_run&fields=study_accession,sample_accession,experiment_accession,run_accession,tax_id,scientific_name,fastq_ftp,submitted_ftp,sra_ftp&format=json&download=true&limit=0")
    json_report = r.json()
    return json_report

def translate_report_to_hca_metadata(json_report, base_sequence_file):
    sequence_files = {}
    for file_report in json_report:
        sequence_files[file_report['sample_accession']] = []
        files = file_report['submitted_ftp'].split(';')
        for file in files:
            base_sequence_file['file_core']['file_name'] = file.split('/')[-1]
            base_sequence_file['insdc_run_accessions'] = [file_report['run_accession']]
            base_sequence_file['library_prep_id'] = file_report['sample_accession']
            base_sequence_file['read_index'] = "read1" if file.split('/')[-1].split('_')[-2] == "R1" else "read2"
            sequence_files[file_report['sample_accession']].append(deepcopy(base_sequence_file))
    return sequence_files


def submit_file(api: IngestApi, submission: dict, file_content: dict):
    submission_url = submission['_links']['self']['href']
    filename = file_content['file_core']['file_name']
    return api.create_file(submission_url, filename, file_content)


def create_process(api: IngestApi, process_id: str, base_process_content: dict, submission: dict):
    base_process_content['process_core']['process_id'] = process_id
    submission_url = submission['_links']['self']['href']
    ingest_process = api.create_process(submission_url, base_process_content)
    return ingest_process

def link_files_with_process(api: IngestApi, files_ingest: list, ingest_process):
    for file in files_ingest:
        api.link_entity(from_entity=file, to_entity=ingest_process, relationship='derivedByProcesses')


def link_biomaterials_with_process(api: IngestApi, biomaterials: list, ingest_process: dict):
    for biomaterial in biomaterials:
        if biomaterial['content'].get('custom').get('sample_descriptor', {}).get('value') == ingest_process['content']['process_core']['process_id']:
            api.link_entity(from_entity=biomaterial, to_entity=ingest_process, relationship='inputToProcesses')
            break


def submit_files_and_processes(api: IngestApi, submission, sequence_files: dict, examples_path:str):
    base_process = fileReader.read_file(os.path.join(examples_path, 'base_process/base_process.json'))
    biomaterials = list(api.get_entities(submission['_links']['self']['href'], 'biomaterials', 'biomaterials'))
    for process_id, files in sequence_files.items():
        files_ingest = []
        for file in files:
            files_ingest.append(submit_file(api, submission, file))
        ingest_process = create_process(api, process_id, base_process, submission)
        link_files_with_process(api, files_ingest, ingest_process)
        link_biomaterials_with_process(api, biomaterials, ingest_process)


def discard_processes_without_inputs(api: IngestApi, submission: dict):
    processes = list(api.get_entities(submission['_links']['self']['href'], 'processes', 'processes'))
    for p in processes:
        if "process_id" in p['content']['process_core']['process_id']:
            continue
        inputBiomat = api.get(p['_links']['inputBiomaterials']['href']).json()
        if not inputBiomat.get('_embedded'):
            files = api.get(p['_links']['derivedFiles']['href']).json()['_embedded']['files']
            for file in files:
                api.delete(file['_links']['self']['href'])
            api.delete(p['_links']['self']['href'])


def extract_bsd_accession_from_filenames(path):
    accessions = [filename.split('_')[0] for filename in os.listdir(path) if "SAMEA" in filename]
    return accessions


def filter_accessions_from_report(json_report, whitelist=(), blacklist=()):
    filtered_accessions = json_report
    filtered_accessions = [file_metadata for file_metadata in filtered_accessions if file_metadata['sample_accession']
                               in whitelist]
    return filtered_accessions


def main(submission_uuid, ena_project_accession, examples_path):
    # Find which files are scRNA seq
    biosamples_accessions = extract_bsd_accession_from_filenames(f"{os.path.join(examples_path, 'output')}")

    json_report = read_ena_json_report(ena_project_accession)

    json_report = filter_accessions_from_report(json_report, biosamples_accessions)

    base_sequence_file = fileReader.read_file(os.path.join(examples_path, "base_sequence_file/base_sequence_file.json"))
    sequence_files = translate_report_to_hca_metadata(json_report, base_sequence_file)
    api = set_ingestapi()
    submission = api.get_submission_by_uuid(submission_uuid)
    submit_files_and_processes(api, submission, sequence_files, examples_path)
    discard_processes_without_inputs(api, submission)



if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])