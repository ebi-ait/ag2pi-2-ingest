# ag2pi-2-ingest
Repository dedicated to the tool development necessary to ingest datasets from the AG2PI into ingest and, finally, into terra.

The folders contain the following:

## examples
Example pig dataset - Contains the input given (In JSON format) and the output files after being cleaned and split
(output). 

For each of the entities present in the input, they have been split up, and given a name based on the sample names (+ type) or the file name.

## src
All the scripts and code written is deposited here - There are 2 main folders:

### json_cleaner
A small class has been written to deal with JSON parsing and operations - Currently, it is able to:
- Add a new field with any value
- Delete null values
- Return the value of a field given a full qualified key
- Replace all values that match a value provided

### utilities
Small scripts, written to help deal with some tasks.

- clean_data.py: Given an input and an output path, read all the JSON files and perform clean-up. The clean-up performed depends on the file, but it can be resumed in:
   * Add missing fields (e.g. `describedBy`)
   * Delete null values
   * Replace values when there is a typo or the value is not allowed
- create_submission.py: Given a project UUID, create an empty submission and link it to that project.
- submit_entities.py: Given an input path with all the entities ready to submit (Post clean-up), and a submission URL (API link), submit the entities to the submission for validation.
- clear_entities.py: Given a submission link, delete all the biomaterials and files present in the submission.

In the next section, there will be a brief "How to" on how to use these scripts for testing, as well as how to validate the entities against the custom schemas.

## How to create a submission

TBD


## Questions

- is there any link (aka, link between samples and files) in the metadata? I've seen the same metadata (e.g. project, secondary project) repeated, which could be avoided
- project information in json format?
# - What types is each of these?
#- Have you thought about the data model? e.g. In the HCA, we have donor, specimen, cell suspension etc
- Where are the data files? 