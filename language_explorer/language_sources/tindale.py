# -*- coding: utf8 -*-
import logging
import math
import string

from bs4 import BeautifulSoup
from language_explorer import constants
from language_explorer.language_sources.base import CachingWebLanguageSource

logging.basicConfig(level=logging.DEBUG)


class TindaleAdapter(CachingWebLanguageSource):
    SOURCE_NAME = constants.TINDALE_SOURCE_ABBREV
    ONE_LANGUAGE_URL_TEMPLATE = "http://archives.samuseum.sa.gov.au/" \
                                "tindaletribes/%s.htm"
    INDEX_URL_TEMPLATE = "http://archives.samuseum.sa.gov.au/" \
                         "tindaletribes/%s.htm"
    # a-y, with no x
    INDEX_PAGES = string.lowercase.translate(None, "xz")
    # Non-existant page: act, koko-
    # Entries without lat lon: kurnai, murngin, wik-
    FALSE_IDS = ["act", "koko-", "kurnai", "murngin", "wik-"]
    # These need manual adjustment due to errors in source data
    #  or unparseable coordinates (njangamarda)
    MANUALLY_ADJUSTED_LAT_LON_DICT = {
        "ngaliwuru": (-16.1666666667, 130.666666667),  # 120E -> 130E
        "kamilaroi": (-30.25, 150.583333333),  # 140E -> 150E
        "njangamarda": (-20.666666667, 122.0),  # Avg of 2 locations
        "lardiil": (-16.583, 139.333),  # 137E -> 139E
    }
    # Hand-matching
    TINDALE_ID_TO_ISO_OVERRIDE_DICT = {
        "wik-kalkan": ["wik"],
        "biria": [constants.ISO_NO_MATCH],  # Bowen River QLD. Not xpa
        "jangaa": [constants.ISO_NO_MATCH],  # Pre-contact group. Not nny
        "jeidji": ["vmi"],  # Not wub
        "miwa": ["vmi"],  # Not wub
        "inawongga": [constants.ISO_NO_MATCH],  # matches nlr, but too distant
        "ninanu": [constants.ISO_NO_MATCH],  # matches nlr, but too distant
        "barkindji": ["drl"],  # Most accurate drl
        "barindji": [constants.ISO_NO_MATCH],  # drl dialect - not best latlon
        "kula": [constants.ISO_NO_MATCH],  # drl dialect - not best latlon
        "milpulo": [constants.ISO_NO_MATCH],  # drl dialect - not best latlon
        "wiri": [constants.ISO_NO_MATCH],  # not xnk. does not appear anywhere
        "goeng": [constants.ISO_NO_MATCH],  # sig match for bxj but too distant
        "dalla": [constants.ISO_NO_MATCH],  # sig match for duj but too distant
        "tulua": [constants.ISO_NO_MATCH],  # sig match for duj but too distant
        "maduwongga": [constants.ISO_NO_MATCH],  # same name as SA tribe but
        # this is in WA
        "ngewin": [constants.ISO_NO_MATCH],  # sig match for nxn but in NT
        "wakaman": ["gvn"],  # dialect of gvn. AIATSIS Y223 -> Y78
        "wikmean": ["wih"],  # Few speakers. AIATSIS Y53
        "mingin": [constants.ISO_NO_MATCH],  # sig match for wim.
        # AIATSIS G26 but no ISO
    }
    REVIEWED_LAT_LON_DISCREPANCIES = [
        "nbj",
        "wmb",
        "dhu",  # Inconclusive: Doesn't appear on AIATSIS Map. No speakers.
        "djd",  # Pref WALS: WALS is closer to AIATSIS Map location.
        "gue",  # Avg: Tindale close to AIATSIS, but no convincing consensus
        "kld",  # Pref Tindale: Large area but Tindale closer to AIATSIS
        "wrg",  # Inconclusive. Not on AIATSIS. No speakers.
        "zmc",  # Pref Tindale: Agree with AIATSIS.
    ]

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
        # Tindale entries put longitude first, then latitude.
        lon, lat = utf8_coord_str.split(lat_lon_splitter)
        lon_degs, lon_mins = lon.split(degree_symbol)
        # Some entries do not have minutes but only have degress
        # e.g. Rembarunga
        if lon_mins == "E":
            lon_mins = "0"
            minute_splitter = minute_symbol
        else:
            if minute_symbol not in lon_mins:
                # Some entries have ´ instead of ' as the symbol for minutes
                # e.g. gungorogone
                minute_splitter = alt_minute_symbol
            else:
                minute_splitter = minute_symbol
            lon_mins = lon_mins.split(minute_splitter)[0]

        # Some entries incorrectly drop the degree symbol when
        #  the minutes value is 0
        # e.g. ngarlawongga
        if degree_symbol not in lat:
            lat_degs = lat.split(minute_splitter)[0]
            lat_mins = "0"
        else:
            lat_degs, lat_mins = lat.split(degree_symbol)
            # Some entries do not have minutes but only have degrees
            # e.g. niabali
            if lat_mins == "S":
                lat_mins = "0"
            else:
                lat_mins = lat_mins.split(minute_splitter)[0]

        # Several entries have typos where l replaces a 1
        # e.g. bilingara, indjilandji, kokobujundji, wurango
        lat_degs = lat_degs.replace("l", "1")
        # Convert minutes to decimal degrees
        lon_as_decimal = int(lon_degs) + float(lon_mins) / 60
        lat_as_decimal = int(lat_degs) + float(lat_mins) / 60
        # Negate longitude, as all are south
        return -lat_as_decimal, lon_as_decimal

    def get_lat_lon_from_tindale_id(self, tindale_id):
        # Some lat lon are hard-coded
        if tindale_id in self.MANUALLY_ADJUSTED_LAT_LON_DICT:
            return self.MANUALLY_ADJUSTED_LAT_LON_DICT[tindale_id]
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (tindale_id,)))
        coord_str = langsoup.find("td", text="Co-ordinates")\
            .next_sibling.text
        utf8_coord_str = coord_str.encode('utf8', 'replace')
        return TindaleAdapter.extract_lat_lon_from_coordinate_str(
            utf8_coord_str)

    def get_iso_from_tindale_id(self, tindale_id):
        # tindale_ids are all lower case, but matching routines are
        #  case sensitive and are stored capitalised. This is ok
        #  because for the few ids that need something more complex
        #  we have used the override dictionary e.g. those with a
        #  dash in their name
        if tindale_id in self.TINDALE_ID_TO_ISO_OVERRIDE_DICT:
            exact_iso_matches = \
                self.TINDALE_ID_TO_ISO_OVERRIDE_DICT[tindale_id]
        else:
            tindale_id = tindale_id.capitalize()
            exact_iso_matches = \
                self.persister.get_iso_list_from_name(tindale_id)
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
        def approx_equal(a, b, tol=1.0):
            return abs(a - b) < tol
        added_count = 0
        multi_match_count = 0
        no_match_count = 0
        attempted_overwrite_count = 0
        for tindale_id in self.get_all_tindale_ids():
            iso = self.get_iso_from_tindale_id(tindale_id)
            if iso == constants.ISO_NO_MATCH:
                no_match_count += 1
            elif iso == constants.ISO_MULTI_MATCH:
                multi_match_count += 1
            else:
                existing_tindale_lat, existing_tindale_lon = \
                    self.persister.get_tindale_lat_lon_from_iso(iso)
                tindale_lat, tindale_lon = \
                    self.get_lat_lon_from_tindale_id(tindale_id)
                if not approx_equal(tindale_lat, existing_tindale_lat) and \
                        not approx_equal(tindale_lon, existing_tindale_lon) and \
                        existing_tindale_lat != constants.LATITUDE_UNKNOWN and \
                        existing_tindale_lon != constants.LONGITUDE_UNKNOWN:
                    logging.warning("Attempting to overwrite existing tindale "
                                    "lat lon for %s with very diff value "
                                    "Current: %.2f, %.2f "
                                    "New: %.2f, %.2f "
                                    "Not overwriting.",
                                    iso,
                                    existing_tindale_lat,
                                    existing_tindale_lon,
                                    tindale_lat,
                                    tindale_lon)
                    attempted_overwrite_count += 1
                else:
                    logging.debug("Adding tindale location to %s. "
                                  "lat: %.3f lon: %.3f",
                                  iso,
                                  tindale_lat,
                                  tindale_lon)
                    self.persister.persist_tindale_lat_lon(
                        iso,
                        tindale_lat,
                        tindale_lon)
                    added_count += 1

        logging.info("SUMMARY: Able to add %s, no match %s, multi %s, "
                     "overwrite %s",
                     added_count, no_match_count, multi_match_count,
                     attempted_overwrite_count)

    def compare_tindale_wals_lat_lons(self):
        """Compares tindale and WALS lat lons for all ISOs
        Assumes all persistence has been done"""
        def ll_is_unknown(lat, lon):
            return lat == constants.LATITUDE_UNKNOWN and \
                lon == constants.LONGITUDE_UNKNOWN

        no_lat_lon_count = 0
        wals_lat_lon_count = 0
        tindale_lat_lon_count = 0
        both_lat_lon_count = 0
        for iso in self.persister.get_all_iso_codes():
            db_lat, db_lon = self.persister.get_lat_lon_from_iso(iso)
            tindale_lat, tindale_lon = \
                self.persister.get_tindale_lat_lon_from_iso(iso)
            if ll_is_unknown(db_lat, db_lon):
                if ll_is_unknown(tindale_lat, tindale_lon):
                    no_lat_lon_count += 1
                    logging.info("ISO %s has no lat lon", iso)
                else:
                    tindale_lat_lon_count += 1
                    logging.info("ISO %s has only tindale lat lon "
                                 "(%.2f, %.2f)",
                                 iso,
                                 tindale_lat,
                                 tindale_lon)
            else:
                if ll_is_unknown(tindale_lat, tindale_lon):
                    wals_lat_lon_count += 1
                    logging.info("ISO %s has only WALS lat lon "
                                 "(%.2f, %.2f)",
                                 iso,
                                 db_lat,
                                 db_lon)
                else:
                    both_lat_lon_count += 1
                    max_discrepancy = max(
                        math.ceil(abs(db_lat - tindale_lat)),
                        math.ceil(abs(db_lon - tindale_lon))
                    )
                    # 1 deg lon in Australia is about 100km
                    # 1 deg lat is about 100km everywhere
                    logging.info("ISO %s has WALS and Tindale lat lon. "
                                 "Max discrepancy < %d deg. "
                                 "WALS: (%.2f, %.2f) "
                                 "Tindale: (%.2f, %.2f) "
                                 "Reviewed: %s",
                                 iso,
                                 max_discrepancy,
                                 db_lat,
                                 db_lon,
                                 tindale_lat,
                                 tindale_lon,
                                 iso in self.REVIEWED_LAT_LON_DISCREPANCIES)

        logging.info("SUMMARY. None: %s, Tindale only: %s, "
                     "WALS only: %s, Both: %s",
                     no_lat_lon_count,
                     tindale_lat_lon_count,
                     wals_lat_lon_count,
                     both_lat_lon_count)
