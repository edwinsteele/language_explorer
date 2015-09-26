import logging
import sys
from language_explorer import settings
from language_explorer.language_sources.jpharvest import JPHarvestAdapter
from language_explorer.language_sources.ethnologue import EthnologueAdapter
from language_explorer.language_sources.wals import WalsAdapter
from language_explorer.language_sources.findabible import FindABibleAdapter
from language_explorer.language_sources.sil_rcem import SilRcemAdapter
from language_explorer.language_sources.austlang import AustlangAdapter
from language_explorer.language_sources.census_2011 import Census2011Adapter
from persistence import LanguagePersistence


logging.basicConfig(level=logging.DEBUG)


def main():
    ethnologue = EthnologueAdapter(settings.CACHE_ROOT)
    p = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)
    joshuaproject = JPHarvestAdapter(settings.JPHARVEST_DB_URL)
    fab = FindABibleAdapter(settings.CACHE_ROOT)
    austlang = AustlangAdapter(settings.CACHE_ROOT)
    wals = WalsAdapter(settings.WALS_DB_URL)
    sil_rcem = SilRcemAdapter(settings.SIL_RCEM_TSV_SOURCE)
    census = Census2011Adapter(settings.CENSUS_CSV_SOURCE, p)
    for source in (ethnologue, joshuaproject, wals):
        for lang in source.get_language_iso_keys():
            source.persist_language(p, lang)
            source.persist_alternate_names(p, lang)
            source.persist_classification(p, lang)
            source.persist_translation(p, lang)

    # FAB can't provide an ISO list, so ask the database!
    # For this reason, this must run after the db is populated with ISO codes
    for lang in p.get_all_iso_codes():
        fab.persist_translation(p, lang)

    for lang in ethnologue.get_language_iso_keys():
        ethnologue.persist_L1_speaker_count(p, lang)
        ethnologue.persist_dialects(p, lang)
        ethnologue.persist_writing_state(p, lang)

    sil_rcem.persist_retirement_relationships(p)
    p.insert_reverse_relationships()
    # Census relies on population of ABS names from Austlang, so this must be
    #  run before any census stuff
    austlang.persist_ABS_names(p)
    wals.persist_latitude_longitudes(p)

    for lang in p.get_all_iso_codes():
        census.persist_L1_speaker_count(p, lang)
        census.persist_english_competency(p, lang)

if __name__ == '__main__':
    sys.exit(main())
