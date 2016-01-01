import re
import logging

from bs4 import BeautifulSoup
from language_explorer import constants

from language_explorer.language_sources.base import CachingWebLanguageSource


__author__ = 'esteele'

logging.basicConfig(level=logging.DEBUG)


class AustlangAdapter(CachingWebLanguageSource):
    SOURCE_NAME = constants.AUSTLANG_SOURCE_ABBREV
    ABS_SOURCE_NAME = constants.AUSTLANG_ABS_SOURCE_ABBREV
    ALL_LANGUAGES_URL = 'http://austlang.aiatsis.gov.au/php/' \
                        'public/query_submit.php?' \
                        'stateFields=^TAS^VIC^NSW^ACT^SA^NT^WA^QLD^TSI'
    ONE_LANGUAGE_URL_TEMPLATE = 'http://austlang.aiatsis.gov.au/php/public/' \
                                'language_profile_all.php?id=%s'

    def get_iso_list_from_austlang_id(self, austlang_id):
        iso_list = []
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (austlang_id,)))
        iso_text = langsoup.find("a", onmouseover=re.compile(
            "International Organization for Standardization")).parent \
            .text.rpartition(":")[2].strip()
        if iso_text:
            logging.info("Found ISO text %s for Austlang id %s",
                         iso_text, austlang_id)
            # We need to convert to lowercase as Gudanji has the ISO as Nji
            iso_list = [iso.lower().strip() for iso in iso_text.split(",")]
        else:
            # TODO: What if we can't find one? Make one up in the austlang NS?
            # TODO: Do we store a map of austlang to iso?
            logging.warn("Unable to find ISO text for Austlang id %s",
                         austlang_id)
        return iso_list

    def get_ABS_name_from_austlang_id(self, austlang_id):
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (austlang_id,)))
        abn_text = langsoup.find("a", onmouseover=re.compile(
            "Australian Bureau of Statistics")).parent \
            .text.rpartition(":")[2].strip()
        return abn_text

    def get_aiatsis_code_from_austlang_id(self, austlang_id):
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (austlang_id,)))
        aiatsis_name = langsoup.find("a", onmouseover=re.compile(
            "Language identification code used at AIATSIS")) \
                .next_sibling.strip()
        return aiatsis_name

    def get_aiatsis_name_from_austlang_id(self, austlang_id):
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (austlang_id,)))
        aiatsis_name = langsoup.find("a", onmouseover=re.compile(
            "Language identification code used at AIATSIS")) \
                .next_sibling.strip()
        return aiatsis_name

    def get_all_austlang_keys(self):
        soup = BeautifulSoup(
            self.get_text_from_url(self.ALL_LANGUAGES_URL))
        keys = []
        metadata_re = re.compile("parent.webpageMngr.displayTypeMetadata")
        for language_link in soup.find_all("a", href=metadata_re):
            mo = re.search(r"(\d+)", language_link.attrs["href"])
            if mo:
                keys.append(int(mo.group(0)))
            else:
                logging.error("Unable to find austlang id in link: %s",
                              language_link)

        return keys

    def get_language_iso_keys(self):
        isos = []
        for key in self.get_all_austlang_keys():
            # Now go and retrieve the individual language page so we can try to
            #  find an ISO.
            iso_list = self.get_iso_list_from_austlang_id(key)
            isos.extend(iso_list)

        return isos

    def persist_ABS_names(self, persister):
        all_isos = []
        for key in self.get_all_austlang_keys():
            abs_name = self.get_ABS_name_from_austlang_id(key)
            iso_list = self.get_iso_list_from_austlang_id(key)
            if abs_name and iso_list:
                for iso in iso_list:
                    all_isos.append(iso)
                    is_existing_iso = persister.get_iso_list_from_iso(iso)
                    if is_existing_iso:
                        logging.info("Persisting ABS name to existing "
                                     "ISO %s (%s)", iso, abs_name)
                    else:
                        logging.info("Persisting ABS name to new "
                                     "ISO %s (%s)", iso, abs_name)
                    persister.persist_language(iso,
                                               abs_name,
                                               self.ABS_SOURCE_NAME)

        for abs_name, iso in constants.ABS_ISO_EXTRA_MAPPINGS.items():
            if iso in all_isos:
                logging.info("Persisting ABS alias name for ISO %s (%s)",
                             iso,
                             abs_name)
                persister.persist_alternate(iso,
                                            abs_name,
                                            self.ABS_SOURCE_NAME)
            else:
                is_existing_iso = persister.get_iso_list_from_iso(iso)
                if is_existing_iso:
                    logging.info("Persisting ABS name to existing "
                                 "ISO %s (%s) (ABS Extra Mappings)",
                                 iso, abs_name)
                else:
                    logging.info("Persisting ABS name to new "
                                 "ISO %s (%s) (ABS Extra Mappings)",
                                 iso, abs_name)
                persister.persist_language(iso,
                                           abs_name,
                                           self.ABS_SOURCE_NAME)

    def persist_external_references(self, persister):
        for key in self.get_all_austlang_keys():
            iso_list = self.get_iso_list_from_austlang_id(key)
            for iso in iso_list:
                persister.persist_external_reference(
                    iso, key,
                    self.get_aiatsis_code_from_austlang_id(key),
                    constants.AUSTLANG_SOURCE_ABBREV)
