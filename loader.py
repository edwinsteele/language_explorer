import logging
import sys
from language_sources.jpharvest import JPHarvestAdapter
from persistence import LanguagePersister


LANGUAGE_EXPLORER_DB_URL = 'postgresql://esteele@localhost/language_explorer'
JPHARVEST_DB_URL = 'postgresql://esteele@localhost/jpharvest'

logging.basicConfig(level=logging.DEBUG)


def main():
    p = LanguagePersister(LANGUAGE_EXPLORER_DB_URL)
    jp_db = JPHarvestAdapter(JPHARVEST_DB_URL)
    for lang in jp_db.get_language_iso_keys():
        jp_db.persist_language(p, lang)
        jp_db.persist_alternate_names(p, lang)


if __name__ == '__main__':
    sys.exit(main())
