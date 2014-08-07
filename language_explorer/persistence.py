import itertools
import collections
import dataset
import logging
from language_explorer import constants

__author__ = 'esteele'

logging.basicConfig(level=logging.DEBUG)


class LanguagePersistence(object):
    ALIAS_TABLE = "language_alias"
    LANGUAGE_TABLE = "language"
    CLASSIFICATION_TABLE = "classification"
    TRANSLATION_TABLE = "translation"
    RELATIONSHIP_TABLE = "relationship"
    PRIMARY_NAME_TYPE = "p"
    ALTERNATE_NAME_TYPE = "a"
    DIALECT_TYPE = "d"
    REVERSIBLE_RELATIONSHIPS = [
        constants.RELTYPE_SIMILAR_TO,
        constants.RELTYPE_SIMILAR_TO,
        constants.RELTYPE_LIMITED_MUTUAL_INTELLIGIBILITY,
        constants.RELTYPE_RETIREMENT_SPLIT_INTO,
        constants.RELTYPE_RETIREMENT_MERGED_INTO]

    def __init__(self, db_url):
        self.lang_db = dataset.connect(db_url)
        self.translation_state_cache = {}
        self.l1_speaker_count_cache = {}
        self.ethnologue_primary_name_cache = {}
        self.retirement_state_cache = {}

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
        self.lang_db[self.LANGUAGE_TABLE].upsert(
            {"iso": iso,
             "L1_speaker_count_%s" % (source,): c,
             },
            ["iso"]
        )

    def persist_writing_state(self, iso, state):
        """Persist state of writing. Only ethnologue at this stage
        (hence no source)
        """
        self.lang_db[self.LANGUAGE_TABLE].upsert(
            {"iso": iso,
             "writing_state": state,
             },
            ["iso"]
        )

    def persist_english_competency(self, iso, pessimistic, optimistic):
        self.lang_db[self.LANGUAGE_TABLE].upsert(
            {"iso": iso,
             "english_competency_pess": pessimistic,
             "english_competency_optim": optimistic,
             },
            ["iso"]
        )

    def get_all_iso_codes(self):
        return sorted(list(set(
            [row["iso"] for row in
             self.lang_db[self.ALIAS_TABLE].distinct("iso")])))

    def get_primary_names_by_iso(self, iso):
        """Return list of primary names from each data source"""
        primary_list = self.lang_db[self.ALIAS_TABLE] \
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

    def get_writing_state_by_iso(self, iso):
        iso_row = self.lang_db[self.LANGUAGE_TABLE].find_one(iso=iso)
        if iso_row:
            return iso_row["writing_state"]
        else:
            return constants.WRITING_STATE_NOT_RECORDED

    def get_english_competency_by_iso(self, iso):
        iso_row = self.lang_db[self.LANGUAGE_TABLE].find_one(iso=iso)
        if iso_row:
            return iso_row["english_competency_pess"], \
                iso_row["english_competency_optim"]
        else:
            # Perhaps unknown, with a formatting method in the template?
            return "N/A", "N/A"

    def get_primary_name_for_display(self, iso):
        """Only for display. Use Ethnologue, or nothing

        duplicates a bit of logic from get_primary_names_by_iso but this
        code is here for a significant optimisation on rendering"""
        if not self.ethnologue_primary_name_cache:
            all_rows = self.lang_db[self.ALIAS_TABLE] \
                .find(alias_type=self.PRIMARY_NAME_TYPE,
                      source=constants.ETHNOLOGUE_SOURCE_ABBREV)
            for row in all_rows:
                self.ethnologue_primary_name_cache[row["iso"]] = row["name"]

        return self.ethnologue_primary_name_cache.get(iso,
                                                      "Not in Ethnologue")

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
        if source not in self.l1_speaker_count_cache:
            self.l1_speaker_count_cache[source] = {}
            all_rows = self.lang_db[self.LANGUAGE_TABLE].all()
            for row in all_rows:
                if row['L1_speaker_count_%s' % (source,)] is None:
                    c = constants.SPEAKER_COUNT_UNKNOWN
                else:
                    c = int(row['L1_speaker_count_%s' % (source,)])
                self.l1_speaker_count_cache[source][row["iso"]] = c

        return self.l1_speaker_count_cache[source].get(
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

    def get_reversible_relationships(self):
        """Relationships expressed in terms of a -> b that also infer b -> a
        only interested in relationships from primary source i.e. those that
        have two character sources
        """
        r = self.lang_db[self.RELATIONSHIP_TABLE].find(
            rel_verb=self.REVERSIBLE_RELATIONSHIPS,
            source=filter(lambda x: len(x) == 2,
                          constants.source_abbrev_name_dict.keys())
        )
        return r

    def reverse_relationship(self, subject_iso, rel_type, source, object_iso):
        """
        New source is old source name + I (i.e. implied from original source).
        """
        if rel_type in [constants.RELTYPE_RELATED_TO,
                        constants.RELTYPE_SIMILAR_TO,
                        constants.RELTYPE_LIMITED_MUTUAL_INTELLIGIBILITY]:
            return [object_iso, rel_type, source + "I", subject_iso]
        elif rel_type == constants.RELTYPE_RETIREMENT_MERGED_INTO:
            return [object_iso,
                    constants.RELTYPE_RETIREMENT_MERGED_FROM,
                    source + "I",
                    subject_iso]
        elif rel_type == constants.RELTYPE_RETIREMENT_SPLIT_INTO:
            return [object_iso,
                    constants.RELTYPE_RETIREMENT_SPLIT_FROM,
                    source + "I",
                    subject_iso]
        else:
            logging.warning("Unable to reverse relationships of type %s",
                            rel_type)
            return []

    def insert_reverse_relationships(self):
        for row in self.get_reversible_relationships():
            rev_subject_iso, rel_verb, implied_source, rev_object_iso = \
                self.reverse_relationship(row["subject_iso"],
                                          row["rel_verb"],
                                          row["source"],
                                          row["object_iso"])
            # Check whether the forward relationship already
            #  exists, i.e. rev_object_iso rev_verb's rev_subject_iso
            # This means we won't duplicate forward and reverse rels
            if self.lang_db[self.RELATIONSHIP_TABLE].find_one(
                    source=implied_source[:-1],
                    subject_iso=rev_object_iso,
                    rel_verb=rel_verb,
                    object_iso=rev_subject_iso):
                logging.info("Not persisting rev rel: subj = %s verb = %s"
                             " source = %s obj = %s because forward rel"
                             " already exists", rev_subject_iso, rel_verb,
                             implied_source, rev_object_iso)
            else:
                logging.info("Persisting rev rel: subj = %s verb = %s"
                             " source = %s obj = %s", rev_subject_iso, rel_verb,
                             implied_source, rev_object_iso)
                self.persist_relationship(rev_subject_iso,
                                          [(rel_verb, rev_object_iso)],
                                          implied_source)

    def could_have_L1_speakers(self, iso):
        """True if a language either has L1 speakers, or the number of L1
        speakers is unknown
        """
        c = self.get_L1_speaker_count_by_iso(
            iso, constants.ETHNOLOGUE_SOURCE_ABBREV)
        return c > 0 or c == constants.SPEAKER_COUNT_UNKNOWN

    def iso_is_retired(self, iso):
        if not self.retirement_state_cache:
            # dataset.Table.distinct can't handle filters with lists
            #  i.e. "in" even though dataset.Table.filter can
            sql = """
            select distinct "subject_iso" from "%s" where
            "rel_verb" in %s
            """ % (self.RELATIONSHIP_TABLE, tuple([
                constants.RELTYPE_RETIREMENT_CHANGE,
                constants.RELTYPE_RETIREMENT_DUPLICATE,
                constants.RELTYPE_RETIREMENT_NON_EXISTENT,
                constants.RELTYPE_RETIREMENT_SPLIT_INTO,
                constants.RELTYPE_RETIREMENT_MERGED_INTO])
            )
            all_retirements = self.lang_db.query(sql)
            for row in all_retirements:
                self.retirement_state_cache[row['subject_iso']] = True

        return self.retirement_state_cache.get(iso, False)

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
        if self.iso_is_retired(iso):
            retirement_css_class = constants.ISO_RETIRED_CSS_STATE
        else:
            retirement_css_class = constants.ISO_ACTIVE_CSS_STATE
        return '<span class="%s %s %s">%s</span>' % \
               (scripture_css_class,
                l1_speaker_css_class,
                retirement_css_class,
                iso)

    def format_speaker_count(self, count):
        if int(count) == constants.SPEAKER_COUNT_UNKNOWN:
            return "Unknown"
        elif int(count) == constants.SPEAKER_COUNT_NONE_EXPECTED:
            return "None (likely extinct)"
        elif int(count) == constants.SPEAKER_COUNT_AMBIGUOUS:
            return "N/A (ambiguity)"
        else:
            return count

    def format_ebu_percentage(self, perc):
        """English bible users"""
        if int(perc) in (constants.ENGLISH_COMPETENCY_UNKNOWN_OPTIMISTIC,
                         constants.ENGLISH_COMPETENCY_UNKNOWN_PESSIMISTIC):
            return "N/A"
        else:
            return "%s%%" % (perc,)

    def get_table_data(self):
        table_data = []
        all_isos = self.get_all_iso_codes()
        for iso in all_isos:
            # Only interested in relationships where the other lang has a
            #  translation
            relations = [[src, rel_type, obj_iso] for
                         src, rel_type, obj_iso in
                         self.get_relationships_by_iso(iso)
                         if self.get_best_translation_state(obj_iso) > 1]
            ecp, eco = self.get_english_competency_by_iso(iso)
            iso_data = (iso,
                        self.get_L1_speaker_count_by_iso(
                            iso, constants.ETHNOLOGUE_SOURCE_ABBREV),
                        self.get_L1_speaker_count_by_iso(
                            iso, constants.AUS_CENSUS_2011_ABBREV),
                        self.get_best_translation_state(iso),
                        self.get_writing_state_by_iso(iso),
                        ecp,
                        eco,
                        relations
                        )
            table_data.append(iso_data)
        return table_data
