from collections import namedtuple


def convert_dict(d):
    return namedtuple('GenericDict', d.keys())(**d)
