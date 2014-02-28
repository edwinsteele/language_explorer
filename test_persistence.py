import unittest
from persistence import LanguagePersistence
import settings

__author__ = 'esteele'


class TestPersistence(unittest.TestCase):

    def setUp(self):
        self.p = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)

    def test_isos_with_shared_aliases(self):
        iso_name_list = \
            [("a", "lang a"), ("b", "lang a"),
             ("c", "lang b"), ("d", "lang b"),
             ("e", "lang c"), ("f", "lang c"), ("g", "lang c")]
        grouped_by_name = list(self.p._isos_with_shared_aliases(iso_name_list))
        self.assertEquals(grouped_by_name, [["a", "b"],
                                            ["c", "d"],
                                            ["e", "f", "g"]])

    def test_same_name_different_iso(self):
        sndi_list = self.p.get_same_name_different_iso_list()
        print sndi_list
        self.assertEquals(len(sndi_list), 29)
        self.assertIn(('tbh', 'yxg'), sndi_list)
        # Should have same contents with different order
        self.assertNotIn(('yxg', 'tbh'), sndi_list)