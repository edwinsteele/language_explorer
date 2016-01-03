import os

# Data sources
DATA_BASEDIR = '/Users/esteele/Code/language_explorer/data'
LANGUAGE_EXPLORER_DB_URL = 'postgresql://esteele@/language_explorer'
JPHARVEST_DB_URL = 'postgresql://esteele@/jpharvest'
WALS_DB_URL = 'postgresql://esteele@/wals2013'
SIL_RCEM_TSV_SOURCE = os.path.join(DATA_BASEDIR, 'iso-639-3_Retirements.tab')
CENSUS_CSV_SOURCE = os.path.join(DATA_BASEDIR, 'census_2011_LANP_ENGLP.csv')

CACHE_ROOT = os.path.join(DATA_BASEDIR, ".cache")
TEST_CACHE_ROOT = CACHE_ROOT  # For the moment
