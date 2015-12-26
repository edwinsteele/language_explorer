# -*- coding utf-8 -*-

import collections
import itertools
import re
import logging
# from language_explorer import constants

__author__ = 'esteele'

logging.basicConfig(level=logging.INFO)


class NamingHelper(object):
    mappings = [
        # (unichr(8217), unichr(39)),  # e.g. the stop in adt
        ('n\'a', 'nya'),
        # non-alphanumeric transitions go above here
        (r'\W', ''),  # remove non-alphanumerics
        ('[ij]a', 'ya'),
        ('yau', 'yaw'),
        ('ie', 'y'),
        ('^u', 'w'),
        (r'([aei])n[dt]y?i$', r'\g<1>ndji'),  # d subsequently replaced
        (r'a+$', 'A'),  # Preserve terminal vowel completely
        (r'e+$', 'E'),  # Preserve terminal vowel completely
        (r'i+$', 'I'),  # Preserve terminal vowel completely
        (r'o+$', 'O'),  # Preserve terminal vowel completely
        (r'u+$', 'U'),  # Preserve terminal vowel completely
        (r'y+$', 'Y'),  # Preserve terminal vowel completely
        (r'(.)[aeiou]\1', r'\g<1>#\g<1>'),  # Preserve syllables
        (r'(.)[aeiou]\1', r'\g<1>#\g<1>'),  # 2nd run to diff nnr vs jay
        # Vowel transitions go above here
        ('[aeiou]+', ''),  # remove non-terminal vowels
        ('d', 't'),
        ('th', 't'),
        ('nh', 'n'),
        ('tyn', 'tn'),
        ('rmb', 'mb'),  # particularly nrx
        ('p', 'b'),
        ('^gn', 'ng'),
        ('k', 'g'),
        (r'(.)\1', r'\g<1>'),  # conflate repeating letters
    ]

    @staticmethod
    def signature(word):
        logging.debug(">>> %s", word.encode('utf-8'))
        word = word.lower()
        for patt, repl in NamingHelper.mappings:
            logging.debug(">%s<", word.encode('utf-8'))
            word = re.sub(patt, repl, word, flags=re.UNICODE)
        return word

    @staticmethod
    def summarise_mappings(iso_name_list):
        """summarises tuples groupoing isos by signature

        iso_name_list: list of (iso <str>, name <str>) tuples
        return type dictionary key: signature <str> value: list of isos <str>
        """
        mappings = collections.defaultdict(list)
        for iso, name in iso_name_list:
            sig = NamingHelper.signature(name)
            mappings[sig].append((iso, name))

        return mappings

    @staticmethod
    def format_mappings(mappings):
        sigs_per_iso = collections.Counter()
        isos_per_sig = collections.Counter()
        iso_sig_map = {}
        for signature in sorted(mappings.keys()):
            for iso, _ in mappings[signature]:
                iso_sig_map[iso] = collections.defaultdict(list)
        for signature in sorted(mappings.keys()):
            iso_name_map = collections.defaultdict(list)
            [iso_name_map[iso].append(name) for iso, name
             in mappings[signature]]
            [iso_sig_map[iso][signature].append(name) for iso, name
             in mappings[signature]]
            logging.info("%s (%s ISOs): %s",
                         signature,
                         len(iso_name_map.keys()),
                         iso_name_map.items())
            isos_per_sig[len(iso_name_map.keys())] += 1
        for iso in sorted(iso_sig_map.keys()):
            logging.info("%s (%s sigs): %s",
                         iso,
                         len(iso_sig_map[iso].items()),
                         iso_sig_map[iso].items())
            sigs_per_iso[len(iso_sig_map[iso].items())] += 1
        logging.info("SUMMARY: sigs per iso. %s",
                     sigs_per_iso.items())
        logging.info("SUMMARY: isos per sig. %s",
                     isos_per_sig.items())

    @staticmethod
    def get_name_summary_list(persister):
        nsl = []
        all_isos = persister.get_all_iso_codes()
        for iso in all_isos:
            name_set = set(itertools.chain(
                *persister.get_primary_names_by_iso(iso).values()))
            name_set.update(itertools.chain(
                *persister.get_alternate_names_by_iso(iso).values()))
            name_set.update(itertools.chain(
                *persister.get_dialect_names_by_iso(iso).values()))
            for name in name_set:
                nsl.append((iso, name))
        return nsl
