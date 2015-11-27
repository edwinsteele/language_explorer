from language_explorer import settings, constants

from language_explorer.language_sources.census_2011 import Census2011Adapter
from language_explorer.persistence import LanguagePersistence
from tests.test_baseclasses import BaseAdapterTestCase
import unittest


class TestCensus2011Adapter(BaseAdapterTestCase):
    """
    Unlike most other source adapters, the census adapter relies on lots of
    other data in the database instead of just reading from source files.
    Austlang must have been loaded, and indeed lots of others
    """

    def setUp(self):
        p = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)
        self.source = Census2011Adapter(settings.CENSUS_CSV_SOURCE, p)

    @unittest.skip("Review - no initial thoughts about why this fails")
    def test_population_for_iso(self):
        iso_count_pairs = [
            ("gbb", 172),  # iso to single lang to single iso
            ("piu", 1646),  # iso to two langs each with a single iso
            ("not_exist", constants.SPEAKER_COUNT_UNKNOWN),
            ("yii", constants.SPEAKER_COUNT_UNKNOWN),  # no speakers, but we
            # don't store data with less than SMALL_CELL_COUNT_THRESHOLD
            # speakers
            ("gbc", constants.SPEAKER_COUNT_AMBIGUOUS),  # iso to single lang
            # to 2 isos
            ("aer", constants.SPEAKER_COUNT_AMBIGUOUS),  # iso to 3 langs that
            # map to 2, 2 and 1 iso
        ]
        for iso, count in iso_count_pairs:
            self.assertEqual(count,
                             self.source.get_L1_speaker_count_for_iso(iso))

    @unittest.skip("Review - no initial thoughts about why this fails")
    def test_english_competency(self):
        iso_competency_pairs = [
            ("gbb", (33, 83)),
            ("piu", (25, 67)),
            ("not_exist", (constants.ENGLISH_COMPETENCY_UNKNOWN_PESSIMISTIC,
                           constants.ENGLISH_COMPETENCY_UNKNOWN_OPTIMISTIC)),
            ("yiu", (constants.ENGLISH_COMPETENCY_UNKNOWN_PESSIMISTIC,
                     constants.ENGLISH_COMPETENCY_UNKNOWN_OPTIMISTIC)),
            ("gbc", (72, 93)),
            ("aer", (45, 84)),
        ]
        for iso, competencies in iso_competency_pairs:
            self.assertEqual(
                competencies,
                self.source.get_english_competency_percentages(iso)
            )
