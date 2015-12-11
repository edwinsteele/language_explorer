# -*- coding utf-8 -*-

import re
import logging
# from language_explorer import constants

__author__ = 'esteele'

logging.basicConfig(level=logging.DEBUG)


class NamingHelper(object):
    mappings = [
        # (unichr(8217), unichr(39)),  # e.g. the stop in adt
        ('n\'a', 'nya'),
        # non-alphanumeric transitions go above here
        (r'\W', ''),  # remove non-alphanumerics
        ('[ij]a', 'ya'),
        ('yau', 'yaw'),
        ('ie', 'y'),
        (r'([aei])n[dt]y?i$', r'\g<1>ndji'),  # d subsequently replaced
        # Vowel transitions go above here
        ('[aeiou]+', ''),  # remove vowels
        ('d', 't'),
        ('th', 't'),
        ('nh', 'n'),
        ('tyn', 'tn'),
        ('p', 'b'),
        ('^gn', 'ng'),
        ('k', 'g'),
        (r'(.)\1', r'\g<1>'),  # conflate repeating letters
    ]

    @staticmethod
    def signature(word):
        print ">>> %s" % (word,)
        word = word.lower()
        for patt, repl in NamingHelper.mappings:
            print ">%s<" % (word,)
            word = re.sub(patt, repl, word, flags=re.UNICODE)
        return word
