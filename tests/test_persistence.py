import unittest
from language_explorer.persistence import LanguagePersistence
from language_explorer import settings

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
        self.assertEquals(len(sndi_list), 13)
        self.assertIn(('duj', 'gnn'), sndi_list)
        self.assertIn(('unp', 'wro'), sndi_list)
        # Should have same contents with different order
        self.assertNotIn(('gnn', 'duj'), sndi_list)

    def test_common_names_for_iso_list(self):
        iso_list_common_name_list = \
            [(("aer", "are"), ["Arrernte", "Aranda", "Arunta"]),
             # One match where names appear in 2 DBs (JP+AB)
             ]
        for iso_list, common_name_list in iso_list_common_name_list:
            self.assertEqual(common_name_list,
                             self.p.get_common_names_for_iso_list(iso_list))

    def test_get_iso_list_from_name(self):
        name_iso_list = \
            [("terry", []),  # no match
             ("Arunta", ["aer", "are"]),  # 2 matches
             ("Adynyamathanha", ["adt"]),  # 1 match
             (" Yugambal ", []),  # no matches. string stripping done in flask
             ("yugambal", []),  # no matches, we're case sensitive
             ]
        for name, iso_list in name_iso_list:
            self.assertEqual(iso_list, self.p.get_iso_list_from_name(name))
