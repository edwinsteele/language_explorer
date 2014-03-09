from collections import defaultdict

__author__ = 'esteele'

ETHNOLOGUE_SOURCE_ABBREV = "EL"
FIND_A_BIBLE_SOURCE_ABBREV = "FB"
WALS_SOURCE_ABBREV = "WA"
JOSHUA_PROJECT_SOURCE_ABBREV = "JP"
AUSTLANG_SOURCE_ABBREV = "AL"

source_abbrev_name_dict = {
    ETHNOLOGUE_SOURCE_ABBREV: "Ethnologue",
    FIND_A_BIBLE_SOURCE_ABBREV: "Find A Bible",
    WALS_SOURCE_ABBREV: "WALS",
    JOSHUA_PROJECT_SOURCE_ABBREV: "Joshua Project",
    AUSTLANG_SOURCE_ABBREV: "AustLang",
}

TRANSLATION_STATE_WHOLE_BIBLE = 5  # Findabible
TRANSLATION_STATE_NEW_TESTAMENT = 4  # Findabible
TRANSLATION_STATE_PORTIONS = 3  # Ethnologue isn't specific
TRANSLATION_STATE_COMPLETE_BOOK = 2  # Findabible
TRANSLATION_STATE_NO_SCRIPTURE = 1  # Findabible
TRANSLATION_STATE_NO_RECORD = 0
TRANSLATION_STATE_UNKNOWN_YEAR = -1
TRANSLATION_STATE_POSITIVE_YEAR = 2013  # Listed being present but no year

TRANSLATION_STATE_STATE_KEY = "TS"
TRANSLATION_STATE_YEAR_KEY = "YR"

translation_abbrev_name_dict = {
    TRANSLATION_STATE_COMPLETE_BOOK: "A book of scripture",
    TRANSLATION_STATE_PORTIONS: "Portions of scripture",
    TRANSLATION_STATE_NEW_TESTAMENT: "New Testament",
    TRANSLATION_STATE_WHOLE_BIBLE: "Whole Bible",
    TRANSLATION_STATE_NO_SCRIPTURE: "No scripture",
    TRANSLATION_STATE_NO_RECORD: "No record of any translation"
}

translation_abbrev_css_class_dict = {
    TRANSLATION_STATE_COMPLETE_BOOK: "scripture_book",
    TRANSLATION_STATE_PORTIONS: "scripture_portions",
    TRANSLATION_STATE_NEW_TESTAMENT: "scripture_nt",
    TRANSLATION_STATE_WHOLE_BIBLE: "scripture_wb",
    TRANSLATION_STATE_NO_SCRIPTURE: "scripture_none",
    TRANSLATION_STATE_NO_RECORD: "scripture_record_absent"
}


# See note in EthnologueAdapter.get_L1_speaker_count_for_iso
SPEAKER_COUNT_NONE_EXPECTED = -1
SPEAKER_COUNT_UNKNOWN = -2
# It's helpful to have it > 0. This number should never be shown directly
SPEAKER_COUNT_FEW = 1.5

# Let's say that "few" is less than 10
SPEAKER_COUNT_FEW_THRESHOLD = 10
SPEAKER_COUNT_FEW_CSS_CLASS = "speakers_few"
SPEAKER_COUNT_SOME_CSS_CLASS = "speakers_some"
SPEAKER_COUNT_UNKNOWN_CSS_CLASS = "speakers_unknown"

l1_speaker_css_class_dict = dict.fromkeys(range(1, SPEAKER_COUNT_FEW_THRESHOLD),
                                          SPEAKER_COUNT_FEW_CSS_CLASS)
l1_speaker_css_class_dict.update({
    0: "speakers_none",
    SPEAKER_COUNT_NONE_EXPECTED: "speakers_none",
    SPEAKER_COUNT_FEW: SPEAKER_COUNT_FEW_CSS_CLASS,
    SPEAKER_COUNT_UNKNOWN: SPEAKER_COUNT_UNKNOWN_CSS_CLASS,
})
# Set default value
l1_speaker_css_class_dict = defaultdict(lambda: SPEAKER_COUNT_SOME_CSS_CLASS,
                                        l1_speaker_css_class_dict)
