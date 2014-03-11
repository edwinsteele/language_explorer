# -*- coding: utf-8 -*-
import logging
import re

from bs4 import BeautifulSoup
import itertools

from language_explorer import constants
from language_explorer.language_sources.base import CachingWebLanguageSource


__author__ = 'esteele'

logging.basicConfig(level=logging.DEBUG)


class EthnologueAdapter(CachingWebLanguageSource):
    SOURCE_NAME = constants.ETHNOLOGUE_SOURCE_ABBREV
    ALL_LANGUAGES_URL = "http://www.ethnologue.com/country/AU/languages"
    ONE_LANGUAGE_URL_TEMPLATE = "http://www.ethnologue.com/language/%s"

    def get_language_iso_keys(self):
        soup = BeautifulSoup(
            self.get_text_from_url(self.ALL_LANGUAGES_URL))
        keys = []
        vrs = soup.find_all(class_="views-row")
        for vr in vrs:
            keys.append(vr.find("a").text[1:4])

        return keys

    def get_primary_name_for_iso(self, iso):
        soup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
        ))
        return soup.find(id="page-title").text

    def get_alternate_names_for_iso(self, iso):
        soup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
        ))
        alt_base_div = soup.find(class_="field-name-field-alternate-names")
        # Some don't have alternate names e.g. aid
        if alt_base_div:
            return [s.strip() for s in
                    alt_base_div.find(class_="field-item").text.split(",")]
        else:
            return []

    def get_classification(self, iso):
        # everything seems to have a classification, but there are between
        #  two and four classifications
        soup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
        ))
        classification_string = soup\
            .find(class_="field-name-language-classification-link") \
            .find(class_="field-item").text
        return [s.strip() for s in classification_string.split(",")]

    def get_translation_info_for_iso(self, iso):
        # convenience
        STATE = constants.TRANSLATION_STATE_STATE_KEY
        YEAR = constants.TRANSLATION_STATE_YEAR_KEY

        d = {}
        soup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
        ))
        lang_development_div = soup\
            .find(class_="field-name-field-language-development")
        if lang_development_div:
            lang_development_string = lang_development_div \
                .find(class_="field-item").text
            # Note the long dash, not a hyphen
            # We take the second year if there's a range, to put the emphasis
            #  on recent translation efforts
            ts_re = u'(?P<tr_state>Bible[ a-z]*): ' \
                    u'([0-9]{4}–)?(?P<tr_year>[0-9]{4})'
            mo = re.search(ts_re, lang_development_string)
            if mo:
                if "portions" in mo.group('tr_state'):
                    # Ethnologue provides no distinction between one book & NT
                    d[STATE] = constants.TRANSLATION_STATE_PORTIONS
                else:
                    d[STATE] = constants.TRANSLATION_STATE_WHOLE_BIBLE
                d[YEAR] = int(mo.group('tr_year'))
            else:
                # Some have language development divs but no mention of Bible
                d[STATE] = constants.TRANSLATION_STATE_NO_RECORD
                d[YEAR] = constants.TRANSLATION_STATE_UNKNOWN_YEAR
        else:
            d[STATE] = constants.TRANSLATION_STATE_NO_RECORD
            d[YEAR] = constants.TRANSLATION_STATE_UNKNOWN_YEAR
        return d

    def get_L1_speaker_count_for_iso(self, iso):
        """Focus on L1 count, even though there is more info in Ethnologue

        :return: Count of L1 speakers for this iso
        :rtype: int
        """
        # Ethnologue ljw, xwd, ygu, yry are missing Population records but as
        #  all list their language status as 8b (nearly extinct), I'm going to
        #  infer that there aren't any remaining L1 speakers and record that
        #  there are SPEAKER_COUNT_NONE_EXPECTED speakers
        ISOS_WITHOUT_POPULATION_DATA = ["ljw", "xwd", "ygu", "yry"]
        NO_REMAINING_L1_SPEAKERS_STRS = [
            "No remaining speakers.",
            "No known L1 speakers.",
            "No known L1 users."
        ]
        if iso in ISOS_WITHOUT_POPULATION_DATA:
            return constants.SPEAKER_COUNT_NONE_EXPECTED
        else:
            soup = BeautifulSoup(self.get_text_from_url(
                self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
            ))
            population_div = soup \
                .find(class_="field-name-field-population")
            if population_div:
                # use strip because there's a newline in the string
                population_string = population_div \
                    .find(class_="field-item").text.strip()
                mo = re.match("([\d,]+)", population_string)
                if mo:
                    # Make unicode string (which is a number anyway) into a
                    #  regular string, because the unicode translate method
                    #  doesn't accept the deletechars argument
                    return int(str(mo.group(1)).translate(None, ","))
                elif list(itertools.ifilter(lambda x: x in population_string,
                                            NO_REMAINING_L1_SPEAKERS_STRS)):
                    return 0
                elif "ew speakers" in population_string:
                    return constants.SPEAKER_COUNT_FEW
                elif iso == "coa":
                    # Malay is an odd format. We really don't care because
                    #  it's outside Australia. Trust me that it's 1000.
                    return 1000
                else:
                    logging.warning("Unable to interpret Population field for"
                                    " iso %s. Field is ->%s<-."
                                    "Using SPEAKER_COUNT_UNKNOWN",
                                    iso, population_string)
                    return constants.SPEAKER_COUNT_UNKNOWN

            else:
                logging.warning("Unable to find expected Population field for"
                                " iso %s. Using SPEAKER_COUNT_UNKNOWN", iso)
                return constants.SPEAKER_COUNT_UNKNOWN

    def parse_dialect_phrase_similar(self, dialect_phrase):
        """extract "similar" relationship types from the phrase

        Note that this bundles "similar" with "very similar" and "most similar"
        """
        rel_list = []
        # FIXME - what about languages with multiple words in their name?
        similar_re = 'similar to [\w ]+ \[(?P<iso_1>\w{3})\]' \
                     '( and [\w ]+ \[(?P<iso_2>\w{3})\])?'
        mo = re.search(similar_re, dialect_phrase, re.IGNORECASE)
        if mo:
            rel_list.append((constants.RELTYPE_SIMILAR_TO, mo.group("iso_1")))
            # Not all "Similar to" dialect phrases have a second group, but
            #  all of them have either one or two groups
            if mo.group("iso_2"):
                rel_list.append((constants.RELTYPE_SIMILAR_TO,
                                 mo.group("iso_2")))
        return rel_list

    def parse_dialect_phrase_related(self, dialect_phrase):
        """extract "related" relationship types from the phrase


        """
        rel_list = []
        related_re = 'related to [\w ]+ \[(?P<iso_1>\w{3})\](, [\w ]+ \[(?P<iso_comma>\w{3})\])*( and [\w ]+ \[(?P<iso_2>\w{3})\])?'
        return rel_list

    def parse_dialect_phrase(self, dialect_phrase):
        """returns relationship types from a single dialect phrase

        :return: list of relationship tuples (reltype, iso)
        :rtype: tuple

        Phrase will contain one of:

        - Similar to
        - A list of dialects (if no descriptor matches)
        """
        rel_list = []
        # FIXME could bail out after one of these is non-empty...
        if not rel_list:
            rel_list.extend(self.parse_dialect_phrase_similar(dialect_phrase))
        if not rel_list:
            rel_list.extend(self.parse_dialect_phrase_related(dialect_phrase))
        if not rel_list:
            logging.warning("Unable to parse dialect phrase '%s", dialect_phrase)
        return rel_list

    def get_dialects_for_iso(self, iso):
        """returns relationship types from the dialect string

        Dialect string may have several sections, but splitting on period
         tokenises them
        """
        soup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
        ))
        dialect_div_string = soup \
            .find(class_="field-name-field-dialects")
        if dialect_div_string:
            dialect_string = dialect_div_string.find(class_="field-item")\
                .text.strip().split(".")
            dialect_phrases = filter(None, dialect_string)
        else:
            dialect_phrases = []

        relationship_types = []
        for p in dialect_phrases:
            relationship_types.extend(self.parse_dialect_phrase(p))
        return relationship_types

    def persist_dialects(self, persister, iso):
        relationships = self.get_dialects_for_iso(iso)
        if relationships:
            logging.info("Persisting dialect info for ISO %s", iso)
            persister.persist_relationship(iso, relationships,
                                            self.SOURCE_NAME)
