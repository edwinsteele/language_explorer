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
        self._lang_to_pse_cache = {}

    def get_lang_to_iso_dict(self):
        """Returns a dictionary keyed on ABS Language name, with the value as
        a list of ISOs that correspond to the ABS language.
        """
        if not self._lang_to_iso_cache:
            self._populate_lang_iso_data_caches()
        return self._lang_to_iso_cache

    def get_lang_to_count_dict(self):
        if not self._lang_to_count_cache:
            self._populate_lang_iso_data_caches()
        return self._lang_to_count_cache

    def get_iso_to_lang_dict(self):
        if not self._iso_to_lang_cache:
            self._populate_lang_iso_data_caches()
        return self._iso_to_lang_cache

    def get_lang_to_pse_dict(self):
        if not self._lang_to_pse_cache:
            self._populate_lang_iso_data_caches()
        return self._lang_to_pse_cache

    def lanp_data_lines(self):
        """
        Fields:
        - dummy
        - ENGLP
        - Speaks English only
        - Speaks other language and speaks English: Very well
        - Speaks other language and speaks English: Well
        - Speaks other language and speaks English: Not well
        - Speaks other language and speaks English: Not at all
        - Not stated - both language (LANP) and proficiency (ENGP) not stated
        - Not stated - language (LANP) stated, proficiency (ENGP) not stated
        - Total
        - dummy
        """
        reader = csv.reader(open(self.csv_source, 'r'), delimiter=",")
        for line_fields in reader:
            # data lines have eleven fields
            if len(line_fields) != 11:
                continue
            # All data lines start with , i.e. empty first field
            if line_fields[0] != '':
                continue

            # Total and header lines look like data, but isn't
            if line_fields[1] in ("Total", "ENGLP"):
                continue

            yield line_fields[1],\
                line_fields[3],\
                line_fields[4],\
                line_fields[5],\
                line_fields[6],\
                line_fields[7] + line_fields[8],\
                line_fields[9]

    def _populate_lang_iso_data_caches(self):
        """
        See explanation of fields in get_english_competency_percentiles
        """
        # pse = proficiency in spoken english. See fields in lanp_data_lines
        for full_name, pse_vw, pse_w, pse_nw, pse_naa, pse_ns, count in \
                self.lanp_data_lines():
            if full_name in self.LESSER_DUPLICATES or \
               full_name in self.BROAD_CATEGORIES:
                # Ignore these, so we can best map an ABS name to
                #  a single ISO
                continue

            # split out "nfd", "nec" for further analysis, but use both as
            # keys in the caches, so we can get best matching
            name = full_name.split(",")[0]
            self._lang_to_count_cache[name] = int(count)
            self._lang_to_count_cache[full_name] = int(count)
            isos = self.persister.get_iso_list_from_name(name)
            # If we can't match the part name, try the full name
            if len(isos) == 0:
                isos = self.persister.get_iso_list_from_name(full_name)

            # Only count reasonably sized languages (to avoid placing
            #  too much value on error prone small cells
            if int(count) > self.SMALL_CELL_COUNT_THRESHOLD:
                pse_values = (int(pse_vw),
                              int(pse_w),
                              int(pse_nw),
                              int(pse_naa),
                              int(pse_ns))
                self._lang_to_iso_cache[name] = isos
                self._lang_to_iso_cache[full_name] = isos
                self._lang_to_pse_cache[name] = pse_values
                self._lang_to_pse_cache[full_name] = pse_values
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
                    c += self.get_lang_to_count_dict()[lang]
        else:
            c = constants.SPEAKER_COUNT_UNKNOWN

        return c

    def get_english_competency_percentages(self, iso):
        """Returns percentages in proficiency in spoken english

        Gives percentages of those who actually stated their proficiency in
        english i.e. 100% is the total - not-stated. While this assumes the
        distribution of those who did not state their proficiency is similar
        to those that did, it makes it much easier to process

        We return two metrics:
        "Could study English bible (pessimistic)"
        = % Very Well (assumes one who only speaks english well could not
                       study an english bible)
        "Could study English bible (optimistic)"
        = % Very Well + % Well (assumes one who speaks english well could
                                study an english bible)

        By returning percentages we can obtain numbers, albeit with coarser
        granularity, for census language groups that map to more than one iso

        And all of this is for spoken english, so we're assuming that there are
        spoken english resources that they could use, or that spoken english
        indicates a similar level of reading ability
        """
        langs = self.get_iso_to_lang_dict()[iso]
        lang_to_count_dict = self.get_lang_to_count_dict()
        lang_to_pse_dict = self.get_lang_to_pse_dict()
        total_stated_count = 0
        total_optimistic_count = 0
        total_pessimistic_count = 0
        if langs:
            # sum data for all langs that apply
            for lang in langs:
                total_stated_count += \
                    lang_to_count_dict[lang] - lang_to_pse_dict[lang][4]
                total_optimistic_count += \
                    lang_to_pse_dict[lang][0] + lang_to_pse_dict[lang][1]
                total_pessimistic_count += lang_to_pse_dict[lang][0]
            if total_stated_count == 0:
                # Don't divide by zero :-)
                return constants.ENGLISH_COMPETENCY_UNKNOWN_PESSIMISTIC, \
                    constants.ENGLISH_COMPETENCY_UNKNOWN_OPTIMISTIC
            else:
                return (
                    int(round(100.0 * total_pessimistic_count /
                              total_stated_count)),
                    int(round(100.0 * total_optimistic_count /
                              total_stated_count)),
                )
        else:
            return constants.ENGLISH_COMPETENCY_UNKNOWN_PESSIMISTIC, \
                constants.ENGLISH_COMPETENCY_UNKNOWN_OPTIMISTIC

    def persist_english_competency(self, persister, iso):
        ecp, eco = self.get_english_competency_percentages(iso)
        logging.info("Persisting english language competency for ISO %s: "
                     "pess = %s, opt = %s", iso, ecp, eco)
        persister.persist_english_competency(iso, ecp, eco)