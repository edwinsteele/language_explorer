from language_explorer import app, settings, constants
from language_explorer.language_sources.wals import WalsAdapter
from language_explorer.language_sources.census_2011 import Census2011Adapter
from language_explorer.persistence import LanguagePersistence
from flask import render_template

lp = LanguagePersistence(settings.LANGUAGE_EXPLORER_DB_URL)
wals = WalsAdapter(settings.WALS_DB_URL)
census = Census2011Adapter(settings.CENSUS_CSV_SOURCE, lp)


@app.route('/')
def index():
    return render_template(
        'index.html',
        lp=lp,
    )


@app.route('/language/all')
def show_all_languages():
    iso_list = lp.get_all_iso_codes()
    return render_template(
        'show_all_languages.html',
        lp=lp,
        iso_list=iso_list,
    )


@app.route('/notes')
def show_notes():
    sndi_list = lp.get_same_name_different_iso_list()
    common_name_list = []
    # Same Name Different ISO
    for sndi_iso_tuple in sndi_list:
        common_name_list.append(
            lp.get_common_names_for_iso_list(sndi_iso_tuple))
    sndi_info = zip(sndi_list, common_name_list)

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

    # Census Ambiguity List
    ca_info = sorted([(census_name, matching_iso_list)
                      for census_name, matching_iso_list
                      in census.get_lang_to_iso_dict().iteritems()
                      if len(matching_iso_list) > 1])

    return render_template(
        'notes.html',
        lp=lp,
        sndi_info=sndi_info,
        sabn_info=sabn_info,
        ca_info=ca_info,
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


@app.route('/map')
def show_map():
    map_data = lp.get_map_data()
    #map_data = [d for d in map_data if d[0] in (
    #    "kkp", "gvn", "kjn", "kvs", "aea", "adt", "bia")]
    # lp needed for iso formatting
    return render_template(
        'large_map.tmpl',
        lp=lp,
        constants=constants,
        map_data=map_data,
    )


@app.route('/search')
def show_search_table():
    td = lp.get_search_table_data()
    return render_template(
        'search_static.html',
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
    ecp, _ = lp.get_english_competency_by_iso(iso639_3_code)
    wals_keys = wals.get_wals_keys_for_iso(iso639_3_code)
    jp_L1_count = lp.get_L1_speaker_count_by_iso(
        iso639_3_code, constants.JOSHUA_PROJECT_SOURCE_ABBREV)
    census_L1_count = lp.get_L1_speaker_count_by_iso(
        iso639_3_code, constants.AUS_CENSUS_2011_ABBREV)
    lat, lon = lp.get_lat_lon_from_iso(iso639_3_code)
    tindale_lat, tindale_lon = lp.get_tindale_lat_lon_from_iso(iso639_3_code)
    austlang_refs = lp.get_external_references_by_iso(
        iso639_3_code, constants.AUSTLANG_SOURCE_ABBREV)
    cannot_read_english_count = lp.get_cannot_read_english_count(iso639_3_code)
    return render_template(
        'show_language.html',
        lp=lp,
        iso639_3_code=iso639_3_code,
        primary_names_dict=pn_dict,
        alternate_names_dict=an_dict,
        dialect_names_dict=di_dict,
        classification_dict=cl_dict,
        translation_dict=tr_dict,
        constants=constants,
        wals_keys=wals_keys,
        rel_list=rel_list,
        jp_L1_count=jp_L1_count,
        census_L1_count=census_L1_count,
        english_competency_pessimistic=ecp,
        cannot_read_english_count=cannot_read_english_count,
        lat=lat, lon=lon,
        austlang_refs=austlang_refs,
        tindale_lat=tindale_lat, tindale_lon=tindale_lon,
    )
