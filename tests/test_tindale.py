# -*- coding: utf8 -*-
from language_explorer import settings
from language_explorer.language_sources.tindale import TindaleAdapter
from tests.test_baseclasses import BaseAdapterTestCase


class TestTindaleAdapter(BaseAdapterTestCase):
    def setUp(self):
        self.source = TindaleAdapter(settings.TEST_CACHE_ROOT)

    def test_extract_lat_lon_from_coordinate_str(self):
        coord_latlon_pairs = [
            ("139°5'E x 26°50'S", (139.08333333333334, 26.833333333333332)),
        ]
        for utf8_coord_str, latlon_list in coord_latlon_pairs:
            self.assertEqual(
                latlon_list,
                self.source.
                extract_lat_lon_from_coordinate_str(utf8_coord_str))

    def test_get_lat_lon_from_tindale_id(self):
        tindale_id_latlon_pairs = [
            ("ngameni", (139.08333333333334, 26.833333333333332)),
            # 139 deg 5'E, 26 deg 50'S
        ]
        for tindale_id, latlon_list in tindale_id_latlon_pairs:
            self.assertEqual(latlon_list,
                             self.source.
                             get_lat_lon_from_tindale_id(tindale_id))
