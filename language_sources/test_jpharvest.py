import settings
from jpharvest import JPHarvestAdapter
from test_baseclasses import BaseAdapterTestCase

__author__ = 'esteele'


class TestJPHarvestAdapter(BaseAdapterTestCase):

    def setUp(self):
        self.source = JPHarvestAdapter(settings.JPHARVEST_DB_URL)

    def test_all_iso_keys(self):
        keys = self.source.get_language_iso_keys()
        self.assertEquals(len(keys), 67)
        self.assertEquals(keys[0], "aer")
        self.assertEquals(keys[-1], "zmt")
        self._do_test_all_iso_keys_common()

    def test_primary_name_retrieval(self):
        iso_primary_name_pairs = [
            ("aly", "Alyawarr"),  # normal
            ("are", "Arrarnta, Western"),  # spaces and commas
            ("kuy", "Kuuku-Ya'u"),  # single quote
            ("tcs", "Torres Strait Creole"),  # three words
        ]
        self._do_test_primary_name_retrieval(iso_primary_name_pairs)

    def test_alternate_name_retrieval(self):
        iso_alternate_name_pairs = [
            ("djb", []),  # No alternates
            ("djj", ["Gunavidji"]),  # One alternate
            ("amx", ["Anmatyerr", "Anmatjirra"]),  # Two alternates
            ("aer", ["Upper Aranda", "Eastern Aranda", "Arunta"]),  # Has spaces
            ("tgz", ["Tarkalag", "Targa-lag", "Takalak", "Dagalang",
                     "Da:galag"]),  # Names with colons and dashes
        ]
        self._do_test_alternate_name_retrieval(iso_alternate_name_pairs)

    def test_classification_retrieval(self):
        # Not implemented
        self.assertEquals([], self.source.get_classification("dummy"))