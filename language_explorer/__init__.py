__author__ = 'esteele'

from flask import Flask

app = Flask(__name__)
# cyclic, in that views imports language_explorer.app
from language_explorer import views
