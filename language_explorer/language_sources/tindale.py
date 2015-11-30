# -*- coding: utf8 -*-
__author__ = 'esteele'
import logging
import string

from bs4 import BeautifulSoup
from language_explorer import constants
from language_explorer.language_sources.base import CachingWebLanguageSource

logging.basicConfig(level=logging.DEBUG)


class TindaleAdapter(CachingWebLanguageSource):
    SOURCE_NAME = constants.ETHNOLOGUE_SOURCE_ABBREV
    ONE_LANGUAGE_URL_TEMPLATE = "http://archives.samuseum.sa.gov.au/" \
                                "tindaletribes/%s.htm"
    INDEX_URL_TEMPLATE = "http://archives.samuseum.sa.gov.au/" \
                         "tindaletribes/%s.htm"
    # a-y, with no x
    INDEX_PAGES = string.lowercase.translate(None, "xz")
    # Administrative areas: ACT
    # Broken page: koko-
    # Entries without lat lon: kurnai, murngin, wik-
    # XXX - Entries needing alternative parsing (but data is there):
    #       njangarmarda
    FALSE_IDS = ["act", "koko-", "kurnai", "murngin", "njangamarda", "wik-"]

    def __init__(self, cache_root, persister):
        self.persister = persister
        super(TindaleAdapter, self).__init__(cache_root)

    @staticmethod
    def extract_lat_lon_from_coordinate_str(utf8_coord_str):
        """139°5'E x 26°50'S -> [139.083, -26.833]

        Only degrees and minutes, never seconds.
        Always assume lat is East and lon is South
        """
        lat_lon_splitter = " x "
        minute_symbol = "'"
        alt_minute_symbol = "´"
        degree_symbol = "\xc2\xb0"
        # Some entries split by "x" instead of " x "
        # e.g. kungkalenja
        if lat_lon_splitter not in utf8_coord_str:
            lat_lon_splitter = "x"
        lat, lon = utf8_coord_str.split(lat_lon_splitter)
        lat_degs, lat_mins = lat.split(degree_symbol)
        # Some entries do not have minutes but only have degress
        # e.g. Rembarunga
        if lat_mins == "E":
            lat_mins = "0"
            minute_splitter = minute_symbol
        else:
            if minute_symbol not in lat_mins:
                # Some entries have ´ instead of ' as the symbol for minutes
                # e.g. gungorogone
                minute_splitter = alt_minute_symbol
            else:
                minute_splitter = minute_symbol
            lat_mins = lat_mins.split(minute_splitter)[0]

        # Some entries incorrectly drop the degree symbol when
        #  the minutes value is 0
        # e.g. ngarlawongga
        if degree_symbol not in lon:
            lon_degs = lon.split(minute_splitter)[0]
            lon_mins = "0"
        else:
            lon_degs, lon_mins = lon.split(degree_symbol)
            # Some entries do not have minutes but only have degrees
            # e.g. niabali
            if lon_mins == "S":
                lon_mins = "0"
            else:
                lon_mins = lon_mins.split(minute_splitter)[0]

        # Several entries have typos where l replaces a 1
        # e.g. bilingara, indjilandji, kokobujundji, wurango
        lon_degs = lon_degs.replace("l", "1")
        # Convert minutes to decimal degrees
        lat_as_decimal = int(lat_degs) + float(lat_mins) / 60
        lon_as_decimal = int(lon_degs) + float(lon_mins) / 60
        # Negate longitude, as all are south
        return lat_as_decimal, -lon_as_decimal

    def get_lat_lon_from_tindale_id(self, tindale_id):
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (tindale_id,)))
        coord_str = langsoup.find("td", text="Co-ordinates")\
            .next_sibling.text
        utf8_coord_str = coord_str.encode('utf8', 'replace')
        return TindaleAdapter.extract_lat_lon_from_coordinate_str(
            utf8_coord_str)

    def get_iso_from_tindale_id(self, tindale_id):
        # tindale_ids are all lower case, but matching routines are
        #  case sensitive and are stored capitalised
        # XXX - need to do better than just simple capitalisation but
        #  it's a start. Perhaps it's not that bad... there appear to
        #  only be 3 that have a dash Koko- Wiki- Wik-kalkan
        tindale_id = tindale_id.capitalize()
        exact_iso_matches = self.persister.get_iso_list_from_name(tindale_id)
        if len(exact_iso_matches) == 1:
            logging.debug("Exact match for Tindale id '%s' to iso %s",
                          tindale_id,
                          exact_iso_matches[0])
            return exact_iso_matches[0]
        elif len(exact_iso_matches) > 1:
            # XXX - attempt to match alternative names
            logging.debug("Multiple match for Tindale id '%s' to isos: %s",
                          tindale_id,
                          ",".join(exact_iso_matches))
            return constants.ISO_MULTI_MATCH
        else:
            logging.debug("No match for Tindale id '%s'",
                          tindale_id)
            return constants.ISO_NO_MATCH

    def get_all_tindale_ids(self):
        tindale_ids = set()
        for index_page in self.INDEX_PAGES:
            soup = BeautifulSoup(self.get_text_from_url(
                self.INDEX_URL_TEMPLATE % (index_page,)))
            tribeIndexTable = soup.find(id="TribeIndex")
            tindale_ids.update(
                [id_anchor["href"].split(".")[0]
                 for id_anchor in tribeIndexTable.find_all("a")
                 if id_anchor["href"].split(".")[0] not in self.FALSE_IDS])

        return sorted(list(tindale_ids))

    def persist_latitude_longitudes(self):
        new_latlon = already_has_latlon = multi = nomatch = 0
        for tindale_id in self.get_all_tindale_ids():
            iso = self.get_iso_from_tindale_id(tindale_id)
            if iso == constants.ISO_NO_MATCH:
                nomatch += 1
            elif iso == constants.ISO_MULTI_MATCH:
                multi += 1
            else:
                db_lat, db_lon = self.persister.get_lat_lon_from_iso(iso)
                if db_lat != constants.LATITUDE_UNKNOWN and \
                   db_lon != constants.LONGITUDE_UNKNOWN:
                    logging.info("Able to add lat lon for %s", iso)
                    new_latlon += 1
                else:
                    # XXX check that it's not too dissimilar to existing one
                    logging.info("Lat lon already exists for %s", iso)
                    already_has_latlon += 1

        print self.persister.get_no_lat_lon_count()
        logging.info("Able to add %s, already has %s, no match %s, multi %s",
                     new_latlon, already_has_latlon, nomatch, multi)
