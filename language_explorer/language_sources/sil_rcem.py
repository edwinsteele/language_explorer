import logging
import re
from austlang import constants

logging.basicConfig(level=logging.DEBUG)


class SilRcemAdapter(object):
    """SIL Retired Core Element Mappings"""
    SOURCE_NAME = constants.SIL_RCEM_SOURCE_ABBREV
    # Mappings defined the in schema
    RETIREMENT_TYPE_CHANGE = "C"
    RETIREMENT_TYPE_DUPLICATE = "D"
    RETIREMENT_TYPE_NON_EXISTENT = "N"
    RETIREMENT_TYPE_SPLIT = "S"
    RETIREMENT_TYPE_MERGE = "M"

    def __init__(self, tsv_file_location):
        self.source = tsv_file_location
        self.tsv_cache = []

    def _read_tsv(self):
        with open(self.source, 'r') as f:
            # Ignore Header row
            return f.readlines()[1:]

    def parse_one_line(self, line):
        iso, _, retirement_reason, change_to, split_merge_instructions, _ = \
            line.split('\t')
        if retirement_reason == self.RETIREMENT_TYPE_CHANGE:
            return [(iso, constants.RELTYPE_RETIREMENT_CHANGE, change_to)]
        elif retirement_reason == self.RETIREMENT_TYPE_DUPLICATE:
            return [(iso, constants.RELTYPE_RETIREMENT_DUPLICATE, change_to)]
        elif retirement_reason == self.RETIREMENT_TYPE_NON_EXISTENT:
            return [(iso, constants.RELTYPE_RETIREMENT_NON_EXISTENT, None)]
        elif retirement_reason == self.RETIREMENT_TYPE_SPLIT:
            return [(iso, constants.RELTYPE_RETIREMENT_SPLIT, lang) for lang
                    in re.findall('\[([a-z]{3})\]', split_merge_instructions)]
        elif retirement_reason == self.RETIREMENT_TYPE_MERGE:
            return [(iso, constants.RELTYPE_RETIREMENT_MERGE, change_to)]
        else:
            logging.warn("Don't know how to handle retirement type '%s'"
                         " for iso '%s'", retirement_reason, iso)
        return []

    def persist_retirement_relationships(self, persister):
        for line in self._read_tsv():
            relationships = self.parse_one_line(line)
            for subject_iso, rel_type, object_iso in relationships:
                persister.persist_relationship(subject_iso,
                                              [(rel_type, object_iso)],
                                              self.SOURCE_NAME)
