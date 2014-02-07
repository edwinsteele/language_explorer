import dataset

__author__ = 'esteele'


class LanguagePersister(object):
    ALIAS_TABLE = "language_alias"
    LANGUAGE_TABLE = "language"
    PRIMARY_NAME_TYPE = "p"
    ALTERNATE_NAME_TYPE = "a"
    DIALECT_TYPE = "d"

    def __init__(self, db_url):
        self.lang_db = dataset.connect(db_url)

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