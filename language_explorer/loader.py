import logging
import sys
from language_explorer import settings
from language_explorer.language_sources.jpharvest import JPHarvestAdapter
from language_explorer.language_sources.wals import WalsAdapter
from language_explorer.language_sources.findabible import FindABibleAdapter
from language_explorer.language_sources.sil_rcem import SilRcemAdapter
from language_explorer.language_sources.austlang import AustlangAdapter
from language_explorer.language_sources.census_2011 import Census2011Adapter
from language_explorer.language_sources.tindale import TindaleAdapter
from persistence import LanguagePersistence


logging.basicConfig(level=logging.DEBUG)


def main():
    p = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)
    joshuaproject = JPHarvestAdapter(settings.JPHARVEST_DB_URL)
    fab = FindABibleAdapter(settings.CACHE_ROOT)
    austlang = AustlangAdapter(settings.CACHE_ROOT)
    wals = WalsAdapter(settings.WALS_DB_URL)
    sil_rcem = SilRcemAdapter(settings.SIL_RCEM_TSV_SOURCE)
    census = Census2011Adapter(settings.CENSUS_CSV_SOURCE, p)
    tindale = TindaleAdapter(settings.CACHE_ROOT, p)

    # jpharvest and wals have their own databases with iso keys
    #  and do not need to attempt matching on names, so together
    #  they form our definitive list, and we can load them ignoring
    #  the state of the database (which is not true for subsequent
    #  sources
    all_known_isos = sorted(
        set(wals.get_language_iso_keys()).union(
            set(joshuaproject.get_language_iso_keys()))
        )

    for lang in all_known_isos:
        joshuaproject.persist_L1_speaker_count(p, lang)

    for source in (joshuaproject, wals):
        for lang in all_known_isos:
            source.persist_language(p, lang)
            source.persist_alternate_names(p, lang)
            source.persist_classification(p, lang)
            source.persist_translation(p, lang)

    wals.persist_latitude_longitudes(p)

    # FAB can't provide an ISO list, so ask the database!
    # For this reason, this must run after the db is populated with ISO codes
    for lang in all_known_isos:
        fab.persist_translation(p, lang)

    # JH has speaker count and dialects too
    for lang in all_known_isos:
        joshuaproject.persist_L1_speaker_count(p, lang)
    #    jpharvest.persist_dialects(p, lang)

    sil_rcem.persist_retirement_relationships(p)
    p.insert_reverse_relationships()
    # Census relies on population of ABS names from Austlang, so this must be
    #  run before any census stuff.
    # Austlang can create new ISOs, so from this point we need to ask the db
    #  for all it's ISO codes instead of using "all_known_isos"
    austlang.persist_ABS_names(p)

    for lang in p.get_all_iso_codes():
        census.persist_L1_speaker_count(p, lang)
        census.persist_english_competency(p, lang)
    tindale.persist_latitude_longitudes()
    # tindale.compare_tindale_wals_lat_lons()


if __name__ == '__main__':
    sys.exit(main())
