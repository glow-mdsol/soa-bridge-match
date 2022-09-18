import os
import argparse
import random

from soa_bridge_match.dataset import Naptha

def process_file(filename, blinded=False):
    # getting the bundle
    print("Processing file: {}".format(filename))
    ds = Naptha(filename)
    subject_id = os.path.basename(filename).split('_')[3]
    assert subject_id.startswith('01-701')
    (spec, site, _id) = subject_id.split('-')
    _subject_id = "-".join([spec, site, str(int(_id) + 1000 + random.randint(0, 100))])
    try:
        print("Cloning {} to {}".format(subject_id, _subject_id))
        _ds = ds.clone(_subject_id)
        assert _ds != ds
        _ds.merge_ex_statement(subject_id=subject_id, blinded=blinded, d_subject_id=_subject_id)
        _ds.content.dump(target_dir=os.path.dirname(filename))
    except Exception as e:
        print("Cloning {subject_id} failed: {e}".format(subject_id=subject_id, e=e))


def process_dir(dirname, blinded=False):
    for fname in os.listdir(dirname):
        if fname.endswith('.json'):
            process_file(os.path.join(dirname, fname), blinded=blinded)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Path to the directory or file')
    parser.add_argument('--blinded', action='store_true', help='Blinded mode')
    opts = parser.parse_args()
    process_dir(opts.path, opts.blinded)
