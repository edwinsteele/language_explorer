import logging
import sys
from language_sources.jpharvest import JPHarvestAdapter
from language_sources.ethnologue import EthnologueAdapter
from language_sources.wals import WalsAdapter
from persistence import LanguagePersistence
import settings


logging.basicConfig(level=logging.DEBUG)


def main():
    ethnologue = EthnologueAdapter(settings.CACHE_ROOT)
    p = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)
    joshuaproject = JPHarvestAdapter(settings.JPHARVEST_DB_URL)
    wals = WalsAdapter(settings.WALS_DB_URL)
    for source in (ethnologue, joshuaproject, wals):
        for lang in source.get_language_iso_keys():
            source.persist_language(p, lang)
            source.persist_alternate_names(p, lang)
            source.persist_classification(p, lang)


if __name__ == '__main__':
    sys.exit(main())
