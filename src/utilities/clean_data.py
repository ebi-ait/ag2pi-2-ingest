import os
import sys
import json

sys.path.insert(0, '/Users/enrique/HumanCellAtlas/ag2pi-2-ingest/src')

from json_cleaner.json_cleaner import JsonCleaner

def main(input_path, output_path):
    for file in os.listdir(input_path):
        if os.path.isdir(f"{input_path}/{file}"):
            continue
        with open(f"{input_path}/{file}", 'r') as f:
            data = json.load(f)
    # scRNA-seq.json
        if "scRNA" in file:
            for scrna in data['scrna-seq']:
                cleaner = JsonCleaner(scrna)
                cleaner.add_field("https://raw.githubusercontent.com/FAANG/dcc-metadata/hca/json_schema/type/experiments/faang_experiments_scrna-seq.metadata_rules.json", "describedBy")
                cleaner.clean_null_values()
                cleaner.replace_all_values("10X v3.1", "10X v3")
                cleaner.replace_all_values("second(sense)", "second (sense)")
                cleaner.save(os.path.join(output_path, f"{scrna['custom']['sample_descriptor']['value']}_scrna.json"))
    # samples.json
        if "samples" in file:
            for donor in data['organism']:
                # Needs to add value (describedBy)
                cleaner = JsonCleaner(donor)
                cleaner.add_field("https://raw.githubusercontent.com/FAANG/dcc-metadata/hca/json_schema/type/samples/faang_samples_organism.metadata_rules.json", "describedBy")
                cleaner.clean_null_values()
                cleaner.save(os.path.join(output_path, f"{donor['custom']['sample_name']['value']}_donor.json"))
            for specimen in data['specimen_from_organism']:
                cleaner = JsonCleaner(specimen)
                cleaner.add_field("https://raw.githubusercontent.com/FAANG/dcc-metadata/hca/json_schema/type/samples/faang_samples_specimen.metadata_rules.json", "describedBy")
                cleaner.clean_null_values()
                cleaner.save(os.path.join(output_path, f"{specimen['custom']['sample_name']['value']}_specimen.json"))
            for cell_specimen in data['cell_specimen']:
                cleaner = JsonCleaner(cell_specimen)
                cleaner.add_field("https://raw.githubusercontent.com/FAANG/dcc-metadata/hca/json_schema/type/samples/faang_samples_single_cell_specimen.metadata_rules.json", "describedBy")
                cleaner.clean_null_values()
                cleaner.add_field("{'value': 'fluids'}", 'tissue_dissociation')
                cleaner.add_field("{'value': 'centrifugation'}", 'cell_enrichment')
                cleaner.add_field("{'value': 'https://data.faang.org/api/fire_api/samples/ISU_SOP_sorting_swine_immune_cells_20210113.pdf'}", 'single_cell_isolation_protocol')
                cleaner.save(os.path.join(output_path, f"{cell_specimen['custom']['sample_name']['value']}_cell_specimen.json"))
    # analysis.json
        if 'analysis' in file:
            for analysis in data['faang_hca']:
                cleaner = JsonCleaner(analysis)
                cleaner.add_field("https://raw.githubusercontent.com/FAANG/dcc-metadata/hca/json_schema/type/analyses/faang_analyses_faang_hca.metadata_rules.json", "describedBy")
                cleaner.clean_null_values()
                cleaner.replace_all_values("CellRanger v4.0.0", "cell ranger")
                cleaner.replace_all_values(".h5seurat", "h5seurat")
                cleaner.save(f"/Users/enrique/HumanCellAtlas/ag2pi-2-ingest/examples/input/clean_datasets/{analysis['alias']['value']}_{analysis['analysis_file_name']['value']}.json")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
