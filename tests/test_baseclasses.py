import unittest

__author__ = 'esteele'


class BaseAdapterTestCase(unittest.TestCase):

    def _do_test_all_iso_keys_common(self):
        keys = self.source.get_language_iso_keys()
        # Check no dupes
        self.assertEquals(len(keys), len(list(set(keys))))
        for key in keys:
            self.assertIsInstance(key, basestring)
            self.assertEquals(len(key), 3)

    def _do_test_primary_name_retrieval(self, iso_primary_name_pairs):
        for iso, name in iso_primary_name_pairs:
            self.assertEquals(name,
                              self.source.get_primary_name_for_iso(iso))

    def _do_test_alternate_name_retrieval(self, iso_alternate_name_pairs):
        for iso, alternate_list in iso_alternate_name_pairs:
            self.assertEquals(alternate_list,
                              self.source.get_alternate_names_for_iso(iso))

    def _do_test_classification_retrieval(self, iso_classification_pairs):
        for iso, classification_list in iso_classification_pairs:
            self.assertEquals(classification_list,
                              self.source.get_classification(iso))

    def _do_test_get_translation_info(self, iso_translation_pairs):
        for iso, ts_dict in iso_translation_pairs:
            self.assertEquals(ts_dict,
                              self.source.get_translation_info_for_iso(iso))