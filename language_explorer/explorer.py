from flask import Flask, request
from flask import render_template
from language_explorer import settings, constants
from language_explorer.language_sources.wals import WalsAdapter
from language_explorer.persistence import LanguagePersistence
from flask_debugtoolbar import DebugToolbarExtension
from flask_debugtoolbar_lineprofilerpanel.profile import line_profile


app = Flask(__name__)
# For debug toolbar
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
# toolbar = DebugToolbarExtension(app)

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
        lp=lp,
        iso_list=iso_list,
    )


@app.route('/search', methods=['GET', 'POST'])
def search_languages_by_name():
    language_name = request.form['language_name'].strip()
    iso_set = set(lp.get_iso_list_from_name(language_name))
    iso_set.update(lp.get_iso_list_from_iso(language_name))
    return render_template(
        'search.html',
        lp=lp,
        iso_list=sorted(list(iso_set)),
        search_term=language_name,
    )


@app.route('/investigations')
def show_investigations():
    sndi_list = lp.get_same_name_different_iso_list()
    common_name_list = []
    for sndi_iso_tuple in sndi_list:
        common_name_list.append(
            lp.get_common_names_for_iso_list(sndi_iso_tuple))
    sndi_info = zip(sndi_list, common_name_list)

    # SNDI list where one of the group has some confirmed scripture
    # Scripture Association By Name
    sabn_list = []
    sabn_common_name_list = []
    for sndi_iso_tuple in sndi_list:
        if filter(lambda x: lp.get_best_translation_state(x) >
                  constants.TRANSLATION_STATE_NO_SCRIPTURE,
                  sndi_iso_tuple):
            # We're only interested in languages that don't have scripture if
            #  they have active speakers. We are interested in languages that
            #  have a translation, even if they don't have any speakers
            s = filter(lambda x: (lp.get_best_translation_state(x) >
                       constants.TRANSLATION_STATE_NO_SCRIPTURE) or
                       lp.could_have_L1_speakers(x), sndi_iso_tuple)
            # If there are still two languages left, then we still have a
            #  grouping of interest
            if len(s) > 1:
                sabn_list.append(s)
    for sabn_iso_tuple in sabn_list:
        sabn_common_name_list.append(
            lp.get_common_names_for_iso_list(sabn_iso_tuple))
    sabn_info = zip(sabn_list, sabn_common_name_list)

    return render_template(
        'investigations.html',
        lp=lp,
        sndi_info=sndi_info,
        sabn_info=sabn_info,
    )


@app.route('/table')
def show_table():
    td = lp.get_table_data()
    return render_template(
        'table.html',
        table_data=td,
        lp=lp,
        constants=constants,
    )


@app.route('/language/iso/<iso639_3_code>')
def show_language(iso639_3_code):
    # show the profile for the language
    pn_dict = lp.get_primary_names_by_iso(iso639_3_code)
    an_dict = lp.get_alternate_names_by_iso(iso639_3_code)
    di_dict = lp.get_dialect_names_by_iso(iso639_3_code)
    cl_dict = lp.get_classifications_by_iso(iso639_3_code)
    rel_list = lp.get_relationships_by_iso(iso639_3_code)
    tr_dict = lp.get_translations_by_iso(iso639_3_code)
    ecp, eco = lp.get_english_competency_by_iso(iso639_3_code)
    writing_state = lp.get_writing_state_by_iso(iso639_3_code)
    wals_keys = wals.get_wals_keys_for_iso(iso639_3_code)
    eth_L1_count = lp.get_L1_speaker_count_by_iso(
        iso639_3_code, constants.ETHNOLOGUE_SOURCE_ABBREV)
    return render_template(
        'show_language.html',
        lp=lp,
        iso639_3_code=iso639_3_code,
        primary_names_dict=pn_dict,
        alternate_names_dict=an_dict,
        dialect_names_dict=di_dict,
        classification_dict=cl_dict,
        translation_dict=tr_dict,
        writing_state=writing_state,
        constants=constants,
        wals_keys=wals_keys,
        rel_list=rel_list,
        eth_L1_count=eth_L1_count,
        english_competency_pessimistic=ecp,
        english_competency_optimistic=eco,
    )

if __name__ == "__main__":
        app.run(debug=True)
