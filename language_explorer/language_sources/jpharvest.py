import sqlsoup

from language_explorer import constants
from language_explorer.language_sources.base import AbstractLanguageSource


__author__ = 'esteele'


class JPHarvestAdapter(AbstractLanguageSource):
    SOURCE_NAME = constants.JOSHUA_PROJECT_SOURCE_ABBREV

    def __init__(self, db_url):
        self.db = sqlsoup.SQLSoup(db_url)

    def get_language_iso_keys(self):
        """get a list of languages, with the most common key available in the db

        this might mean we can insert it straight into our db, but it might need
        some processing if the available keys need translation to be a key in
        our db


        SELECT DISTINCT("tblLNG3Languages"."ROL3"), "Language" FROM "tbllnkLNGtoPEOGEO", "tblPEO3PeopleGroups", "tblLNG3Languages" where
        "tblPEO3PeopleGroups"."PeopleID3" = "tbllnkLNGtoPEOGEO"."PeopleID3" AND
        "tbllnkLNGtoPEOGEO"."ROL3" = "tblLNG3Languages"."ROL3" AND
        "tblPEO3PeopleGroups"."PeopleID2" = '100' and
        "tbllnkLNGtoPEOGEO"."ROG3" = 'AS'
        ORDER by "ROL3"
        """
        # We need labels because both tables have PeopleID3 as the join key
        #  and sqlsoup needs labels to avoid ambiguity
        l_to_pg_labels = self.db.with_labels(self.db.tbllnkLNGtoPEOGEO)
        pg_labels = self.db.with_labels(self.db.tblPEO3PeopleGroups)
        j1 = self.db.join(self.db.tbllnkLNGtoPEOGEO, pg_labels,
                          self.db.tbllnkLNGtoPEOGEO.PeopleID3 ==
                          pg_labels.tblPEO3PeopleGroups_PeopleID3,
                          isouter=True)
        all_iso = set([row.ROL3 for row in j1.filter(
            j1.ROG3 == "AS",
            j1.tblPEO3PeopleGroups_PeopleID2 == 100).all()])\
            .difference(self.EXCLUDED_AU_LANGUAGES)
        return sorted(list(all_iso))

    def get_primary_name_for_iso(self, iso):
        return self.db.tblLNG3Languages.get(iso).Language

    def get_alternate_names_for_iso(self, iso):
        return [l.LangAltName for l in
                self.db.tblLNG6LanguageAlternateNames.filter(
                    self.db.tblLNG6LanguageAlternateNames.ROL3 == iso).all()]

    def get_dialects_for_iso(self, iso):
        """Language ISO also appears in tblLNG4Dialects. Not sure whether we
        want to duplicate it all (if indeed it is duplicated). Haven't
        investigated tblLNG7DialectAlternateNames
        """
        # For the momen
        return []

    def get_classification(self, iso):
        """Can't be implemented. JPHarvest doesn't provide classification"""
        return []

    def get_translation_info_for_iso(self, iso):
        """Has additional information on top of ethnologue and findabible
        e.g. mwp and rop have NT dates
        Extra data is likely from the world christian database, at least
        based on http://www.joshuaproject.net/data-sources.php

        Note that we only return the date associated with the largest body of
        work. If we have a NT, there's no need to report on portions.
        Some year values are ranges, some are single years and one (bdy)
        is "yes" !!!
        """
        d = {}
        STATE = constants.TRANSLATION_STATE_STATE_KEY
        YEAR = constants.TRANSLATION_STATE_YEAR_KEY
        # Combine into a single query
        bible_year = self.db.tblLNG3Languages.filter(
            self.db.tblLNG3Languages.ROL3 == iso).first().BibleYear
        if bible_year:
            d[STATE] = constants.TRANSLATION_STATE_WHOLE_BIBLE
            d[YEAR] = int(bible_year.rpartition("-")[2])
            return d
        nt_year = self.db.tblLNG3Languages.filter(
            self.db.tblLNG3Languages.ROL3 == iso).first().NTYear
        if nt_year:
            d[STATE] = constants.TRANSLATION_STATE_NEW_TESTAMENT
            d[YEAR] = int(nt_year.rpartition("-")[2])
            return d
        portions_year = self.db.tblLNG3Languages.filter(
            self.db.tblLNG3Languages.ROL3 == iso).first().PortionsYear
        if portions_year:
            d[STATE] = constants.TRANSLATION_STATE_PORTIONS
            if portions_year == "Yes":  # bdy
                d[YEAR] = constants.TRANSLATION_STATE_POSITIVE_YEAR
            else:
                d[YEAR] = int(portions_year.rpartition("-")[2])

            return d
        d[STATE] = constants.TRANSLATION_STATE_NO_SCRIPTURE
        d[YEAR] = constants.TRANSLATION_STATE_UNKNOWN_YEAR
        return d