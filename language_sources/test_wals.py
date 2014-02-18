import unittest
import settings
from wals import WalsAdapter

__author__ = 'esteele'


class TestWalsAdapter(unittest.TestCase):

    def setUp(self):
        self.wals = WalsAdapter(settings.WALS_DB_URL)

    def test_all_iso_keys(self):
        keys = self.wals.get_language_iso_keys()

        self.assertEquals(len(keys), 154)
        self.assertEquals(keys[0], "adt")
        self.assertEquals(keys[-1], "zmu")

        # Check no dupes
        self.assertEquals(len(keys), len(list(set(keys))))
        for key in keys:
            self.assertIsInstance(key, basestring)
            self.assertEquals(len(key), 3)

    def test_primary_name_retrieval(self):
        iso_primary_name_pairs = [
            ("kij", "Kilivila"),  # normal
            ("rop", "Kriol (Ngukurr)"),  # brackets and spaces
            ("nam", "Ngan'gityemerri"),  # Single quote
            ("mpj", "Mantjiltjara"),  # Multiple WALS to single ISO
            ("are", "Arrernte (Western)"),  # Multiple WALS to single ISO and
                                            #  some WALS have 2 ISOs
        ]
        for iso, name in iso_primary_name_pairs:
            self.assertEquals(name,
                              self.wals.get_primary_name_for_iso(iso))

    def test_wals_key_for_iso_retrieval(self):
        iso_wals_pairs = [
            ("kij", ["klv"]),  # normal
            ("are", ["arr", "awe"]),  # multiple wals to single ISO where some
                                      #  WALS have 2 ISOs
            ("mpj", ["mnj", "mwa", "ylb"]),  # multiple wals to single ISO
        ]
        for iso, wals_list in iso_wals_pairs:
            self.assertEquals(wals_list,
                              self.wals.get_wals_keys_for_iso(iso))