import itertools
import collections
import dataset
# import logging
from language_explorer import constants

__author__ = 'esteele'


class LanguagePersistence(object):
    ALIAS_TABLE = "language_alias"
    LANGUAGE_TABLE = "language"
    CLASSIFICATION_TABLE = "classification"
    TRANSLATION_TABLE = "translation"
    RELATIONSHIP_TABLE = "relationship"
    PRIMARY_NAME_TYPE = "p"
    ALTERNATE_NAME_TYPE = "a"
    DIALECT_TYPE = "d"

    def __init__(self, db_url):
        self.lang_db = dataset.connect(db_url)
        self.translation_state_cache = {}
        self.l1_speaker_count_cache = {}

    def persist_language(self, iso, primary_name, source):
        """write iso to main table

        write primary source to language names table
        """
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

    def persist_relationship(self, iso, relationships, source):
        for rel_type, other_iso in relationships:
            self.lang_db[self.RELATIONSHIP_TABLE].upsert(dict(
                subject_iso=iso,
                source=source,
                rel_verb=rel_type,
                object_iso=other_iso,
            ), ["subject_iso", "source", "rel_verb", "object_iso"])

    def persist_translation(self, iso, tr_dict, source):
        self.lang_db[self.TRANSLATION_TABLE].upsert(dict(
            iso=iso,
            source=source,
            status=tr_dict[constants.TRANSLATION_STATE_STATE_KEY],
            year=tr_dict[constants.TRANSLATION_STATE_YEAR_KEY],
        ), ["iso", "source"])

    def persist_L1_speaker_count(self, iso, c, source):
        """Persists L1 speaker count

        :param iso: language ISO
        :type iso: string
        :param c: L1 speaker count
        :type c: int
        """
        self.lang_db[self.LANGUAGE_TABLE].upsert({
            "iso": iso,
            "L1_speaker_count_%s" % (source,): c,
        }, ["iso"]
        )

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

    def get_dialect_names_by_iso(self, iso):
        """Return list of dialect names from each data source"""
        dialect_list = self.lang_db[self.ALIAS_TABLE] \
            .find(iso=iso, alias_type=self.DIALECT_TYPE)
        d = collections.defaultdict(list)
        for primary_row in dialect_list:
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

    def get_relationships_by_iso(self, iso):
        return sorted(
            [(r_row["source"], r_row["rel_verb"], r_row["object_iso"])
             for r_row in
             self.lang_db[self.RELATIONSHIP_TABLE].find(subject_iso=iso)])

    def get_primary_name_for_display(self, iso):
        """Only for display. Use Ethnologue, or nothing"""
        eth_primary_list = self.get_primary_names_by_iso(iso)[
            constants.ETHNOLOGUE_SOURCE_ABBREV]
        if eth_primary_list:
            return eth_primary_list[0]
        else:
            return "Not in Ethnologue"

    def _isos_with_shared_aliases(self, iso_name_list):
        """Yields a tuple of isos that share an alias

        :param iso_name_list: a list of (iso, name) tuples sorted by name
        :type iso_name_list: list
        :return: A list of iso codes that share an alias
        :rtype: list
        """
        for _, grouper in itertools.groupby(iso_name_list, lambda x: x[1]):
            yield [iso for iso, lang_name in grouper]

    def get_L1_speaker_count_by_iso(self, iso, source):
        # FIXME Breaks if we have speaker counts for multiple sources
        if not self.l1_speaker_count_cache:
            all_rows = self.lang_db[self.LANGUAGE_TABLE].all()
            for row in all_rows:
                self.l1_speaker_count_cache[row["iso"]] = \
                    int(row['L1_speaker_count_%s' % (source,)])

        return self.l1_speaker_count_cache.get(
            iso, constants.SPEAKER_COUNT_UNKNOWN)

    def get_common_names_for_iso_list(self, iso_list):
        """Finds common language names for a list of languages"""
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
        """Finds language groups that share a common name or alias"""
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
        return [row["iso"] for row in
                self.lang_db[self.ALIAS_TABLE].
                distinct("iso", name=name)]

    def get_iso_list_from_iso(self, iso):
        # probably redundant, but just in case we want to search on partial iso
        # partial match is ok
        return [row["iso"] for row in
                self.lang_db[self.ALIAS_TABLE].
                distinct("iso", iso=iso)]

    def get_best_translation_state(self, iso):
        """
        return: best translation state associated with the iso in all sources
        :rtype: int
        """
        # If we have any cached state, assume it's complete. Populate if not
        if not self.translation_state_cache:
            sql = """
            SELECT "iso", max("status") ms from "%s"
            GROUP BY "iso"
             """ % (self.TRANSLATION_TABLE,)
            for row in self.lang_db.query(sql):
                self.translation_state_cache[row['iso']] = int(row['ms'])

        return self.translation_state_cache.get(
            iso, constants.TRANSLATION_STATE_NO_RECORD)

    def could_have_L1_speakers(self, iso):
        """True if a language either has L1 speakers, or the number of L1
        speakers is unknown
        """
        c = self.get_L1_speaker_count_by_iso(
            iso, constants.ETHNOLOGUE_SOURCE_ABBREV)
        return c > 0 or c == constants.SPEAKER_COUNT_UNKNOWN

    def format_iso(self, iso):
        # html element
        # probably should live elsewhere... fix later
        scripture_css_class = constants.translation_abbrev_css_class_dict[
            self.get_best_translation_state(iso)]
        # Only use Ethnologue ATM. Expand to add others at some stage,
        #  with preference stated
        l1_speaker_count = self.get_L1_speaker_count_by_iso(
            iso, constants.ETHNOLOGUE_SOURCE_ABBREV)
        l1_speaker_css_class = constants.l1_speaker_css_class_dict[
            l1_speaker_count]
        return '<span class="%s %s">%s</span>' %\
               (scripture_css_class, l1_speaker_css_class, iso)

    def get_table_data(self):
        table_data = []
        all_isos = self.get_all_iso_codes()
        for iso in all_isos:
            relations = self.get_relationships_by_iso(iso)
            iso_data = (iso,
                        self.get_L1_speaker_count_by_iso(
                            iso, constants.ETHNOLOGUE_SOURCE_ABBREV),
                        self.get_best_translation_state(iso),
                        relations
            )
            table_data.append(iso_data)
        return table_data

