import logging
import sys
from language_sources.jpharvest import JPHarvestAdapter
from language_sources.ethnologue import EthnologueAdapter
from persistence import LanguagePersister


LANGUAGE_EXPLORER_DB_URL = 'postgresql://esteele@localhost/language_explorer'
JPHARVEST_DB_URL = 'postgresql://esteele@localhost/jpharvest'

logging.basicConfig(level=logging.DEBUG)


def main():
    CACHE_ROOT = "/Users/esteele/Code/language_explorer/data/.cache"
    ethnologue = EthnologueAdapter(CACHE_ROOT)
    p = LanguagePersister(LANGUAGE_EXPLORER_DB_URL)
    joshuaproject = JPHarvestAdapter(JPHARVEST_DB_URL)
    for source in (ethnologue, joshuaproject):
        for lang in source.get_language_iso_keys():
            source.persist_language(p, lang)
            source.persist_alternate_names(p, lang)


if __name__ == '__main__':
    sys.exit(main())
