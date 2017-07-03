import os

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(TOP_DIR, "../resources/")


def get_resource(filename):
    return os.path.join(RESOURCE_DIR, filename)
