# Prod-like, but with resources in different locations

# Data sources
LANGUAGE_EXPLORER_DB_URL = 'postgresql://esteele@/language_explorer'
JPHARVEST_DB_URL = 'postgresql://esteele@/jpharvest'
WALS_DB_URL = 'postgresql://esteele@/wals2013'
SIL_RCEM_TSV_SOURCE = '/Users/esteele/Code/language_explorer/data/iso-639-3_Retirements.tab'
CENSUS_CSV_SOURCE  = '/Users/esteele/Code/language_explorer/data/census_2011_LANP_ENGLP.csv'

CACHE_ROOT = "/Users/esteele/lex_data_bundles/cache"
TEST_CACHE_ROOT = CACHE_ROOT  # For the moment
