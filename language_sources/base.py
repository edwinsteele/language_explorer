import logging

__author__ = 'esteele'


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