# Using the Sample Resource file

Download it from:
* https://sourceforge.net/projects/fhirloinc2sdtm/files/LZZT_Study_Bundle/

## Patching and splitting the file
There are a couple of changes made to the sample resource file including:
* Use Subject ID for the ResearchSubject ID, rather than the Patient ID
* Ensure the IDs are unique

Run the script:
```
python patch_json.py LZZT_FHIR_Bundle_10_Patients_All_Resources.json subjects
```

It will generate a file per subject in a subjects subdirectory.

The files herein are:
* [LZZT_FHIR_Bundle_10_Patients_All_Resources.json]() - the source FHIR bundled copied from the link above
* [LZZT_FHIR_Bundle_10_Patients_All_Resources_Patched.json]() - the patched FHIR bundle

## Adding the encounters 

The subjects can have one or more Encounters merged into the file using the **SV** domain as a source; 

In this case the subject bundles are in the `subjects` subdirectory.
```shell
python add_visits.py subjects_31
```

example output is:
```
Processing file: subjects_31/LZZT_FHIR_Bundle_01-701-1115_All_Resources.json
Processing patient 01-701-1115 -> 1.0
Adding resource to bundle: CarePlan
Adding resource to bundle: ServiceRequest
Adding resource to bundle: Encounter
Processing patient 01-701-1115 -> 2.0
Adding resource to bundle: CarePlan
Adding resource to bundle: ServiceRequest
Adding resource to bundle: Encounter
Processing patient 01-701-1115 -> 3.0
Adding resource to bundle: CarePlan
Adding resource to bundle: ServiceRequest
Adding resource to bundle: Encounter
```

## Adding the medications 

The subjects can have medications added for the subject

### Using MedicationAdministration Records
In this case the subject bundles are in the `subjects` subdirectory.
```shell
python add_medications.py subjects_31
```

This will clone the subject to a subject ID + 1000 (ie 2028)

Output will look something like the following
```
```

### Using MedicationStatement Records
In this case the subject bundles are in the `subjects` subdirectory.
```shell
python add_medication_statements.py subjects_31
```

This will clone the subject to a subject ID + 2000 (ie 3028)

Output will look something like the following
```
```

## Cloning a Research Subject
A subject bundle can be cloned into a new file using the following command:

```shell
python clone_subject.py --subject-id 01-701-9998 subjects/LZZT_FHIR_Bundle_01-701-1118_All_Resources.json
```

## Synthea Data

You can use the **Synthea** data to add resources for a subject.  In this case we use a script to add Observation Resources

1. Download the dataset from: [Synthea Synthetic Data](https://github.com/synthetichealth/synthea-sample-data)
2. Extact the zip file, record the path to the extracted files 
3. Create a `.env` file with the following variables:
    ```dotenv
    SYNTHEA_DATA_DIR=/path/to/synthea-sample-data
    ```
4. Run the script (in this example we add 10 lab results for one subject)
    ```
    python add_random_obs.py -f subjects/LZZT_FHIR_Bundle_01-701-9999_All_Resources.json -n 10 -t laboratory
    ```
