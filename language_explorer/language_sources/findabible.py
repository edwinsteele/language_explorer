import logging
import re

from bs4 import BeautifulSoup

from language_explorer import constants
from language_explorer.language_sources.base import CachingWebLanguageSource


__author__ = 'esteele'

logging.basicConfig(level=logging.DEBUG)


class FindABibleAdapter(CachingWebLanguageSource):
    SOURCE_NAME = constants.FIND_A_BIBLE_SOURCE_ABBREV
    # XXX Findabible redid their site post-2014, so this needs reworking
    ONE_LANGUAGE_URL_TEMPLATE = "http://208.72.3.146/find_a_bible/" \
                                "default.aspx?Language=%s"
    NO_RECORD_TEXT = "We have no record of a scripture work in this language."
    COMPLETE_BOOK_TEXT = "A complete book of Scripture"
    NT_TEXT = "The New Testament"
    WB_TEXT = "The Bible"

    def _extract_translation_state(self, translation_str):
        """Return translation state & date"""
        d = {}
        # Convenience
        STATE = constants.TRANSLATION_STATE_STATE_KEY
        YEAR = constants.TRANSLATION_STATE_YEAR_KEY

        ts_re = '(?P<tr_state>.*?) is known to have been' \
                ' completed in this language in (?P<tr_year>[0-9]{4})'
        mo = re.match(ts_re, translation_str)
        if mo:
            if mo.group('tr_state') == self.COMPLETE_BOOK_TEXT:
                d[STATE] = constants.TRANSLATION_STATE_COMPLETE_BOOK
            elif mo.group('tr_state') == self.NT_TEXT:
                d[STATE] = constants.TRANSLATION_STATE_NEW_TESTAMENT
            elif mo.group('tr_state') == self.WB_TEXT:
                d[STATE] = constants.TRANSLATION_STATE_WHOLE_BIBLE
            else:
                logging.error("Unable to recognise translation state '%s'",
                              (mo.group('tr_state'),))
            d[YEAR] = int(mo.group('tr_year'))
        else:
            assert(translation_str == self.NO_RECORD_TEXT)
            d[STATE] = constants.TRANSLATION_STATE_NO_SCRIPTURE
            d[YEAR] = constants.TRANSLATION_STATE_UNKNOWN_YEAR

        return d

    def get_translation_info_for_iso(self, iso):
        soup = BeautifulSoup(
            self.get_text_from_url(self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)))
        translation_span = soup.find(id=re.compile("TranslationDescription"))
        if translation_span:
            return self._extract_translation_state(translation_span.text)
        else:
            return {constants.TRANSLATION_STATE_STATE_KEY:
                    constants.TRANSLATION_STATE_NO_RECORD,
                    constants.TRANSLATION_STATE_YEAR_KEY:
                    constants.TRANSLATION_STATE_UNKNOWN_YEAR}
