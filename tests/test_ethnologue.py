# -*- coding: utf-8 -*-
import unittest
from language_explorer import settings, constants
from language_explorer.language_sources.ethnologue import EthnologueAdapter
from tests.test_baseclasses import BaseAdapterTestCase

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

    def test_get_L1_speaker_count(self):
        iso_count_pairs = [
            ('ygu', constants.SPEAKER_COUNT_NONE_EXPECTED),
            ("coa", 1000),   # Malay, special case
            ("znk", 0),  # No remaining speakers
            ("jng", 0),  # No known L1 speakers
            ("nha", constants.SPEAKER_COUNT_FEW),
            ("xni", 5),  # single character
            ("thd", 29),  # multiple characters, with extra text
            ("wim", 1060),  # comma separating thousands
            ("pii", 10),  # No space after number
        ]
        for iso, c in iso_count_pairs:
            self.assertEquals(c,
                              self.source.get_L1_speaker_count_for_iso(iso))

    def test_parse_dialect_phrase_similar(self):
        dialect_string_relationship_pairs = [
            ("Similar to Maringarr [zmt] and Marithiel [mfr]", [
                (constants.RELTYPE_SIMILAR_TO, "zmt"),
                (constants.RELTYPE_SIMILAR_TO, "mfr")]),  # zmg
            ("Similar to Uradhi [urf]", [
                (constants.RELTYPE_SIMILAR_TO, "urf")]),  # xpj
            ("Speakers say it is similar to Kunggari [kgl]", [
                (constants.RELTYPE_SIMILAR_TO, "kgl")]),  # gdj
            ("Lexical similarity: 80% with English.", []),
            # tcs - no match despite "similar" appearing
        ]
        for dstring, reltypes in dialect_string_relationship_pairs:
            self.assertEqual(reltypes,
                             self.source.parse_dialect_phrase_similar(dstring))

    @unittest.skip("Skipping test: Related phrase parsing incomplete")
    def test_parse_dialect_phrase_related(self):
        # include guf, djj
        dialect_string_relationship_pairs = [
            ("Related to Ngamini [nmv], which may have no remaining speakers", [
                (constants.RELTYPE_RELATED_TO, "nmw")]),  # dif (1 related)
            ("Related to Dalabon [ngk] and Rembarunga [rmb]", [
                (constants.RELTYPE_RELATED_TO, "ngk"),
                (constants.RELTYPE_RELATED_TO, "rmb")]),  # nig (2 related)
            ("Related to Alyawarr [aly], Western Arrarnta [are],"
             " Anmatyerre [amx], and Kaytetye [gbb]", [
                 (constants.RELTYPE_RELATED_TO, "aly"),
                 (constants.RELTYPE_RELATED_TO, "are"),
                 (constants.RELTYPE_RELATED_TO, "amx"),
                 (constants.RELTYPE_RELATED_TO, "gbb")]),  # aer (4 related)
            ("Was related to Nyigina [nyh], Warrwa [wwr], Nimanbur [nmp],"
             " Dyaberdyaber [dyb], Nyulnyul [nyv], and Bardi [bcj]", [
                 (constants.RELTYPE_RELATED_TO, "nyh"),
                 (constants.RELTYPE_RELATED_TO, "wwr"),
                 (constants.RELTYPE_RELATED_TO, "nmp"),
                 (constants.RELTYPE_RELATED_TO, "dyb"),
                 (constants.RELTYPE_RELATED_TO, "nyv"),
                 (constants.RELTYPE_RELATED_TO, "bcj")]),
            # ywr (6 related) with case change on "related"
        ]
        for dstring, reltypes in dialect_string_relationship_pairs:
            self.assertEqual(reltypes,
                             self.source.parse_dialect_phrase_related(dstring))

    def test_get_dialects_for_iso(self):
        iso_rtype_pairs = [
            ("xpj", [(constants.RELTYPE_SIMILAR_TO, "urf")]),
        ]
        for iso, rel_list in iso_rtype_pairs:
            self.assertEqual(rel_list,
                             self.source.get_dialects_for_iso(iso))
