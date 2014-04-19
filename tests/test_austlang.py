from language_explorer import settings, constants
from language_explorer.language_sources.austlang import AustlangAdapter
from tests.test_baseclasses import BaseAdapterTestCase


class TestAustlangAdapter(BaseAdapterTestCase):
    def setUp(self):
        self.source = AustlangAdapter(settings.TEST_CACHE_ROOT)

    def test_get_iso_list_from_austlang_id(self):
        austlang_iso_pairs = [
            (145, ["are", "aer"]),
            (418, ["adt"]),
            (1144, []),
        ]
        for austlang_id, iso_list in austlang_iso_pairs:
            self.assertEqual(iso_list,
                             self.source.get_iso_list_from_austlang_id(
                                 austlang_id))

    def test_get_ABS_name_from_austlang_id(self):
        austlang_name_pairs = [
            (145, "Arrernte"),
            (418, "Adnymathanha"),
            (1144, ""),
        ]
        for austlang_id, abs_name in austlang_name_pairs:
            self.assertEqual(abs_name,
                             self.source.get_ABS_name_from_austlang_id(
                                 austlang_id))