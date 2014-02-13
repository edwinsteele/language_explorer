import logging
from language_sources.base import CachingWebLanguageSource
from bs4 import BeautifulSoup

__author__ = 'esteele'

logging.basicConfig(level=logging.DEBUG)


class EthnologueAdapter(CachingWebLanguageSource):
    SOURCE_NAME = "EL"
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
        logging.info("Getting primary name for iso %s", iso)
        soup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
        ))
        return soup.find(id="page-title").text

    def get_alternate_names_for_iso(self, iso):
        # Some don't have alternate names e.g. aid - robustify
        soup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
        ))
        alt_base_div = soup.find(class_="field-name-field-alternate-names")
        if alt_base_div:
            return [s.strip() for s in
                    alt_base_div.find(class_="field-item").text.split(",")]
        else:
            return []

    def get_dialects_for_iso(self, iso):
        # Some don't have dialects e.g. aid - robustify
        soup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (iso,)
        ))
        dialect_string = soup.find(class_="field-name-field-dialects") \
            .find(class_="field-item").text
        print "Ethnologue '%s': Found dialects %s" % (iso, dialect_string,)

        return []
