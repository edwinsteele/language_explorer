from collections import defaultdict

__author__ = 'esteele'

ETHNOLOGUE_SOURCE_ABBREV = "EL"
FIND_A_BIBLE_SOURCE_ABBREV = "FB"
WALS_SOURCE_ABBREV = "WA"
JOSHUA_PROJECT_SOURCE_ABBREV = "JP"
AUSTLANG_SOURCE_ABBREV = "AL"
SIL_RCEM_SOURCE_ABBREV = "SI"

source_abbrev_name_dict = {
    ETHNOLOGUE_SOURCE_ABBREV: "Ethnologue",
    SIL_RCEM_SOURCE_ABBREV: "SIL Retired Codes",
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

RELTYPE_SIMILAR_TO = "SI"  # Ethnologue
RELTYPE_RELATED_TO = "RE"  # Ethnologue
RELTYPE_DIFFERENT_FROM = "DI"  # Ethnologue
RELTYPE_MAY_BE_INTELLIGIBLE = "MI"  # Ethnologue
RELTYPE_LIMITED_MUTUAL_INTELLIGIBILITY = "LI"  # Ethnologue

RELTYPE_RETIREMENT_CHANGE = "C"
RELTYPE_RETIREMENT_DUPLICATE = "D"
RELTYPE_RETIREMENT_NON_EXISTENT = "N"
RELTYPE_RETIREMENT_SPLIT = "S"
RELTYPE_RETIREMENT_MERGE = "M"


DIALECT_NAME = "DN"

relationship_abbrev_name_dict = {
    RELTYPE_SIMILAR_TO: "is similar to",
    RELTYPE_RELATED_TO: "is related to",
    RELTYPE_DIFFERENT_FROM: "is different to",
    RELTYPE_MAY_BE_INTELLIGIBLE: "may be intelligible with",
    RELTYPE_LIMITED_MUTUAL_INTELLIGIBILITY: "limited intelligibility with",
    RELTYPE_RETIREMENT_CHANGE: "retired, changed into",
    RELTYPE_RETIREMENT_DUPLICATE: "retired, duplicates",
    RELTYPE_RETIREMENT_NON_EXISTENT: "retired, does not exist",
    RELTYPE_RETIREMENT_SPLIT: "retired, split into",
    RELTYPE_RETIREMENT_MERGE: "retired, merged into",
}

# See note in EthnologueAdapter.get_L1_speaker_count_for_iso
SPEAKER_COUNT_NONE_EXPECTED = -1
SPEAKER_COUNT_UNKNOWN = -2
# It's helpful to have it > 0. This number should never be shown directly
SPEAKER_COUNT_FEW = 1.5

# Let's say that "few" is less than 10
SPEAKER_COUNT_FEW_THRESHOLD = 10
SPEAKER_COUNT_MANY_THRESHOLD = 100
SPEAKER_COUNT_FEW_CSS_CLASS = "speakers_few"
SPEAKER_COUNT_SOME_CSS_CLASS = "speakers_some"
SPEAKER_COUNT_MANY_CSS_CLASS = "speakers_many"
SPEAKER_COUNT_UNKNOWN_CSS_CLASS = "speakers_unknown"

# TODO: Move this into a class so that it's not executed for every module import
l1_speaker_css_class_dict = dict.fromkeys(range(1, SPEAKER_COUNT_FEW_THRESHOLD),
                                          SPEAKER_COUNT_FEW_CSS_CLASS)
l1_speaker_css_class_dict.update(dict.fromkeys(
    range(SPEAKER_COUNT_FEW_THRESHOLD, SPEAKER_COUNT_MANY_THRESHOLD),
    SPEAKER_COUNT_SOME_CSS_CLASS))
l1_speaker_css_class_dict.update({
    0: "speakers_none",
    SPEAKER_COUNT_NONE_EXPECTED: "speakers_none",
    SPEAKER_COUNT_FEW: SPEAKER_COUNT_FEW_CSS_CLASS,
    SPEAKER_COUNT_UNKNOWN: SPEAKER_COUNT_UNKNOWN_CSS_CLASS,
})
# Set default value
l1_speaker_css_class_dict = defaultdict(lambda: SPEAKER_COUNT_MANY_CSS_CLASS,
                                        l1_speaker_css_class_dict)

TABLE_SPEAKER_COUNT_COL = "SC"
