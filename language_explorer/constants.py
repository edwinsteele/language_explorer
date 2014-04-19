from collections import defaultdict

__author__ = 'esteele'

# Primary sources have two characters
# Implied or derived sources have three characters
ETHNOLOGUE_SOURCE_ABBREV = "EL"
ETHNOLOGUE_IMPLIED_SOURCE_ABBREV = "ELI"
FIND_A_BIBLE_SOURCE_ABBREV = "FB"
WALS_SOURCE_ABBREV = "WA"
JOSHUA_PROJECT_SOURCE_ABBREV = "JP"
AUSTLANG_SOURCE_ABBREV = "AL"
AUSTLANG_ABS_SOURCE_ABBREV = "AB"
SIL_RCEM_SOURCE_ABBREV = "SI"
SIL_RCEM_IMPLIED_SOURCE_ABBREV = "SII"
AUS_CENSUS_2011_ABBREV = "CN"

source_abbrev_name_dict = {
    ETHNOLOGUE_SOURCE_ABBREV: "Ethnologue",
    ETHNOLOGUE_IMPLIED_SOURCE_ABBREV: "Ethnologue (implied)",
    SIL_RCEM_SOURCE_ABBREV: "SIL Retired Codes",
    SIL_RCEM_IMPLIED_SOURCE_ABBREV: "SIL Retired Codes (implied)",
    FIND_A_BIBLE_SOURCE_ABBREV: "Find A Bible",
    WALS_SOURCE_ABBREV: "WALS",
    JOSHUA_PROJECT_SOURCE_ABBREV: "Joshua Project",
    AUSTLANG_SOURCE_ABBREV: "AustLang",
    AUSTLANG_ABS_SOURCE_ABBREV: "Australian Bureau of Statistics",
    AUS_CENSUS_2011_ABBREV: "Census 2011",
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

ISO_RETIRED_CSS_STATE = "retired_iso"
ISO_ACTIVE_CSS_STATE = "active_iso"

RELTYPE_SIMILAR_TO = "SI"  # Ethnologue
RELTYPE_RELATED_TO = "RE"  # Ethnologue
RELTYPE_DIFFERENT_FROM = "DI"  # Ethnologue
RELTYPE_MAY_BE_INTELLIGIBLE = "MI"  # Ethnologue
RELTYPE_LIMITED_MUTUAL_INTELLIGIBILITY = "LI"  # Ethnologue

RELTYPE_RETIREMENT_CHANGE = "C"  # SIL
RELTYPE_RETIREMENT_DUPLICATE = "D"  # SIL
RELTYPE_RETIREMENT_NON_EXISTENT = "N"  # SIL
RELTYPE_RETIREMENT_SPLIT_INTO = "S"  # SIL
RELTYPE_RETIREMENT_MERGED_INTO = "M"  # SIL

RELTYPE_RETIREMENT_SPLIT_FROM = "SF"  # SIL (implied)
RELTYPE_RETIREMENT_MERGED_FROM = "MF"  # SIL (implied)

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
    RELTYPE_RETIREMENT_SPLIT_INTO: "retired, split into",
    RELTYPE_RETIREMENT_MERGED_INTO: "retired, merged into",
    RELTYPE_RETIREMENT_SPLIT_FROM: "split from retired ISO",
    RELTYPE_RETIREMENT_MERGED_FROM: "merged from retired ISO",
}

# See note in EthnologueAdapter.get_L1_speaker_count_for_iso
SPEAKER_COUNT_NONE_EXPECTED = -1
SPEAKER_COUNT_UNKNOWN = -2
SPEAKER_COUNT_AMBIGUOUS = -3  # Census data
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

WRITING_STATE_UNWRITTEN = "U"   # Ethnologue. Unwritten
WRITING_STATE_LATIN_SCRIPT = "L"  # Ethnologue. Latin script.
WRITING_STATE_LATIN_SCRIPT_NIU = "N"  # Ethnologue. Latin script, but not in use
WRITING_STATE_NOT_RECORDED = "R"  # Not recorded in Ethnologue

writing_state_abbrev_dict = {
    WRITING_STATE_UNWRITTEN: "Unwritten",
    WRITING_STATE_LATIN_SCRIPT: "Latin script",
    WRITING_STATE_LATIN_SCRIPT_NIU: "Latin script, unused",
    WRITING_STATE_NOT_RECORDED: "Not recorded",
}
