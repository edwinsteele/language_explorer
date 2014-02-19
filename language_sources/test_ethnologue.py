import unittest
from ethnologue import EthnologueAdapter

__author__ = 'esteele'


class TestEthnologueAdapter(unittest.TestCase):
    TEST_CACHE_ROOT = "/Users/esteele/Code/language_explorer/data/.cache"

    def setUp(self):
        self.ethnologue = EthnologueAdapter(self.TEST_CACHE_ROOT)

    def test_all_iso_keys(self):
        keys = self.ethnologue.get_language_iso_keys()
        self.assertEquals(len(keys), 390)
        # Check no dupes
        self.assertEquals(len(keys), len(list(set(keys))))
        for key in keys:
            self.assertIsInstance(key, basestring)
            self.assertEquals(len(key), 3)

    def test_all_first_and_last_iso(self):
        keys = self.ethnologue.get_language_iso_keys()
        self.assertEquals(keys[0], "dth")
        self.assertEquals(keys[-1], "yxu")

    def test_primary_name_retrieval(self):
        iso_primary_name_pairs = [
            ("dth", "Adithinngithigh"),  # normal
            ("yxu", "Yuyu"),  # normal
            ("xmp", u"Kuku-Mu\u2019inh"),  # quotes
            ("tcs", "Torres Strait Creole"),  # spaces
        ]
        for iso, name in iso_primary_name_pairs:
            self.assertEquals(name,
                              self.ethnologue.get_primary_name_for_iso(iso))

    def test_alternate_name_retrieval(self):
        iso_alternate_name_pairs = [
            ("dth", ["Adetingiti"]),  # One alternate
            ("yij", ["Jindjibandi", "Yinjtjipartnti"]),  # Two alternates
            ("aid", []),  # No alternates
            ("dax", [u"Dha\u2019i", u"Dhay\u2019yi"]),  # Names with quotes
            ("aer", ["Arunta", "Eastern Aranda", "Upper Aranda"]),  # Has spaces
        ]
        for iso, alternate_list in iso_alternate_name_pairs:
            self.assertEquals(alternate_list,
                              self.ethnologue.get_alternate_names_for_iso(iso))

    def test_classification_retrieval(self):
        iso_classification_pairs = [
            ("asf", ["Deaf sign language"]),  # 1 classification, and spaces
            ("bcj", ["Australian", "Nyulnyulan"]),  # 2 classifications
            ("amg", ["Australian", "Yiwaidjan", "Amaragic"]),  # 3
            ("dax", ["Australian", "Pama-Nyungan", "Yuulngu", "Dhuwal"]),  # 4
        ]
        for iso, classification_list in iso_classification_pairs:
            self.assertEquals(classification_list,
                              self.ethnologue.get_classification(iso))