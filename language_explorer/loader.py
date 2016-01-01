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

# Put these at module level so that we can more easily test by importing
p = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)
joshuaproject = JPHarvestAdapter(settings.JPHARVEST_DB_URL)
fab = FindABibleAdapter(settings.CACHE_ROOT)
austlang = AustlangAdapter(settings.CACHE_ROOT)
wals = WalsAdapter(settings.WALS_DB_URL)
sil_rcem = SilRcemAdapter(settings.SIL_RCEM_TSV_SOURCE)
census = Census2011Adapter(settings.CENSUS_CSV_SOURCE, p)
tindale = TindaleAdapter(settings.CACHE_ROOT, p)


def load_data_from_db_driven_sources(iso_list):
    """To be run whenever new isos are added to our db"""
    for lang in iso_list:
        joshuaproject.persist_L1_speaker_count(p, lang)
        # joshuaproject.persist_dialects(p, lang)

    for source in (joshuaproject, wals):
        for lang in iso_list:
            source.persist_language(p, lang)
            source.persist_alternate_names(p, lang)
            source.persist_classification(p, lang)
            source.persist_translation(p, lang)

    wals.persist_latitude_longitudes(p)


def load_data_for_new_isos(last_complete_iso_list):
    current_complete_iso_list = p.get_all_iso_codes()
    newly_added_isos = set(current_complete_iso_list) \
        .difference(set(last_complete_iso_list))
    logging.info("Processing newly added ISOs: %s", newly_added_isos)
    load_data_from_db_driven_sources(newly_added_isos)
    # And return what we know as the complete list
    return current_complete_iso_list


def main():
    # jpharvest and wals have their own databases with iso keys
    #  and do not need to attempt matching on names, so together
    #  they form our definitive list, and we can load them ignoring
    #  the state of the database (which is not true for subsequent
    #  sources
    all_known_isos = sorted(
        set(wals.get_language_iso_keys()).union(
            set(joshuaproject.get_language_iso_keys()))
        )

    load_data_from_db_driven_sources(all_known_isos)

    sil_rcem.persist_retirement_relationships(p)
    p.insert_reverse_relationships()
    # Census relies on population of ABS names from Austlang, so this must
    #  be run before any census stuff.
    # Austlang can create new ISOs, so from this point we need to ask the
    #  db for all it's ISO codes instead of using "all_known_isos"
    austlang.persist_ABS_names(p)
    austlang.persist_external_references(p)
    # Tindale can also create new ISOs, based on an override dictionary
    tindale.persist_latitude_longitudes()
    # tindale.compare_tindale_wals_lat_lons()

    all_known_isos = load_data_for_new_isos(all_known_isos)

    for lang in all_known_isos:
        census.persist_L1_speaker_count(p, lang)
        census.persist_english_competency(p, lang)

    # XXX - can census create ISOs?
    all_known_isos = load_data_for_new_isos(all_known_isos)

    # FAB can't provide an ISO list, so ask the database! For this
    #  reason, this must run after the db is populated with ISO codes
    for lang in all_known_isos:
        fab.persist_translation(p, lang)


def test():
    # [(iso, <str of comma sep names>), (..) ]
    # from language_explorer.naming_helper import NamingHelper
    # nsl_data = NamingHelper.get_name_summary_list(p)
    # NamingHelper.format_mappings(NamingHelper.summarise_mappings(nsl_data))
    # census.print_stuff()
    # tindale.persist_latitude_longitudes()
    # tindale.compare_tindale_wals_lat_lons()
    austlang.persist_external_references(p)
    #print austlang.get_aiatsis_name_from_austlang_id(989)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-t":
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        sys.exit(test())
    else:
        sys.exit(main())
