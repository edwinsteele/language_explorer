import constants
import settings
from test_baseclasses import BaseAdapterTestCase
from language_sources.findabible import FindABibleAdapter

__author__ = 'esteele'


class TestFindABibleAdapter(BaseAdapterTestCase):
    def setUp(self):
        self.source = FindABibleAdapter(settings.TEST_CACHE_ROOT)

    def test_get_translation_info_for_iso(self):
        # Convenience
        STATE = constants.TRANSLATION_STATE_STATE_KEY
        YEAR = constants.TRANSLATION_STATE_YEAR_KEY
        iso_translation_pairs = [
            ("are", {STATE: constants.TRANSLATION_STATE_NEW_TESTAMENT,
                     YEAR: 1956}),
            ("rop", {STATE: constants.TRANSLATION_STATE_WHOLE_BIBLE,
                     YEAR: 2007}),
            ("gia", {STATE: constants.TRANSLATION_STATE_COMPLETE_BOOK,
                     YEAR: 1978}),
            ("adt", {STATE: constants.TRANSLATION_STATE_NO_SCRIPTURE,
                     YEAR: constants.TRANSLATION_STATE_UNKNOWN_YEAR}),
            ("gwm", {STATE: constants.TRANSLATION_STATE_NO_RECORD,
                     YEAR: constants.TRANSLATION_STATE_UNKNOWN_YEAR})
        ]
        self._do_test_get_translation_info(iso_translation_pairs)
