from werkzeug.contrib.fixers import ProxyFix
from language_explorer import app
import settings

app.debug = settings.DEBUG
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['DEBUG_TB_PANELS'] = settings.DEBUG_TB_PANELS
app.config['SERVER_NAME'] = settings.SERVER_NAME

if settings.TOOLBAR:
    toolbar = settings.TOOLBAR(app)
if settings.WSGI_APP:
    app.wsgi_app = settings.WSGI_APP(app.wsgi_app)

app.run()
