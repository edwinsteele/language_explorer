from language_explorer import settings, constants
from language_explorer.language_sources.jpharvest import JPHarvestAdapter
from tests.test_baseclasses import BaseAdapterTestCase
import unittest

__author__ = 'esteele'


class TestJPHarvestAdapter(BaseAdapterTestCase):

    def setUp(self):
        self.source = JPHarvestAdapter(settings.JPHARVEST_DB_URL)

    def test_all_iso_keys(self):
        keys = self.source.get_language_iso_keys()
        self.assertEquals(len(keys), 82)
        self.assertEquals(keys[0], "adt")
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
            ("aer", ["Upper Aranda", "Eastern Aranda", "Arunta"]),  # spaces
            ("tgz", ["Tarkalag", "Targa-lag", "Takalak", "Dagalang",
                     "Da:galag"]),  # Names with colons and dashes
        ]
        self._do_test_alternate_name_retrieval(iso_alternate_name_pairs)

    def test_classification_retrieval(self):
        # Not implemented
        self.assertEquals([], self.source.get_classification("dummy"))

    def test_get_translation_info_for_iso(self):
        # Convenience
        STATE = constants.TRANSLATION_STATE_STATE_KEY
        YEAR = constants.TRANSLATION_STATE_YEAR_KEY
        iso_translation_pairs = [
            ("are", {STATE: constants.TRANSLATION_STATE_NEW_TESTAMENT,
                     YEAR: 1956}),  # NT + portions date
            ("dif", {STATE: constants.TRANSLATION_STATE_NEW_TESTAMENT,
                     YEAR: 1897}),  # No portions date, only NT date
            ("rop", {STATE: constants.TRANSLATION_STATE_WHOLE_BIBLE,
                     YEAR: 2007}),  # Whole bible
            ("aly", {STATE: constants.TRANSLATION_STATE_PORTIONS,
                     YEAR: 2003}),  # Range in portions
            ("adg", {STATE: constants.TRANSLATION_STATE_NO_SCRIPTURE,
                     YEAR: constants.TRANSLATION_STATE_UNKNOWN_YEAR}),
            # No matches
            ("bdy", {STATE: constants.TRANSLATION_STATE_PORTIONS,
                     YEAR: constants.TRANSLATION_STATE_POSITIVE_YEAR})
            # bdy has no translation date
        ]
        self._do_test_get_translation_info(iso_translation_pairs)
