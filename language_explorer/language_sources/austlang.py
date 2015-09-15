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

    # We can't associate the following ABS names with ISOs because the
    #  particular spelling doesn't exist in our names or aliases. I've looked
    #  at the Austlang records and have worked out the mappings below.
    # It's possible that this extra set of mappings exists because austlang
    #  mappings to ISO codes are incomplete, or because I've incorrectly
    #  made an association, or that austlang records are more fine grained
    #  than the records in this data, perhaps because austlang prefers not
    #  to associate dialects with iso codes.
    # We include the full ABS name, even the nfd "Not further defined"
    #  (grouped bucket - coarser granularity and the nec
    #  "Not elsewhere classified" (bucket of last resort)
    ABS_ISO_EXTRA_MAPPINGS = {
        'Bilinarra': "nbj",  # dialect of Ngarinyman (nbj) => 59 speakers
        'Eastern Arrernte': "aer",
        'Galpu': "dhg",  # Dialect of Djangu => 146 speakers
        'Gun-nartpa': "bvr",  # Dialect of Burarra => 89 speakers
        'Gundjeihmi': "gup",  # Dialect of Gunwinngu => 29 speakers
        'Kanai': "unn",  # Is Kurnai
        #'Kaurna', # Not in Ethnologue => 58 speakers. WALS code kaq
        'Murrinh Patha': "mwf",  # Is Murrinh-Patha
        "Ngan'gikurunggurr": "nam",  # Is Nangikurrunggurr
        'Nhangu, nec': "jay",  # Is Yan-nhangu (even though it is a Yolngu language)
        # 'Thaynakwith',  # Unable to find anything. => 3 speakers
        'Wagilak': "rit",  # Is Ritarungo => 16 speakers
        'Wangkatha': "pti",
        'Western Arrarnta': "are",
        #'Wik Ngathan': "wig",  # Is Wig-Ngathana => 4 speakers  XXX seems too small
        'Yumplatok (Torres Strait Creole)': "tcs",  # => 5368 speakers
    }

    def get_iso_list_from_austlang_id(self, austlang_id):
        iso_list = []
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (austlang_id,)))
        iso_text = langsoup.find("a",  onmouseover=re.compile(
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
            # logging.warn("Unable to find ISO for Austlang id %s",
            #              austlang_id)
            pass
        return iso_list

    def get_ABS_name_from_austlang_id(self, austlang_id):
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (austlang_id,)))
        abn_text = langsoup.find("a",  onmouseover=re.compile(
            "Australian Bureau of Statistics")).parent \
            .text.rpartition(":")[2].strip()
        return abn_text

    def get_all_austlang_keys(self):
        soup = BeautifulSoup(
            self.get_text_from_url(self.ALL_LANGUAGES_URL))
        keys = []
        for language_link in soup.find_all(
                "a", href=re.compile("parent.webpageMngr.displayTypeMetadata")):
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
                    logging.info("Persisting ABS name for ISO %s (%s)",
                                 iso,
                                 abs_name)
                    persister.persist_language(iso,
                                               abs_name,
                                               self.ABS_SOURCE_NAME)

        for abs_name, iso in self.ABS_ISO_EXTRA_MAPPINGS.items():
            if iso in all_isos:
                logging.info("Persisting ABS alias name for ISO %s (%s)",
                             iso,
                             abs_name)
                persister.persist_alternate(iso,
                                            abs_name,
                                            self.ABS_SOURCE_NAME)
            else:
                logging.info("Persisting ABS name for ISO %s (%s)",
                             iso,
                             abs_name)
                persister.persist_language(iso,
                                           abs_name,
                                           self.ABS_SOURCE_NAME)
