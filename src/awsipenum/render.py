import json
import yaml


def to_yaml(list):
    s = yaml.dump(list)
    return s


def to_json(list):
    s = json.dumps(list, indent=4)
    return s
