from fhir.resources.bundle import Bundle
import os
import sys

def check_file(filename):
    if os.path.exists(filename):
        bundle = Bundle.parse_file(filename)

if __name__ == "__main__":
    check_file(sys.argv[1])
