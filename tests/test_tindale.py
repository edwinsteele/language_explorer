# -*- coding: utf8 -*-
from language_explorer import settings
from language_explorer.language_sources.tindale import TindaleAdapter
from tests.test_baseclasses import BaseAdapterTestCase
from language_explorer.persistence import LanguagePersistence


class TestTindaleAdapter(BaseAdapterTestCase):
    def setUp(self):
        p = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)
        self.source = TindaleAdapter(settings.TEST_CACHE_ROOT, p)

    def test_extract_lat_lon_from_coordinate_str(self):
        coord_latlon_pairs = [
            # standard form
            ("139°5'E x 26°50'S", (139.08333333333334, -26.833333333333332)),
            # bilingara typo (l rather than 1)
            ("131°40'E x l5°55'S", (131.66666666666666, -15.916666666666666)),
            # gungorogone alternatve minute symbol
            ("134°20´E x 12°30´S", (134.33333333333334, -12.5)),
            # kungkalenja alternative splitter
            ("139°15'Ex23°45'S", (139.25, -23.75)),
            # ngarlawongga missing degree sign
            ("118°55'E x 20'S", (118.916666666666666, -20.0)),
            # niabali missing minutes
            ("120°10'E x 23°S", (120.16666666666667, -23.0)),
            # rembarunga missing minutes, and has extra space
            ("134°E x 13° 15'S", (134.0, -13.25)),
            # wurango typo (two l's rather than 1s)
            ("132°5'E x ll°15'S", (132.08333333333334, -11.25)),
        ]
        for utf8_coord_str, latlon_list in coord_latlon_pairs:
            self.assertEqual(
                latlon_list,
                self.source.
                extract_lat_lon_from_coordinate_str(utf8_coord_str))

    def test_get_lat_lon_from_tindale_id(self):
        tindale_id_latlon_pairs = [
            ("ngameni", (139.08333333333334, -26.833333333333332)),
            # 139 deg 5'E, 26 deg 50'S
            ("bilingara", (131.66666666666666, -15.916666666666666)),
            # 131 deg 40E, 15 deg 55'S
        ]
        for tindale_id, latlon_list in tindale_id_latlon_pairs:
            self.assertEqual(latlon_list,
                             self.source.
                             get_lat_lon_from_tindale_id(tindale_id))

    def test_get_all_tindale_ids(self):
        tindale_ids = self.source.get_all_tindale_ids()
        self.assertEqual(len(tindale_ids), 593)
