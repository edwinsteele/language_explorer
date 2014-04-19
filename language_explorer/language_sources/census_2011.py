from collections import defaultdict
import csv
import logging
from language_explorer import constants
from language_explorer.language_sources.base import AbstractLanguageSource

logging.basicConfig(level=logging.DEBUG)


class Census2011Adapter(AbstractLanguageSource):

    SOURCE_NAME = constants.AUS_CENSUS_2011_ABBREV
    # Don't include those with small cell counts - they're more affect
    #  by introduction of random error in the census
    # http://www.abs.gov.au/ausstats/abs@.nsf/Lookup/2901.0Chapter38202011
    SMALL_CELL_COUNT_THRESHOLD = 20
    # These names map to an ISO that has a dramatically larger population
    #  count. Given they're so small, and that the census introduces errors
    #  in small data sets to protect privacy, we ignore these Census languages
    #  in order to map a single Census language to a single ISO, which allows
    #  easier consumption of data associated with that Census language
    # Include nfd and nec
    LESSER_DUPLICATES = [
        'Central Anmatyerr',  # amx => 5 speakers
        'Eastern Anmatyerr',  # amx => 4 speakers
        'Antekerrepenh',  # adg, aer => 0 speakers
        'Anmatyerr, nfd',  # amx => 0 speakers (Anmatyerr, nfd)
        'Jawi',  # bcj => 0 speakers
        'Gambera',  # wub => 0 speakers
    ]

    # These Census categories are too broad for use, at least until we are
    #  able to, and comfortable with mapping Census stats for these categories
    #  to many ISOs. This mapping is easiest if the ISOs do not already have
    #  a census to ISO mapping.
    BROAD_CATEGORIES = [
        'Aboriginal English, so described',
        'Arnhem Land and Daly River Region Languages, nec',
        'Arnhem Land and Daly River Region Languages, nfd',
        'Cape York Peninsula Languages, nec',
        'Cape York Peninsula Languages, nfd',
        'Australian Indigenous Languages, nfd',
        'Kimberley Area Languages, nec',
        'Kimberley Area Languages, nfd',
        'Other Australian Indigenous Languages, nec',
        'Other Australian Indigenous Languages, nfd',
        'Torres Strait Island Languages, nfd',
        'Yolngu Matha, nfd',
    ]

    def __init__(self, lanp_source, persister):
        # Census adapter requires a database connection in order to resolve
        #  names as ISOs
        self.persister = persister
        self.csv_source = lanp_source
        self._lang_to_iso_cache = defaultdict(list)
        self._iso_to_lang_cache = defaultdict(list)
        self._lang_to_count_cache = {}

    def get_lang_to_iso_dict(self):
        """Returns a dictionary keyed on ABS Language name, with the value as
        a list of ISOs that correspond to the ABS language.
        """
        if not self._lang_to_iso_cache:
            self._populate_lang_iso_count_caches()
        return self._lang_to_iso_cache

    def get_lang_to_count_dict(self):
        if not self._lang_to_count_cache:
            self._populate_lang_iso_count_caches()
        return self._lang_to_count_cache

    def get_iso_to_lang_dict(self):
        if not self._iso_to_lang_cache:
            self._populate_lang_iso_count_caches()
        return self._iso_to_lang_cache

    def lanp_data_lines(self):
        reader = csv.reader(open(self.csv_source, 'r'), delimiter=",")
        for line_fields in reader:
            # data lines have four fields
            if len(line_fields) != 11:
                continue
            # All data lines start with , i.e. empty first field
            if line_fields[0] != '':
                continue

            # Total and header lines look like data, but isn't
            if line_fields[1] in ("Total", "ENGLP"):
                continue

            yield line_fields[1], line_fields[-2]

    def _populate_lang_iso_count_caches(self):
        for full_name, count in self.lanp_data_lines():
            if full_name in self.LESSER_DUPLICATES or \
               full_name in self.BROAD_CATEGORIES:
                # Ignore these, so we can best map an ABS name to
                #  a single ISO
                continue

            # split out "nfd", "nec" for further analysis
            name = full_name.split(",")[0]
            self._lang_to_count_cache[name] = count
            self._lang_to_count_cache[full_name] = count
            isos = self.persister.get_iso_list_from_name(name)
            # If we can't match the part name, try the full name
            if len(isos) == 0:
                isos = self.persister.get_iso_list_from_name(full_name)

            # Only count reasonably sized languages (to avoid placing
            #  too much value on error prone small cells
            if int(count) > self.SMALL_CELL_COUNT_THRESHOLD:
                self._lang_to_iso_cache[name] = isos
                self._lang_to_iso_cache[full_name] = isos
                for iso in isos:
                    self._iso_to_lang_cache[iso].append(full_name)

    def print_stuff(self):
        def n(name):
            return "%s (%s)" % (name,
                                self.get_lang_to_count_dict().get(name, "?"))

        no_match_langs = []
        one_match_langs = []
        multi_match_langs = []
        for lang, isos in self.get_lang_to_iso_dict().iteritems():
            if len(isos) == 0:
                no_match_langs.append(lang)
            elif len(isos) == 1:
                one_match_langs.append(lang)
            else:
                multi_match_langs.append(lang)
        print "---------------------"
        print "No Match Langs (%s): %s" % \
              (len(no_match_langs), [n(name) for name in no_match_langs])
        print "---"
        print "One Match Langs (%s): %s" % \
              (len(one_match_langs), [n(name) for name in one_match_langs])
        print "---"
        print "Multi Match Langs (%s): %s" % \
              (len(multi_match_langs), [n(name) for name in multi_match_langs])
        print "---"

        import pprint
        pprint.pprint(self.get_iso_to_lang_dict())
        for k, v in self.get_iso_to_lang_dict().items():
            if len(v) > 1:
                print "Iso: %s matched %s languages %s" % \
                      (k, len(v), [n(name) for name in v])

    def get_L1_speaker_count_for_iso(self, iso):
        """Get the population count associated with the iso

        This is only possible from the census data if:
        - the iso does not share the population associated with a language
          with any other iso (it is not possible to work out how much is
          associated with each iso). i.e.

        If the iso only maps to one language, and only one language
        maps to the iso
        """
        langs = self.get_iso_to_lang_dict()[iso]
        c = 0
        if langs:
            for lang in langs:
                if len(self.get_lang_to_iso_dict()[lang]) > 1:
                    # Then the language count is shared among several isos
                    #  and so we can't use it.
                    return constants.SPEAKER_COUNT_AMBIGUOUS
                else:
                    c += int(self.get_lang_to_count_dict()[lang])
        else:
            c = constants.SPEAKER_COUNT_UNKNOWN

        return c
