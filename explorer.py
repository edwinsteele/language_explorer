import collections
from flask import Flask
from flask import render_template
from persistence import LanguagePersister
import settings
app = Flask(__name__)

ISO639_3_TO_WALS = {
    "aly": ["aly", ],
    "aer": ["amp", "arr"],  # Actually maps to two WALS ids... "arr" too!
    "are": ["arr", "awe"],
}

ISO639_3_TO_GLOTTOCODE = {
    "aly": ["alya1239", ],
    "aer": ["east2379", ],   # only maps to one glottocode
    "are": ["west2441", ],
}

# This is really just a model placeholder!
lp = LanguagePersister(settings.LANGUAGE_EXPLORER_DB_URL)


def primary_names_from_iso(iso):
    """Return list of primary names from each data source"""
    primary_list = lp.lang_db[lp.ALIAS_TABLE]\
        .find(iso=iso, alias_type=lp.PRIMARY_NAME_TYPE)
    d = collections.defaultdict(list)
    for primary_row in primary_list:
        d[primary_row["source"]].append(primary_row["name"])
    return d


def alternate_names_from_iso(iso):
    """Return list of primary names from each data source"""
    alternate_list = lp.lang_db[lp.ALIAS_TABLE] \
        .find(iso=iso, alias_type=lp.ALTERNATE_NAME_TYPE)
    d = collections.defaultdict(list)
    for primary_row in alternate_list:
        d[primary_row["source"]].append(primary_row["name"])
        d[primary_row["source"]].sort()
    return d


@app.route('/')
def index():
        return 'Index Page'


@app.route('/language/iso639_3/<iso639_3_code>')
def show_language(iso639_3_code):
    # show the profile for the language
    pn_dict = primary_names_from_iso(iso639_3_code)
    an_dict = alternate_names_from_iso(iso639_3_code)
    return render_template(
        'show_language.html',
        iso639_3_code=iso639_3_code,
        primary_names_dict=pn_dict,
        alternate_names_dict=an_dict,
    )

if __name__ == "__main__":
        app.run(debug=True)
