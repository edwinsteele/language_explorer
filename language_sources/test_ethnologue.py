# -*- coding: utf-8 -*-
import constants
from ethnologue import EthnologueAdapter
from test_baseclasses import BaseAdapterTestCase
import settings

__author__ = 'esteele'


class TestEthnologueAdapter(BaseAdapterTestCase):
    def setUp(self):
        self.source = EthnologueAdapter(settings.TEST_CACHE_ROOT)

    def test_all_iso_keys(self):
        keys = self.source.get_language_iso_keys()
        self.assertEquals(len(keys), 390)
        self.assertEquals(keys[0], "dth")
        self.assertEquals(keys[-1], "yxu")
        self._do_test_all_iso_keys_common()

    def test_primary_name_retrieval(self):
        iso_primary_name_pairs = [
            ("dth", "Adithinngithigh"),  # normal
            ("yxu", "Yuyu"),  # normal
            ("xmp", u"Kuku-Mu’inh"),  # quotes
            ("tcs", "Torres Strait Creole"),  # spaces
        ]
        self._do_test_primary_name_retrieval(iso_primary_name_pairs)

    def test_alternate_name_retrieval(self):
        iso_alternate_name_pairs = [
            ("dth", ["Adetingiti"]),  # One alternate
            ("yij", ["Jindjibandi", "Yinjtjipartnti"]),  # Two alternates
            ("aid", []),  # No alternates
            ("dax", [u"Dha’i", u"Dhay’yi"]),  # Names with quotes
            ("aer", ["Arunta", "Eastern Aranda", "Upper Aranda"]),  # Has spaces
        ]
        self._do_test_alternate_name_retrieval(iso_alternate_name_pairs)

    def test_classification_retrieval(self):
        iso_classification_pairs = [
            ("asf", ["Deaf sign language"]),  # 1 classification, and spaces
            ("bcj", ["Australian", "Nyulnyulan"]),  # 2 classifications
            ("amg", ["Australian", "Yiwaidjan", "Amaragic"]),  # 3
            ("dax", ["Australian", "Pama-Nyungan", "Yuulngu", "Dhuwal"]),  # 4
        ]
        self._do_test_classification_retrieval(iso_classification_pairs)

    def test_get_translation_info_for_iso(self):
        # Convenience
        STATE = constants.TRANSLATION_STATE_STATE_KEY
        YEAR = constants.TRANSLATION_STATE_YEAR_KEY
        iso_translation_pairs = [
            ("tcs", {STATE: constants.TRANSLATION_STATE_PORTIONS,
                     YEAR: 1997}),  # Portions w/ one year. No other text
            ("ulk", {STATE: constants.TRANSLATION_STATE_PORTIONS,
                     YEAR: 1994}),  # Portions w/ range. No other text.
            ("aly", {STATE: constants.TRANSLATION_STATE_PORTIONS,
                     YEAR: 2003}),  # portions w/ range and other text.
            ("rop", {STATE: constants.TRANSLATION_STATE_WHOLE_BIBLE,
                     YEAR: 2007}),  # whole bible
            ("adt", {STATE: constants.TRANSLATION_STATE_NO_RECORD,
                     YEAR: constants.TRANSLATION_STATE_UNKNOWN_YEAR}),
            # adt has Language development entry, but no mention of Bible
            ("gwm", {STATE: constants.TRANSLATION_STATE_NO_RECORD,
                     YEAR: constants.TRANSLATION_STATE_UNKNOWN_YEAR}),
            # gwm has no language development entry
        ]
        for iso, ts_dict in iso_translation_pairs:
            self.assertEquals(ts_dict,
                              self.source.get_translation_info_for_iso(iso))