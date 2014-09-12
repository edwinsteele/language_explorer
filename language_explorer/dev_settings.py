from flask_debugtoolbar import DebugToolbarExtension

# Data sources
LANGUAGE_EXPLORER_DB_URL = 'postgresql://esteele@/language_explorer'
JPHARVEST_DB_URL = 'postgresql://esteele@/jpharvest'
WALS_DB_URL = 'postgresql://esteele@/wals2013'
SIL_RCEM_TSV_SOURCE = '/Users/esteele/Code/language_explorer/data/iso-639-3_Retirements.tab'
CENSUS_CSV_SOURCE = '/Users/esteele/Code/language_explorer/data/census_2011_LANP_ENGLP.csv'

CACHE_ROOT = "/Users/esteele/Code/language_explorer/data/.cache"
TEST_CACHE_ROOT = CACHE_ROOT  # For the moment

TOOLBAR = DebugToolbarExtension
# SECRET_KEY is required for toolbar (and only for toolbar)
SECRET_KEY = "yourmum"
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
