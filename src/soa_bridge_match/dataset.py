from __future__ import annotations
from datetime import date
import datetime
import pandas as pd
import hashlib
from math import floor
import random
import time
from typing import Optional

from fhir.resources.bundle import Bundle
from fhir.resources.careplan import CarePlan
from fhir.resources.coding import Coding
from fhir.resources.encounter import Encounter
from fhir.resources.identifier import Identifier
from fhir.resources.patient import Patient
from fhir.resources.period import Period
from fhir.resources.reference import Reference
from fhir.resources.servicerequest import ServiceRequest
from fhir.resources.medicationadministration import MedicationAdministration
from fhir.resources.medicationrequest import MedicationRequest


from .bundler import SourcedBundle
from .connector import Connector


def hh(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


class Naptha:
    def __init__(
        self, templatefile: Optional[str], 
        templatecontent: Optional[Bundle] = None
    ) -> None:
        self._connector = Connector()
        self._subjects = {}
        self._patients = {}
        self._subjects = {}
        self._synthea = None
        # load the template
        if templatecontent:
            self._content = templatecontent
        else:
            self._content = SourcedBundle.from_bundle_file(templatefile)

    @property
    def content(self):
        return self._content

    def dump(self, target_dir: Optional[str] = None, name_suffix: Optional[str] = None):
        self._content.dump(target_dir, name_suffix)

    def get_subjects(self):
        """
        Get the list of subjects from the CDISC Pilot Dataset
        """
        dataset = self._connector.load_cdiscpilot_dataset("DM")
        return dataset.USUBJID.unique()

    def get_subject_data(self, subject_id: str, domain: str):
        """
        Get the data for a subject for a given domain
        """
        if subject_id not in self.get_subjects():
            raise ValueError(f"Subject {subject_id} does not exist")
        dataset = self._connector.load_cdiscpilot_dataset(domain)
        dataset = dataset[dataset.USUBJID == subject_id]
        return dataset

    def get_subject_cm(self, subject_id: str):
        """
        Get the demographics for a subject from the dataset
        """
        return self.get_subject_data(subject_id, "CM")

    def get_subject_ex(self, subject_id: str):
        """
        Get the exposure for a subject from the dataset
        """
        return self.get_subject_data(subject_id, "EX")

    def get_subject_dm(self, subject_id: str):
        """
        Get the demographics for a subject from the dataset
        """
        return self.get_subject_data(subject_id, "DM")

    def get_subject_sv(self, subject_id: str):
        """
        Get the demographics for a subject from the dataset
        """
        return self.get_subject_data(subject_id, "SV")

    # def parse_dataset(self, dataset_name: str):
    #     """
    #     Parse a CDISC Pilot Dataset
    #     """
    #     if not os.path.exists(os.path.join("../../doc/config", f"{dataset_name}.yml")):
    #         print("Unable to process configuration file")
    #     config = Configuration.from_file(os.path.join("../../doc/config", f"{dataset_name}.yml"))
    #     _columns = [x for x in config.columns()]
    #     dataset = self._connector.load_cdiscpilot_dataset(dataset_name)
    #     for offset, record in enumerate(dataset.iterrows()):
    #         # generate a patient resource
    #         patient = self._generate_patient(record.USUBJID)
    #         # generate a bundle
    #         bundle = Bundle()
    #         # add the patient to the bundle
    #         bundle.add_entry(patient)
    #         # add the bundle to the content
    #         self.content.add_entry(bundle)

    # def _generate_patient(self, subject_id: str) -> Patient:
    #     """
    #     Generate a Patient resource
    #     """
    #     # Use a hash id for the Patient Resource
    #     _patient_id = hashlib.md5(subject_id.encode('utf-8')).hexdigest()
    #     dm = self.get_subject_dm(subject_id)
    #     patient = Patient(id=_patient_id)
    #     return patient

    def clone(self, subject_id: str) -> Naptha:
        cloned = self._content.clone_subject(subject_id)
        return Naptha(templatefile=None, templatecontent=cloned)

    def merge_ex(self, subject_id: Optional[str] = None):
        """
        Merge a dataset into the template
        """
        if subject_id is None:
            for _subject_id in self.get_subjects():
                self.merge_ex(_subject_id)
            else:
                return
        if subject_id not in self.get_subjects():
            raise ValueError(f"Subject {subject_id} does not exist")
        print("Adding medications for {}".format(subject_id))
    
        patient_hash_id = hh(subject_id)
        # get the set of records for a subject
        ex = self.get_subject_ex(subject_id)
        dm = self.get_subject_dm(subject_id)
        sv = self.get_subject_sv(subject_id)
        # get the arm
        arm = dm.ARMCD.unique()[0]
        # Medication Request
        medication = {
            "Pbo": "H2Q-MC-LZZT-LY246708-1",
            "Xan_Hi": "H2Q-MC-LZZT-LY246708-3",
            "Xan_Lo": "H2Q-MC-LZZT-LY246708-2",
            "Scrnfail": "",
        }
        records = []
        # get the medication request
        for offset, record in ex.iterrows():
            if pd.isna(record.EXENDTC):
                print("Subject", subject_id, f"has missing end date at {offset}")
                continue
            delta = (record.EXENDTC - record.EXSTDTC).days
            print(f"Adding medication for {subject_id} from {record.EXSTDTC} to {record.EXENDTC} ({delta} days)")
            if not isinstance(delta, (int, )):
                print("Subject", subject_id, f"has a weird delta for {record.EXSEQ} Start {record.EXSTDTC} End {record.EXENDTC}")
                delta = floor(delta)
            _mr_id = hh(f"{subject_id}-{record.EXSEQ}")
            # medication_request = MedicationRequest(id=_mr_id)
            for dt in range(delta):
                _date = record.EXSTDTC + datetime.timedelta(days=dt)
                _id = hh(f"{subject_id}-{record.EXSEQ}-{dt}")
                _stt = datetime.datetime.combine(_date, datetime.time(8, 0, 0))
                # add a little variation around the start/end for the medication
                if time.time() % 2 == 0:
                    _start_time =  _stt - datetime.timedelta(
                        minutes=random.randint(0, 60)
                    )
                else:
                    _start_time =  _stt - + datetime.timedelta(
                        minutes=random.randint(0, 60)
                    )
                medication_admin = MedicationAdministration(
                    id=_id,
                    status="completed",
                    medicationReference=Reference(
                        reference=f"Medication/{medication[arm]}"
                    ),
                    subject=Reference(reference=f"Patient/{patient_hash_id}"),
                    effectivePeriod=Period(
                        start = _start_time,
                        end = _start_time + datetime.timedelta(hours=12),
                    ),
                )
                # get the medication request
                # medication_request = self._generate_medication_request(subject_id, _date, medication[arm])
                # add the medication request to the content
                # self.content.add_entry(medication_request)
                records.append(medication_admin)
        print(f"Generated {len(records)} medication administrations for {subject_id}")
        for record in records:
            self.content.add_resource(record)
        print("Done")

    def merge_unscheduled_visit(self, subject_id: str, visit_num: str):
        """
        Add an unscheduled visit for an individual
        """
        if subject_id not in self.get_subjects():
            raise ValueError(f"Subject {subject_id} does not exist")
        plan_def_id = "H2Q-MC-LZZT-Study-Unscheduled-Visit"
        # slice the dataset
        sv = self.get_subject_sv(subject_id)
        prior_visit = visit_number.split(".")[0]
        before = sv[sv.VISITNUM == prior_visit]["SVSTDTC"].values[0]     
        visdt = before + datetime.timedelta(days=random.randint(1, 7)))   
        # generate the careplan
        care_plan_description = f"{patient_hash_id}-{visit_num}-CarePlan"
        care_plan_id = hh(care_plan_description)
        # create a care plan
        care_plan = CarePlan(
            id=care_plan_id,
            status="completed",
            intent="order",
            subject=Reference(reference=f"Patient/{patient_hash_id}"),
            instantiatesCanonical=[f"PlanDefinition/{plan_def_id}"],
            title=f"Subject {record.USUBJID} {visit_num}",
        )
        care_plan.identifier = [Identifier(value=care_plan_description)]
        # bind the care plan - todo!
        # create the service request
        service_request_description = (
            f"{patient_hash_id}-{visit_num}-ServiceRequest"
        )
        service_request_id = hh(service_request_description)
        service_request = ServiceRequest(
            id=service_request_id,
            status="completed",
            intent="order",
            subject=Reference(reference=f"Patient/{patient_hash_id}"),
            basedOn=[Reference(reference=f"CarePlan/{care_plan_id}")],
        )
        service_request.identifier = [
            Identifier(value=f"{service_request_description}")
        ]
        encounter = Encounter(
            id=hh(f"{care_plan_id}-{record.VISITNUM}-Encounter"),
            status="finished",
            class_fhir=Coding(code="IMP", system="http://hl7.org/fhir/v3/ActCode"),
            subject=Reference(reference=f"Patient/{patient_hash_id}"),
            basedOn=[Reference(reference=f"ServiceRequest/{service_request_id}")],
        )
        encounter.identifier = [Identifier(value=f"{care_plan_id}-Encounter")]
        period = {}
        period["start"] = visdt
        period["end"] = visdt
        encounter.period = Period(**period)
        # later
        # encounter.serviceProvider = Reference(reference=f"Organization/{self.org_id}")
        self.content.add_resource(care_plan)
        self.content.add_resource(service_request)
        self.content.add_resource(encounter)
        # add the observations
        

    def merge_sv(self, subject_id: Optional[str] = None):
        """
        Parse the SV dataset for a subject
        """
        if subject_id is None:
            for _subject_id in self.get_subjects():
                self.merge_sv(_subject_id)
            else:
                return
        if subject_id not in self.get_subjects():
            raise ValueError(f"Subject {subject_id} does not exist")
        # the bundle will include the ResearchStudy, ResearchSubject, and Patient resources
        patient_hash_id = hh(subject_id)
        # slice the dataset
        sv = self.get_subject_sv(subject_id)
        pd_map = {
            "1.0": "H2Q-MC-LZZT-Study-Visit-1",
            "2.0": "H2Q-MC-LZZT-Study-Visit-2",
            "3.0": "H2Q-MC-LZZT-Study-Visit-3",
            "3.5": "H2Q-MC-LZZT-Study-Visit-3A",
            "4.0": "H2Q-MC-LZZT-Study-Visit-4",
            "5.0": "H2Q-MC-LZZT-Study-Visit-5",
            "6.0": "H2Q-MC-LZZT-Study-Visit-6",
            "7.0": "H2Q-MC-LZZT-Study-Visit-7",
            "8.0": "H2Q-MC-LZZT-Study-Visit-8",
            "8.1": "H2Q-MC-LZZT-Study-Visit-8T",
            "9.0": "H2Q-MC-LZZT-Study-Visit-9",
            "9.1": "H2Q-MC-LZZT-Study-Visit-9T",
            "10.0": "H2Q-MC-LZZT-Study-Visit-10",
            "10.1": "H2Q-MC-LZZT-Study-Visit-10T",
            "11.0": "H2Q-MC-LZZT-Study-Visit-11",
            "11.1": "H2Q-MC-LZZT-Study-Visit-11T",
            "12.0": "H2Q-MC-LZZT-Study-Visit-12",
            "13.0": "H2Q-MC-LZZT-Study-Visit-13",
            "101.0": "H2Q-MC-LZZT-Study-ET-14",
            "201.0": "H2Q-MC-LZZT-Study-RT-15",
            "501.0": "H2Q-MC-LZZT-Study-RASH-FU",
        }
        for record in sv.itertuples():
            if record.USUBJID not in self.content.subjects:
                continue
            print("Processing patient {} -> {}".format(record.USUBJID, record.VISITNUM))
            visit_num = record.VISITNUM
            if str(visit_num) not in pd_map:
                print("Visit {} is unscheduled".format(visit_num))
                plan_def_id = "H2Q-MC-LZZT-Study-Unscheduled-Visit"
            else:
                plan_def_id = pd_map[str(visit_num)]
            if plan_def_id is None:
                print("Ignoring visit", visit_num, "as Telephone contact")
                continue
            care_plan_description = f"{patient_hash_id}-{visit_num}-CarePlan"
            care_plan_id = hh(care_plan_description)
            # create a care plan
            care_plan = CarePlan(
                id=care_plan_id,
                status="completed",
                intent="order",
                subject=Reference(reference=f"Patient/{patient_hash_id}"),
                instantiatesCanonical=[f"PlanDefinition/{plan_def_id}"],
                title=f"Subject {record.USUBJID} {visit_num}",
            )
            care_plan.identifier = [Identifier(value=care_plan_description)]
            # bind the care plan - todo!
            # create the service request
            service_request_description = (
                f"{patient_hash_id}-{visit_num}-ServiceRequest"
            )
            service_request_id = hh(service_request_description)
            service_request = ServiceRequest(
                id=service_request_id,
                status="completed",
                intent="order",
                subject=Reference(reference=f"Patient/{patient_hash_id}"),
                basedOn=[Reference(reference=f"CarePlan/{care_plan_id}")],
            )
            service_request.identifier = [
                Identifier(value=f"{service_request_description}")
            ]
            encounter = Encounter(
                id=hh(f"{care_plan_id}-{record.VISITNUM}-Encounter"),
                status="finished",
                class_fhir=Coding(code="IMP", system="http://hl7.org/fhir/v3/ActCode"),
                subject=Reference(reference=f"Patient/{patient_hash_id}"),
                basedOn=[Reference(reference=f"ServiceRequest/{service_request_id}")],
            )
            encounter.identifier = [Identifier(value=f"{care_plan_id}-Encounter")]
            period = {}
            if record.SVSTDTC:
                period["start"] = record.SVSTDTC
            if record.SVENDTC:
                period["end"] = record.SVENDTC
            if period:
                encounter.period = Period(**period)
            # later
            # encounter.serviceProvider = Reference(reference=f"Organization/{self.org_id}")
            self.content.add_resource(care_plan)
            self.content.add_resource(service_request)
            self.content.add_resource(encounter)
