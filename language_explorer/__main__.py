from werkzeug.contrib.fixers import ProxyFix
from language_explorer import app

from flask_debugtoolbar import DebugToolbarExtension

app.debug = True
app.config['SECRET_KEY'] = 'yourmum'
app.config['DEBUG_TB_PANELS'] = [
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

toolbar = DebugToolbarExtension(app)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.run()
