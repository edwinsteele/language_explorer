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