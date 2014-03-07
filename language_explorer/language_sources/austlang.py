import re
import logging

from bs4 import BeautifulSoup
from language_explorer import constants

from language_explorer.language_sources.base import CachingWebLanguageSource


__author__ = 'esteele'

logging.basicConfig(level=logging.DEBUG)


class AustlangAdapter(CachingWebLanguageSource):
    SOURCE_NAME = constants.AUSTLANG_SOURCE_ABBREV
    ALL_LANGUAGES_URL = 'http://austlang.aiatsis.gov.au/php/' \
                        'public/query_submit.php?' \
                        'stateFields=^TAS^VIC^NSW^ACT^SA^NT^WA^QLD^TSI'
    ONE_LANGUAGE_URL_TEMPLATE = 'http://austlang.aiatsis.gov.au/php/public/' \
                                'language_profile_all.php?id=%s'

    def get_iso_list_from_austlang_id(self, austlang_id):
        iso_list = []
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (austlang_id,)))
        iso = langsoup.find("a",  onmouseover=re.compile(
            "International Organization for Standardization")).parent \
            .text.rpartition(":")[2].strip()
        # logging.info("IFC ->%s<-", iso_field_container)
        if iso:
            # FIXME - this can be a list e.g. id 145 (aer, are)
            logging.info("Found ISO %s for Austlang id %s",
                         iso, austlang_id)
            iso_list.append(iso)
        else:
            # TODO: What if we can't find one? Make one up in the austlang NS?
            # TODO: Do we store a map of austlang to iso?
            logging.warn("Unable to find ISO for Austlang id %s",
                         austlang_id)
        return iso_list

    def get_language_iso_keys(self):
        soup = BeautifulSoup(
            self.get_text_from_url(self.ALL_LANGUAGES_URL))
        keys = []
        for language_link in soup.find_all(
                "a", href=re.compile("parent.webpageMngr.displayTypeMetadata")):
            mo = re.search(r"(\d+)", language_link.attrs["href"])
            if mo:
                austlang_id = int(mo.group(0))
            else:
                logging.error("Unable to find austlang id in link: %s",
                              language_link)
                austlang_id = -1

            # Now go and retrieve the individual language page so we can try to
            #  find an ISO.
            iso_list = self.get_iso_list_from_austlang_id(austlang_id)
            keys.extend(iso_list)

        return keys
