import constants
import collections
import dataset

__author__ = 'esteele'


class LanguagePersistence(object):
    ALIAS_TABLE = "language_alias"
    LANGUAGE_TABLE = "language"
    CLASSIFICATION_TABLE = "classification"
    TRANSLATION_TABLE = "translation"
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

    def persist_classification(self, iso, c_list, source):
        for c_idx, c_name in enumerate(c_list):
            self.lang_db[self.CLASSIFICATION_TABLE].upsert(dict(
                iso=iso,
                source=source,
                level=c_idx,
                name=c_name,
            ), ["iso", "source", "level"])

    def persist_translation(self, iso, tr_dict, source):
        self.lang_db[self.TRANSLATION_TABLE].upsert(dict(
            iso=iso,
            source=source,
            status=tr_dict[constants.TRANSLATION_STATE_STATE_KEY],
            year=tr_dict[constants.TRANSLATION_STATE_YEAR_KEY],
        ), ["iso", "source"])

    def get_all_iso_codes(self):
        return sorted(list(set(
            [row["iso"] for row in
             self.lang_db[self.ALIAS_TABLE].distinct("iso")])))

    def get_primary_names_by_iso(self, iso):
        """Return list of primary names from each data source"""
        primary_list = self.lang_db[self.ALIAS_TABLE]\
            .find(iso=iso, alias_type=self.PRIMARY_NAME_TYPE)
        d = collections.defaultdict(list)
        for primary_row in primary_list:
            d[primary_row["source"]].append(primary_row["name"])
        return d

    def get_alternate_names_by_iso(self, iso):
        """Return list of alternate names from each data source"""
        alternate_list = self.lang_db[self.ALIAS_TABLE] \
            .find(iso=iso, alias_type=self.ALTERNATE_NAME_TYPE)
        d = collections.defaultdict(list)
        for primary_row in alternate_list:
            d[primary_row["source"]].append(primary_row["name"])
            d[primary_row["source"]].sort()
        return d

    def get_classifications_by_iso(self, iso):
        classification_list = self.lang_db[self.CLASSIFICATION_TABLE] \
            .find(iso=iso, order_by=["iso", "level"])
        d = collections.defaultdict(list)
        for c_row in classification_list:
            d[c_row["source"]].append(c_row["name"])
        return d
