import os
from re import S
import sys
from typing import Optional
import argparse

from soa_bridge_match.dataset import Naptha
from yaml import parse

# Subject range 4000-4999


def process_file(filename: str, visit_number: str):
    # getting the bundle
    print("Processing file: {}".format(filename))
    ds = Naptha(filename)
    subject_id = os.path.basename(filename).split('_')[3]
    assert subject_id.startswith('01-701')
    (spec, site, _id) = subject_id.split('-')
    if int(_id) > 2000:
        return
    _subject_id = "-".join([spec, site, str(int(_id) + 3000) ])
    try:
        print("Cloning {} to {}".format(subject_id, _subject_id))
        _ds = ds.clone(_subject_id)
        assert _ds != ds
        success = _ds.merge_unscheduled_visit(subject_id=subject_id, visit_number=visit_number)
        # if we don't add a visit, we don't need to save the file
        if success:
            _ds.content.dump(target_dir=os.path.dirname(filename))
    except Exception as e:
        print("Cloning {subject_id} failed: {e}".format(subject_id=subject_id, e=e))


def process_dir(dirname: str, visit_number: str, subject_id: Optional[str], ):
    for fname in os.listdir(dirname):
        if fname.endswith('.json'):
            if subject_id is None or subject_id in fname:
                process_file(os.path.join(dirname, fname), visit_number=visit_number)


def main(subject_bundle: str, subject_id: str, visit_number: str):
    process_dir(subject_bundle, subject_id, visit_number)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add an unscheduled visit to a subject')
    parser.add_argument('--subject-id', help='Specify a subject id to process', default=None)
    parser.add_argument('--visit-number', help='Specify the visit number to add', default='4.1')
    parser.add_argument('subject_bundle', help='Specify the subject bundle directory')
    opts = parser.parse_args()
    main(opts.subject_bundle, opts.visit_number, opts.subject_id )