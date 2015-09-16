import re
import itertools

import wals3.models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from language_explorer import constants
from language_explorer.language_sources.base import AbstractLanguageSource


__author__ = 'esteele'


class WalsAdapter(AbstractLanguageSource):
    SOURCE_NAME = constants.WALS_SOURCE_ABBREV

    def __init__(self, db_url):
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def get_language_iso_keys(self):
        """WALS3 can make a single WALS language to more than iso code and
        one iso code to more than one WALS language
        e.g. WALS language  Arrernte maps to iso aer & are
        e.g. iso aer maps to WALS Arrernte & Arrernte (Mparntwe)

        What do we do when there's no ISO key? (there are some!). Create a
         fake one, perhaps of the form wals_xxx where xxx is the wals id
        """
        # Australia is country_pk == 8
        all_iso_code_fields = [
            l.iso_codes for l in
            self.session.query(wals3.models.Language)
            .filter(wals3.models.CountryLanguage.language_pk ==
                    wals3.models.Language.pk)
            .filter(wals3.models.CountryLanguage.country_pk == 8)
            .all()]
        # we still have entries like 'aer, are' that we need to split and strip
        all_iso_codes_with_nested_lists = [re.split(",\s", x)
                                           for x in all_iso_code_fields]
        # flatten and remove empty codes, and remove duplicates, and remove
        #  those that we want to explicitly exclude
        return sorted(list(set(filter(
            None, itertools.chain(*all_iso_codes_with_nested_lists)))
            .difference(self.EXCLUDED_AU_LANGUAGES)))

    def get_primary_name_for_iso(self, iso):
        # We use like %iso% because we want to include those that have several
        #  iso_codes, but we make sure we get the best match by returning the
        #  one with the shortest iso_codes field i.e. the most specific one.
        return self.session.query(wals3.models.WalsLanguage) \
            .filter(wals3.models.WalsLanguage.pk ==
                    wals3.models.Language.pk) \
            .filter(wals3.models.WalsLanguage.iso_codes.
                    like('%%%s%%' % (iso,))).order_by("length(iso_codes)")\
            .first().name

    def get_alternate_names_for_iso(self, iso):
        # WALS includes alternative names from other sources. We will treat
        #  them as WALS alternatives, even though they're aggregating
        lang = self.session.query(wals3.models.WalsLanguage) \
            .filter(wals3.models.WalsLanguage.pk ==
                    wals3.models.Language.pk) \
            .filter(wals3.models.WalsLanguage.iso_codes.
                    like('%%%s%%' % (iso,))).order_by("length(iso_codes)") \
            .first()
        # We already have Ethnologue, so exclude them. They also split on commas
        #  which means we'd need extra logic to extract the names from what is
        #  normally a comma separated string
        alt_name_strings = [
            i.name for i in lang.identifiers if i.type == 'name' and
            i.description.capitalize() != "ethnologue".capitalize()]
        # We have several alternate sources, and they are dupes sometimes
        return list(set([s2.strip() for s2 in itertools.chain(
            *[s.split(",") for s in alt_name_strings])]))

    def get_wals_keys_for_iso(self, iso):
        return [l.id for l in
                self.session.query(wals3.models.WalsLanguage)
                .filter(wals3.models.WalsLanguage.pk ==
                        wals3.models.Language.pk)
                .filter(wals3.models.WalsLanguage.iso_codes
                .like('%%%s%%' % (iso,))).all()]

    def get_classification(self, iso):
        """Not worth implementing this, as there are only Family and Genus
        e.g. Australian, Pama-Nyungan
        Which is insufficient to give any value
        """
        return []

    def get_translation_info_for_iso(self, iso):
        """Not available in WALS"""
        return {}
