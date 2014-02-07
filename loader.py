import logging
import sys
import dataset
import sqlsoup
from sqlalchemy import and_


LANGUAGE_EXPLORER_DB_URL = 'postgresql://esteele@localhost/language_explorer'
JPHARVEST_DB_URL = 'postgresql://esteele@localhost/jpharvest'

logging.basicConfig(level=logging.DEBUG)

class LanguagePersister(object):
    ALIAS_TABLE = "language_alias"
    LANGUAGE_TABLE = "language"
    PRIMARY_NAME_TYPE = "p"
    ALTERNATE_NAME_TYPE = "a"
    DIALECT_TYPE = "d"

    def __init__(self):
        self.lang_db = dataset.connect(LANGUAGE_EXPLORER_DB_URL)

    def persist_language(self, iso, primary_name, source):
        """write iso to main table

        write primary source to language names table
        """
        # self.lang_db[self.LANGUAGE_TABLE].upsert(dict(
        #     iso=iso,
        # ))
        self.lang_db[self.ALIAS_TABLE].upsert(dict(
            iso=iso,
            alias_type=self.PRIMARY_NAME_TYPE,
            name=primary_name,
            source=source,
        ), ["iso", "alias_type", "source", "name"])

    def persist_dialect(self, iso, alternate_name, source):
        self._persist_alias(iso, self.DIALECT_TYPE, alternate_name, source)

    def persist_alternate(self, iso, alternate_name, source):
        self._persist_alias(iso, self.ALTERNATE_NAME_TYPE,
                            alternate_name, source)

    def _persist_alias(self, iso, alternate_type, alternate_name, source):
        self.lang_db[self.ALIAS_TABLE].upsert(dict(
            iso=iso,
            alias_type=alternate_type,
            name=alternate_name,
            source=source,
        ), ["iso", "alias_type", "source", "name"])

    def persist_language_status(self, iso, status):
        self.lang_db[self.LANGUAGE_TABLE].update(dict(
            iso=iso,
            status=status
        ), ['status'])


class AbstractLanguageSource(object):
    SOURCE_NAME = None

    def get_primary_name_for_iso(self, iso):
        raise NotImplementedError

    def get_alternate_names_for_iso(self, iso):
        raise NotImplementedError

    def persist_language(self, persister, iso):
        primary_name = self.get_primary_name_for_iso(iso)
        logging.info("Persisting language entry for ISO %s (%s)",
                    iso,
                    primary_name)
        persister.persist_language(iso, primary_name, source=self.SOURCE_NAME)

    def persist_alternate_names(self, persister, iso):
        alternate_names = self.get_alternate_names_for_iso(iso)
        if alternate_names:
            logging.info("Persisting alternate names for ISO %s (%s)",
                        iso,
                        ", ".join(alternate_names))
        for alternate_name in alternate_names:
            persister.persist_alternate(iso, alternate_name, self.SOURCE_NAME)


class JPHarvestAdapter(AbstractLanguageSource):
    SOURCE_NAME = "JP"

    def __init__(self):
        self.db = sqlsoup.SQLSoup(JPHARVEST_DB_URL)

    def get_language_iso_keys(self):
        """get a list of languages, with the most common key available in the db

        this might mean we can insert it straight into our db, but it might need
        some processing if the available keys need translation to be a key in
        our db
        """
        where = and_(self.db.tblLnkGEOtoLNG.ROG3 == "AS",
                     self.db.tblLnkGEOtoLNG.Indigenous == "Y")
        return [l.ROL3 for l in self.db.tblLnkGEOtoLNG.filter(where).all()]

    def get_primary_name_for_iso(self, iso):
        return self.db.tblLNG3Languages.get(iso).Language

    def get_alternate_names_for_iso(self, iso):
        return [l.LangAltName for l in
                self.db.tblLNG6LanguageAlternateNames.filter(
                    self.db.tblLNG6LanguageAlternateNames.ROL3 == iso).all()]


def main():
    p = LanguagePersister()
    jp_db = JPHarvestAdapter()
    for lang in jp_db.get_language_iso_keys():
        jp_db.persist_language(p, lang)
        jp_db.persist_alternate_names(p, lang)


if __name__ == '__main__':
    sys.exit(main())
