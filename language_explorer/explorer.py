from flask import Flask, request
from flask import render_template
from language_explorer import settings, constants
from language_explorer.language_sources.wals import WalsAdapter
from language_explorer.persistence import LanguagePersistence

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
    return render_template('index.html')


@app.route('/language/all')
def show_all_languages():
    iso_list = lp.get_all_iso_codes()
    return render_template(
        'show_all_languages.html',
        iso_list=iso_list,
        lp=lp,
    )

@app.route('/search', methods=['GET', 'POST'])
def search_languages_by_name():
    language_name = request.form['language_name'].strip()
    iso_list = lp.get_iso_list_from_name(language_name)
    return render_template(
        'search.html',
        iso_list=iso_list,
        search_term=language_name,
        lp=lp,
    )

@app.route('/investigations')
def show_investigations():
    sndi_list = lp.get_same_name_different_iso_list()
    common_name_list = []
    for sndi_iso_tuple in sndi_list:
        common_name_list.append(lp.get_common_names_for_iso_list(sndi_iso_tuple))

    sndi_info = zip(sndi_list, common_name_list)
    return render_template(
        'investigations.html',
        sndi_info=sndi_info,
        lp=lp,
    )

@app.route('/language/iso/<iso639_3_code>')
def show_language(iso639_3_code):
    # show the profile for the language
    pn_dict = lp.get_primary_names_by_iso(iso639_3_code)
    an_dict = lp.get_alternate_names_by_iso(iso639_3_code)
    cl_dict = lp.get_classifications_by_iso(iso639_3_code)
    tr_dict = lp.get_translations_by_iso(iso639_3_code)
    wals_keys = wals.get_wals_keys_for_iso(iso639_3_code)
    eth_L1_count = lp.get_L1_speaker_count_by_iso(
        iso639_3_code, constants.ETHNOLOGUE_SOURCE_ABBREV)
    return render_template(
        'show_language.html',
        iso639_3_code=iso639_3_code,
        primary_names_dict=pn_dict,
        alternate_names_dict=an_dict,
        classification_dict=cl_dict,
        translation_dict=tr_dict,
        constants=constants,
        wals_keys=wals_keys,
        eth_L1_count=eth_L1_count,
    )

if __name__ == "__main__":
        app.run(debug=True)
