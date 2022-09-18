from genericpath import isdir
from fhir.resources.bundle import Bundle
import os
import sys

def check_file(filename):
    if os.path.exists(filename):
        bundle = Bundle.parse_file(filename)
        for entry in bundle.entry:
            _id = entry.resource.id
            _type = entry.resource.resource_type
            if entry.request:
                if 'url' not in entry.request:
                    _patch_type, _patch_id = entry.request.url.split('/')
                    if _id != _patch_id:
                        print("resource {_type} {_id} does not match patch {_patch_type} {_patch_id} in {filename}".format(**locals()))

def check_dir(dirname):
    for filename in os.listdir(dirname):
        check_file(os.path.join(dirname, filename))

if __name__ == "__main__":
    if os.path.isdir(sys.argv[1]):
        check_dir(sys.argv[1])
    else:
        check_file(sys.argv[1])
