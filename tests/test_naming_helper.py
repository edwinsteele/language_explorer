# -*- coding: utf-8 -*-

from language_explorer import naming_helper
from language_explorer import data_massaging
from language_explorer.persistence import CacheableAliasRow
import unittest


class NamingHelperTestCase(unittest.TestCase):
    def setUp(self):
        self.nh = naming_helper.NamingHelper()

    def _perform_signature_test(self, ref_sig, names):
        for name in names:
            name_sig = self.nh.signature(name)
            #print "ref_sig ->%s<- name_sig ->%s<-" % \
            #    ([ord(c) for c in ref_sig],
            #     [ord(c) for c in name_sig])
            self.assertEqual(ref_sig, name_sig,
                             "name '%s' has signature '%s' instead of "
                             "expected signature of '%s'" %
                             (name, name_sig, ref_sig))

    def test_dwm_signature(self):
        self._perform_signature_test(
            "mtbrA",
            ["Mutpura", "Mudbara", "Mudbera", "Moodburra", "Mudbra",
             "Mudburra", "Madbara", "Mudbura", "Mootburra"]
        )

    def test_mfr_signature(self):
        self._perform_signature_test(
            "mrtyl",
            ["Marithiel", "Marithiyel", "Maridhiel", "Maridhiyel",
             "Marrithiyel"]
        )

    def test_adt1_signature(self):
        """ADT five syllable test, leading with an ejective, not a nasal
           Most have ^tn and a few have ^nj.
           Most have mtn$ and a few have mt$.
           Stop before vowel is different to stop before consonant
           Ignore the latter in both cases"""
        self._perform_signature_test(
            "tnymtnA",
            ["Adynyamathanha", "Ad'n'amadana", "Ad'n'amadana", "Adnyamathanha",
             "Adnymathanha", "Atynyamatana", "Atynyamathanha"]
        )

    @unittest.skip("Can't support unicode yet - perhaps translate at boundary")
    def test_adt1_unicode_signature(self):
        """ADT with unicode - per adt1"""
        self._perform_signature_test(
            "tnymtn",
            ["Ad’n’amadana"]
        )

    def test_aly_signature(self):
        """Ignore 'yowera' - diff number of syllables"""
        self._perform_signature_test(
            "lywrA",
            ["Alyawarra", "Iliaura", "Aljawara"]
        )

    def test_aly2_signature(self):
        self._perform_signature_test(
            "lywr",
            ["Alyawarr"]
        )

    def test_nid_signature(self):
        self._perform_signature_test(
            "ngntjI",
            ["Ngandi", "Ngandji"]
        )

    def test_drl_signature(self):
        self._perform_signature_test(
            "bgntjI",
            ["Paakantyi", "Paakintyi", "Bagandji",
             "Baagandji", "Paakanti"]
        )

    def test_nck_signature(self):
        self._perform_signature_test(
            "ngrA",
            ["Na-kara", "Nagara", "Nakara", "Nakarra", "Nakkara"]
        )

    def test_nrx_signature(self):
        """Ignore gnumbu, and oormbur as they look more like outliers than
        other forms"""
        self._perform_signature_test(
            "ngmbr",
            ["Ngumbur", "Ngormbur", "Ngurmbur", "Gnormbur"]
        )

    def test_guradjara_signature(self):
        """Used below for no-iso test so make sure it's being
        signature'd in line with the test below"""
        self._perform_signature_test(
            "grtyrA",
            ["Guradjara"]
        )

    def test_summarising_standard_single_iso_single_name(self):
        t = (CacheableAliasRow("aly", "Alywarr", "_"),)
        self.assertEquals(self.nh.summarise_list_as_dict(t)["lywr"],
                          set(['aly']))

    def test_summarising_standard_single_iso_mult_names(self):
        t = (CacheableAliasRow("aly", "Alywarr", "_"),
             CacheableAliasRow("aly", "Yowera", "_"))
        self.assertEquals(self.nh.summarise_list_as_dict(t)["lywr"],
                          set(['aly']))
        self.assertEquals(self.nh.summarise_list_as_dict(t)["ywrA"],
                          set(['aly']))

    def test_summarising_override_noiso(self):
        t = (CacheableAliasRow("gbd", "Guradjara", "_"),)
        self.assertEquals(self.nh.summarise_list_as_dict(t)["grtyrA"],
                          set([]))
