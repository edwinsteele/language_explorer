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
            iso = vr.find("a").text[1:4]
            if iso not in self.EXCLUDED_AU_LANGUAGES:
                keys.append(iso)

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

        The related phrase contains repeats of a pattern, and I can't work out
        how to process it with a single regex, however the iso key is always
        in square brackets, so is easy to extract.
        """
        rel_list = []
        initial_re = 'related to [\w ]+ \[(\w{3})\]'
        if re.search(initial_re, dialect_phrase, re.IGNORECASE):
            iso_re = '\[(\w{3})\]'
            rel_list = zip(itertools.repeat(constants.RELTYPE_RELATED_TO),
                           re.findall(iso_re, dialect_phrase))
        return rel_list

    def parse_dialect_phrase_different(self, dialect_phrase):
        """extract "different" relationship types from the phrase

        There are only two, ktd and kux, but let's do them anyway
        """
        rel_list = []
        different_re = 'different from [\w ]+ \[(\w{3})\]'
        mo = re.search(different_re, dialect_phrase, re.IGNORECASE)
        if mo:
            rel_list = [(constants.RELTYPE_DIFFERENT_FROM, mo.group(1))]
        return rel_list

    def parse_dialect_phrase_intellible(self, dialect_phrase):
        """extract "intelligible" or "intelligibility" relationship types

        "may be intelligible"
        "mutual intelligibility"
        """
        rel_list = []
        initial_mi_re = 'may be intelligible with [\w ]+ \[(\w{3})\]'
        li_re = 'Limited mutual intelligibility of [\w ]+ \[(\w{3})\]'
        if re.search(initial_mi_re, dialect_phrase, re.IGNORECASE):
            iso_re = '\[(\w{3})\]'
            rel_list = zip(
                itertools.repeat(constants.RELTYPE_MAY_BE_INTELLIGIBLE),
                re.findall(iso_re, dialect_phrase)
            )
        else:
            mo = re.search(li_re, dialect_phrase, re.IGNORECASE)
            if mo:
                rel_list = [(constants.RELTYPE_LIMITED_MUTUAL_INTELLIGIBILITY,
                            mo.group(1))]
        return rel_list

    def parse_dialect_phrase_dialects(self, dialect_phrase):
        """extra list of dialect names from the phrase.

        We do not attempt to match up dialect alternative names with dialects
         so this produces a bunch of dialect names but does not preserve their
         relationship to the parent dialect where there are alternative names
         i.e. it's a list of dialect names in the language

        split on commas and ( and )
        dialects have at most three words "roper river kriol" so we can classify
        all that don't fit in this pattern as not being a part of the dialect
        name list

        This should be the last function in the list of phrase parsing methods
         as all the others are more specific.
        """
        dialect_candidates = [s.strip() for s in
                              re.split("[,\(\)]", dialect_phrase)]
        dialect_words_re = re.compile("([\w-]+) ?([\w-]+)? ?([\w-]+)?$")
        return zip(
            itertools.repeat(constants.DIALECT_NAME),
            itertools.ifilter(lambda x: dialect_words_re.match(x),
                              dialect_candidates)
        )

    def is_ignored_dialect_phrase(self, dialect_phrase):
        if "Lexical similarity:" in dialect_phrase:
            return True
        elif dialect_phrase.strip() in ["Dialects inherently intelligible",
                                        "(Black 1983)"]:
            # wmb has phrases that would match dialect patterns, but aren't
            #  dialects
            return True
        else:
            return False

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
        if self.is_ignored_dialect_phrase(dialect_phrase):
            return rel_list
        if not rel_list:
            rel_list.extend(self.parse_dialect_phrase_similar(dialect_phrase))
        if not rel_list:
            rel_list.extend(self.parse_dialect_phrase_related(dialect_phrase))
        if not rel_list:
            rel_list.extend(
                self.parse_dialect_phrase_intellible(dialect_phrase))
        if not rel_list:
            rel_list.extend(
                self.parse_dialect_phrase_different(dialect_phrase))
        if not rel_list:
            rel_list.extend(
                self.parse_dialect_phrase_dialects(dialect_phrase))
        if not rel_list:
            logging.warning("Unable to parse dialect phrase '%s",
                            dialect_phrase)
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
            dialect_names = [
                dialect_name for x, dialect_name in relationships
                if x == constants.DIALECT_NAME]
            if dialect_names:
                for dialect_name in dialect_names:
                    persister.persist_dialect(iso, dialect_name,
                                              self.SOURCE_NAME)
            dialect_relationships = [
                (x, y) for x, y in relationships
                if x is not constants.DIALECT_NAME]
            if dialect_relationships:
                persister.persist_relationship(iso, dialect_relationships,
                                               self.SOURCE_NAME)

    def get_writing_state_for_iso(self, iso):
        # Latin Script, Unwritten, Latin Script unused
        soup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
        ))
        writing_div_string = soup.find(class_="field-name-field-writing")
        if writing_div_string:
            writing_string = writing_div_string.find(class_="field-item").text
            if writing_string == "Unwritten.":
                writing_state = constants.WRITING_STATE_UNWRITTEN
            elif writing_string in ["Latin script.",
                                    "Latin script, in development."]:
                writing_state = constants.WRITING_STATE_LATIN_SCRIPT
            elif writing_string == "Latin script, no longer in use.":
                writing_state = constants.WRITING_STATE_LATIN_SCRIPT_NIU
            else:
                logging.warning("Unable to parse writing state '%s' for "
                                "iso %s", writing_string, iso)
                writing_state = constants.WRITING_STATE_NOT_RECORDED
        else:
            writing_state = constants.WRITING_STATE_NOT_RECORDED

        return writing_state

    def persist_writing_state(self, persister, iso):
        writing_state = self.get_writing_state_for_iso(iso)
        persister.persist_writing_state(iso, writing_state)