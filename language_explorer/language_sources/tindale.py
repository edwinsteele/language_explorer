# -*- coding: utf8 -*-
__author__ = 'esteele'
import logging

from bs4 import BeautifulSoup
from language_explorer import constants
from language_explorer.language_sources.base import CachingWebLanguageSource

logging.basicConfig(level=logging.DEBUG)


class TindaleAdapter(CachingWebLanguageSource):
    SOURCE_NAME = constants.ETHNOLOGUE_SOURCE_ABBREV
    ONE_LANGUAGE_URL_TEMPLATE = "http://archives.samuseum.sa.gov.au/" \
                                "tindaletribes/%s.htm"

    def extract_lat_lon_from_coordinate_str(self, utf8_coord_str):
        """139°5'E x 26°50'S -> [139.083, -26.833]

        Only degrees and minutes, never seconds.
        Always assume lat is East and lon is South
        """
        lat, lon = utf8_coord_str.split(" x ")
        lat_degs, lat_mins = lat.split("\xc2\xb0")
        lat_mins = lat_mins.split("'")[0]
        lon_degs, lon_mins = lon.split("\xc2\xb0")
        lon_mins = lon_mins.split("'")[0]
        # Convert minutes to decimal degrees
        lat_as_decimal = int(lat_degs) + float(lat_mins) / 60
        lon_as_decimal = int(lon_degs) + float(lon_mins) / 60
        return lat_as_decimal, lon_as_decimal

    def get_lat_lon_from_tindale_id(self, tindale_id):
        langsoup = BeautifulSoup(self.get_text_from_url(
            self.ONE_LANGUAGE_URL_TEMPLATE % (tindale_id,)))
        coord_str = langsoup.find("td", text="Co-ordinates")\
            .next_sibling.text
        utf8_coord_str = coord_str.encode('utf8', 'replace')
        return self.extract_lat_lon_from_coordinate_str(utf8_coord_str)
