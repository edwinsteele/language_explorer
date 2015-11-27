from language_explorer import settings
from language_explorer.language_sources.wals import WalsAdapter
from tests.test_baseclasses import BaseAdapterTestCase
import unittest

__author__ = 'esteele'


class TestWalsAdapter(BaseAdapterTestCase):

    def setUp(self):
        self.source = WalsAdapter(settings.WALS_DB_URL)

    @unittest.skip("Review - likely broken due to updated wals db")
    def test_all_iso_keys(self):
        keys = self.source.get_language_iso_keys()
        self.assertEquals(len(keys), 154)
        self.assertEquals(keys[0], "adt")
        self.assertEquals(keys[-1], "zmu")
        self._do_test_all_iso_keys_common()

    def test_primary_name_retrieval(self):
        iso_primary_name_pairs = [
            ("kij", "Kilivila"),  # normal
            ("rop", "Kriol (Ngukurr)"),  # brackets and spaces
            ("nam", "Ngan'gityemerri"),  # Single quote
            ("mpj", "Mantjiltjara"),  # Multiple WALS to single ISO
            ("are", "Arrernte (Western)"),  # Multiple WALS to single ISO and
                                            #  some WALS have 2 ISOs
        ]
        self._do_test_primary_name_retrieval(iso_primary_name_pairs)

    def test_alternate_name_retrieval(self):
        iso_alternate_name_pairs = [
            ("yij", ["Yindjibarndi", "Kurama"]),  # Two unique alternates
            ("adt", ["Adynyamathanha", "Atynyamathanha", "Atynyamatana",
                     "Wailpi"]),
            ("aer", ["Aranda", "E. Arrernte", "Arrernte (Eastern)",
                     "Aranda (Eastern)", "Mparntwe Arrernte", "E Aranda"]),
            # aer has multiple matches
        ]
        self._do_test_alternate_name_retrieval(iso_alternate_name_pairs)

    def test_wals_key_for_iso_retrieval(self):
        iso_wals_pairs = [
            ("kij", ["klv"]),  # normal
            ("are", ["arr", "awe"]),  # multiple wals to single ISO where some
                                      #  WALS have 2 ISOs
            ("mpj", ["mnj", "mwa", "ylb"]),  # multiple wals to single ISO
        ]
        for iso, wals_list in iso_wals_pairs:
            self.assertEquals(wals_list,
                              self.source.get_wals_keys_for_iso(iso))

    def test_classification_retrieval(self):
        # Not implemented
        self.assertEquals([], self.source.get_classification("dummy"))
