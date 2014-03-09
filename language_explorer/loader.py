import logging
import sys
from language_explorer import settings
from language_explorer.language_sources.jpharvest import JPHarvestAdapter
from language_explorer.language_sources.ethnologue import EthnologueAdapter
from language_explorer.language_sources.wals import WalsAdapter
from language_explorer.language_sources.findabible import FindABibleAdapter
from persistence import LanguagePersistence


logging.basicConfig(level=logging.DEBUG)


def main():
    ethnologue = EthnologueAdapter(settings.CACHE_ROOT)
    p = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)
    joshuaproject = JPHarvestAdapter(settings.JPHARVEST_DB_URL)
    fab = FindABibleAdapter(settings.CACHE_ROOT)
    wals = WalsAdapter(settings.WALS_DB_URL)
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

if __name__ == '__main__':
    sys.exit(main())
