import logging
import sys
from language_sources.jpharvest import JPHarvestAdapter
from language_sources.ethnologue import EthnologueAdapter
from persistence import LanguagePersister
import settings


logging.basicConfig(level=logging.DEBUG)


def main():
    ethnologue = EthnologueAdapter(settings.CACHE_ROOT)
    p = LanguagePersister(settings.LANGUAGE_EXPLORER_DB_URL)
    joshuaproject = JPHarvestAdapter(settings.JPHARVEST_DB_URL)
    for source in (ethnologue, joshuaproject):
        for lang in source.get_language_iso_keys():
            source.persist_language(p, lang)
            source.persist_alternate_names(p, lang)


if __name__ == '__main__':
    sys.exit(main())
