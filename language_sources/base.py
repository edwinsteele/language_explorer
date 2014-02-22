import codecs
import logging
import os
import requests

__author__ = 'esteele'


class AbstractLanguageSource(object):
    SOURCE_NAME = None

    def get_primary_name_for_iso(self, iso):
        raise NotImplementedError

    def get_alternate_names_for_iso(self, iso):
        raise NotImplementedError

    def get_dialects_for_iso(self, iso):
        raise NotImplementedError

    def get_translation_info_for_iso(self, iso):
        raise NotImplementedError

    def get_classification(self, iso):
        """
        Returns a list of classifications, from Family, Genus, Subgenus etc
        """
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

    def persist_classification(self, persister, iso):
        classification_list = self.get_classification(iso)
        if classification_list:
            logging.info("Persisting classification for ISO %s (%s)",
                         iso,
                         ", ".join(classification_list))
        persister.persist_classification(iso, classification_list,
                                         self.SOURCE_NAME)

    def persist_translation(self, persister, iso):
        translation_dict = self.get_translation_info_for_iso(iso)
        if translation_dict:
            persister.persist_translation(iso, translation_dict,
                                          self.SOURCE_NAME)


class CachingWebLanguageSource(AbstractLanguageSource):
    def __init__(self, cache_root):
        self.cache_root = cache_root
        # TODO: make sure it exists

    def generate_filename_from_url(self, url):
        # Convert slashes to hashes
        #  and periods to underscores
        #  and colons to tildes
        return url.replace("/", "#") \
                  .replace(".", "_") \
                  .replace(":", "~")

    def get_text_from_url(self, url):
        cached_location = os.path.join(self.cache_root,
                                       self.generate_filename_from_url(url))
        if not os.path.exists(cached_location):
            print "retrieving url from the web: %s" % (url,)
            r = requests.get(url)
            with open(cached_location, "wb") as f:
                f.write(r.content)
        # Yeah, we're writing then reading if we don't have a cached copy
        #  but it simplifies the unicode handling
        with codecs.open(cached_location, "r", encoding="utf-8") as f:
            text = f.read()
        return text
