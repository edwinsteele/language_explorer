from flask import Flask
from flask import render_template
import constants
from language_sources.wals import WalsAdapter
from persistence import LanguagePersistence
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

lp = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)
wals = WalsAdapter(settings.WALS_DB_URL)


@app.route('/')
def index():
        return '<a href="/language/all">All languages</a>'


@app.route('/language/all')
def show_all_languages():
    iso_list = lp.get_all_iso_codes()
    return render_template(
        'show_all_languages.html',
        iso_list=iso_list,
    )


@app.route('/language/iso639_3/<iso639_3_code>')
def show_language(iso639_3_code):
    # show the profile for the language
    pn_dict = lp.get_primary_names_by_iso(iso639_3_code)
    an_dict = lp.get_alternate_names_by_iso(iso639_3_code)
    cl_dict = lp.get_classifications_by_iso(iso639_3_code)
    tr_dict = lp.get_translations_by_iso(iso639_3_code)
    wals_keys = wals.get_wals_keys_for_iso(iso639_3_code)
    return render_template(
        'show_language.html',
        iso639_3_code=iso639_3_code,
        primary_names_dict=pn_dict,
        alternate_names_dict=an_dict,
        classification_dict=cl_dict,
        translation_dict=tr_dict,
        constants=constants,
        wals_keys=wals_keys,
    )

if __name__ == "__main__":
        app.run(debug=True)
