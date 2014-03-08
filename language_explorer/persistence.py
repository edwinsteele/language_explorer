import itertools
import collections
import dataset
from language_explorer import constants

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

    def get_translations_by_iso(self, iso):
        translation_list = self.lang_db[self.TRANSLATION_TABLE].find(iso=iso)
        d = collections.defaultdict(list)
        for t_row in translation_list:
            d[t_row["source"]].append((t_row["status"], t_row["year"]))
        return d

    def _isos_with_shared_aliases(self, iso_name_list):
        """Yields a tuple of isos that share an alias

        :param iso_name_list: a list of (iso, name) tuples sorted by name
        :type iso_name_list: list
        :return: A list of iso codes that share an alias
        :rtype: list
        """
        for _, grouper in itertools.groupby(iso_name_list, lambda x: x[1]):
            yield [iso for iso, lang_name in grouper]

    def get_common_names_for_iso_list(self, iso_list):
        common_names = set()
        for iso in iso_list:
            name_list = [row["name"] for row in
                         self.lang_db[self.ALIAS_TABLE].find(iso=iso)]
            if not common_names:
                # First iso
                common_names.update(name_list)
            else:
                common_names.intersection_update(name_list)
        return list(common_names)

    def get_same_name_different_iso_list(self):
        # Return a list of tuples of iso-codes that share an alias
        sql = """
        select "iso", "name" from "language_alias" where
        "name" in (select "name" from
        (
        select "name", count(*) as iso_with_this_alias_c FROM
        (
        SELECT "name", "iso"
        FROM "language_alias"
        group by "name", "iso"
        ) as "t1"
        group by "name"
        ) as "t2"
        where "iso_with_this_alias_c" > 1
        )
        group by "iso", "name"
        ORDER by "name"
        """
        iso_group_set = set()
        for unsorted_group_list in self._isos_with_shared_aliases(
                [(row["iso"], row["name"]) for row in self.lang_db.query(sql)]):
            iso_group_set.add(tuple(sorted(unsorted_group_list)))
        return list(iso_group_set)

    def get_iso_list_from_name(self, name):
        # exact match on name only
        return sorted(list(set([row["iso"] for row in
                      self.lang_db[self.ALIAS_TABLE].find(name=name)])))

    def format_iso(self, iso):
        # html element
        # probably should live elsewhere... fix later
        sql = """
        SELECT max("status") ms from "%s" where iso = '%s'
         """ % (self.TRANSLATION_TABLE, iso)
        res = self.lang_db.query(sql)
        scripture_css_class = constants.translation_abbrev_css_class_dict[
            int(list(res)[0].get('ms', constants.TRANSLATION_STATE_NO_RECORD))]
        return '<span class="%s">%s</span>' % (scripture_css_class, iso)
