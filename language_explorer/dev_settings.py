import os
from flask_debugtoolbar import DebugToolbarExtension

# Data sources
DATA_BASEDIR = '/Users/esteele/Code/language_explorer/data'
LANGUAGE_EXPLORER_DB_URL = 'postgresql://esteele@/language_explorer'
JPHARVEST_DB_URL = 'postgresql://esteele@/jpharvest'
WALS_DB_URL = 'postgresql://esteele@/wals2013'
SIL_RCEM_TSV_SOURCE = os.path.join(DATA_BASEDIR, 'iso-639-3_Retirements.tab')
CENSUS_CSV_SOURCE = os.path.join(DATA_BASEDIR, 'census_2011_LANP_ENGLP.csv')

CACHE_ROOT = os.path.join(DATA_BASEDIR, ".cache")
TEST_CACHE_ROOT = CACHE_ROOT  # For the moment

TOOLBAR = DebugToolbarExtension
# SECRET_KEY is required for toolbar (and only for toolbar)
SECRET_KEY = "yourmum"
SERVER_NAME = "localhost:8765"
DEBUG = True
DEBUG_TB_PANELS = [
    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flask_debugtoolbar.panels.template.TemplateDebugPanel',
    'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
    'flask_debugtoolbar.panels.logger.LoggingPanel',
    'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
    # Add the line profiling
    'flask_debugtoolbar_lineprofilerpanel.panels.LineProfilerPanel'
]
