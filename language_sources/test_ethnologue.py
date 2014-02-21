from ethnologue import EthnologueAdapter
from test_baseclasses import BaseAdapterTestCase
import settings

__author__ = 'esteele'


class TestEthnologueAdapter(BaseAdapterTestCase):
    def setUp(self):
        self.source = EthnologueAdapter(settings.TEST_CACHE_ROOT)

    def test_all_iso_keys(self):
        keys = self.source.get_language_iso_keys()
        self.assertEquals(len(keys), 390)
        self.assertEquals(keys[0], "dth")
        self.assertEquals(keys[-1], "yxu")
        self._do_test_all_iso_keys_common()

    def test_primary_name_retrieval(self):
        iso_primary_name_pairs = [
            ("dth", "Adithinngithigh"),  # normal
            ("yxu", "Yuyu"),  # normal
            ("xmp", u"Kuku-Mu\u2019inh"),  # quotes
            ("tcs", "Torres Strait Creole"),  # spaces
        ]
        self._do_test_primary_name_retrieval(iso_primary_name_pairs)

    def test_alternate_name_retrieval(self):
        iso_alternate_name_pairs = [
            ("dth", ["Adetingiti"]),  # One alternate
            ("yij", ["Jindjibandi", "Yinjtjipartnti"]),  # Two alternates
            ("aid", []),  # No alternates
            ("dax", [u"Dha\u2019i", u"Dhay\u2019yi"]),  # Names with quotes
            ("aer", ["Arunta", "Eastern Aranda", "Upper Aranda"]),  # Has spaces
        ]
        self._do_test_alternate_name_retrieval(iso_alternate_name_pairs)

    def test_classification_retrieval(self):
        iso_classification_pairs = [
            ("asf", ["Deaf sign language"]),  # 1 classification, and spaces
            ("bcj", ["Australian", "Nyulnyulan"]),  # 2 classifications
            ("amg", ["Australian", "Yiwaidjan", "Amaragic"]),  # 3
            ("dax", ["Australian", "Pama-Nyungan", "Yuulngu", "Dhuwal"]),  # 4
        ]
        self._do_test_classification_retrieval(iso_classification_pairs)