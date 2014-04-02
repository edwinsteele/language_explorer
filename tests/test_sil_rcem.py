from language_explorer import settings, constants
from language_explorer.language_sources.sil_rcem import SilRcemAdapter
from tests.test_baseclasses import BaseAdapterTestCase


class TestSilRcemAdapter(BaseAdapterTestCase):

    def setUp(self):
        self.source = SilRcemAdapter(settings.SIL_RCEM_TSV_SOURCE)

    def test_retirement_retrieval(self):
        iso_retirement_rel_pairs = [
            ("gbc\tGarawa\tS\t\tSplit into Garrwa [wrk] and Wanyi [wny]"
             "\t2012-02-03",
             [("gbc", constants.RELTYPE_RETIREMENT_SPLIT_INTO, "wrk"),
              ("gbc", constants.RELTYPE_RETIREMENT_SPLIT_INTO, "wny")]),
            ("pun\tPubian\tM\tljp\t\t2008-01-14",
             [("pun", constants.RELTYPE_RETIREMENT_MERGED_INTO, "ljp")]),
            ("fri\tWestern Frisian\tC\tfry\t\t2007-02-01",
             [("fri", constants.RELTYPE_RETIREMENT_CHANGE, "fry")]),
            ("bgh\tBogan\tD\tbbh\t\t2007-07-18",
             [("bgh", constants.RELTYPE_RETIREMENT_DUPLICATE, "bbh")]),
            ("aay\tAariya\tN\t\t\t2009-01-16",
             [("aay", constants.RELTYPE_RETIREMENT_NON_EXISTENT, None)]),
        ]
        for line, retirement_rel_list in iso_retirement_rel_pairs:
            self.assertEqual(retirement_rel_list,
                             self.source.parse_one_line(line))
