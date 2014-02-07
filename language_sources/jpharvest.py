from sqlalchemy import and_
import sqlsoup
from language_sources.base import AbstractLanguageSource

__author__ = 'esteele'


class JPHarvestAdapter(AbstractLanguageSource):
    SOURCE_NAME = "JP"

    def __init__(self, db_url):
        self.db = sqlsoup.SQLSoup(db_url)

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